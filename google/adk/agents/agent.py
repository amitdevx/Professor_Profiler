"""Provider-neutral agent abstraction with Gemini and NVIDIA NIM support.

This module defines a reusable Agent class that:
- Executes LLM calls via Gemini or an OpenAI-compatible NIM client
- Supports tool/function calling
- Allows hierarchical composition via sub-agents
- Provides lifecycle hooks for post-processing
"""
import json
import logging
import os
from typing import Any, Callable, Dict, List, Optional

from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class Agent:
    """LLM-powered agent with tool support and optional sub-agent orchestration."""

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
        gemini_model: Optional[str] = None,
        nim_model: Optional[str] = None,
        **kwargs
    ):
        self.name = name
        self.model = model
        self.gemini_model = gemini_model
        self.nim_model = nim_model
        self.description = description
        self.instruction = instruction
        self.tools = tools or []
        self.sub_agents = sub_agents or []
        self.output_key = output_key
        self.after_agent_callback = after_agent_callback
        self.kwargs = kwargs
        self.client = None
        self.provider = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.context = {}

    def __repr__(self):
        """Readable representation for debugging and logs."""
        return f"Agent(name='{self.name}', model='{self.model}')"

    async def initialize(self, client, provider: Optional[str] = None):
        """Attach an LLM client to this agent and all sub-agents."""
        self.client = client
        self.provider = (provider or getattr(client, "provider", None) or os.getenv("LLM_PROVIDER", "gemini")).lower()
        for sub_agent in self.sub_agents:
            await sub_agent.initialize(client, provider=self.provider)

    async def run(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Execute the agent on a given prompt and optional shared context."""
        if not self.client:
            raise RuntimeError(f"Agent {self.name} not initialized with client")

        self.context = context or {}
        system_instruction = self._build_system_instruction()
        full_prompt = self._build_full_prompt(prompt)
        tool_config = self._prepare_tool_config()

        try:
            response = await self._execute_llm(
                full_prompt,
                system_instruction,
                tool_config
            )

            if self.sub_agents:
                response = await self._execute_sub_agents(response)

            if self.after_agent_callback:
                from .callback_context import CallbackContext
                ctx = CallbackContext(agent=self, response=response)
                callback_result = self.after_agent_callback(ctx)
                if callback_result:
                    response = callback_result

            return {
                "agent": self.name,
                "response": response,
                "output_key": self.output_key,
                "provider": self._current_provider(),
            }

        except Exception as e:
            logger.exception("Agent %s failed", self.name)
            return {
                "agent": self.name,
                "error": str(e),
                "output_key": self.output_key,
                "provider": self._current_provider(),
            }

    def _build_system_instruction(self) -> str:
        """Assemble the system instruction passed to the LLM."""
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
        """Merge the user prompt with structured execution context."""
        if not self.context:
            return prompt

        context_str = "\n\nContext:\n"
        for key, value in self.context.items():
            if isinstance(value, (dict, list)):
                context_str += f"- {key}: {json.dumps(value, indent=2)}\n"
            else:
                context_str += f"- {key}: {value}\n"

        return prompt + context_str

    def _prepare_tool_config(self) -> Optional[Any]:
        """Convert registered tools into the active provider's tool schema."""
        if not self.tools:
            return None

        provider = self._current_provider()
        if provider == "nim":
            tool_declarations = []
            for tool in self.tools:
                if hasattr(tool, 'to_openai_schema'):
                    tool_declarations.append(tool.to_openai_schema())
                elif hasattr(tool, 'to_gemini_declaration'):
                    declaration = tool.to_gemini_declaration()
                    tool_declarations.append({
                        "type": "function",
                        "function": {
                            "name": declaration.get("name", "tool"),
                            "description": declaration.get("description", ""),
                            "parameters": declaration.get("parameters", {"type": "object", "properties": {}}),
                        },
                    })
            return tool_declarations or None

        tool_declarations = []
        for tool in self.tools:
            if hasattr(tool, 'to_gemini_declaration'):
                tool_declarations.append(tool.to_gemini_declaration())

        if not tool_declarations:
            return None

        return {"function_declarations": tool_declarations}

    async def _execute_llm(
        self,
        prompt: str,
        system_instruction: str,
        tool_config: Optional[Any]
    ) -> str:
        """Execute an LLM call against the active provider."""
        provider = self._current_provider()
        if provider == "nim":
            return await self._execute_nim_llm(prompt, system_instruction, tool_config)
        return await self._execute_gemini_llm(prompt, system_instruction, tool_config)

    async def _execute_gemini_llm(
        self,
        prompt: str,
        system_instruction: str,
        tool_config: Optional[Dict[str, Any]]
    ) -> str:
        """Execute a Gemini model call with optional tool support."""
        config = {
            "temperature": self.kwargs.get("temperature", 0.7),
            "top_p": self.kwargs.get("top_p", 0.95),
            "top_k": self.kwargs.get("top_k", 40),
            "max_output_tokens": self.kwargs.get("max_output_tokens", 2048),
        }

        contents = [
            genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=prompt)]
            )
        ]

        generate_kwargs = {
            "model": self._resolved_model("gemini"),
            "contents": contents,
            "config": genai_types.GenerateContentConfig(**config)
        }

        if system_instruction:
            generate_kwargs["config"].system_instruction = system_instruction
        if tool_config:
            generate_kwargs["config"].tools = [tool_config]

        response = await self.client.aio.models.generate_content(**generate_kwargs)

        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and candidate.content.parts:
                for part in candidate.content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        return await self._execute_tool_call(part.function_call)
                return candidate.content.parts[0].text

        return str(response.text) if hasattr(response, 'text') else ""

    async def _execute_nim_llm(
        self,
        prompt: str,
        system_instruction: str,
        tool_config: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Execute an NVIDIA NIM model call with optional tool support."""
        if not hasattr(self.client, "generate_content"):
            raise RuntimeError("NIM provider requires a NIMClient-compatible client")

        response = await self.client.generate_content(
            model=self._resolved_model("nim"),
            prompt=prompt,
            system_instruction=system_instruction,
            tools=tool_config,
            temperature=self.kwargs.get("temperature", 0.7),
            top_p=self.kwargs.get("top_p", 0.95),
            max_output_tokens=self.kwargs.get("max_output_tokens", 2048),
        )

        if response.startswith("TOOL_CALL:"):
            try:
                _, tool_name, raw_args = response.split(":", 2)
                args = json.loads(raw_args or "{}")
            except (ValueError, json.JSONDecodeError) as exc:
                return json.dumps({"error": f"Invalid NIM tool call: {exc}"})
            return await self._execute_tool_call_by_name(tool_name, args)

        return response

    async def _execute_tool_call(self, function_call) -> str:
        """Execute a Gemini-style tool invocation."""
        function_name = function_call.name
        args = dict(function_call.args) if hasattr(function_call, 'args') else {}
        return await self._execute_tool_call_by_name(function_name, args)

    async def _execute_tool_call_by_name(self, function_name: str, args: Dict[str, Any]) -> str:
        """Execute a registered tool by name and serialize its result."""
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name == function_name:
                if hasattr(tool, 'execute'):
                    result = await tool.execute(**args)
                    return json.dumps(result)
                if hasattr(tool, 'func'):
                    result = tool.func(**args)
                    return json.dumps(result)

        for sub_agent in self.sub_agents:
            if sub_agent.name == function_name:
                logger.info("Routing hallucinated tool call '%s' to sub-agent", function_name)
                # Try to extract the prompt from typical args, default to the whole args dict or prompt
                sub_prompt = args.get("prompt") or args.get("input_text") or args.get("question") or json.dumps(args)
                result = await sub_agent.run(prompt=sub_prompt, context=self.context)
                
                # Convert any non-serializable objects (like Content) to safe representations
                serializable_result = {}
                for k, v in result.items():
                    if v is None or isinstance(v, (str, int, float, bool, list, dict)):
                        serializable_result[k] = v
                    elif hasattr(v, "to_json"):
                        try:
                            serializable_result[k] = json.loads(v.to_json())
                        except Exception:
                            serializable_result[k] = str(v)
                    else:
                        serializable_result[k] = str(v)
                return json.dumps(serializable_result)

        return json.dumps({"error": f"Tool {function_name} not found"})

    async def _execute_sub_agents(self, parent_response: str) -> str:
        """Run sub-agents sequentially using the parent agent's response."""
        results = [f"[{self.name} Initial Response]\n{parent_response}"]

        for sub_agent in self.sub_agents:
            result = await sub_agent.run(
                prompt=parent_response,
                context=self.context
            )
            response_text = result.get("response", "")
            if not response_text and result.get("error"):
                response_text = f"Error: {result['error']}"
            results.append(f"\n[{sub_agent.name} Response]\n{response_text}")

        return "\n".join(results)

    def _current_provider(self) -> str:
        return (self.provider or os.getenv("LLM_PROVIDER", "gemini")).lower()

    def _resolved_model(self, provider: str) -> str:
        if provider == "nim" and self.nim_model:
            return self.nim_model
        if provider == "gemini" and self.gemini_model:
            return self.gemini_model
        return self.model
