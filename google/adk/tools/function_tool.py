"""Function tool wrapper for Gemini API integration."""
import inspect
from typing import Callable, Dict, Any, Optional


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

        # Parse function signature if available
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
            param_info = {
                "type": "string",  # Default to string
                "description": f"Parameter {param_name}"
            }

            # Try to infer type from annotation
            if param.annotation != inspect.Parameter.empty:
                annotation = param.annotation
                if annotation == str:
                    param_info["type"] = "string"
                elif annotation == int:
                    param_info["type"] = "integer"
                elif annotation == float:
                    param_info["type"] = "number"
                elif annotation == bool:
                    param_info["type"] = "boolean"
                elif annotation == dict or annotation == Dict:
                    param_info["type"] = "object"
                elif annotation == list:
                    param_info["type"] = "array"

            # Check if required
            if param.default == inspect.Parameter.empty:
                param_info["required"] = True
            else:
                param_info["required"] = False
                param_info["default"] = param.default

            params[param_name] = param_info

        return params

    def to_gemini_declaration(self) -> Dict[str, Any]:
        """Convert to Gemini function declaration format."""
        # Extract required parameters
        required_params = [
            name for name, info in self.parameters.items()
            if info.get("required", False)
        ]

        # Build parameter schema
        properties = {}
        for name, info in self.parameters.items():
            properties[name] = {
                "type": info["type"],
                "description": info["description"]
            }

        declaration = {
            "name": self.name,
            "description": self.description or f"Execute {self.name} function",
            "parameters": {
                "type": "object",
                "properties": properties,
            }
        }

        if required_params:
            declaration["parameters"]["required"] = required_params

        return declaration

    async def execute(self, **kwargs) -> Any:
        """Execute the wrapped function."""
        if not self.func:
            raise RuntimeError(f"No function defined for tool {self.name}")

        # Check if function is async
        if inspect.iscoroutinefunction(self.func):
            return await self.func(**kwargs)
        else:
            return self.func(**kwargs)

    def __call__(self, **kwargs) -> Any:
        """Allow tool to be called directly."""
        if inspect.iscoroutinefunction(self.func):
            import asyncio
            return asyncio.create_task(self.execute(**kwargs))
        return self.func(**kwargs)

    def __repr__(self):
        return f"FunctionTool(name='{self.name}')"
