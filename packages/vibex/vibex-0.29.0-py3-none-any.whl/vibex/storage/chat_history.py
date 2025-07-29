"""
Chat History Storage

Handles persistence of chat conversations with support for streaming messages.
Key features:
- Persist complete messages only (not streaming chunks)
- Handle streaming completion with final message consolidation
- Efficient storage with message deduplication
- Support for both in-memory and file-based storage
"""

import json
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..core.message import Message, ConversationHistory, TaskStep, StreamChunk
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ChatHistoryStorage:
    """Manages chat history persistence for tasks."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        # History folder at same level as artifacts/ and logs/
        self.history_dir = self.project_path / "history"
        self.history_file = self.history_dir / "messages.jsonl"
        self.temp_streaming_messages: Dict[str, Dict] = {}  # Track incomplete streaming messages
        
    async def save_message(self, project_id: str, message: Message) -> None:
        """Save a complete message to persistent storage."""
        try:
            # Ensure history directory exists
            self.history_dir.mkdir(parents=True, exist_ok=True)
            
            # Create message record using exact Message structure with parts
            message_record = {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "parts": [part.model_dump() for part in message.parts],
                "timestamp": message.timestamp.isoformat()
            }
            
            # Append to JSONL file (each line is a JSON object)
            # This supports continuing conversations by appending to existing history
            with open(self.history_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(message_record) + "\n")
                
            logger.debug(f"Saved message {message.id} for task {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to save message {message.id} for task {project_id}: {e}")
            
    async def save_step(self, project_id: str, step: TaskStep) -> None:
        """Save a task step as an assistant message to maintain unified chat history."""
        try:
            # Convert Task to Message format for unified storage
            # Extract text content from parts
            content = ""
            for part in task.parts:
                if hasattr(part, 'text'):
                    content += part.text
                elif hasattr(part, 'content'):
                    content += str(part.content)
            
            # Create message from task
            task_message = Message(
                id=task.step_id,
                role="assistant",
                content=content,
                parts=task.parts,  # Preserve original parts structure
                timestamp=task.timestamp
            )
            
            # Save as regular message
            await self.save_message(project_id, task_message)
            
        except Exception as e:
            logger.error(f"Failed to save task {task.step_id} for project {project_id}: {e}")
    
    async def handle_streaming_chunk(self, project_id: str, chunk: StreamChunk) -> None:
        """Handle streaming message chunks - accumulate but don't persist until complete."""
        step_id = chunk.step_id
        
        # Initialize or update streaming message
        if step_id not in self.temp_streaming_messages:
            self.temp_streaming_messages[step_id] = {
                "agent_name": chunk.agent_name,
                "content": "",
                "chunks": [],
                "start_time": chunk.timestamp,
                "project_id": project_id
            }
        
        # Accumulate content
        self.temp_streaming_messages[step_id]["content"] += chunk.text
        self.temp_streaming_messages[step_id]["chunks"].append({
            "text": chunk.text,
            "timestamp": chunk.timestamp.isoformat(),
            "token_count": chunk.token_count
        })
        
        # If this is the final chunk, create and save the complete message
        if chunk.is_final:
            await self._finalize_streaming_message(project_id, step_id)
    
    async def _finalize_streaming_message(self, project_id: str, step_id: str) -> None:
        """Convert accumulated streaming chunks into a final message and persist it."""
        if step_id not in self.temp_streaming_messages:
            logger.warning(f"No streaming message found for step {step_id}")
            return
        
        streaming_data = self.temp_streaming_messages[step_id]
        
        # Create final message
        final_message = Message.assistant_message(
            content=streaming_data["content"]
        )
        final_message.id = step_id  # Use step_id as message_id for consistency
        
        # Save the complete message
        await self.save_message(project_id, final_message)
        
        # Clean up streaming data
        del self.temp_streaming_messages[step_id]
        
        logger.debug(f"Finalized streaming message for step {step_id}")
    
    async def load_history(self, project_id: str) -> ConversationHistory:
        """Load chat history from persistent storage."""
        history = ConversationHistory(project_id=project_id)
        
        if not self.history_file.exists():
            logger.debug(f"No chat history file found for task {project_id}")
            return history
        
        try:
            from ..core.message import TextPart, ToolCallPart, ToolResultPart
            
            with open(self.history_file, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                        
                    record = json.loads(line)
                    
                    # Reconstruct parts from JSON
                    parts = []
                    for part_data in record.get("parts", []):
                        part_type = part_data.get("type")
                        if part_type == "text":
                            parts.append(TextPart(**part_data))
                        elif part_type == "tool_call":
                            parts.append(ToolCallPart(**part_data))
                        elif part_type == "tool_result":
                            parts.append(ToolResultPart(**part_data))
                        # Add other part types as needed
                    
                    # Reconstruct Message with exact format
                    message = Message(
                        id=record["id"],
                        role=record["role"],
                        content=record["content"],
                        parts=parts,
                        timestamp=datetime.fromisoformat(record["timestamp"])
                    )
                    history.add_message(message)
            
            logger.info(f"Loaded chat history for task {project_id}: {len(history.messages)} messages")
            
        except Exception as e:
            logger.error(f"Failed to load chat history for task {project_id}: {e}")
        
        return history
    
    async def clear_history(self, project_id: str) -> None:
        """Clear chat history for a task by removing the entire history file."""
        try:
            if self.history_file.exists():
                # For task-specific history files, simply remove the entire file
                # Since each task has its own history directory structure
                self.history_file.unlink()
                logger.info(f"Cleared chat history file for task {project_id}")
            
            # Clear any temporary streaming messages for this task
            to_remove = [step_id for step_id, data in self.temp_streaming_messages.items() 
                        if data.get("project_id") == project_id]
            for step_id in to_remove:
                del self.temp_streaming_messages[step_id]
                
        except Exception as e:
            logger.error(f"Failed to clear chat history for task {project_id}: {e}")
    
    def get_active_streaming_messages(self, project_id: str) -> List[Dict]:
        """Get currently active streaming messages for a task."""
        return [
            {
                "step_id": step_id,
                "agent_name": data["agent_name"],
                "partial_content": data["content"],
                "chunk_count": len(data["chunks"]),
                "start_time": data["start_time"].isoformat()
            }
            for step_id, data in self.temp_streaming_messages.items()
            if data.get("project_id") == project_id
        ]


class ChatHistoryManager:
    """Global manager for chat history storage across all tasks."""
    
    def __init__(self):
        self._storage_instances: Dict[str, ChatHistoryStorage] = {}
    
    def get_storage(self, project_path: str) -> ChatHistoryStorage:
        """Get or create a chat history storage instance for a project."""
        if project_path not in self._storage_instances:
            self._storage_instances[project_path] = ChatHistoryStorage(project_path)
        return self._storage_instances[project_path]
    
    async def save_message(self, project_id: str, project_path: str, message: Message) -> None:
        """Save a message using the appropriate storage instance."""
        storage = self.get_storage(project_path)
        await storage.save_message(project_id, message)
    
    async def save_step(self, project_id: str, project_path: str, step: TaskStep) -> None:
        """Save a task step using the appropriate storage instance."""
        storage = self.get_storage(project_path)
        await storage.save_step(project_id, step)
    
    async def load_history(self, project_id: str, project_path: str) -> ConversationHistory:
        """Load history using the appropriate storage instance."""
        storage = self.get_storage(project_path)
        return await storage.load_history(project_id)


# Global chat history manager
chat_history_manager = ChatHistoryManager()