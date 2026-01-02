"""Agent abstraction with Gemini API integration.

This module defines a reusable Agent class that:
- Executes LLM calls via Gemini
- Supports tool/function calling
- Allows hierarchical composition via sub-agents
- Provides lifecycle hooks for post-processing
"""
import asyncio
import json
from typing import List, Dict, Any, Optional, Callable
from google.genai import types as genai_types


class Agent:
    """LLM-powered agent with tool support and optional sub-agent orchestration.

    An Agent represents a single reasoning/execution unit that can:
    - Call a Gemini model
    - Invoke registered tools/functions
    - Delegate work to sub-agents
    - Post-process results via callbacks
    """
    
    def __init__(
        self,
        name: str,
        model: str,
        description: str = "",
        instruction: str = "",
        tools: Optional[List[Any]] = None,
        sub_agents: Optional[List['Agent']] = None,
        output_key: Optional[str] = None,
        after_agent_callback: Optional[Callable] = None,
        **kwargs
    ):
        # Agent identity and model configuration
        self.name = name
        self.model = model
        
        # High-level role and behavioral instructions
        self.description = description
        self.instruction = instruction
        
        # Execution extensions
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        
        # Output routing / post-processing metadata
        self.output_key = output_key
        self.after_agent_callback = after_agent_callback
        
        # Model generation parameters (temperature, top_p, etc.)
        self.kwargs = kwargs
        
        # Runtime state (initialized later)
        self.client = None
        self.context = {}
        
    def __repr__(self):
        """Readable representation for debugging and logs."""
        return f"Agent(name='{self.name}', model='{self.model}')"
    
    async def initialize(self, client):
        """Attach a Gemini client to this agent and all sub-agents.

        This method must be called before `run()` to ensure
        the agent has access to the LLM backend.
        """
        self.client = client
        for sub_agent in self.sub_agents:
            await sub_agent.initialize(client)
        
    async def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the agent on a given prompt and optional shared context.

        Handles:
        - Prompt and system instruction construction
        - Tool configuration
        - LLM execution
        - Sub-agent delegation
        - Post-execution callbacks
        """
        if not self.client:
            raise RuntimeError(f"Agent {self.name} not initialized with client")
        
        # Store execution-scoped context
        self.context = context or {}
        
        # Construct system-level instructions (role, constraints, metadata)
        system_instruction = self._build_system_instruction()
        
        # Combine user prompt with structured context
        full_prompt = self._build_full_prompt(prompt)
        
        # Prepare Gemini-compatible tool declarations
        tool_config = self._prepare_tool_config()
        
        try:
            # Execute the primary LLM call
            response = await self._execute_llm(
                full_prompt,
                system_instruction,
                tool_config
            )
            
            # Sequentially run sub-agents on the parent response
            if self.sub_agents:
                response = await self._execute_sub_agents(response)
            
            # Optional post-processing hook
            if self.after_agent_callback:
                from .callback_context import CallbackContext
                ctx = CallbackContext(agent=self, response=response)
                callback_result = self.after_agent_callback(ctx)
                if callback_result:
                    response = callback_result
            
            # Standardized agent output envelope
            return {
                "agent": self.name,
                "response": response,
                "output_key": self.output_key
            }
            
        except Exception as e:
            # Fail safely without crashing the agent runtime
            return {
                "agent": self.name,
                "error": str(e),
                "output_key": self.output_key
            }
    
    def _build_system_instruction(self) -> str:
        """Assemble the system instruction passed to the LLM.

        Includes:
        - Agent role description
        - Behavioral instructions
        - Available tools
        - Sub-agent awareness
        """
        parts = []
        
        if self.description:
            parts.append(f"Role: {self.description}")
        
        if self.instruction:
            parts.append(f"Instructions: {self.instruction}")
        
        if self.tools:
            tool_names = [getattr(t, 'name', 'tool') for t in self.tools]
            parts.append(f"Available tools: {', '.join(tool_names)}")
        
        if self.sub_agents:
            agent_names = [a.name for a in self.sub_agents]
            parts.append(f"Sub-agents: {', '.join(agent_names)}")
        
        return "\n\n".join(parts)
    
    def _build_full_prompt(self, prompt: str) -> str:
        """Merge the user prompt with structured execution context.

        Context is serialized in a readable, model-friendly format.
        """
        if not self.context:
            return prompt
        
        context_str = "\n\nContext:\n"
        for key, value in self.context.items():
            if isinstance(value, (dict, list)):
                context_str += f"- {key}: {json.dumps(value, indent=2)}\n"
            else:
                context_str += f"- {key}: {value}\n"
        
        return prompt + context_str
    
    def _prepare_tool_config(self) -> Optional[Dict[str, Any]]:
        """Convert registered tools into Gemini function declarations.

        Returns None if no valid tools are available.
        """
        if not self.tools:
            return None
        
        tool_declarations = []
        for tool in self.tools:
            if hasattr(tool, 'to_gemini_declaration'):
                tool_declarations.append(tool.to_gemini_declaration())
        
        if not tool_declarations:
            return None
        
        return {
            "function_declarations": tool_declarations
        }
    
    async def _execute_llm(
        self,
        prompt: str,
        system_instruction: str,
        tool_config: Optional[Dict[str, Any]]
    ) -> str:
        """Execute a Gemini model call with optional tool support.

        Handles:
        - Generation configuration
        - Tool-aware requests
        - Tool call detection and execution
        """
        from google import genai
        
        # Model generation parameters
        config = {
            "temperature": self.kwargs.get("temperature", 0.7),
            "top_p": self.kwargs.get("top_p", 0.95),
            "top_k": self.kwargs.get("top_k", 40),
            "max_output_tokens": self.kwargs.get("max_output_tokens", 2048),
        }
        
        # User content payload
        contents = [
            genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=prompt)]
            )
        ]
        
        # Request configuration
        generate_kwargs = {
            "model": self.model,
            "contents": contents,
            "config": genai_types.GenerateContentConfig(**config)
        }
        
        if system_instruction:
            generate_kwargs["config"].system_instruction = system_instruction
        
        if tool_config:
            generate_kwargs["config"].tools = [tool_config]
        
        # Invoke Gemini
        response = await self.client.aio.models.generate_content(**generate_kwargs)
        
        # Inspect model output for tool calls or text responses
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        # Execute the requested tool
                        return await self._execute_tool_call(part.function_call)
                
                # Default to returning textual output
                return candidate.content.parts[0].text
        
        return str(response.text) if hasattr(response, 'text') else ""
    
    async def _execute_tool_call(self, function_call) -> str:
        """Execute a tool invoked by the LLM.

        Matches the function name to a registered tool and
        returns the serialized result.
        """
        function_name = function_call.name
        args = dict(function_call.args) if hasattr(function_call, 'args') else {}
        
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name == function_name:
                if hasattr(tool, 'execute'):
                    result = await tool.execute(**args)
                    return json.dumps(result)
                elif hasattr(tool, 'func'):
                    result = tool.func(**args)
                    return json.dumps(result)
        
        return json.dumps({"error": f"Tool {function_name} not found"})
    
    async def _execute_sub_agents(self, parent_response: str) -> str:
        """Run sub-agents sequentially using the parent agent's response.

        Each sub-agent receives the same context and the
        previous agent’s output as its prompt.
        """
        results = [f"[{self.name} Initial Response]\n{parent_response}"]
        
        for sub_agent in self.sub_agents:
            result = await sub_agent.run(
                prompt=parent_response,
                context=self.context
            )
            response_text = result.get("response", "")
            results.append(f"\n[{sub_agent.name} Response]\n{response_text}")
        
        return "\n".join(results)
