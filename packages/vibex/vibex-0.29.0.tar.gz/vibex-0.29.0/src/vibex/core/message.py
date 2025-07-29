from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union, Literal, TYPE_CHECKING
from ..utils.id import generate_short_id
from vibex.utils.logger import get_logger

# This file defines the core data structures for the VibeX framework,
# as specified in design document 03-data-and-events.md.

# --- Core Data Structures ---

# Note: ToolCall and ToolResult are defined in core.tool, not here. This separation is intentional:
# - ToolCall/ToolResult = tool execution models (core.tool)
# - ToolCallPart/ToolResultPart = conversation representations (here in message.py)
# The conversation parts are self-contained and don't depend on tool execution models

class Artifact(BaseModel):
    """Artifact reference with versioning and metadata."""
    uri: str  # e.g., "file://artifacts/main.py"
    mime_type: str
    size_bytes: Optional[int] = None
    description: Optional[str] = None
    version: Optional[str] = None  # For artifact versioning
    checksum: Optional[str] = None  # For integrity verification
    metadata: Dict[str, Any] = Field(default_factory=dict)  # Extensible metadata
    created_by: Optional[str] = None  # Agent or tool that created it
    tags: List[str] = Field(default_factory=list)  # For categorization and search

# --- TaskStep and its Parts ---

class MessagePart(BaseModel):
    """
    A union of all possible content types that can be part of a message.
    This allows for rich, multi-modal messages (e.g., text with images).

    """
    pass

class TextPart(MessagePart):
    """Text content part with language and confidence support."""
    type: Literal["text"] = "text"
    text: str
    language: Optional[str] = None  # For multilingual support
    confidence: Optional[float] = None  # LLM confidence score

class ToolCallPart(MessagePart):
    """Tool call request part - conversation representation."""
    type: Literal["tool_call"] = "tool_call"
    tool_call_id: str
    tool_name: str
    args: Dict[str, Any]
    expected_output_type: Optional[str] = None

class ToolResultPart(MessagePart):
    """Tool execution result part."""
    type: Literal["tool_result"] = "tool_result"
    tool_call_id: str
    tool_name: str
    result: Any
    is_error: bool = False

class ArtifactPart(MessagePart):
    """Artifact reference part."""
    type: Literal["artifact"] = "artifact"
    artifact: Artifact

class ImagePart(MessagePart):
    """Image content part with metadata."""
    type: Literal["image"] = "image"
    image_url: str  # Can be data URL or artifact reference
    alt_text: Optional[str] = None
    dimensions: Optional[Dict[str, int]] = None  # width, height
    format: Optional[str] = None  # png, jpg, etc.

class AudioPart(MessagePart):
    """Audio content part with metadata."""
    type: Literal["audio"] = "audio"
    audio_url: str  # Can be data URL or artifact reference
    transcript: Optional[str] = None
    duration_seconds: Optional[float] = None
    format: Optional[str] = None  # mp3, wav, etc.
    sample_rate: Optional[int] = None

class MemoryReference(BaseModel):
    """Memory reference with relevance scoring."""
    memory_id: str
    memory_type: str  # "short_term", "long_term", "semantic", "episodic"
    relevance_score: Optional[float] = None
    retrieval_query: Optional[str] = None

class MemoryPart(MessagePart):
    """Memory operation part."""
    type: Literal["memory"] = "memory"
    operation: str  # "store", "retrieve", "search", "consolidate"
    references: List[MemoryReference]
    content: Optional[Dict[str, Any]] = None

class GuardrailCheck(BaseModel):
    """Individual guardrail check result."""
    check_id: str
    check_type: str  # "input_validation", "content_filter", "rate_limit", "policy"
    status: str  # "passed", "failed", "warning"
    message: Optional[str] = None
    policy_violated: Optional[str] = None
    severity: Optional[str] = None  # "low", "medium", "high", "critical"

class GuardrailPart(MessagePart):
    """Guardrail check results part."""
    type: Literal["guardrail"] = "guardrail"
    checks: List[GuardrailCheck]
    overall_status: str  # "passed", "failed", "warning"

