"""
Tool component for function calling and code execution.

This is the single canonical source for all tool-related models and functionality.
"""

import asyncio
import inspect
import time
import json
from typing import Dict, List, Optional, Any, Callable, get_type_hints, Type
from dataclasses import dataclass
from datetime import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, create_model

from ..utils.logger import get_logger
from ..utils.id import generate_short_id

logger = get_logger(__name__)


# ============================================================================
# TOOL DEFINITION MODELS
# ============================================================================

class ToolFunction(BaseModel):
    """A single callable function within a tool."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema
    return_description: str = ""
    function: Optional[Callable] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True


class ToolCall(BaseModel):
    """Tool call specification with retry policy."""
    id: str = Field(default_factory=lambda: f"tc_{generate_short_id()}")
    tool_name: str
    args: Dict[str, Any]
    expected_output_type: Optional[str] = None
    timeout: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None


class ToolResult(BaseModel):
    """
    Canonical tool execution result model.

    This is the single source of truth for tool execution results across the framework.
    """
    # Core execution results
    success: bool
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

    # Execution metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: Optional[str] = None  # ISO format string for JSON serialization

    # Tool call context (for messaging)
    tool_call_id: Optional[str] = None
    tool_name: Optional[str] = None

    # Artifacts and resources (for file operations)
    artifacts: List[str] = Field(default_factory=list)
    resource_usage: Optional[Dict[str, Any]] = None
    exit_code: Optional[int] = None

    def __init__(self, **data):
        # Auto-generate timestamp if not provided
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.now().isoformat()
        super().__init__(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return self.model_dump()

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json()

    @classmethod
    def success_result(cls, result: Any, **kwargs) -> "ToolResult":
        """Create a successful result."""
        return cls(success=True, result=result, **kwargs)

    @classmethod
    def error_result(cls, error: str, **kwargs) -> "ToolResult":
        """Create an error result."""
        return cls(success=False, error=error, **kwargs)


# ============================================================================
# TOOL REGISTRY MODELS
# ============================================================================

class ToolRegistryEntry(BaseModel):
    """Entry in the tool registry."""
    tool: "Tool" = Field(exclude=True)  # Don't serialize the tool instance
    callable_func: Callable = Field(exclude=True)  # Don't serialize the callable
    pydantic_model: Optional[BaseModel] = Field(default=None, exclude=True)
    name: str
    description: str
    tool_schema: Dict[str, Any]  # Renamed from 'schema' to avoid shadowing BaseModel.schema()

    class Config:
        arbitrary_types_allowed = True


# ============================================================================
# TOOL EXECUTION CONTEXT MODELS
# ============================================================================

class ToolExecutionContext(BaseModel):
    """Context information for tool execution."""
    project_id: str
    agent_name: Optional[str] = None
    taskspace_path: Optional[str] = None
    execution_id: str = Field(default_factory=lambda: f"exec_{generate_short_id()}")
    started_at: datetime = Field(default_factory=datetime.now)
    timeout: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ToolExecutionStats(BaseModel):
    """Statistics for tool execution."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    average_execution_time: float = 0.0
    total_execution_time: float = 0.0
    last_execution: Optional[datetime] = None
    error_rate: float = 0.0


# ============================================================================
# JSON SERIALIZATION UTILITIES
# ============================================================================

def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize complex objects to JSON-compatible format.
    Handles dataclasses, Pydantic models, and other complex types.
    """
    if hasattr(obj, 'model_dump'):
        # Pydantic model
        return obj.model_dump()
    elif hasattr(obj, '__dataclass_fields__'):
        # Dataclass
        from dataclasses import asdict
        return asdict(obj)
    elif hasattr(obj, '__dict__'):
        # Regular object with __dict__
        return {k: safe_json_serialize(v) for k, v in obj.__dict__.items()
                if not k.startswith('_')}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    else:
        # Unknown type - this should be handled explicitly
        raise ValueError(f"Cannot serialize object of type {type(obj).__name__}: {obj!r}")


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely dump complex objects to JSON string.
    Uses safe_json_serialize to handle complex types.
    """
    serializable_obj = safe_json_serialize(obj)
    return json.dumps(serializable_obj, **kwargs)


