#!/usr/bin/env python3
"""
Modification Models
===================

Data models for agent modification tracking.

WHY: These models are extracted from agent_modification_tracker.py to centralize
data definitions and enable reuse across services.

DESIGN DECISION: Modification tracking models are kept separate because:
- They represent a distinct domain (change tracking)
- Multiple services need to work with modifications
- The structure can evolve independently of other models
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import time


class ModificationType(Enum):
    """Types of agent modifications."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    MOVE = "move"
    RESTORE = "restore"


class ModificationTier(Enum):
    """Agent hierarchy tiers for modification tracking.
    
    WHY: This enum is used across multiple services to ensure
    consistent tier classification throughout the system.
    """
    PROJECT = "project"
    USER = "user"
    SYSTEM = "system"


@dataclass
class AgentModification:
    """Agent modification record with comprehensive metadata.
    
    WHY: This model captures all relevant information about a single
    modification event, enabling detailed audit trails and rollback capabilities.
    """
    
    modification_id: str
    agent_name: str
    modification_type: ModificationType
    tier: ModificationTier
    file_path: str
    timestamp: float
    user_id: Optional[str] = None
    modification_details: Dict[str, Any] = field(default_factory=dict)
    file_hash_before: Optional[str] = None
    file_hash_after: Optional[str] = None
    file_size_before: Optional[int] = None
    file_size_after: Optional[int] = None
    backup_path: Optional[str] = None
    validation_status: str = "pending"
    validation_errors: List[str] = field(default_factory=list)
    related_modifications: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def modification_datetime(self) -> datetime:
        """Get modification timestamp as datetime."""
        return datetime.fromtimestamp(self.timestamp)
    
    @property
    def age_seconds(self) -> float:
        """Get age of modification in seconds."""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['modification_type'] = self.modification_type.value
        data['tier'] = self.tier.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentModification':
        """Create from dictionary."""
        data['modification_type'] = ModificationType(data['modification_type'])
        data['tier'] = ModificationTier(data['tier'])
        return cls(**data)


@dataclass
class ModificationHistory:
    """Complete modification history for an agent.
    
    WHY: Aggregates all modifications for a single agent, providing
    a complete change history for analysis and rollback.
    """
    
    agent_name: str
    modifications: List[AgentModification] = field(default_factory=list)
    current_version: Optional[str] = None
    total_modifications: int = 0
    first_seen: Optional[float] = None
    last_modified: Optional[float] = None
    
    def add_modification(self, modification: AgentModification) -> None:
        """Add a modification to history."""
        self.modifications.append(modification)
        self.total_modifications += 1
        self.last_modified = modification.timestamp
        
        if self.first_seen is None:
            self.first_seen = modification.timestamp
    
    def get_recent_modifications(self, hours: int = 24) -> List[AgentModification]:
        """Get modifications within specified hours."""
        cutoff = time.time() - (hours * 3600)
        return [mod for mod in self.modifications if mod.timestamp >= cutoff]
    
    def get_modifications_by_type(self, mod_type: ModificationType) -> List[AgentModification]:
        """Get modifications by type."""
        return [mod for mod in self.modifications if mod.modification_type == mod_type]