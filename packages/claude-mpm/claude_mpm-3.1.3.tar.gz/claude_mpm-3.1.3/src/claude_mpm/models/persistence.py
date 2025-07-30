#!/usr/bin/env python3
"""
Persistence Models
==================

Data models for agent persistence operations.

WHY: These models are extracted from agent_persistence_service.py to centralize
data definitions and maintain consistency across services.

DESIGN DECISION: Persistence models are minimal because actual persistence
is now handled by AgentManager, but we maintain these for API compatibility.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Dict


class PersistenceStrategy(Enum):
    """Agent persistence strategies.
    
    WHY: Different strategies allow flexibility in how agents are persisted
    based on their tier and use case.
    """
    USER_OVERRIDE = "user_override"
    PROJECT_SPECIFIC = "project_specific"
    SYSTEM_DEFAULT = "system_default"


class PersistenceOperation(Enum):
    """Persistence operation types."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    BACKUP = "backup"
    RESTORE = "restore"


@dataclass
class PersistenceRecord:
    """Record of a persistence operation.
    
    WHY: Tracks persistence operations for audit trails and debugging,
    even though actual persistence is delegated to AgentManager.
    """
    operation_id: str
    operation_type: PersistenceOperation
    agent_name: str
    source_tier: Any  # Can be ModificationTier or string
    target_tier: Optional[Any] = None
    strategy: Optional[PersistenceStrategy] = None
    success: bool = True
    timestamp: float = 0.0
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)