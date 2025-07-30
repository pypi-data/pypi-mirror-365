#!/usr/bin/env python3
"""
Registry Models
===============

Data models for agent registry and discovery.

WHY: These models are extracted from agent_registry.py to centralize
data definitions and avoid duplication with agent_definition.py models.

DESIGN DECISION: Registry models are kept separate from agent definitions
because they serve different purposes:
- Registry models are for discovery and management
- Agent definitions are for execution and behavior
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional
import time


class AgentTier(Enum):
    """Agent hierarchy tiers for registry.
    
    WHY: Different from ModificationTier because registry uses a
    simpler two-tier system (user/system) for discovery.
    """
    USER = "user"
    SYSTEM = "system"


@dataclass
class AgentRegistryMetadata:
    """Registry-specific metadata for discovered agents.
    
    WHY: This is different from AgentMetadata in agent_definition.py because:
    - Registry needs discovery-specific information (path, checksum, etc.)
    - Agent definitions need behavior-specific information
    - Keeping them separate avoids coupling discovery to execution
    
    NOTE: This replaces the AgentMetadata class in agent_registry.py to avoid
    conflicts with the one in agent_definition.py
    """
    name: str
    path: str
    tier: AgentTier
    agent_type: str  # Using string instead of AgentType enum to avoid conflicts
    description: str = ""
    version: str = "0.0.0"
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    file_size: int = 0
    checksum: str = ""
    is_valid: bool = True
    validation_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Compatibility properties for existing code
    @property
    def type(self) -> str:
        """Compatibility property for existing code expecting 'type' attribute."""
        return self.agent_type
    
    @property
    def validated(self) -> bool:
        """Compatibility property for existing code expecting 'validated' attribute."""
        return self.is_valid
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['tier'] = self.tier.value
        # Include compatibility fields
        data['type'] = self.agent_type
        data['validated'] = self.is_valid
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentRegistryMetadata':
        """Create from dictionary."""
        # Handle compatibility fields
        if 'type' in data and 'agent_type' not in data:
            data['agent_type'] = data['type']
        if 'validated' in data and 'is_valid' not in data:
            data['is_valid'] = data['validated']
        
        data['tier'] = AgentTier(data['tier'])
        return cls(**data)