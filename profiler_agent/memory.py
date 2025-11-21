"""Memory bank for long-term context storage and retrieval."""
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import hashlib
from .paths import get_output_path


class MemoryBank:
    """Long-term memory storage for agent context."""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path is None:
            # Default to output directory
            storage_path = str(get_output_path("memory_bank.json"))
        self.storage_path = storage_path
        self.memories: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.load()
    
    def load(self):
        """Load memories from disk."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.memories = defaultdict(list, data)
            except Exception as e:
                print(f"Warning: Failed to load memory bank: {e}")
    
    def save(self):
        """Persist memories to disk."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(dict(self.memories), f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save memory bank: {e}")
    
    def add_memory(
        self,
        user_id: str,
        memory_type: str,
        content: Dict[str, Any],
        tags: Optional[List[str]] = None
    ) -> str:
        """
        Add a new memory.
        
        Args:
            user_id: User identifier
            memory_type: Type of memory (e.g., 'exam_analysis', 'study_plan', 'preference')
            content: Memory content
            tags: Optional tags for categorization
        
        Returns:
            Memory ID
        """
        memory_id = self._generate_id(user_id, memory_type, content)
        
        memory = {
            "id": memory_id,
            "user_id": user_id,
            "type": memory_type,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "access_count": 0,
            "last_accessed": None
        }
        
        self.memories[user_id].append(memory)
        self.save()
        
        return memory_id
    
    def get_memories(
        self,
        user_id: str,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve memories for a user.
        
        Args:
            user_id: User identifier
            memory_type: Filter by memory type
            tags: Filter by tags (must have all tags)
            limit: Maximum number of memories to return
        
        Returns:
            List of matching memories
        """
        user_memories = self.memories.get(user_id, [])
        
        # Filter by type
        if memory_type:
            user_memories = [m for m in user_memories if m["type"] == memory_type]
        
        # Filter by tags
        if tags:
            user_memories = [
                m for m in user_memories
                if all(tag in m.get("tags", []) for tag in tags)
            ]
        
        # Sort by most recent and update access count
        user_memories.sort(key=lambda m: m["created_at"], reverse=True)
        
        # Update access count for returned memories
        for memory in user_memories[:limit]:
            memory["access_count"] += 1
            memory["last_accessed"] = datetime.now().isoformat()
        
        self.save()
        
        return user_memories[:limit]
    
    def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search memories by text content.
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of matching memories
        """
        user_memories = self.memories.get(user_id, [])
        query_lower = query.lower()
        
        # Simple text-based search
        matches = []
        for memory in user_memories:
            content_str = json.dumps(memory["content"]).lower()
            tags_str = " ".join(memory.get("tags", [])).lower()
            
            if query_lower in content_str or query_lower in tags_str:
                # Calculate simple relevance score
                score = content_str.count(query_lower) + tags_str.count(query_lower) * 2
                matches.append((score, memory))
        
        # Sort by relevance
        matches.sort(key=lambda x: x[0], reverse=True)
        
        return [m for _, m in matches[:limit]]
    
    def update_memory(
        self,
        user_id: str,
        memory_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update an existing memory.
        
        Args:
            user_id: User identifier
            memory_id: Memory to update
            updates: Fields to update
        
        Returns:
            True if memory was found and updated
        """
        for memory in self.memories.get(user_id, []):
            if memory["id"] == memory_id:
                memory["content"].update(updates.get("content", {}))
                if "tags" in updates:
                    memory["tags"] = updates["tags"]
                memory["updated_at"] = datetime.now().isoformat()
                self.save()
                return True
        
        return False
    
    def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a memory."""
        user_memories = self.memories.get(user_id, [])
        initial_count = len(user_memories)
        
        self.memories[user_id] = [m for m in user_memories if m["id"] != memory_id]
        
        if len(self.memories[user_id]) < initial_count:
            self.save()
            return True
        
        return False
    
    def get_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary statistics for user's memories."""
        user_memories = self.memories.get(user_id, [])
        
        type_counts = defaultdict(int)
        for memory in user_memories:
            type_counts[memory["type"]] += 1
        
        return {
            "total_memories": len(user_memories),
            "by_type": dict(type_counts),
            "most_accessed": sorted(
                user_memories,
                key=lambda m: m["access_count"],
                reverse=True
            )[:5] if user_memories else []
        }
    
    def compact_context(
        self,
        user_id: str,
        memory_types: Optional[List[str]] = None,
        max_tokens: int = 2000
    ) -> str:
        """
        Compact memories into a context string for LLM.
        
        Args:
            user_id: User identifier
            memory_types: Types of memories to include
            max_tokens: Approximate max tokens (rough estimate: 1 token ~= 4 chars)
        
        Returns:
            Compacted context string
        """
        user_memories = self.get_memories(user_id, limit=20)
        
        # Filter by type if specified
        if memory_types:
            user_memories = [m for m in user_memories if m["type"] in memory_types]
        
        # Build context string
        context_parts = ["Historical Context:"]
        current_length = len(context_parts[0])
        max_chars = max_tokens * 4  # Rough estimate
        
        for memory in user_memories:
            memory_str = f"\n- [{memory['type']}] {json.dumps(memory['content'])}"
            
            if current_length + len(memory_str) > max_chars:
                break
            
            context_parts.append(memory_str)
            current_length += len(memory_str)
        
        return "\n".join(context_parts)
    
    def _generate_id(self, user_id: str, memory_type: str, content: Dict) -> str:
        """Generate unique memory ID."""
        data = f"{user_id}:{memory_type}:{json.dumps(content)}:{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def clear_user_memories(self, user_id: str) -> int:
        """Clear all memories for a user."""
        count = len(self.memories.get(user_id, []))
        if user_id in self.memories:
            del self.memories[user_id]
            self.save()
        return count
