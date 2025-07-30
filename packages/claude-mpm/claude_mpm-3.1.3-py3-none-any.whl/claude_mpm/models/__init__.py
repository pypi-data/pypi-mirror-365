"""
Claude MPM Models Package
=========================

Centralized data models for the Claude MPM system.

WHY: This package centralizes all data models to:
- Prevent circular imports
- Reduce code duplication
- Ensure consistent data structures
- Make models easily discoverable

DESIGN DECISION: Models are organized by domain:
- agent_definition: Core agent behavior models
- lifecycle: Agent lifecycle management models
- modification: Change tracking models
- persistence: Storage operation models
- registry: Discovery and management models
- common: Shared constants and enums
"""

# Agent definition models
from .agent_definition import (
    AgentType,
    AgentSection,
    AgentPermissions,
    AgentWorkflow,
    AgentMetadata,
    AgentDefinition
)

# Lifecycle models
from .lifecycle import (
    LifecycleOperation,
    LifecycleState,
    AgentLifecycleRecord,
    LifecycleOperationResult
)

# Modification models
from .modification import (
    ModificationType,
    ModificationTier,
    AgentModification,
    ModificationHistory
)

# Persistence models
from .persistence import (
    PersistenceStrategy,
    PersistenceOperation,
    PersistenceRecord
)

# Registry models
from .registry import (
    AgentTier,
    AgentRegistryMetadata
)

# Common constants
from .common import (
    AGENT_FILE_EXTENSIONS,
    AGENT_IGNORE_PATTERNS,
    CORE_AGENT_TYPES,
    SPECIALIZED_AGENT_TYPES,
    ALL_AGENT_TYPES
)

__all__ = [
    # Agent definition
    'AgentType',
    'AgentSection',
    'AgentPermissions',
    'AgentWorkflow',
    'AgentMetadata',
    'AgentDefinition',
    
    # Lifecycle
    'LifecycleOperation',
    'LifecycleState',
    'AgentLifecycleRecord',
    'LifecycleOperationResult',
    
    # Modification
    'ModificationType',
    'ModificationTier',
    'AgentModification',
    'ModificationHistory',
    
    # Persistence
    'PersistenceStrategy',
    'PersistenceOperation',
    'PersistenceRecord',
    
    # Registry
    'AgentTier',
    'AgentRegistryMetadata',
    
    # Common
    'AGENT_FILE_EXTENSIONS',
    'AGENT_IGNORE_PATTERNS',
    'CORE_AGENT_TYPES',
    'SPECIALIZED_AGENT_TYPES',
    'ALL_AGENT_TYPES'
]