# ============================================================================
# DECORATOR
# ============================================================================

def tool(description: str = "", return_description: str = ""):
    """
    Decorator to mark methods as available tool calls.

    Args:
        description: Clear description of what this tool does
        return_description: Description of what the tool returns
    """
    def decorator(func):
        func._is_tool_call = True
        func._tool_description = description or func.__doc__ or ""
        func._return_description = return_description
        return func
    return decorator


def _create_pydantic_model_from_signature(func: Callable) -> Optional[Type[BaseModel]]:
    """Create a Pydantic model from function signature for validation and schema generation."""
    sig = inspect.signature(func)
    type_hints = get_type_hints(func)
    docstring = func.__doc__ or ""

    # Extract parameter descriptions from docstring
    param_descriptions = _extract_all_param_descriptions(docstring)

    fields = {}
    for param_name, param in sig.parameters.items():
        if param_name in ['self', 'kwargs']:
            continue

        param_type = type_hints.get(param_name, str)
        param_desc = param_descriptions.get(param_name, f"Parameter {param_name}")

        if param.default != inspect.Parameter.empty:
            # Optional parameter with default
            fields[param_name] = (param_type, Field(default=param.default, description=param_desc))
        else:
            # Required parameter
            fields[param_name] = (param_type, Field(description=param_desc))

    if not fields:
        return None

    # Create dynamic Pydantic model
    # Handle Mock objects in tests that don't have __name__
    func_name = getattr(func, '__name__', 'unknown_function')
    model_name = f"{func_name.title()}Params"
    return create_model(model_name, **fields)


def _extract_all_param_descriptions(docstring: str) -> Dict[str, str]:
    """Extract all parameter descriptions from docstring."""
    descriptions = {}
    if not docstring:
        return descriptions

    lines = docstring.split('\n')
    in_args_section = False

    for line in lines:
        line = line.strip()
        if line.lower().startswith('args:') or line.lower().startswith('parameters:'):
            in_args_section = True
            continue
        elif line.lower().startswith('returns:') or line.lower().startswith('return:'):
            in_args_section = False
            continue
        elif in_args_section and ':' in line:
            # Handle both "param: description" and "param (type): description"
            colon_idx = line.find(':')
            param_part = line[:colon_idx].strip()
            desc_part = line[colon_idx + 1:].strip()

            # Extract parameter name (remove type annotation if present)
            if '(' in param_part and ')' in param_part:
                param_name = param_part.split('(')[0].strip()
            else:
                param_name = param_part

            descriptions[param_name] = desc_part

    return descriptions


class Tool(ABC):
    """Base class for tools that provide multiple callable methods for LLMs."""

    def __init__(self, name: str = ""):
        self.name = name or self.__class__.__name__.lower().replace('tool', '')

    def get_callable_methods(self) -> Dict[str, Callable]:
        """Get all methods marked with @tool decorator."""
        methods = {}
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if callable(attr) and hasattr(attr, '_is_tool_call'):
                tool_name = attr_name
                methods[tool_name] = attr
        return methods

    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed OpenAI function schemas for all callable methods using Pydantic."""
        schemas = {}
        methods = self.get_callable_methods()

        for tool_name, method in methods.items():
            # Use Pydantic for schema generation
            pydantic_model = _create_pydantic_model_from_signature(method)
            if pydantic_model:
                # Get Pydantic's JSON schema
                pydantic_schema = pydantic_model.model_json_schema()

                # Convert to OpenAI function calling format
                schema = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": getattr(method, '_tool_description', ''),
                        "parameters": pydantic_schema
                    }
                }

                # Add return information if available
                if hasattr(method, '_return_description') and getattr(method, '_return_description', None):
                    schema["function"]["returns"] = {
                        "description": getattr(method, '_return_description', '')
                    }

                schemas[tool_name] = schema
            else:
                # Methods with no parameters
                schemas[tool_name] = {
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "description": getattr(method, '_tool_description', ''),
                        "parameters": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }

        return schemas

# Note: ToolRegistry implementation is in vibex.tool.registry
# This module only contains the core tool models and functions
