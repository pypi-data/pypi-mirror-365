#!/usr/bin/env python3
"""
Common Models
=============

Shared enums and models used across multiple services.

WHY: This module contains enums and models that are used by multiple
services but don't belong to any specific domain.

DESIGN DECISION: Creating a common module prevents:
- Circular imports between specific model modules
- Duplication of shared enums
- Inconsistencies in shared constants
"""

from enum import Enum


# Note: We're not creating a unified TierType enum here because:
# 1. ModificationTier uses PROJECT/USER/SYSTEM for modification tracking
# 2. AgentTier uses USER/SYSTEM for registry discovery
# 3. AgentType in agent_definition.py is for agent classification (CORE/PROJECT/CUSTOM/etc)
# These serve different purposes and should remain separate.

# Common constants that might be shared across services
AGENT_FILE_EXTENSIONS = {'.md', '.json', '.yaml', '.yml'}
AGENT_IGNORE_PATTERNS = {'__pycache__', '.git', 'node_modules', '.pytest_cache'}

# Core agent types used for classification
CORE_AGENT_TYPES = {
    'engineer', 'architect', 'qa', 'security', 'documentation',
    'ops', 'data', 'research', 'version_control'
}

SPECIALIZED_AGENT_TYPES = {
    'pm_orchestrator', 'frontend', 'backend', 'devops', 'ml',
    'database', 'api', 'mobile', 'cloud', 'testing'
}

ALL_AGENT_TYPES = CORE_AGENT_TYPES | SPECIALIZED_AGENT_TYPES