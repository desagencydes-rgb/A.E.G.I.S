"""
Orchestrator Agent
Central coordinator that routes tasks to specialized agents
"""

from typing import Dict, Any, List, AsyncGenerator, Optional
from agents.base_agent import BaseAgent
from agents.researcher import ResearchAgent
from agents.coding import CodingAgent
from agents.tool_executor import ToolExecutorAgent
from agents.security_agent import SecurityAgent
# FeatureDevAgent imported lazily in __init__ to avoid circular dependency
from core.mode import ModeManager, Mode
from tools.definitions import get_tool_definitions
from memory.manager import MemoryManager
from loguru import logger
import json
import ollama
from core.config import config

class OrchestratorAgent(BaseAgent):
    """
    Main agent that handles user interaction and delegation
    """
    
    def __init__(self):
        super().__init__(
            name="Orchestrator",
            agent_type="orchestrator"
        )
        
        # Initialize sub-agents
        self.researcher = ResearchAgent()
        self.coder = CodingAgent()
        self.security = SecurityAgent()
        self.tool_executor = ToolExecutorAgent()
        
        # Lazy import to avoid circular dependency
        from agents.feature_dev import FeatureDevAgent
        self.feature_dev = FeatureDevAgent()
        
        self.memory_manager = MemoryManager() # Renamed to avoid confusion with BaseAgent potential future props
        
        # Initialize mode manager
        self.mode_manager = ModeManager()
        
        # Load tools
        self.tools = get_tool_definitions()
        
        logger.info("OrchestratorAgent initialized with sub-agents and memory")

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a specific task delegated to this agent
        For Orchestrator, this wraps handle_message
        """
        message = task.get("message") or task.get("instruction")
        if not message:
            return {"success": False, "error": "No message provided"}
            
        response = ""
        async for chunk in self.handle_message(message):
            response += chunk
            
        return {"success": True, "result": response}

    async def handle_message(self, user_message: str) -> AsyncGenerator[str, None]:
        """
        Main loop: Process user message, switch modes, delegate tools
        """
        # 1. Check for mode switch commands
        if user_message.startswith("/"):
            response = self.mode_manager.handle_command(user_message)
            yield f"{response}\n"
            return

        # 2. Retrieve Context from Memory (RAG)
        context_str = ""
        try:
             memories = await self.memory_manager.search_memory(user_message, limit=3)
             if memories:
                 context_str = "\n".join(memories)
                 yield f"🧠 Recalled {len(memories)} memories...\n"
        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")

        # 3. Prepare messages with context
        messages = self._prepare_messages(user_message)
        
        # Inject memory context if available
        if context_str:
            # We insert it as a system message or user message context
            # Let's append it to the last user message or add a system note
            # Adding as system context is safer
            messages.insert(1, {
                "role": "system",
                "content": f"RELEVANT MEMORY CONTEXT:\n{context_str}\n\nUse this context to answer if relevant. If the answer is in memory, you do not need to use tools."
            })

        client = ollama.AsyncClient(host=config.ollama_host)
        
        # Get current model based on mode
        self.model = config.orchestrator_model
        
        # Model options
        options = {
            "num_ctx": config.max_context,
            "temperature": config.mode_config.get("mode", {}).get("temperature", 0.7)
        }

        try:
            # 4. Chat with LLM (First pass to see if tools are needed)
            logger.debug(f"Sending request to model {self.model} with {len(messages)} messages")
            response = await client.chat(
                model=self.model,
                messages=messages,
                options=options,
                tools=self.tools,
                stream=False # Tool calling usually requires non-streaming first to get the JSON
            )
            
            message = response['message']
            logger.debug(f"Received message from LLM with role: {message.get('role')}")
            
            # Check for tool calls
            if message.get('tool_calls'):
                logger.info(f"Model requested {len(message['tool_calls'])} tool calls")
                # Execute tools
                for tool_call in message['tool_calls']:
                    function_name = tool_call['function']['name']
                    args = tool_call['function']['arguments']
                    
                    yield f"🛠️ Executing: {function_name}...\n"
                    
                    result = None
                    if function_name == "delegate_research":
                        # We pass the memory manager if needed, but researcher has its own now
                        result = await self.researcher.process_task(args)
                    elif function_name == "delegate_coding":
                        result = await self.coder.process_task(args)
                    elif function_name == "delegate_security":
                        # Delegate to Security Agent (HAT mode)
                        result = await self.security.process_task(args)
                    elif function_name == "delegate_feature_dev":
                        # Delegate to Feature Development Agent
                        feature_request = args.get("feature_request")
                        yield f"\n🚀 Starting Feature Development Workflow...\n"
                        async for update in self.feature_dev.start_workflow(feature_request):
                            yield update
                        result = {"success": True, "result": "Feature development workflow initiated"}
                    else:
                        # Fallback to ToolExecutor for other tools(read_file, etc)
                        task = {
                            "tool": function_name,
                            "params": args,
                            "user_message": user_message
                        }
                        result = await self.tool_executor.process_task(task)
                        
                    # Add result to history
                    # Convert message object to dict if needed (Ollama returns Message objects)
                    if isinstance(message, dict):
                        messages.append(message)
                    else:
                        # Convert Message object to dict
                        messages.append({
                            "role": message.get("role", "assistant"),
                            "content": message.get("content", ""),
                            "tool_calls": message.get("tool_calls", [])
                        })
                    
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result),
                        "name": function_name
                    })
                    
                    # Yield tool output summary
                    if result.get('success'):
                        yield f"✅ Tool {function_name} completed.\n"
                        if function_name == "delegate_research":
                            yield f"📝 Research Summary:\n{result.get('result')}\n\n"
                        elif function_name == "delegate_coding":
                            yield f"💻 Coding Action: {result.get('action')}\n\n"
                        elif function_name == "delegate_security":
                            yield f"🔒 Security Scan:\n{result.get('report', result.get('result'))}\n\n"
                    else:
                        yield f"❌ Tool {function_name} failed: {result.get('error')}\n"

                # Get final response after tool execution
                async for part in await client.chat(
                    model=self.model,
                    messages=messages,
                    options=options,
                    stream=True
                ):
                    if 'message' in part and 'content' in part['message']:
                        yield part['message']['content']

                # 5. Save final interaction to memory
                # We can't easily capture the full streamed response here to save it
                # The main loop handles display, but we should probably save it.
                # ideally, the main loop calls memory.add, but we can do it here if we aggregate.
                # For now, let's rely on the individual agents saving their specialized outputs.
                        
            else:
                # No tool calls, just yield the content
                content = message.get('content')
                if content:
                    yield content
                else:
                    logger.warning("LLM returned empty content and no tool calls")
                    yield "I processed your request but didn't have anything to say or a tool to call. Could you please rephrase?"
                
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            yield f"❌ Error: {str(e)}"
            
    def get_mode_display(self) -> str:
        return self.mode_manager.current_mode.value.upper()
