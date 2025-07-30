"""
Analysis components for CopycatM.
"""

from .metadata import MetadataExtractor
from .complexity import ComplexityAnalyzer
from .algorithm_detector import AlgorithmDetector
from .invariant_extractor import InvariantExtractor
from .algorithmic_normalizer import AlgorithmicNormalizer
from .algorithm_types import AlgorithmType
from .invariant_extractor_improved import ImprovedInvariantExtractor, InvariantType
from .algorithm_detector_enhanced import EnhancedAlgorithmDetector
from .mathematical_invariance import MathematicalInvariantDetector, MathematicalProperty
from .coherence_validator import CoherenceValidator, CoherenceLevel, CoherenceResult

__all__ = [
    "MetadataExtractor",
    "ComplexityAnalyzer", 
    "AlgorithmDetector",
    "InvariantExtractor",
    "AlgorithmicNormalizer",
    "AlgorithmType",
    "ImprovedInvariantExtractor",
    "InvariantType",
    "EnhancedAlgorithmDetector",
    "MathematicalInvariantDetector",
    "MathematicalProperty",
    "CoherenceValidator",
    "CoherenceLevel",
    "CoherenceResult",
] 