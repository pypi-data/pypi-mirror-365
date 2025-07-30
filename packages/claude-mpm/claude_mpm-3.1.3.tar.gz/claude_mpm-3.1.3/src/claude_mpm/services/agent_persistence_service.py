#!/usr/bin/env python3
"""
Agent Persistence Service (Stub)
================================

WHY: This is a stub implementation to support the AgentLifecycleManager integration.
The actual persistence is now handled by AgentManager, but we maintain this interface
for backward compatibility.

DESIGN DECISION: Creating a minimal stub because:
- AgentManager handles the actual file persistence
- This maintains the existing API contract
- Allows for future extension if needed
"""

from typing import Optional, Any
import time

from claude_mpm.models.persistence import (
    PersistenceStrategy,
    PersistenceOperation,
    PersistenceRecord
)

# Backward compatibility exports
__all__ = [
    'PersistenceStrategy',
    'PersistenceOperation',
    'PersistenceRecord',
    'AgentPersistenceService'
]


class AgentPersistenceService:
    """
    Stub implementation for agent persistence service.
    
    WHY: Maintains compatibility with AgentLifecycleManager while
    actual persistence is delegated to AgentManager.
    """
    
    def __init__(self):
        """Initialize the persistence service."""
        pass
    
    async def start(self) -> None:
        """Start the persistence service."""
        # No-op for stub
        pass
    
    async def stop(self) -> None:
        """Stop the persistence service."""
        # No-op for stub
        pass
    
    async def persist_agent(self, agent_name: str, agent_content: str,
                           source_tier: Any, target_tier: Optional[Any] = None,
                           strategy: Optional[PersistenceStrategy] = None) -> PersistenceRecord:
        """
        Create a persistence record (actual persistence handled by AgentManager).
        
        WHY: This method exists for API compatibility but doesn't perform
        actual file operations since AgentManager handles that.
        """
        return PersistenceRecord(
            operation_id=f"persist_{agent_name}_{time.time()}",
            operation_type=PersistenceOperation.UPDATE,
            agent_name=agent_name,
            source_tier=source_tier,
            target_tier=target_tier or source_tier,
            strategy=strategy or PersistenceStrategy.USER_OVERRIDE,
            success=True,
            timestamp=time.time()
        )