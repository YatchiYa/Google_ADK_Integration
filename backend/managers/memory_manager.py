"""
Memory Management System for Google ADK
Handles conversation memory, context persistence, and retrieval
"""

import uuid
import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from pathlib import Path
from loguru import logger


@dataclass
class MemoryEntry:
    """Memory entry data structure"""
    entry_id: str
    user_id: str
    session_id: Optional[str]
    agent_id: Optional[str]
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    importance: float = 1.0
    relevance_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class MemoryManager:
    """
    Memory management system for conversation persistence and retrieval
    Supports semantic search, importance weighting, and automatic cleanup
    """
    
    def __init__(self, db_path: str = "memory.db", max_entries: int = 10000):
        """
        Initialize memory manager
        
        Args:
            db_path: Path to SQLite database
            max_entries: Maximum number of entries to keep
        """
        self.db_path = db_path
        self.max_entries = max_entries
        self._lock = Lock()
        
        # Initialize database
        self._init_database()
        
        logger.info(f"Memory manager initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS memory_entries (
                        entry_id TEXT PRIMARY KEY,
                        user_id TEXT NOT NULL,
                        session_id TEXT,
                        agent_id TEXT,
                        content TEXT NOT NULL,
                        metadata TEXT,
                        tags TEXT,
                        importance REAL DEFAULT 1.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for better performance
                conn.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON memory_entries(user_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_session_id ON memory_entries(session_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_agent_id ON memory_entries(agent_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON memory_entries(created_at)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_entries(importance)")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_memory(self,
                     user_id: str,
                     content: str,
                     session_id: Optional[str] = None,
                     agent_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None,
                     importance: float = 1.0) -> str:
        """
        Create a new memory entry
        
        Args:
            user_id: User identifier
            content: Memory content
            session_id: Optional session identifier
            agent_id: Optional agent identifier
            metadata: Optional metadata dictionary
            tags: Optional list of tags
            importance: Importance score (0.0 to 1.0)
            
        Returns:
            str: Memory entry ID
        """
        try:
            entry_id = str(uuid.uuid4())
            
            # Create memory entry
            entry = MemoryEntry(
                entry_id=entry_id,
                user_id=user_id,
                session_id=session_id,
                agent_id=agent_id,
                content=content,
                metadata=metadata or {},
                tags=tags or [],
                importance=max(0.0, min(1.0, importance))
            )
            
            # Store in database
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO memory_entries 
                        (entry_id, user_id, session_id, agent_id, content, metadata, tags, importance, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        entry.entry_id,
                        entry.user_id,
                        entry.session_id,
                        entry.agent_id,
                        entry.content,
                        json.dumps(entry.metadata),
                        json.dumps(entry.tags),
                        entry.importance,
                        entry.created_at.isoformat(),
                        entry.updated_at.isoformat()
                    ))
                    conn.commit()
            
            # Cleanup old entries if needed
            self._cleanup_old_entries()
            
            logger.info(f"Created memory entry {entry_id} for user {user_id}")
            return entry_id
            
        except Exception as e:
            logger.error(f"Failed to create memory entry: {e}")
            raise
    
    def get_memory(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get memory entry by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM memory_entries WHERE entry_id = ?",
                    (entry_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_memory_entry(row)
                return None
                
        except Exception as e:
            logger.error(f"Failed to get memory entry {entry_id}: {e}")
            return None
    
    def get_session_context(self,
                           user_id: str,
                           session_id: str,
                           agent_id: Optional[str] = None,
                           limit: int = 20) -> List[MemoryEntry]:
        """
        Get conversation context for a specific session
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            agent_id: Optional agent identifier
            limit: Maximum number of entries
            
        Returns:
            List of memory entries for the session, ordered by creation time
        """
        try:
            sql = "SELECT * FROM memory_entries WHERE user_id = ? AND session_id = ?"
            params = [user_id, session_id]
            
            if agent_id:
                sql += " AND agent_id = ?"
                params.append(agent_id)
            
            sql += " ORDER BY created_at ASC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                memories = [self._row_to_memory_entry(row) for row in rows]
                logger.info(f"Retrieved {len(memories)} session context entries for session {session_id}")
                return memories
                
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return []
    
    def add_message_to_memory(self,
                             user_id: str,
                             session_id: str,
                             agent_id: str,
                             role: str,
                             content: str,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a message to session memory immediately
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            agent_id: Agent identifier
            role: Message role (user/assistant/system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            str: Memory entry ID
        """
        try:
            # Create memory entry for the message
            entry_metadata = {
                "type": "message",
                "role": role,
                "session_id": session_id,
                **(metadata or {})
            }
            
            # Determine importance based on role and content length
            importance = 0.8 if role == "user" else 0.6
            if len(content) > 200:
                importance += 0.1
            
            return self.create_memory(
                user_id=user_id,
                content=content,
                session_id=session_id,
                agent_id=agent_id,
                metadata=entry_metadata,
                tags=["message", role, "session"],
                importance=min(1.0, importance)
            )
            
        except Exception as e:
            logger.error(f"Failed to add message to memory: {e}")
            raise
    
    def search_memories(self,
                       user_id: str,
                       query: str,
                       limit: int = 10,
                       min_relevance: float = 0.5,
                       tags: Optional[List[str]] = None,
                       session_id: Optional[str] = None,
                       agent_id: Optional[str] = None) -> List[MemoryEntry]:
        """
        Search memories using simple text matching
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
            min_relevance: Minimum relevance score
            tags: Optional tag filter
            session_id: Optional session filter
            agent_id: Optional agent filter
            
        Returns:
            List of matching memory entries with relevance scores
        """
        try:
            # Build SQL query
            sql = "SELECT * FROM memory_entries WHERE user_id = ?"
            params = [user_id]
            
            # Add filters
            if session_id:
                sql += " AND session_id = ?"
                params.append(session_id)
            
            if agent_id:
                sql += " AND agent_id = ?"
                params.append(agent_id)
            
            # Simple text search (case-insensitive)
            if query:
                sql += " AND LOWER(content) LIKE ?"
                params.append(f"%{query.lower()}%")
            
            # Order by importance and creation date
            sql += " ORDER BY importance DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                memories = []
                for row in rows:
                    memory = self._row_to_memory_entry(row)
                    
                    # Calculate simple relevance score
                    if query:
                        relevance = self._calculate_relevance(memory.content, query)
                        if relevance >= min_relevance:
                            memory.relevance_score = relevance
                            memories.append(memory)
                    else:
                        memory.relevance_score = 1.0
                        memories.append(memory)
                
                # Filter by tags if specified
                if tags:
                    memories = [m for m in memories if any(tag in m.tags for tag in tags)]
                
                # Sort by relevance score
                memories.sort(key=lambda x: (x.relevance_score or 0, x.importance), reverse=True)
                
                logger.info(f"Found {len(memories)} memories for query '{query}'")
                return memories[:limit]
                
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def update_memory(self,
                     entry_id: str,
                     content: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[str]] = None,
                     importance: Optional[float] = None) -> bool:
        """Update memory entry"""
        try:
            updates = []
            params = []
            
            if content is not None:
                updates.append("content = ?")
                params.append(content)
            
            if metadata is not None:
                updates.append("metadata = ?")
                params.append(json.dumps(metadata))
            
            if tags is not None:
                updates.append("tags = ?")
                params.append(json.dumps(tags))
            
            if importance is not None:
                updates.append("importance = ?")
                params.append(max(0.0, min(1.0, importance)))
            
            if not updates:
                return False
            
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(entry_id)
            
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        f"UPDATE memory_entries SET {', '.join(updates)} WHERE entry_id = ?",
                        params
                    )
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Updated memory entry {entry_id}")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update memory entry {entry_id}: {e}")
            return False
    
    def delete_memory(self, entry_id: str) -> bool:
        """Delete memory entry"""
        try:
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM memory_entries WHERE entry_id = ?",
                        (entry_id,)
                    )
                    conn.commit()
                    
                    if cursor.rowcount > 0:
                        logger.info(f"Deleted memory entry {entry_id}")
                        return True
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to delete memory entry {entry_id}: {e}")
            return False
    
    def list_memories(self,
                     user_id: str,
                     limit: int = 50,
                     offset: int = 0,
                     session_id: Optional[str] = None,
                     agent_id: Optional[str] = None) -> List[MemoryEntry]:
        """List memories for a user"""
        try:
            sql = "SELECT * FROM memory_entries WHERE user_id = ?"
            params = [user_id]
            
            if session_id:
                sql += " AND session_id = ?"
                params.append(session_id)
            
            if agent_id:
                sql += " AND agent_id = ?"
                params.append(agent_id)
            
            sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(sql, params)
                rows = cursor.fetchall()
                
                return [self._row_to_memory_entry(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to list memories: {e}")
            return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Total entries
                cursor = conn.execute("SELECT COUNT(*) FROM memory_entries")
                total_entries = cursor.fetchone()[0]
                
                # Entries by user
                cursor = conn.execute("""
                    SELECT user_id, COUNT(*) 
                    FROM memory_entries 
                    GROUP BY user_id 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                """)
                entries_by_user = dict(cursor.fetchall())
                
                # Entries by agent
                cursor = conn.execute("""
                    SELECT agent_id, COUNT(*) 
                    FROM memory_entries 
                    WHERE agent_id IS NOT NULL 
                    GROUP BY agent_id 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                """)
                entries_by_agent = dict(cursor.fetchall())
                
                # Average importance
                cursor = conn.execute("SELECT AVG(importance) FROM memory_entries")
                avg_importance = cursor.fetchone()[0] or 0.0
                
                # Storage size (approximate)
                cursor = conn.execute("SELECT SUM(LENGTH(content)) FROM memory_entries")
                storage_size_bytes = cursor.fetchone()[0] or 0
                storage_size_mb = storage_size_bytes / (1024 * 1024)
                
                return {
                    "total_entries": total_entries,
                    "entries_by_user": entries_by_user,
                    "entries_by_agent": entries_by_agent,
                    "storage_size_mb": round(storage_size_mb, 2),
                    "average_importance": round(avg_importance, 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}
    
    def cleanup_old_memories(self, days: int = 30, keep_important: bool = True) -> int:
        """Clean up old memories"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            sql = "DELETE FROM memory_entries WHERE created_at < ?"
            params = [cutoff_date.isoformat()]
            
            if keep_important:
                sql += " AND importance < 0.8"
            
            with self._lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(sql, params)
                    conn.commit()
                    deleted_count = cursor.rowcount
            
            logger.info(f"Cleaned up {deleted_count} old memory entries")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old memories: {e}")
            return 0
    
    def _cleanup_old_entries(self):
        """Cleanup entries if we exceed max_entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM memory_entries")
                total_count = cursor.fetchone()[0]
                
                if total_count > self.max_entries:
                    # Delete oldest entries with low importance
                    excess = total_count - self.max_entries
                    conn.execute("""
                        DELETE FROM memory_entries 
                        WHERE entry_id IN (
                            SELECT entry_id FROM memory_entries 
                            ORDER BY importance ASC, created_at ASC 
                            LIMIT ?
                        )
                    """, (excess,))
                    conn.commit()
                    
                    logger.info(f"Cleaned up {excess} old entries to maintain max_entries limit")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old entries: {e}")
    
    def _row_to_memory_entry(self, row) -> MemoryEntry:
        """Convert database row to MemoryEntry"""
        return MemoryEntry(
            entry_id=row['entry_id'],
            user_id=row['user_id'],
            session_id=row['session_id'],
            agent_id=row['agent_id'],
            content=row['content'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            tags=json.loads(row['tags']) if row['tags'] else [],
            importance=row['importance'],
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
    
    def _calculate_relevance(self, content: str, query: str) -> float:
        """Calculate simple relevance score"""
        try:
            content_lower = content.lower()
            query_lower = query.lower()
            
            # Simple scoring based on word matches
            query_words = query_lower.split()
            content_words = content_lower.split()
            
            if not query_words:
                return 0.0
            
            matches = 0
            for word in query_words:
                if word in content_words:
                    matches += 1
            
            # Basic relevance score
            relevance = matches / len(query_words)
            
            # Boost for exact phrase matches
            if query_lower in content_lower:
                relevance += 0.3
            
            return min(1.0, relevance)
            
        except Exception:
            return 0.0