# --- Standard Chat Message Format (compatible with Vercel AI SDK) ---

class Message(BaseModel):
    """
    Standard chat message format compatible with LLM APIs and Vercel AI SDK.

    This follows the industry standard format with role/content/parts structure.
    """
    id: str = Field(default_factory=generate_short_id)
    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: str = ""  # Backward compatibility - text content
    parts: List[MessagePart] = Field(default_factory=list)  # Modern structured content
    timestamp: datetime = Field(default_factory=datetime.now)

    @classmethod
    def user_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create a user message."""
        return cls(
            role="user",
            content=content,
            parts=parts or [TextPart(text=content)]
        )

    @classmethod
    def assistant_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create an assistant message."""
        return cls(
            role="assistant",
            content=content,
            parts=parts or [TextPart(text=content)]
        )

    @classmethod
    def system_message(cls, content: str, parts: Optional[List[MessagePart]] = None) -> "Message":
        """Create a system message."""
        return cls(
            role="system",
            content=content,
            parts=parts or [TextPart(text=content)]
        )

class UserMessage(Message):
    """User message - alias for Message with role='user'."""
    role: Literal["user"] = "user"

class TaskStep(BaseModel):
    """
    Represents a single execution step taken by an agent within a task.
    
    A TaskStep contains the actions performed by an agent, including tool calls,
    their results, and any other content generated during task execution.
    """
    id: str = Field(default_factory=generate_short_id)
    agent_name: str = Field(description="Name of the agent that performed this step")
    parts: List[MessagePart] = Field(default_factory=list, description="Content parts of this step")
    timestamp: datetime = Field(default_factory=datetime.now)
    task_id: Optional[str] = Field(None, description="ID of the task this step belongs to")
    
    def to_message(self) -> Message:
        """Convert TaskStep to a Message for unified chat history."""
        # Combine all text parts for content
        text_parts = [part.text for part in self.parts if isinstance(part, TextPart)]
        content = " ".join(text_parts) if text_parts else ""
        
        return Message(
            id=self.id,
            role="assistant",
            content=content,
            parts=self.parts,
            timestamp=self.timestamp
        )

class MessageQueue(BaseModel):
    """Queue for managing message flow in tasks."""
    messages: List[Message] = Field(default_factory=list)
    max_size: int = 1000

    def add(self, message: Message) -> None:
        """Add a message to the queue."""
        self.messages.append(message)
        if len(self.messages) > self.max_size:
            self.messages.pop(0)  # Remove oldest message

    def get_all(self) -> List[Message]:
        """Get all messages in the queue."""
        return self.messages.copy()

    def clear(self) -> None:
        """Clear all messages from the queue."""
        self.messages.clear()

class ConversationHistory(BaseModel):
    """Project conversation history with messages and metadata."""
    project_id: str
    messages: List[Message] = Field(default_factory=list)
    steps: List[TaskStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def add_message(self, message: Message) -> None:
        """Add a message to the history."""
        self.messages.append(message)
        self.updated_at = datetime.now()

    def add_step(self, step: TaskStep) -> None:
        """Add a task step to the history."""
        self.steps.append(step)
        self.updated_at = datetime.now()

# --- Streaming Models ---

class StreamChunk(BaseModel):
    """
    Token-by-token message streaming from LLM.

    This is Channel 1 of the dual-channel system - provides low-latency
    UI updates for "typing" effect. This is message streaming, not events.
    """
    type: Literal["content_chunk"] = "content_chunk"
    step_id: str  # Links to the TaskStep being generated
    agent_name: str
    text: str
    is_final: bool = False  # True for the last chunk of a response
    token_count: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StreamError(BaseModel):
    """
    Error in message streaming.
    """
    type: Literal["stream_error"] = "stream_error"
    step_id: str
    agent_name: str
    error_message: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StreamComplete(BaseModel):
    """
    Message streaming completion marker.
    """
    type: Literal["stream_complete"] = "stream_complete"
    step_id: str
    agent_name: str
    total_tokens: Optional[int] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
