"""Function tool wrapper for Gemini and OpenAI-compatible LLM APIs."""
import inspect
from typing import Any, Callable, Dict, List, Optional, Union, get_args, get_origin


class FunctionTool:
    """Wrapper for Python functions to be used as LLM tools."""

    def __init__(
        self,
        func: Optional[Callable] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs
    ):
        self.func = func or kwargs.get('func')
        self.name = name or (func.__name__ if func else kwargs.get('name', 'tool'))
        self.description = description or (func.__doc__ if func else kwargs.get('description', ''))
        self.kwargs = kwargs

        if self.func:
            self.signature = inspect.signature(self.func)
            self.parameters = self._extract_parameters()
        else:
            self.signature = None
            self.parameters = {}

    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract parameter schema from function signature."""
        params = {}

        for param_name, param in self.signature.parameters.items():
            if param_name == "self":
                continue

            schema = self._annotation_to_schema(param.annotation)
            param_info = {
                "type": schema["type"],
                "description": f"Parameter {param_name}",
                "required": param.default == inspect.Parameter.empty,
            }
            if "items" in schema:
                param_info["items"] = schema["items"]
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default

            params[param_name] = param_info

        return params

    def _annotation_to_schema(self, annotation: Any) -> Dict[str, Any]:
        """Map a Python type annotation to a JSON-schema fragment."""
        if annotation == inspect.Parameter.empty:
            return {"type": "string"}

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is Union:
            non_none_args = [arg for arg in args if arg is not type(None)]
            return self._annotation_to_schema(non_none_args[0]) if non_none_args else {"type": "string"}
        if origin in (list, List):
            item_schema = self._annotation_to_schema(args[0]) if args else {"type": "string"}
            return {"type": "array", "items": item_schema}
        if origin in (dict, Dict):
            return {"type": "object"}

        if annotation == str:
            return {"type": "string"}
        if annotation == int:
            return {"type": "integer"}
        if annotation == float:
            return {"type": "number"}
        if annotation == bool:
            return {"type": "boolean"}
        if annotation == dict:
            return {"type": "object"}
        if annotation == list:
            return {"type": "array", "items": {"type": "string"}}

        return {"type": "string"}

    def _json_schema_parameters(self) -> Dict[str, Any]:
        required_params = [
            name for name, info in self.parameters.items()
            if info.get("required", False)
        ]

        properties = {}
        for name, info in self.parameters.items():
            schema = {
                "type": info["type"],
                "description": info["description"],
            }
            if "items" in info:
                schema["items"] = info["items"]
            if "default" in info and isinstance(info["default"], (str, int, float, bool, type(None))):
                schema["default"] = info["default"]
            properties[name] = schema

        parameters = {
            "type": "object",
            "properties": properties,
        }
        if required_params:
            parameters["required"] = required_params
        return parameters

    def to_gemini_declaration(self) -> Dict[str, Any]:
        """Convert to Gemini function declaration format."""
        return {
            "name": self.name,
            "description": self.description or f"Execute {self.name} function",
            "parameters": self._json_schema_parameters(),
        }

    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert to OpenAI/NVIDIA NIM tool schema format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description or f"Execute {self.name} function",
                "parameters": self._json_schema_parameters(),
            },
        }

    async def execute(self, **kwargs) -> Any:
        """Execute the wrapped function."""
        if not self.func:
            raise RuntimeError(f"No function defined for tool {self.name}")

        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        return self.func(**kwargs)

    def __call__(self, **kwargs) -> Any:
        """Allow tool to be called directly."""
        if inspect.iscoroutinefunction(self.func):
            import asyncio
            return asyncio.create_task(self.execute(**kwargs))
        return self.func(**kwargs)

    def __repr__(self):
        return f"FunctionTool(name='{self.name}')"
