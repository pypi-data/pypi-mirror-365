"""
Task executor for the Coding Agent Framework using LangChain.

This module handles the execution of tasks using LangChain's agent framework,
eliminating low-level implementation details while properly supporting the
disable_system_prompt feature.
"""

import asyncio
import logging
import time
import signal
import sys
from typing import Dict, List, Any, Optional, AsyncIterator, Type
from datetime import datetime
import json

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from langchain_core.tools import BaseTool
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict
from typing import Annotated
from pydantic import BaseModel

from ..core.types import (
    TaskType, TaskStatus, ToolCall, ToolResult, 
    ExecutionMode, AgentEvent, ConversationTurn, LLMResponse, TaskResult
)
from ..core.config import AgentConfig
from ..core.path_utils import (
    parse_pydantic_output, format_pydantic_for_llm, extract_json_from_text
)
from ..llm.client import LLMClient
from ..tools.manager import ToolManager
from ..context.manager import ContextManager
from .planner import TaskPlanner


class GracefulShutdown:
    """Handle graceful shutdown for long-running operations."""
    
    def __init__(self):
        self.shutdown_requested = False
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        try:
            # Handle SIGINT (Ctrl+C) and SIGTERM
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
        except (ValueError, OSError):
            # Signal handling might not be available in all environments
            pass
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown."""
        print(f"\nReceived signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    def check_shutdown(self):
        """Check if shutdown has been requested."""
        return self.shutdown_requested


# Global shutdown handler
_shutdown_handler = GracefulShutdown()


class AgentState(TypedDict):
    """State for LangGraph workflow."""
    messages: Annotated[list, add_messages]


class CustomLangChainModel(BaseChatModel):
    """LangChain-compatible wrapper for our LLMClient."""
    
    def __init__(self, llm_client: LLMClient, config: AgentConfig, **kwargs):
        super().__init__(**kwargs)
        # Use object.__setattr__ to bypass Pydantic validation for custom attributes
        object.__setattr__(self, 'llm_client', llm_client)
        object.__setattr__(self, 'config', config)
        object.__setattr__(self, 'logger', logging.getLogger(__name__))
    
    @property
    def _llm_type(self) -> str:
        return "custom_llm_client"
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response (sync version)."""
        # Use async version and run it
        return asyncio.run(self._agenerate(messages, stop, run_manager, **kwargs))
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a response asynchronously."""
        
        # Convert LangChain messages to our format
        formatted_messages = []
        
        # Convert to our format
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                # Handle tool calls in AI messages
                if hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
                    # Create assistant message with tool calls
                    tool_calls = []
                    for tc in msg.additional_kwargs['tool_calls']:
                        tool_calls.append({
                            "id": tc.get("id"),
                            "type": "function",
                            "function": {
                                "name": tc.get("function", {}).get("name"),
                                "arguments": tc.get("function", {}).get("arguments", "{}")
                            }
                        })
                    
                    formatted_messages.append({
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": tool_calls
                    })
                else:
                    # Regular assistant message without tool calls
                    formatted_messages.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                # Handle disable_system_prompt: convert system message to user message with prefix
                if self.config.llm_config.disable_system_prompt:
                    formatted_messages.append({
                        "role": "user", 
                        "content": f"System instructions: {msg.content}"
                    })
                else:
                    formatted_messages.append({"role": "system", "content": msg.content})
            elif isinstance(msg, ToolMessage):
                # Handle disable_tool_role: convert tool message to user message with prefix
                if self.config.llm_config.disable_tool_role:
                    formatted_messages.append({
                        "role": "user",
                        "content": f"Tool result for call_id {msg.tool_call_id}: {msg.content}"
                    })
                else:
                    # Convert tool message to our format
                    formatted_messages.append({
                        "role": "tool",
                        "content": msg.content,
                        "tool_call_id": msg.tool_call_id
                    })
        
        # Call our LLM client
        response = await self.llm_client.complete_with_messages(formatted_messages)
        
        # Convert response back to LangChain format
        if response.tool_calls:
            # Create AI message with tool calls
            tool_calls = []
            for tc in response.tool_calls:
                tool_calls.append({
                    "id": tc.id or tc.call_id,
                    "type": "function", 
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments)
                    }
                })
            
            ai_message = AIMessage(
                content=response.content or "",
                additional_kwargs={"tool_calls": tool_calls}
            )
        else:
            ai_message = AIMessage(content=response.content)
        
        # Create chat generation
        generation = ChatGeneration(message=ai_message)
        return ChatResult(generations=[generation])
    
    def bind_tools(self, tools):
        """Bind tools to the model. For our implementation, this just returns self."""
        # Don't modify the LLM client's function schemas - they are already properly registered by the agent
        # The executor should not overwrite the detailed schemas with basic ones
        return self


class CustomLangChainTool(BaseTool):
    """LangChain-compatible wrapper for our tools."""
    
    def __init__(self, tool_name: str, tool_manager: ToolManager, description: str = "", executor: 'TaskExecutor' = None):
        # Initialize with proper name and description for Pydantic validation
        super().__init__(
            name=tool_name,
            description=description or f"Execute {tool_name}"
        )
        # Store additional attributes using object.__setattr__
        object.__setattr__(self, 'tool_name', tool_name)
        object.__setattr__(self, 'tool_manager', tool_manager)
        object.__setattr__(self, 'executor', executor)
    
    def _run(self, **kwargs) -> str:
        """Run the tool synchronously."""
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        """Run the tool asynchronously."""
        try:
            # Check if this tool is restricted based on execution mode
            if self._is_tool_restricted():
                return f"Error: Tool '{self.tool_name}' is only available in AGENT execution mode, not in CHAT mode."
            
            result = await self.tool_manager.execute_tool(self.tool_name, kwargs)
            if result.success:
                return str(result.result)
            else:
                return f"Error: {result.error}"
        except Exception as e:
            return f"Error executing {self.tool_name}: {str(e)}"
    
    def _is_tool_restricted(self) -> bool:
        """Check if the tool is restricted based on current execution mode."""
        if not self.executor:
            return False
        
        current_mode = self.executor.get_execution_mode()
        
        # Define tools that are only allowed in AGENT mode (read-write operations)
        agent_only_tools = {
            'edit_file',      # Can modify existing files
            'create_file',    # Can create new files
        }
        
        # Check if current tool is restricted and we're not in CHAT mode
        if self.tool_name in agent_only_tools and current_mode != ExecutionMode.AGENT:
            return True
        
        return False


class TaskExecutor:
    """Executes tasks using LangChain's agent framework."""
    
    def __init__(self, llm_client: LLMClient, tool_manager: ToolManager, 
                 context_manager: ContextManager, planner: TaskPlanner, config: AgentConfig):
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.context_manager = context_manager
        self.planner = planner
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Execution state
        self.execution_history: List[AgentEvent] = []
        self.conversation_history: List[ConversationTurn] = []
        self.current_execution_mode: ExecutionMode = ExecutionMode.CHAT  # Default to CHAT mode
        
        # Debug information
        self.debug_mode = config.debug if hasattr(config, 'debug') else False
        
        # Initialize LangChain components will be called later after tools are registered
        self.langchain_tools = []
        self.model = None
        self.model_with_tools = None
        self.workflow_app = None
        
        # Log initialization info
        self.logger.debug(f"TaskExecutor initialized with LangChain backend")
        if self.debug_mode:
            self.logger.debug(f"Available tools: {self.tool_manager.list_tools()}")
            self.logger.debug(f"disable_system_prompt: {self.config.llm_config.disable_system_prompt}")
    
    def set_execution_mode(self, execution_mode: ExecutionMode) -> None:
        """Set the current execution mode."""
        self.current_execution_mode = execution_mode
        self.logger.debug(f"Execution mode set to: {execution_mode.value}")
    
    def get_execution_mode(self) -> ExecutionMode:
        """Get the current execution mode."""
        return self.current_execution_mode
    
    def setup_langchain_components(self):
        """Set up LangChain tools, model, and workflows. Should be called after tools are registered."""
        self._setup_langchain_components()
        self.logger.debug(f"LangChain components set up with {len(self.langchain_tools)} tools")
    

    
    def _setup_langchain_components(self):
        """Set up LangChain tools, model, and workflows."""
        # Create LangChain-compatible model
        self.model = CustomLangChainModel(self.llm_client, self.config)
        
        # Convert our tools to LangChain format
        self.langchain_tools = self._create_langchain_tools()
        
        # Bind tools to model
        self.model_with_tools = self.model.bind_tools(self.langchain_tools)
        
        # Create workflow for agent execution
        self.workflow_app = self._create_workflow()
    
    def _create_langchain_tools(self) -> List[BaseTool]:
        """Convert our tool manager tools to LangChain format."""
        langchain_tools = []
        
        # Get our tool schemas
        tool_schemas = self.tool_manager.get_tool_schemas()
        available_tools = self.tool_manager.list_tools()
        
        for tool_name in available_tools:
            if self.tool_manager.is_tool_disabled(tool_name):
                continue
                
            schema = tool_schemas.get(tool_name, {})
            func_schema = schema.get('function', {})
            description = func_schema.get('description', f'Execute {tool_name}')
            
            # Create LangChain tool
            tool = CustomLangChainTool(tool_name, self.tool_manager, description, self)
            langchain_tools.append(tool)
        
        return langchain_tools
    
    def _create_workflow(self):
        """Create LangGraph workflow for agent execution."""
        # Create workflow
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(self.langchain_tools))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges using custom condition instead of tools_condition
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # Add edge back to agent
        workflow.add_edge("tools", "agent")
        
        # Compile without recursion_limit (it's passed to astream instead)
        return workflow.compile()
    
    def _should_continue(self, state: AgentState) -> str:
        """Determine whether to continue with tools or end the workflow."""
        messages = state["messages"]
        if not messages:
            return "end"
        
        last_message = messages[-1]
        
        # Check if the last message has tool calls
        has_tool_calls = self._has_tool_calls(last_message)
        
        if self.debug_mode:
            self.logger.debug(f"_should_continue: has_tool_calls={has_tool_calls}, message_type={type(last_message).__name__}")
        
        if has_tool_calls:
            return "continue"
        else:
            return "end"
    
    async def _call_model(self, state: AgentState):
        """Call model node for workflow."""
        messages = state["messages"]
        
        # Add system message if not already present
        has_system_message = any(isinstance(msg, SystemMessage) for msg in messages)
        if not has_system_message:
            system_content = self._create_system_message()
            system_msg = SystemMessage(content=system_content)
            messages = [system_msg] + messages
        
        # Call model with tools
        response = await self.model_with_tools.ainvoke(messages)
        return {"messages": [response]}
    
    def add_conversation_turn(self, turn: ConversationTurn) -> None:
        """Add a conversation turn to the history."""
        self.conversation_history.append(turn)
    
    def get_conversation_history(self) -> List[ConversationTurn]:
        """Get the conversation history."""
        return self.conversation_history
    
    async def execute_task(self, task: str, execution_mode: ExecutionMode = ExecutionMode.AGENT, 
                          context: Optional[Dict[str, Any]] = None,
                          output_pydantic: Optional[Type[BaseModel]] = None) -> AsyncIterator[AgentEvent]:
        """Execute a task using LangChain workflow with optional Pydantic output support."""
        
        # Set the execution mode for this task
        self.set_execution_mode(execution_mode)
        
        self.logger.debug(f"Executing task: {task}")
        yield AgentEvent(event_type="task_started", data={"task": task, "execution_mode": execution_mode.value})
        
        # Get timeout from configuration
        task_timeout = getattr(self.config.execution_config, 'task_timeout', 600)
        max_iterations = getattr(self.config.execution_config, 'max_iterations', 50)
        
        try:
            # Create task prompt
            prompt = await self.planner.create_task_prompt(task, context)
            
            # Add Pydantic formatting instructions if output_pydantic is specified
            if output_pydantic:
                pydantic_instructions = format_pydantic_for_llm(output_pydantic)
                prompt = f"{prompt}\n\n{pydantic_instructions}"
                self.logger.debug(f"Added Pydantic formatting instructions for model: {output_pydantic.__name__}")
            
            # Execute with LangGraph workflow with proper config and timeout
            inputs = {"messages": [HumanMessage(content=prompt)]}
            config = {
                "recursion_limit": max_iterations
            }
            
            self.logger.debug(f"Starting workflow execution with timeout: {task_timeout}s, max_iterations: {max_iterations}")
            
            final_content = ""
            execution_events = []
            iteration_count = 0
            
            # Wrap workflow execution with timeout using asyncio.wait_for for Python 3.8+ compatibility
            try:
                # Stream through the workflow with timeout and shutdown checks
                async def process_workflow_with_shutdown_checks():
                    iteration_count = 0
                    try:
                        async for event in self.workflow_app.astream(inputs, config=config):
                            # Check for graceful shutdown request before processing each event
                            if _shutdown_handler.check_shutdown():
                                self.logger.warning("Graceful shutdown requested, stopping task execution")
                                shutdown_event = AgentEvent(
                                    event_type="task_failed",
                                    data={
                                        "task": task,
                                        "error": "Task execution interrupted by shutdown request",
                                        "iteration_count": iteration_count,
                                        "shutdown_requested": True
                                    }
                                )
                                yield shutdown_event
                                raise KeyboardInterrupt("Task execution interrupted by shutdown request")
                            
                            iteration_count += 1
                            
                            # Debug log the event
                            if self.debug_mode:
                                self.logger.debug(f"Workflow event (iteration {iteration_count}): {event}")
                            
                            # Check for potential infinite loops
                            if iteration_count > max_iterations * 2:  # Safety margin
                                self.logger.warning(f"Workflow exceeded safety iteration limit ({max_iterations * 2})")
                                error_event = AgentEvent(
                                    event_type="task_failed",
                                    data={
                                        "task": task,
                                        "error": f"Execution exceeded maximum iterations ({max_iterations * 2})",
                                        "iteration_count": iteration_count
                                    }
                                )
                                yield error_event
                                raise RuntimeError(f"Execution exceeded maximum iterations ({max_iterations * 2})")
                            
                            yield event
                    except Exception as workflow_error:
                        # Handle exceptions that occur during workflow setup or iteration
                        self.logger.error(f"Workflow execution failed: {str(workflow_error)}", exc_info=True)
                        
                        # Create error event for workflow failures
                        error_event = AgentEvent(
                            event_type="task_failed",
                            data={
                                "task": task,
                                "error": f"Workflow execution failed: {str(workflow_error)}",
                                "error_type": type(workflow_error).__name__,
                                "iteration_count": iteration_count
                            }
                        )
                        yield error_event
                        raise workflow_error
                
                # Execute workflow with timeout and process events as they come
                # Create a timeout task that will cancel the workflow if it takes too long
                start_time = asyncio.get_event_loop().time()
                
                async for event in process_workflow_with_shutdown_checks():
                    # Check timeout manually since asyncio.timeout is not available in Python 3.8
                    current_time = asyncio.get_event_loop().time()
                    if current_time - start_time > task_timeout:
                        raise asyncio.TimeoutError(f"Task execution timed out after {task_timeout} seconds")
                    
                    # Check if this is already an AgentEvent (from shutdown or error)
                    if isinstance(event, AgentEvent):
                        yield event
                        if event.event_type == "task_failed" and event.data.get("shutdown_requested"):
                            raise KeyboardInterrupt("Task execution interrupted by shutdown request")
                        continue
                    
                    # Process the raw workflow event
                    try:
                        # Extract agent node information if available
                        agent_data = event.get("agent", {})
                        if not agent_data:
                            continue
                        
                        # Get messages from agent data
                        messages = agent_data.get("messages", [])
                        if not messages:
                            continue
                        
                        # Process the latest message
                        latest_message = messages[-1] if messages else None
                        if not latest_message:
                            continue
                        
                        # Handle different message types
                        message_content = getattr(latest_message, 'content', '') or ''
                        tool_calls = getattr(latest_message, 'tool_calls', []) or []
                        
                        # Check if this is a tool call message
                        if tool_calls:
                            # Emit tool call events
                            for tool_call in tool_calls:
                                tool_name = tool_call.get('name', 'unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'unknown')
                                tool_args = tool_call.get('args', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'args', {})
                                
                                tool_event = AgentEvent(
                                    event_type="tool_call_started",
                                    data={
                                        "tool_name": tool_name,
                                        "parameters": tool_args,
                                        "iteration_count": iteration_count
                                    }
                                )
                                yield tool_event
                        
                        # Handle regular content
                        if message_content and message_content.strip():
                            final_content = message_content
                            
                            # Emit LLM response event
                            response_event = AgentEvent(
                                event_type="llm_response",
                                data={
                                    "content": message_content,
                                    "has_tool_calls": bool(tool_calls),
                                    "tool_call_count": len(tool_calls) if tool_calls else 0,
                                    "iteration_count": iteration_count
                                }
                            )
                            yield response_event
                    
                    except Exception as event_error:
                        self.logger.warning(f"Error processing workflow event: {event_error}")
                        if self.debug_mode:
                            self.logger.debug(f"Event that caused error: {event}")
                        continue
                
            except asyncio.TimeoutError:
                self.logger.error(f"Task execution timed out after {task_timeout} seconds")
                timeout_event = AgentEvent(
                    event_type="task_failed",
                    data={
                        "task": task,
                        "error": f"Task execution timed out after {task_timeout} seconds",
                        "timeout": task_timeout,
                        "iterations_completed": iteration_count
                    }
                )
                yield timeout_event
                raise asyncio.TimeoutError(f"Task execution timed out after {task_timeout} seconds")
                
            except Exception as workflow_error:
                self.logger.error(f"Workflow execution failed: {str(workflow_error)}", exc_info=True)
                
                # Check for specific error types
                error_type = type(workflow_error).__name__
                if "recursion" in str(workflow_error).lower() or "maximum" in str(workflow_error).lower():
                    error_msg = f"Workflow exceeded recursion limit ({max_iterations} iterations)"
                    self.logger.error(f"Recursion limit exceeded: {error_msg}")
                else:
                    error_msg = f"Workflow execution failed: {str(workflow_error)}"
                
                workflow_error_event = AgentEvent(
                    event_type="task_failed",
                    data={
                        "task": task,
                        "error": error_msg,
                        "error_type": error_type,
                        "iterations_completed": iteration_count
                    }
                )
                yield workflow_error_event
                raise workflow_error
            
            self.logger.debug(f"Workflow completed successfully after {iteration_count} iterations")
            
            # Create TaskResult with Pydantic parsing if requested
            task_result = await self._create_task_result(
                final_content, execution_events, output_pydantic
            )
            
            # Emit task completion event with the result
            completion_event = AgentEvent(
                event_type="task_completed",
                data={
                    "task": task,
                    "result": task_result.dict(),
                    "execution_time": task_result.execution_time,
                    "iterations_completed": iteration_count
                }
            )
            execution_events.append(completion_event)
            yield completion_event
            
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}", exc_info=True)
            error_event = AgentEvent(
                event_type="task_failed",
                data={
                    "task": task,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else None
                }
            )
            yield error_event
            raise
        
        # Check for pending todos and process them automatically
        await self._check_and_process_pending_todos()
    
    async def _create_task_result(self, raw_content: str, events: List[AgentEvent], 
                                 output_pydantic: Optional[Type[BaseModel]] = None) -> TaskResult:
        """Create a TaskResult with optional Pydantic parsing."""
        start_time = datetime.now()
        
        # Calculate execution time from events
        execution_time = 0.0
        if events:
            first_event = events[0]
            last_event = events[-1]
            execution_time = (last_event.timestamp - first_event.timestamp).total_seconds()
        
        # Initialize result
        result = TaskResult(
            raw=raw_content,
            execution_time=execution_time,
            events=events,
            output_format="raw"
        )
        
        # Try to parse as Pydantic model if requested
        if output_pydantic and raw_content:
            try:
                pydantic_instance = parse_pydantic_output(raw_content, output_pydantic)
                if pydantic_instance:
                    result.pydantic = pydantic_instance
                    # Use model_dump for Pydantic V2 compatibility
                    if hasattr(pydantic_instance, 'model_dump'):
                        result.json_dict = pydantic_instance.model_dump()
                    else:
                        # Fallback for older Pydantic versions
                        result.json_dict = pydantic_instance.dict()
                    result.output_format = "pydantic"
                    self.logger.debug(f"Successfully parsed output as {output_pydantic.__name__}")
                else:
                    self.logger.warning(f"Failed to parse output as {output_pydantic.__name__}")
                    # Try to extract JSON anyway for json_dict
                    json_str = extract_json_from_text(raw_content)
                    if json_str:
                        try:
                            result.json_dict = json.loads(json_str)
                            result.output_format = "json"
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                self.logger.error(f"Error parsing Pydantic output: {str(e)}")
                # Continue with raw output
        
        return result
    
    async def execute_interactive_chat(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> AsyncIterator[AgentEvent]:
        """Execute interactive chat with enhanced error handling and monitoring."""
        
        # Get timeout from configuration
        chat_timeout = getattr(self.config.execution_config, 'timeout', 300)
        max_iterations = getattr(self.config.execution_config, 'max_iterations', 50)
        
        self.logger.debug(f"Starting interactive chat with timeout: {chat_timeout}s, max_iterations: {max_iterations}")
        
        # Initialize tool call tracking
        tool_call_tracker = {}
        
        try:
            # Execute with LangGraph workflow for streaming with proper config and timeout
            inputs = {"messages": [HumanMessage(content=user_message)]}
            config = {
                "recursion_limit": max_iterations
            }
            
            iteration_count = 0
            
            # Wrap workflow execution with timeout using asyncio.wait_for for Python 3.8+ compatibility
            try:
                # Stream through the workflow with timeout and shutdown checks
                async def process_chat_workflow_with_shutdown_checks():
                    iteration_count = 0
                    async for output in self.workflow_app.astream(inputs, config=config, stream_mode="updates"):
                        # Check for graceful shutdown request before processing each output
                        if _shutdown_handler.check_shutdown():
                            self.logger.warning("Graceful shutdown requested, stopping interactive chat")
                            shutdown_event = AgentEvent(
                                event_type="task_failed",
                                data={
                                    "error": "Interactive chat interrupted by shutdown request",
                                    "iteration_count": iteration_count,
                                    "shutdown_requested": True
                                }
                            )
                            yield shutdown_event
                            raise KeyboardInterrupt("Interactive chat interrupted by shutdown request")
                        
                        iteration_count += 1
                        
                        # Debug log the output
                        if self.debug_mode:
                            self.logger.debug(f"Interactive chat workflow output (iteration {iteration_count}): {output}")
                        
                        # Check for potential infinite loops
                        if iteration_count > max_iterations * 2:  # Safety margin
                            self.logger.warning(f"Interactive chat exceeded safety iteration limit ({max_iterations * 2})")
                            error_event = AgentEvent(
                                event_type="task_failed",
                                data={
                                    "error": f"Interactive chat exceeded maximum iterations ({max_iterations * 2})",
                                    "iteration_count": iteration_count
                                }
                            )
                            yield error_event
                            raise RuntimeError(f"Interactive chat exceeded maximum iterations ({max_iterations * 2})")
                        
                        yield output
                
                # Execute workflow with timeout and process outputs as they come
                # Create a timeout task that will cancel the workflow if it takes too long
                start_time = asyncio.get_event_loop().time()
                
                async for output in process_chat_workflow_with_shutdown_checks():
                    # Check timeout manually since asyncio.timeout is not available in Python 3.8
                    current_time = asyncio.get_event_loop().time()
                    if current_time - start_time > chat_timeout:
                        raise asyncio.TimeoutError(f"Interactive chat timed out after {chat_timeout} seconds")
                    # Process each output immediately
                    for node_name, node_output in output.items():
                        if node_name == "agent":
                            # Agent response
                            message = node_output["messages"][-1]
                            has_tool_calls = self._has_tool_calls(message)
                            tool_call_count = 0
                            
                            if has_tool_calls:
                                # Extract and track tool calls
                                tool_calls = self._extract_tool_calls(message)
                                tool_call_count = len(tool_calls)
                                
                                # Emit tool_call_started events and track them
                                for tool_call in tool_calls:
                                    start_time = time.time()
                                    tool_call_tracker[tool_call.id or tool_call.call_id] = {
                                        "tool_name": tool_call.name,
                                        "start_time": start_time,
                                        "parameters": tool_call.arguments
                                    }
                                    
                                    yield AgentEvent(
                                        event_type="tool_call_started",
                                        data={
                                            "tool_name": tool_call.name,
                                            "parameters": tool_call.arguments,
                                            "call_id": tool_call.id or tool_call.call_id,
                                            "iteration": iteration_count
                                        }
                                    )
                            
                            # Check if this is a final response (no tool calls)
                            if not has_tool_calls and hasattr(message, 'content') and message.content:
                                yield AgentEvent(
                                    event_type="llm_response",
                                    data={
                                        "content": message.content,
                                        "finish_reason": "stop",
                                        "model": self.config.llm_config.model,
                                        "iteration": iteration_count
                                    }
                                )
                        
                        elif node_name == "tools":
                            # Tool execution results
                            messages = node_output["messages"]
                            for message in messages:
                                if hasattr(message, 'tool_call_id') and message.tool_call_id in tool_call_tracker:
                                    # Calculate execution time
                                    tracker_info = tool_call_tracker[message.tool_call_id]
                                    execution_time = time.time() - tracker_info["start_time"]
                                    
                                    # Determine success based on message content
                                    success = not (hasattr(message, 'content') and 
                                                 message.content and 
                                                 'error' in str(message.content).lower())
                                    
                                    yield AgentEvent(
                                        event_type="tool_call_completed",
                                        data={
                                            "tool_name": tracker_info["tool_name"],
                                            "tool_call_id": message.tool_call_id,
                                            "success": success,
                                            "result": message.content if hasattr(message, 'content') else str(message),
                                            "execution_time": execution_time,
                                            "iteration": iteration_count
                                        }
                                    )
                                    
                                    # Remove from tracker
                                    del tool_call_tracker[message.tool_call_id]
                        
            except asyncio.TimeoutError:
                self.logger.error(f"Interactive chat timed out after {chat_timeout} seconds")
                timeout_event = AgentEvent(
                    event_type="task_failed",
                    data={
                        "error": f"Interactive chat timed out after {chat_timeout} seconds",
                        "timeout": chat_timeout,
                        "iterations_completed": iteration_count
                    }
                )
                yield timeout_event
                raise asyncio.TimeoutError(f"Interactive chat timed out after {chat_timeout} seconds")
                
            except Exception as workflow_error:
                # Don't catch TimeoutError here - let it bubble up
                if isinstance(workflow_error, asyncio.TimeoutError):
                    raise workflow_error
                    
                self.logger.error(f"Interactive chat workflow failed: {str(workflow_error)}", exc_info=True)
                
                # Check for specific error types
                error_type = type(workflow_error).__name__
                if "recursion" in str(workflow_error).lower() or "maximum" in str(workflow_error).lower():
                    error_msg = f"Interactive chat exceeded recursion limit ({max_iterations} iterations)"
                    self.logger.error(f"Recursion limit exceeded in chat: {error_msg}")
                else:
                    error_msg = f"Interactive chat workflow failed: {str(workflow_error)}"
                
                workflow_error_event = AgentEvent(
                    event_type="task_failed",
                    data={
                        "error": error_msg,
                        "error_type": error_type,
                        "iterations_completed": iteration_count
                    }
                )
                yield workflow_error_event
                raise workflow_error
            
            self.logger.debug(f"Interactive chat completed successfully after {iteration_count} iterations")
            
            # Emit completion event
            yield AgentEvent(
                event_type="chat_completed",
                data={
                    "message": "Interactive chat completed successfully",
                    "iterations_completed": iteration_count
                },
                timestamp=datetime.now()
            )
            
            # Check for pending todos and process them automatically
            await self._check_and_process_pending_todos()

        except Exception as e:
            # Don't catch TimeoutError here - let it bubble up for proper test handling
            if isinstance(e, asyncio.TimeoutError):
                raise e
                
            self.logger.error(f"Interactive chat failed: {str(e)}", exc_info=True)
            yield AgentEvent(
                event_type="task_failed",
                data={
                    "error": f"Chat execution failed: {str(e)}",
                    "error_type": type(e).__name__,
                    "traceback": str(e.__traceback__) if hasattr(e, '__traceback__') else None
                },
                timestamp=datetime.now()
            )
            
            # Even on failure, check for pending todos and process them
            await self._check_and_process_pending_todos()
    
    def _has_tool_calls(self, message) -> bool:
        """Check if a message has tool calls."""
        if hasattr(message, 'tool_calls') and message.tool_calls:
            return True
        if (hasattr(message, 'additional_kwargs') and 
            message.additional_kwargs and 
            'tool_calls' in message.additional_kwargs and
            message.additional_kwargs['tool_calls']):
            return True
        return False
    
    def _extract_tool_calls(self, message) -> List[ToolCall]:
        """Extract tool calls from a message."""
        tool_calls = []
        
        # Check for tool_calls attribute
        if hasattr(message, 'tool_calls') and message.tool_calls:
            for tc in message.tool_calls:
                tool_call = ToolCall(
                    id=tc.get('id', ''),
                    name=tc.get('name', ''),
                    arguments=tc.get('args', {}),
                    call_id=tc.get('id', '')
                )
                tool_calls.append(tool_call)
        
        # Check for additional_kwargs
        elif (hasattr(message, 'additional_kwargs') and 
              message.additional_kwargs and 
              'tool_calls' in message.additional_kwargs and
              message.additional_kwargs['tool_calls']):
            for tc in message.additional_kwargs['tool_calls']:
                # Parse arguments if they are a JSON string
                arguments = tc.get('function', {}).get('arguments', {})
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                
                tool_call = ToolCall(
                    id=tc.get('id', ''),
                    name=tc.get('function', {}).get('name', ''),
                    arguments=arguments,
                    call_id=tc.get('id', '')
                )
                tool_calls.append(tool_call)
        
        return tool_calls
    
    async def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "execution_history_count": len(self.execution_history),
            "conversation_history_count": len(self.conversation_history),
            "debug_mode": self.debug_mode,
            "langchain_tools_count": len(self.langchain_tools),
            "disable_system_prompt": self.config.llm_config.disable_system_prompt,
            "backend": "LangChain + LangGraph"
        }
    
    async def pause_execution(self) -> bool:
        """Pause execution."""
        self.logger.debug("Execution pause requested")
        return True
    
    async def resume_execution(self) -> bool:
        """Resume execution."""
        self.logger.debug("Execution resume requested")
        return True
    
    async def cancel_execution(self) -> bool:
        """Cancel execution."""
        self.logger.debug("Execution cancel requested")
        return True

    async def cleanup(self) -> None:
        """Clean up resources used by the executor."""
        try:
            # Clear execution history and conversation history
            self.execution_history.clear()
            self.conversation_history.clear()
            
            # Clear LangChain components
            self.langchain_tools.clear()
            self.model = None
            self.model_with_tools = None
            self.workflow_app = None
            
            self.logger.debug("TaskExecutor cleanup complete")
            
        except Exception as e:
            # Log cleanup error but don't raise
            self.logger.warning(f"Warning: Error during executor cleanup: {e}")

    def _create_system_message(self) -> str:
        """
        Create a comprehensive system message for the coding agent.
        
        Note: When disable_system_prompt=True, this message will be automatically
        converted to a user message prefix by the CustomLangChainModel.
        """
        
        self.logger.debug("Creating comprehensive system prompt for coding agent")
        
        available_tools = self.tool_manager.list_tools()
        tools_list = ", ".join(available_tools[:10])
        if len(available_tools) > 10:
            tools_list += f", and {len(available_tools) - 10} more"
        
        if self.debug_mode:
            self.logger.debug(f"Including {len(available_tools)} tools in system prompt: {tools_list}")
        
        system_message = f"""You are an intelligent coding assistant.
Your primary directive is to EXPLORE COMPREHENSIVELY before making decisions.

## CRITICAL EXPLORATION PRINCIPLES
**EXPLORE BEFORE DECIDING** - This is your most important rule:
- ALWAYS Collect complete context before making decisions.
- ALWAYS Follow variables/functions/classes/methods/etc, back to their definitions and usages.
- ALYWAS analyze multiple file when asked about "files" (plural).
- ALWAYS discover instead of guessing.
- ALWAYS discover instead of asking users to provide more information.
- ALWAYS use multiple tools and multiple searches to build complete understanding.
- ALWAYS validate assumptions through systematic exploration.
- ALWAYS focus on the task requirements and ensure fulling the task and only the task. 

## TOOLS Guidelines
**IMPORTANT**: Tools are shown with short descriptions only.
When you need to use a tool for the first time of that tool or need detailed catalog information:
1. **Call `get_tool_help(tool_name="tool_name")` first** to get (the full documentation, examples, and parameters).
2. **Review the full documentation**: Understand parameters, examples, and use cases.
3. **Then use the tool properly**: Apply it with the correct parameters and approach.

Example:
```
# First time using a tool
get_tool_help(tool_name="read_file")  # Get full documentation
# Then use it properly with full understanding
read_file(file_path="...", start_line=1, end_line=50)
```

Use them systematically and in parallel when possible.

## 📋 SYSTEMATIC APPROACH STRATEGIES
### For code analysis and exploration:
1. **Start with structure**:
- Use the search tools and the directory tools.
- When searching file content, use both semantic and keyword search.

2. **Deep dive systematically**:
- Read the snippets require for you to undertand and not miss any case.
- For files > 500 lines, try not to read the whole file, but read the snippets required for you to undertand and not miss any case.

## PARALLEL TOOL USAGE
**Use multiple tools simultaneously** when gathering information
Run multiple searches with different patterns and explore directories in parallel.

## VALIDATION AND VERIFICATION
**Always verify your findings**:
- ALWAYS test your implementation either by unit testing or executing the business logic snippet.
- Cross-reference results from multiple tools.
- Validate file existence before reading.
- Confirm patterns match actual project structure.
- Double-check assumptions with additional searches.

## 🎯 DECISION FRAMEWORK
**Execute the task directly when:**
- Reading or modifying single files
- Performing simple searches or analysis
- Getting project information
- Making straightforward changes

**Create a todo list when:**
- Implementing features across more than 10 files.
- Complex refactoring operations.
- System-wide changes or configurations
- Multi-step operations requiring coordination

## 🚨 CRITICAL REMINDERS
1. **USE get_tool_help() FIRST** when using unfamiliar or complex tools.
2. **NEVER analyze just one random file** when asked about multiple files.
3. **ALWAYS discover options first** before making selections.
4. **USE EVIDENCE** - base conclusions on systematic analysis.
5. **VALIDATE ASSUMPTIONS** - check your understanding with tools.
6. **BE COMPREHENSIVE** - provide complete, thorough answers.
7. **Never ask users to provide more information**.

Remember: You are not just a tool executor - you are an intelligent senior developer.
Think systematically, explore comprehensively, and provide evidence-based insights.
"""

        self.logger.debug(f"System prompt created: {len(system_message)} characters")
        
        return system_message
    
    async def _check_and_process_pending_todos(self) -> None:
        """
        Check for pending todos and automatically trigger processing if any exist.
        """
        try:
            # Import the todo functions
            from ..tools.categories.task_tools import todo_read, todo_process
            
            # Check for pending todos
            todo_result = await todo_read.execute()
            
            if not todo_result.success:
                self.logger.debug(f"Could not check todos: {todo_result.error}")
                return
            
            todo_data = todo_result.result
            aggregated_stats = todo_data.get("aggregated_statistics", {})
            not_started_tasks = aggregated_stats.get("not_started", 0)
            
            if not_started_tasks > 0:
                self.logger.info(f"Found {not_started_tasks} pending tasks, processing automatically...")
                
                # Process all pending tasks
                process_result = await todo_process.execute(process_all=True)
                
                if process_result.success:
                    result_data = process_result.result
                    successful_tasks = result_data.get("successful_tasks", 0)
                    failed_tasks = result_data.get("failed_tasks", 0)
                    
                    if successful_tasks > 0:
                        self.logger.info(f"Successfully processed {successful_tasks} tasks")
                    
                    if failed_tasks > 0:
                        self.logger.warning(f"{failed_tasks} tasks failed")
                        
                else:
                    self.logger.error(f"Failed to process todos: {process_result.error}")
            else:
                self.logger.debug("No pending tasks found")
                
        except Exception as e:
            self.logger.debug(f"Error checking/processing todos: {str(e)}")