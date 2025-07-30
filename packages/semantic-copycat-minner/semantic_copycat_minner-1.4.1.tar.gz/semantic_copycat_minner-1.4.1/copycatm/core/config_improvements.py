"""
Configuration for using improved components in CopycatM.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from ..analysis import ImprovedInvariantExtractor, EnhancedAlgorithmDetector
from ..hashing import ImprovedSemanticHasher


@dataclass
class ImprovementConfig:
    """Configuration for improved components."""
    use_improved_minhash: bool = True
    use_enhanced_algorithm_detector: bool = True
    use_improved_invariant_extractor: bool = True
    minhash_num_perm: int = 256
    minhash_shingle_size: int = 4
    algorithm_context_boost: bool = True
    invariant_type_classification: bool = True


def create_improved_analyzer(base_analyzer):
    """
    Create an analyzer instance with improved components.
    
    Args:
        base_analyzer: The base CopycatAnalyzer instance
        
    Returns:
        Enhanced analyzer with improved components
    """
    config = ImprovementConfig()
    
    # Replace components with improved versions
    if config.use_improved_minhash:
        base_analyzer.semantic_hasher = ImprovedSemanticHasher(
            num_perm=config.minhash_num_perm,
            shingle_size=config.minhash_shingle_size
        )
    
    if config.use_enhanced_algorithm_detector:
        base_analyzer.algorithm_detector = EnhancedAlgorithmDetector()
    
    if config.use_improved_invariant_extractor:
        base_analyzer.invariant_extractor = ImprovedInvariantExtractor()
    
    return base_analyzer


def apply_improvements_to_results(results: Dict[str, Any], analyzer: Any) -> Dict[str, Any]:
    """
    Apply improvements to analysis results.
    
    This function can be used to enhance results from the standard analyzer
    by re-processing with improved components.
    """
    improved_results = results.copy()
    
    # Re-analyze algorithms with enhanced detector if available
    if hasattr(analyzer, 'algorithm_detector') and isinstance(analyzer.algorithm_detector, EnhancedAlgorithmDetector):
        # Enhanced algorithm detection already applied
        pass
    
    # Re-extract invariants with type classification if available
    if hasattr(analyzer, 'invariant_extractor') and isinstance(analyzer.invariant_extractor, ImprovedInvariantExtractor):
        # Improved invariant extraction already applied
        pass
    
    # Re-generate MinHash with improved algorithm if available
    if hasattr(analyzer, 'semantic_hasher') and isinstance(analyzer.semantic_hasher, ImprovedSemanticHasher):
        # Improved MinHash already applied
        pass
    
    return improved_results