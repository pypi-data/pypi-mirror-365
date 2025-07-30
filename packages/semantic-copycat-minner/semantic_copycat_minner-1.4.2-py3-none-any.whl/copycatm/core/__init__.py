"""
Core analysis components for CopycatM.
"""

from .analyzer import CopycatAnalyzer
from .config import AnalysisConfig
from .enhanced_analyzer import EnhancedCopycatAnalyzer
from .exceptions import (
    CopycatError,
    UnsupportedLanguageError,
    ParseError,
    AnalysisError,
    ConfigurationError,
)

__all__ = [
    "CopycatAnalyzer",
    "AnalysisConfig",
    "EnhancedCopycatAnalyzer",
    "CopycatError",
    "UnsupportedLanguageError",
    "ParseError",
    "AnalysisError",
    "ConfigurationError",
] 