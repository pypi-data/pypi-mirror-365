#!/usr/bin/env python3
"""
Lifecycle Models
================

Data models for agent lifecycle management.

WHY: These models are extracted from agent_lifecycle_manager.py to centralize
data definitions and reduce duplication across services.

DESIGN DECISION: Keeping lifecycle-specific models separate allows:
- Clear separation of concerns
- Easy reuse across different services
- Independent evolution of data structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from claude_mpm.models.modification import ModificationTier


class LifecycleOperation(Enum):
    """Agent lifecycle operations."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    RESTORE = "restore"
    MIGRATE = "migrate"
    REPLICATE = "replicate"
    VALIDATE = "validate"


class LifecycleState(Enum):
    """Agent lifecycle states."""
    ACTIVE = "active"
    MODIFIED = "modified"
    DELETED = "deleted"
    CONFLICTED = "conflicted"
    MIGRATING = "migrating"
    VALIDATING = "validating"


@dataclass
class AgentLifecycleRecord:
    """Complete lifecycle record for an agent.
    
    WHY: This model tracks the complete history and state of an agent
    throughout its lifecycle, enabling audit trails and state management.
    """
    
    agent_name: str
    current_state: LifecycleState
    tier: ModificationTier
    file_path: str
    created_at: float
    last_modified: float
    version: str
    modifications: List[str] = field(default_factory=list)  # Modification IDs
    persistence_operations: List[str] = field(default_factory=list)  # Operation IDs
    backup_paths: List[str] = field(default_factory=list)
    validation_status: str = "valid"
    validation_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_days(self) -> float:
        """Get age in days."""
        import time
        return (time.time() - self.created_at) / (24 * 3600)
    
    @property
    def last_modified_datetime(self) -> datetime:
        """Get last modified as datetime."""
        return datetime.fromtimestamp(self.last_modified)


@dataclass
class LifecycleOperationResult:
    """Result of a lifecycle operation.
    
    WHY: Provides a consistent structure for operation results,
    making it easier to track success/failure and gather metrics.
    """
    
    operation: LifecycleOperation
    agent_name: str
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    modification_id: Optional[str] = None
    persistence_id: Optional[str] = None
    cache_invalidated: bool = False
    registry_updated: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)