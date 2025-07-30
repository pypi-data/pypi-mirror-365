"""
Algorithm detector with better specificity to reduce over-similarity.
"""

import re
from typing import Dict, List, Any, Optional, Set, Union
from collections import defaultdict
import hashlib
import json

from .algorithm_types import AlgorithmType
from .algorithmic_normalizer import AlgorithmicNormalizer
from .unknown_algorithm_detector import UnknownAlgorithmDetector
from ..core.config import AnalysisConfig
from ..hashing.direct import DirectHasher
from ..hashing.fuzzy_improved import ImprovedFuzzyHasher
from ..hashing.semantic import SemanticHasher
from ..data.language_configs import (
    get_language_config, 
    detect_oss_signatures,
    get_enhanced_patterns,
    ALGORITHM_PATTERNS
)
import uuid


class AlgorithmDetector:
    """Algorithm detector with improved pattern matching specificity."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.patterns = self._initialize_specific_patterns()
        
        # Define pattern checking priority (higher priority checked first)
        self.pattern_priority = [
            AlgorithmType.AUDIO_CODEC,             # Check audio codec patterns first
            AlgorithmType.VIDEO_CODEC,             # Then video codec patterns
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM, # Then crypto patterns (high confidence)
            AlgorithmType.NUMERICAL_ALGORITHM,     # Then mathematical patterns
            AlgorithmType.SORTING_ALGORITHM,       # Then sorting algorithms
            AlgorithmType.DYNAMIC_PROGRAMMING,     # Then DP patterns
            AlgorithmType.COMPRESSION_ALGORITHM,   # Then compression
            AlgorithmType.SEARCH_ALGORITHM,        # Search algorithms after sorting
            AlgorithmType.ITERATOR_PATTERN,        # Then iterators
            AlgorithmType.POLYFILL_PATTERN,        # Then polyfills
            AlgorithmType.ARRAY_MANIPULATION,      # Then array ops
            AlgorithmType.OBJECT_MANIPULATION,     # Finally object ops
        ]
        
        # Initialize components for hashing
        self.normalizer = AlgorithmicNormalizer()
        self.direct_hasher = DirectHasher()
        self.fuzzy_hasher = ImprovedFuzzyHasher()
        self.semantic_hasher = SemanticHasher(num_perm=128, lsh_bands=config.lsh_bands if config else 20)
        
        # Initialize unknown algorithm detector
        self.unknown_detector = UnknownAlgorithmDetector(min_complexity_score=0.6)
        
    def _initialize_specific_patterns(self) -> Dict[AlgorithmType, Dict]:
        """Initialize highly specific algorithm patterns to reduce false positives."""
        return {
            # Object manipulation algorithms
            AlgorithmType.OBJECT_MANIPULATION: {
                'subtypes': {
                    'object_merge': {
                        'keywords': ['assign', 'merge', 'extend'],
                        'required_patterns': ['property_iteration', 'property_copy', 'hasOwnProperty'],
                        'ast_patterns': ['for_in_loop', 'property_assignment'],
                        'confidence_boost': 0.3
                    },
                    'object_spread': {
                        'keywords': ['__rest', 'spread', 'getOwnPropertySymbols'],
                        'required_patterns': ['property_enumeration', 'symbol_handling'],
                        'ast_patterns': ['property_iteration', 'symbol_check'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Array manipulation algorithms
            AlgorithmType.ARRAY_MANIPULATION: {
                'subtypes': {
                    'array_spread': {
                        'keywords': ['__spread', '__spreadArrays', '__spreadArray'],
                        'required_patterns': ['nested_loops', 'array_indexing', 'length_accumulation'],
                        'ast_patterns': ['for_loop', 'array_assignment'],
                        'confidence_boost': 0.3
                    },
                    'array_concat': {
                        'keywords': ['concat', 'merge', 'flatten'],
                        'required_patterns': ['array_iteration', 'element_copy'],
                        'ast_patterns': ['loop', 'array_access'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Iterator patterns
            AlgorithmType.ITERATOR_PATTERN: {
                'subtypes': {
                    'iterator_protocol': {
                        'keywords': ['__values', 'Symbol.iterator', 'next', 'done'],
                        'required_patterns': ['iterator_interface', 'state_tracking'],
                        'ast_patterns': ['object_return', 'method_definition'],
                        'confidence_boost': 0.3
                    },
                    'async_generator': {
                        'keywords': ['__asyncGenerator', '__await', 'Promise'],
                        'required_patterns': ['state_machine', 'promise_handling'],
                        'ast_patterns': ['switch_statement', 'promise_call'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Polyfill patterns
            AlgorithmType.POLYFILL_PATTERN: {
                'subtypes': {
                    'object_assign_polyfill': {
                        'keywords': ['Object.assign', '__assign'],
                        'required_patterns': ['native_check', 'fallback_loop'],
                        'ast_patterns': ['or_operator', 'for_loop'],
                        'confidence_boost': 0.3
                    },
                    'runtime_helper': {
                        'keywords': ['__extends', '__decorate', '__param'],
                        'required_patterns': ['helper_pattern', 'prototype_chain'],
                        'ast_patterns': ['function_assignment', 'prototype_access'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Sorting algorithms - very specific patterns
            AlgorithmType.SORTING_ALGORITHM: {
                'subtypes': {
                    'quicksort': {
                        'keywords': ['quicksort', 'quick_sort', 'pivot', 'partition'],
                        'required_patterns': ['pivot_selection', 'partition_logic', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'bubble_sort': {
                        'keywords': ['bubble_sort', 'bubble'],
                        'required_patterns': ['nested_loops', 'adjacent_comparison', 'swap_operation'],
                        'ast_patterns': ['double_for_loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.4
                    },
                    'merge_sort': {
                        'keywords': ['merge_sort', 'merge', 'divide'],
                        'required_patterns': ['merge_function', 'divide_conquer', 'recursive_calls'],
                        'ast_patterns': ['recursive_function', 'array_split'],
                        'confidence_boost': 0.3
                    },
                    'heap_sort': {
                        'keywords': ['heap_sort', 'heapify', 'heap'],
                        'required_patterns': ['heapify_operation', 'parent_child_comparison', 'swap_operation'],
                        'ast_patterns': ['loop', 'comparison', 'assignment'],
                        'confidence_boost': 0.3
                    },
                    'generic_sort': {
                        'keywords': ['sort', 'compare'],
                        'required_patterns': ['comparison_operation', 'element_swap'],
                        'ast_patterns': ['loop', 'comparison', 'assignment'],
                        'confidence_boost': -0.1  # Penalty for generic
                    }
                }
            },
            
            # Search algorithms - distinct patterns
            AlgorithmType.SEARCH_ALGORITHM: {
                'subtypes': {
                    'binary_search': {
                        'keywords': ['binary', 'mid', 'middle', 'left', 'right'],
                        'required_patterns': ['mid_calculation', 'binary_division', 'comparison_with_target', 'range_adjustment'],
                        'ast_patterns': ['while_loop_or_recursion', 'arithmetic_operation', 'comparison', 'assignment'],
                        'confidence_boost': 0.3
                    },
                    'linear_search': {
                        'keywords': ['find', 'search', 'linear'],
                        'required_patterns': ['single_loop', 'element_comparison', 'return_on_match'],
                        'ast_patterns': ['for_loop', 'if_statement', 'return_statement'],
                        'confidence_boost': 0.2
                    },
                    'generic_search': {
                        'keywords': ['search', 'find', 'locate'],
                        'required_patterns': ['iteration', 'comparison'],
                        'ast_patterns': ['loop', 'comparison'],
                        'confidence_boost': -0.2  # Penalty for generic
                    }
                }
            },
            
            # Mathematical algorithms - unique patterns
            AlgorithmType.NUMERICAL_ALGORITHM: {
                'subtypes': {
                    'fibonacci': {
                        'keywords': ['fibonacci', 'fib'],
                        'required_patterns': ['n_minus_1', 'n_minus_2', 'addition'],
                        'ast_patterns': ['recursive_or_iterative', 'arithmetic_operation'],
                        'confidence_boost': 0.4
                    },
                    'factorial': {
                        'keywords': ['factorial', 'fact'],
                        'required_patterns': ['n_multiplication', 'decremental_loop_or_recursion'],
                        'ast_patterns': ['multiplication', 'decrement'],
                        'confidence_boost': 0.3
                    },
                    'prime': {
                        'keywords': ['prime', 'divisor'],
                        'required_patterns': ['modulo_operation', 'divisibility_check'],
                        'ast_patterns': ['modulo', 'loop', 'comparison'],
                        'confidence_boost': 0.2
                    },
                    'gcd': {
                        'keywords': ['gcd', 'greatest', 'common', 'divisor'],
                        'required_patterns': ['modulo_operation', 'swap_or_recursion', 'while_with_modulo'],
                        'ast_patterns': ['modulo', 'while_loop_or_recursion'],
                        'confidence_boost': 0.3
                    },
                    'lcm': {
                        'keywords': ['lcm', 'least', 'common', 'multiple'],
                        'required_patterns': ['multiplication', 'division', 'gcd_call_or_impl'],
                        'ast_patterns': ['multiplication', 'division'],
                        'confidence_boost': 0.3
                    },
                    'power': {
                        'keywords': ['power', 'pow', 'exponent', 'base'],
                        'required_patterns': ['exponent_check', 'recursive_multiplication', 'base_exponent'],
                        'ast_patterns': ['loop_or_recursion', 'multiplication', 'if_statement'],
                        'confidence_boost': 0.4
                    }
                }
            },
            
            # Compression algorithms
            AlgorithmType.COMPRESSION_ALGORITHM: {
                'subtypes': {
                    'huffman': {
                        'keywords': ['huffman', 'frequency', 'encoding'],
                        'required_patterns': ['frequency_counting', 'tree_building', 'encoding'],
                        'ast_patterns': ['hash_map', 'tree_structure'],
                        'confidence_boost': 0.3
                    },
                    'lzw': {
                        'keywords': ['lzw', 'dictionary', 'compress'],
                        'required_patterns': ['dictionary_building', 'pattern_matching'],
                        'ast_patterns': ['hash_map', 'string_manipulation'],
                        'confidence_boost': 0.3
                    }
                }
            },
            
            # Dynamic programming
            AlgorithmType.DYNAMIC_PROGRAMMING: {
                'subtypes': {
                    'memoization': {
                        'keywords': ['memo', 'cache', 'dp'],
                        'required_patterns': ['cache_check', 'cache_store', 'recursive_structure'],
                        'ast_patterns': ['hash_map', 'recursive_function'],
                        'confidence_boost': 0.3
                    },
                    'tabulation': {
                        'keywords': ['table', 'dp', 'dynamic'],
                        'required_patterns': ['table_initialization', 'iterative_filling'],
                        'ast_patterns': ['array_initialization', 'nested_loops'],
                        'confidence_boost': 0.2
                    }
                }
            },
            
            # Cryptographic algorithms
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM: {
                'subtypes': {
                    'rsa': {
                        'keywords': ['rsa', 'modulus', 'exponent', 'public_key', 'private_key', 'modpow', 'rsa_encrypt', 'rsa_decrypt'],
                        'required_patterns': ['modular_exponentiation', 'prime_generation_or_check', 'key_generation'],
                        'ast_patterns': ['modulo_operation', 'exponentiation', 'prime_check'],
                        'confidence_boost': 0.4
                    },
                    'aes': {
                        'keywords': ['aes', 'rijndael', 'block_cipher', 'sbox', 'subbytes', 'shiftrows', 'mixcolumns', 'addroundkey'],
                        'required_patterns': ['substitution_table', 'matrix_operations', 'xor_operations'],
                        'ast_patterns': ['array_lookup', 'bitwise_operations', 'for_loop'],
                        'confidence_boost': 0.4
                    },
                    'sha': {
                        'keywords': ['sha', 'sha1', 'sha256', 'sha512', 'digest', 'hash', 'message_digest'],
                        'required_patterns': ['bit_rotation', 'xor_operations', 'constant_array'],
                        'ast_patterns': ['bitwise_operations', 'array_constants', 'loop'],
                        'confidence_boost': 0.4
                    },
                    'md5': {
                        'keywords': ['md5', 'message_digest', 'hash'],
                        'required_patterns': ['bit_rotation', 'xor_operations', 'four_rounds'],
                        'ast_patterns': ['bitwise_operations', 'loop', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'hmac': {
                        'keywords': ['hmac', 'keyed_hash', 'message_authentication'],
                        'required_patterns': ['key_padding', 'inner_hash', 'outer_hash'],
                        'ast_patterns': ['xor_operations', 'hash_function_call', 'concatenation'],
                        'confidence_boost': 0.3
                    },
                    'diffie_hellman': {
                        'keywords': ['diffie', 'hellman', 'dh', 'key_exchange', 'shared_secret'],
                        'required_patterns': ['modular_exponentiation', 'prime_check', 'generator'],
                        'ast_patterns': ['modulo_operation', 'exponentiation'],
                        'confidence_boost': 0.3
                    },
                    'elliptic_curve': {
                        'keywords': ['elliptic', 'curve', 'ecc', 'ecdsa', 'ecdh', 'point_addition', 'scalar_multiplication'],
                        'required_patterns': ['point_operations', 'modular_arithmetic', 'curve_equation'],
                        'ast_patterns': ['coordinate_operations', 'modulo_operation'],
                        'confidence_boost': 0.4
                    },
                    'chacha20': {
                        'keywords': ['chacha', 'chacha20', 'quarter_round', 'stream_cipher'],
                        'required_patterns': ['quarter_round', 'bit_rotation', 'xor_operations'],
                        'ast_patterns': ['bitwise_operations', 'array_manipulation'],
                        'confidence_boost': 0.3
                    },
                    'bcrypt': {
                        'keywords': ['bcrypt', 'blowfish', 'password_hash', 'salt'],
                        'required_patterns': ['salt_generation', 'key_expansion', 'blowfish_operations'],
                        'ast_patterns': ['loop', 'xor_operations', 'substitution'],
                        'confidence_boost': 0.3
                    },
                    'pbkdf2': {
                        'keywords': ['pbkdf2', 'key_derivation', 'iteration_count', 'salt'],
                        'required_patterns': ['hmac_iterations', 'salt_usage', 'xor_accumulation'],
                        'ast_patterns': ['loop', 'hmac_call', 'xor_operations'],
                        'confidence_boost': 0.3
                    },
                    'generic_crypto': {
                        'keywords': ['encrypt', 'decrypt', 'cipher', 'crypto', 'key'],
                        'required_patterns': ['key_usage', 'data_transformation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': -0.1  # Penalty for generic
                    }
                }
            },
            
            # Audio Codec Algorithms
            AlgorithmType.AUDIO_CODEC: {
                'subtypes': {
                    'mp3_codec': {
                        'keywords': ['mp3', 'mpeg', 'layer3', 'layer_3', 'psychoacoustic', 'mdct', 'huffman_decode', 'bit_reservoir', 'granule'],
                        'required_patterns': ['audio_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'aac_codec': {
                        'keywords': ['aac', 'advanced_audio', 'm4a', 'spectral', 'tns', 'pns', 'sbr', 'aac_encode', 'aac_decode'],
                        'required_patterns': ['audio_processing', 'spectral_processing'],
                        'ast_patterns': ['loop', 'transform_operation'],
                        'confidence_boost': 0.3
                    },
                    'opus_codec': {
                        'keywords': ['opus', 'celt', 'silk', 'hybrid_codec', 'opus_encode', 'opus_decode'],
                        'required_patterns': ['audio_processing', 'frame_processing'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'flac_codec': {
                        'keywords': ['flac', 'lossless', 'rice_encoding', 'linear_prediction', 'flac_encode'],
                        'required_patterns': ['audio_processing', 'prediction_operation'],
                        'ast_patterns': ['loop', 'arithmetic_operation'],
                        'confidence_boost': 0.3
                    },
                    'pcm_codec': {
                        'keywords': ['pcm', 'audio_format_pcm', 'pcm_s16', 'pcm_s24', 'raw_audio', 'linear_pcm'],
                        'required_patterns': ['audio_processing'],
                        'ast_patterns': ['assignment', 'array_access'],
                        'confidence_boost': 0.1
                    }
                }
            },
            
            # Video Codec Algorithms
            AlgorithmType.VIDEO_CODEC: {
                'subtypes': {
                    'h264': {
                        'keywords': ['h264', 'avc', 'cabac', 'cavlc', 'intra_prediction', 'deblocking_filter', 'h264_encode', 'h264_decode'],
                        'required_patterns': ['video_processing', 'prediction_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    },
                    'h265': {
                        'keywords': ['h265', 'hevc', 'ctu', 'coding_tree', 'hevc_encode', 'hevc_decode'],
                        'required_patterns': ['video_processing', 'tree_structure'],
                        'ast_patterns': ['loop', 'recursive_structure'],
                        'confidence_boost': 0.3
                    },
                    'vp8': {
                        'keywords': ['vp8', 'webm', 'bool_decoder', 'dct_coefficients', 'vp8_decode'],
                        'required_patterns': ['video_processing', 'transform_operation'],
                        'ast_patterns': ['loop', 'bitwise_operations'],
                        'confidence_boost': 0.3
                    },
                    'vp9': {
                        'keywords': ['vp9', 'superblock', 'transform_size', 'vp9_decode', 'vp9_encode'],
                        'required_patterns': ['video_processing', 'block_processing'],
                        'ast_patterns': ['loop', 'conditional'],
                        'confidence_boost': 0.3
                    },
                    'av1': {
                        'keywords': ['av1', 'aom', 'superres', 'cdef', 'restoration', 'av1_decode'],
                        'required_patterns': ['video_processing', 'filtering_operation'],
                        'ast_patterns': ['loop', 'function_call'],
                        'confidence_boost': 0.3
                    }
                }
            }
        }
    
    def detect(self, ast_tree: Any, language: str, file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity."""
        return self.detect_algorithms(ast_tree, language, file_lines)
    
    def detect_algorithms(self, ast_tree: Any, language: str, file_lines: Optional[int] = None) -> List[Dict[str, Any]]:
        """Detect algorithms with improved specificity and unknown algorithm detection."""
        detected_algorithms = []
        
        # Get language configuration
        lang_config = get_language_config(language)
        min_lines = lang_config.get("min_lines", 20)
        min_func_lines = lang_config.get("min_function_lines", 2)
        unknown_threshold = lang_config.get("unknown_algorithm_threshold", 50)
        
        # Extract functions from AST
        functions = self._extract_functions_from_ast(ast_tree)
        
        # Phase 1: Pattern-based detection for known algorithms
        for func in functions:
            # Skip functions below language-specific threshold
            if func['lines']['total'] < min_func_lines:
                continue
                
            # Analyze each function for specific algorithm patterns
            algorithm = self._analyze_function_with_specificity(func, ast_tree, language)
            if algorithm:
                detected_algorithms.append(algorithm)
        
        # Phase 2: Enhanced pattern detection using language-specific patterns
        if hasattr(ast_tree, 'code'):
            enhanced_algorithms = self._detect_enhanced_patterns(
                ast_tree.code, functions, language, detected_algorithms
            )
            detected_algorithms.extend(enhanced_algorithms)
        
        # Phase 3: Unknown algorithm detection for files above threshold
        if file_lines and file_lines >= unknown_threshold:
            # Get functions that weren't detected as known algorithms
            detected_func_names = {algo.get('function_name', '') for algo in detected_algorithms}
            unclassified_functions = [f for f in functions if f.get('name', '') not in detected_func_names]
            
            # If we have unclassified functions, run unknown algorithm detection
            if unclassified_functions:
                unknown_algorithms = self.unknown_detector.detect_unknown_algorithms(
                    ast_tree, language, file_lines
                )
                detected_algorithms.extend(unknown_algorithms)
        
        # Phase 4: OSS library signature detection
        if hasattr(ast_tree, 'code'):
            oss_signatures = detect_oss_signatures(ast_tree.code, language)
            for sig in oss_signatures:
                # Add OSS signatures as metadata to algorithms or create synthetic entries
                if detected_algorithms:
                    # Boost confidence of algorithms if they match OSS patterns
                    for algo in detected_algorithms:
                        algo['oss_signatures'] = algo.get('oss_signatures', [])
                        algo['oss_signatures'].append(sig)
                        algo['confidence'] = min(algo.get('confidence', 0) + sig['confidence'] * 0.1, 1.0)
                else:
                    # Create a synthetic algorithm entry for OSS detection
                    detected_algorithms.append({
                        "algorithm_type": "OSS_LIBRARY_PATTERN",
                        "subtype": f"{sig['library']}_pattern",
                        "confidence": sig['confidence'],
                        "oss_signatures": [sig],
                        "function_name": f"oss_{sig['library']}_usage",
                        "file_lines": file_lines or 0
                    })
        
        # Filter out zero-confidence detections to reduce noise
        filtered_algorithms = []
        for algo in detected_algorithms:
            confidence = algo.get('confidence_score', algo.get('confidence', 0))
            # Keep algorithms with confidence > 0 or those with explicit evidence
            if confidence > 0.0 or algo.get('oss_signatures') or algo.get('evidence', {}).get('matched_keywords'):
                filtered_algorithms.append(algo)
        
        return filtered_algorithms
    
    def detect_algorithms_from_input(self, 
                                   input_data: Union[str, Any], 
                                   language: str) -> List[Dict[str, Any]]:
        """
        Detect algorithms from either raw content or pre-parsed AST.
        
        This is a convenience method that automatically determines whether the input
        is raw code content or a pre-parsed AST tree and processes it accordingly.
        
        Args:
            input_data: Either string content or pre-parsed AST tree
            language: Programming language (e.g., 'python', 'javascript', 'java')
            
        Returns:
            List of detected algorithms with their properties
            
        Examples:
            # Using with raw content
            content = "def quicksort(arr): ..."
            algorithms = detector.detect_algorithms_from_input(content, "python")
            
            # Using with pre-parsed AST
            ast_tree = parser.parse(content, "python")
            algorithms = detector.detect_algorithms_from_input(ast_tree, "python")
        """
        if isinstance(input_data, str):
            # It's raw content - parse it
            from ..parsers.tree_sitter_parser import TreeSitterParser
            parser = TreeSitterParser()
            ast_tree = parser.parse(input_data, language)
        else:
            # Assume it's already an AST
            ast_tree = input_data
        
        return self.detect_algorithms(ast_tree, language)
    
    def _detect_enhanced_patterns(self, code: str, functions: List[Dict], 
                                 language: str, existing_algorithms: List[Dict]) -> List[Dict[str, Any]]:
        """Detect algorithms using enhanced patterns from language configs."""
        detected = []
        existing_funcs = {algo.get('function_name', '') for algo in existing_algorithms}
        
        # Check each category of enhanced patterns
        for category, patterns in ALGORITHM_PATTERNS.items():
            category_patterns = get_enhanced_patterns(language, category)
            
            for algo_name, pattern_config in category_patterns.items():
                # Check each function against the pattern
                for func in functions:
                    if func['name'] in existing_funcs:
                        continue
                    
                    func_text = func['text'].lower()
                    score = 0
                    matches = []
                    
                    # Check patterns
                    for pattern in pattern_config.get('patterns', []):
                        if re.search(pattern, func_text, re.IGNORECASE | re.MULTILINE):
                            score += 0.15
                            matches.append(pattern)
                    
                    # Check required elements
                    required = pattern_config.get('required_elements', [])
                    if required:
                        required_found = 0
                        for req in required:
                            # Handle OR conditions in requirements
                            req_parts = req.split('|')
                            for part in req_parts:
                                if part in func_text:
                                    required_found += 1
                                    break
                        
                        if required_found < len(required):
                            continue  # Skip if not all required elements found
                    
                    # If we have enough matches, create algorithm entry
                    if score >= pattern_config.get('confidence', 0.5) * 0.5:
                        detected.append({
                            "algorithm_type": category.upper(),
                            "subtype": algo_name,
                            "confidence": min(score + pattern_config.get('confidence', 0.5), 1.0),
                            "function_name": func['name'],
                            "pattern_matches": matches[:3],
                            "enhanced_detection": True,
                            "start_line": func['lines']['start'],
                            "end_line": func['lines']['end'],
                            "complexity": {
                                "cyclomatic": self._calculate_cyclomatic_complexity(func['node'])
                            }
                        })
        
        return detected
    
    def _analyze_function_with_specificity(self, func: Dict[str, Any], ast_tree: Any, language: str) -> Optional[Dict[str, Any]]:
        """Analyze function with specific pattern matching to reduce false positives."""
        func_text = func['text'].lower()
        func_name = func['name'].lower()
        
        # Get language config for minimum lines
        lang_config = get_language_config(language)
        min_func_lines = lang_config.get("min_function_lines", 2)
        
        # Skip very small functions based on language config
        if func['lines']['total'] < min_func_lines:
            return None
        
        best_match = None
        best_confidence = 0.0
        best_subtype = None
        
        # Check each algorithm type in priority order
        for algo_type in self.pattern_priority:
            if algo_type not in self.patterns:
                continue
            
            type_config = self.patterns[algo_type]
            for subtype_name, subtype_pattern in type_config['subtypes'].items():
                confidence = self._calculate_specific_confidence(
                    func_text, func_name, func['node'], 
                    subtype_pattern, subtype_name, language, algo_type
                )
                
                if confidence > best_confidence and confidence >= 0.3:  # Higher threshold
                    best_confidence = confidence
                    best_match = algo_type
                    best_subtype = subtype_name
        
        if best_match:
            return self._create_specific_algorithm_entry(
                func, best_match, best_subtype, best_confidence, 
                ast_tree, language
            )
        
        return None
    
    def _calculate_specific_confidence(self, func_text: str, func_name: str, 
                                     func_node: Any, pattern: Dict, subtype: str, 
                                     language: str = None, algo_type: Any = None) -> float:
        """Calculate confidence with required pattern checking."""
        confidence = 0.0
        
        # 1. Keyword matching (reduced weight)
        keyword_score = self._calculate_keyword_score(func_text, func_name, pattern.get('keywords', []))
        confidence += keyword_score * 0.2  # Only 20% weight
        
        # 2. Required patterns (high weight)
        required_patterns = pattern.get('required_patterns', [])
        if required_patterns:
            required_score = self._check_required_patterns(func_text, func_node, required_patterns)
            # If required patterns exist but score is too low, reject the match
            if required_score < 0.5:
                return 0.0  # Fail fast if required patterns aren't met
            confidence += required_score * 0.5  # 50% weight
        
        # 3. AST pattern matching
        ast_score = self._check_ast_patterns(func_node, pattern.get('ast_patterns', []))
        confidence += ast_score * 0.3  # 30% weight
        
        # 4. Apply confidence boost for highly specific patterns
        if confidence > 0.5:  # Only boost if base confidence is decent
            confidence += pattern.get('confidence_boost', 0)
        
        # 5. Penalty for generic subtypes
        if subtype.endswith('_generic') or subtype == 'generic':
            confidence *= 0.5  # Reduce confidence for generic matches
        
        # 6. Language-specific adjustments
        if language == 'c':
            # C code often has arithmetic/division in non-algorithm contexts (e.g., size calculations)
            if subtype in ['fibonacci', 'factorial', 'lcm', 'gcd'] and confidence < 0.6:
                confidence *= 0.5  # Reduce false positives for weak matches
        
        # 7. Codec-specific minimum thresholds
        if algo_type in [AlgorithmType.AUDIO_CODEC, AlgorithmType.VIDEO_CODEC]:
            # Codecs require higher confidence to avoid false positives
            if confidence < 0.6:
                return 0.0  # Reject weak codec matches
        
        return min(confidence, 1.0)
    
    def _calculate_keyword_score(self, func_text: str, func_name: str, keywords: List[str]) -> float:
        """Calculate keyword matching score with context awareness."""
        if not keywords:
            return 0.0
        
        score = 0.0
        matched_keywords = 0
        
        # Convert to lowercase for case-insensitive matching
        func_text_lower = func_text.lower()
        func_name_lower = func_name.lower()
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Check function name (higher weight)
            if keyword_lower in func_name_lower:
                score += 2.0
                matched_keywords += 1
            # Check function text
            elif re.search(rf'\b{keyword_lower}\b', func_text_lower):
                score += 1.0
                matched_keywords += 1
        
        # Normalize and apply threshold
        if matched_keywords == 0:
            return 0.0
        
        normalized_score = score / (len(keywords) * 2)  # Max possible score
        
        # Require at least 30% keyword match
        return normalized_score if matched_keywords >= len(keywords) * 0.3 else normalized_score * 0.5
    
    def _check_required_patterns(self, func_text: str, func_node: Any, required_patterns: List[str]) -> float:
        """Check for required algorithmic patterns."""
        if not required_patterns:
            return 0.0
        
        pattern_checks = {
            # Sorting patterns
            'pivot_selection': lambda: 'pivot' in func_text and ('//2' in func_text or '/2' in func_text),
            'partition_logic': lambda: 'partition' in func_text or (re.search(r'[<>]=?.*pivot', func_text) is not None),
            'nested_loops': lambda: self._has_nested_loops(func_node),
            'adjacent_comparison': lambda: (re.search(r'\[\s*\w+\s*\].*\[\s*\w+\s*\+\s*1\s*\]', func_text) is not None or
                                           re.search(r'arr\[j\].*arr\[j\s*\+\s*1\]', func_text) is not None),
            'swap_operation': lambda: (re.search(r'=.*,.*=|swap|temp.*=', func_text) is not None or
                                     re.search(r'.*,.*=.*,.*', func_text) is not None),  # Python tuple swap
            'merge_function': lambda: 'merge' in func_text and ('left' in func_text or 'right' in func_text),
            'divide_conquer': lambda: '//2' in func_text or '/2' in func_text,
            'heapify_operation': lambda: 'heapify' in func_text or ('largest' in func_text and 'parent' in func_text),
            'parent_child_comparison': lambda: re.search(r'2\s*\*\s*\w+|left.*right', func_text) is not None,
            
            # Search patterns - more restrictive
            'mid_calculation': lambda: re.search(r'(mid|middle)\s*=.*[+/].*2', func_text) is not None,
            'binary_division': lambda: 'left' in func_text and 'right' in func_text and 'mid' in func_text,
            'comparison_with_target': lambda: 'target' in func_text or 'key' in func_text or 'search' in func_text,
            'range_adjustment': lambda: re.search(r'(left|right)\s*=\s*(mid|middle)', func_text) is not None,
            'single_loop': lambda: self._count_loops(func_node) == 1,
            'return_on_match': lambda: re.search(r'if.*return', func_text) is not None,
            'element_comparison': lambda: re.search(r'==|!=', func_text) is not None,
            
            # Math patterns
            'n_minus_1': lambda: re.search(r'\b(n|num)\s*[-]\s*1\b', func_text) is not None or 
                                ('fibonacci' in func_text.lower() and ('- 1' in func_text or '-1' in func_text)),
            'n_minus_2': lambda: re.search(r'\b(n|num)\s*[-]\s*2\b', func_text) is not None or
                                ('fibonacci' in func_text.lower() and ('- 2' in func_text or '-2' in func_text)),
            'n_multiplication': lambda: '*' in func_text and ('n' in func_text or 'num' in func_text),
            'modulo_operation': lambda: '%' in func_text or 'mod' in func_text,
            'decremental_loop_or_recursion': lambda: self._has_decrement_pattern(func_text),
            'addition': lambda: '+' in func_text,
            'multiplication': lambda: '*' in func_text,
            'division': lambda: '/' in func_text or '//' in func_text,
            'divisibility_check': lambda: re.search(r'%.*==\s*0', func_text) is not None,
            'swap_or_recursion': lambda: 'swap' in func_text or self._has_recursive_pattern(func_text, func_node),
            'gcd_call_or_impl': lambda: 'gcd' in func_text or ('while' in func_text and '%' in func_text),
            'multiplication_loop': lambda: self._has_loops(func_node) and '*' in func_text,
            'base_exponent': lambda: 'base' in func_text or 'exp' in func_text or 'power' in func_text,
            'while_with_modulo': lambda: 'while' in func_text and '%' in func_text,
            'exponent_check': lambda: re.search(r'exponent\s*[=<>!]+\s*\d+', func_text) is not None,
            'recursive_multiplication': lambda: self._has_recursive_pattern(func_text, func_node) and '*' in func_text,
            
            # General patterns
            'recursive_calls': lambda: self._has_recursive_pattern(func_text, func_node),
            'iteration': lambda: self._has_loops(func_node),
            'comparison': lambda: re.search(r'[<>=!]=?', func_text) is not None,
            
            # Polyfill patterns
            'native_check': lambda: '||' in func_text and ('Object.' in func_text or 'Array.' in func_text),
            'fallback_loop': lambda: 'for' in func_text and ('function' in func_text or '=>' in func_text),
            'helper_pattern': lambda: func_text.startswith('__') or 'prototype' in func_text,
            'prototype_chain': lambda: 'prototype' in func_text,
            
            # Object manipulation patterns  
            'property_iteration': lambda: 'for' in func_text and ' in ' in func_text,
            'property_copy': lambda: re.search(r'\[\w+\]\s*=\s*\w+\[\w+\]', func_text) is not None,
            'hasOwnProperty_check': lambda: 'hasownproperty' in func_text,
            'hasOwnProperty': lambda: 'hasownproperty' in func_text,  # Alias for pattern matching
            'property_enumeration': lambda: 'getownpropertysymbols' in func_text or 'propertyisenumerable' in func_text,
            'symbol_handling': lambda: 'symbol' in func_text,
            
            # Array manipulation patterns
            'array_indexing': lambda: re.search(r'\[\s*\w+\s*\]', func_text) is not None,
            'length_accumulation': lambda: re.search(r'\w+\s*\+=.*\.length', func_text) is not None,
            'element_copy': lambda: re.search(r'\[\w+\]\s*=\s*\w+\[\w+\]', func_text) is not None,
            
            # Cryptographic patterns
            'modular_exponentiation': lambda: (('pow' in func_text or '**' in func_text) and '%' in func_text) or re.search(r'modpow|mod_pow|modular.*pow|pow\s*\([^,]+,[^,]+,[^)]+\)', func_text) is not None,
            'prime_generation_or_check': lambda: re.search(r'prime|is_prime|primality|miller_rabin|fermat', func_text) is not None,
            'key_generation': lambda: re.search(r'key|public|private|generate.*key|key.*gen', func_text) is not None,
            'substitution_table': lambda: re.search(r'sbox|s_box|substitution|lookup\s*\[|table\s*\[', func_text) is not None,
            'matrix_operations': lambda: re.search(r'matrix|row|column|state\[\d+\]\[\d+\]', func_text) is not None,
            'xor_operations': lambda: '^' in func_text or 'xor' in func_text,
            'bit_rotation': lambda: re.search(r'<<|>>|rotate|rot[lr]|circular.*shift', func_text) is not None,
            'constant_array': lambda: re.search(r'const.*\[.*\]|K\s*=\s*\[|constants?\s*=', func_text) is not None,
            'four_rounds': lambda: re.search(r'round|rounds|for.*4|range.*4', func_text) is not None,
            'key_padding': lambda: re.search(r'pad|padding|\\x36|\\x5c|ipad|opad', func_text) is not None,
            'inner_hash': lambda: re.search(r'inner|i_key_pad|ipad', func_text) is not None,
            'outer_hash': lambda: re.search(r'outer|o_key_pad|opad', func_text) is not None,
            'generator': lambda: re.search(r'generator|g\s*=\s*\d+|base.*point', func_text) is not None,
            'point_operations': lambda: re.search(r'point.*add|scalar.*mult|double.*point|ec_add|ecc', func_text) is not None,
            'modular_arithmetic': lambda: '%' in func_text and ('+' in func_text or '*' in func_text),
            'curve_equation': lambda: re.search(r'curve|elliptic|y\^2|x\^3|weierstrass', func_text) is not None,
            'quarter_round': lambda: re.search(r'quarter.*round|qr|rotl|rotr', func_text) is not None,
            'salt_generation': lambda: re.search(r'salt|random.*bytes|urandom|generate.*salt', func_text) is not None,
            'key_expansion': lambda: re.search(r'expand.*key|key.*schedule|round.*key', func_text) is not None,
            'blowfish_operations': lambda: re.search(r'blowfish|feistel|f_function', func_text) is not None,
            'hmac_iterations': lambda: re.search(r'iteration|rounds|pbkdf|kdf', func_text) is not None,
            'salt_usage': lambda: 'salt' in func_text,
            'xor_accumulation': lambda: re.search(r'\^=|xor.*=', func_text) is not None,
            'key_usage': lambda: 'key' in func_text,
            'data_transformation': lambda: re.search(r'transform|encrypt|decrypt|encode|decode', func_text) is not None,
            
            # Iterator patterns
            'iterator_interface': lambda: 'next' in func_text and 'done' in func_text,
            'state_tracking': lambda: 'state' in func_text or 'index' in func_text or 'i++' in func_text,
            
            # Audio processing patterns
            'audio_processing': lambda: (
                # Must have explicit audio-related terms
                re.search(r'audio|sound|pcm|sample_rate|audio_frame|audio_channel', func_text) is not None or
                # OR have codec-specific patterns with additional context
                (re.search(r'mp3|aac|opus|flac', func_text) is not None and 
                 re.search(r'bitrate|sample|frequency|channel|frame_size', func_text) is not None)
            ),
            'transform_operation': lambda: re.search(r'mdct|fft|dct|transform|fourier', func_text) is not None,
            'spectral_processing': lambda: re.search(r'spectral|spectrum|frequency|coefficient', func_text) is not None,
            'frame_processing': lambda: re.search(r'frame|window|overlap|segment', func_text) is not None,
            'prediction_operation': lambda: re.search(r'predict|lpc|linear.*prediction|residual', func_text) is not None,
            
            # Video processing patterns
            'video_processing': lambda: re.search(r'video|frame|pixel|yuv|rgb|h264|h265|vp[89]|av1|hevc|avc', func_text) is not None,
            'block_processing': lambda: re.search(r'block|macroblock|superblock|partition|tile', func_text) is not None,
            'tree_structure': lambda: re.search(r'tree|split|quadtree|coding.*tree|ctu', func_text) is not None,
            'filtering_operation': lambda: re.search(r'filter|deblock|smooth|blur|sharpen', func_text) is not None,
            'promise_handling': lambda: 'promise' in func_text or 'then' in func_text,
            'state_machine': lambda: 'switch' in func_text or 'case' in func_text
        }
        
        matched = 0
        for pattern in required_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        # Require at least 60% of required patterns
        return (matched / len(required_patterns)) if matched >= len(required_patterns) * 0.6 else 0.0
    
    def _check_ast_patterns(self, func_node: Any, ast_patterns: List[str]) -> float:
        """Check AST-based patterns."""
        if not ast_patterns or not func_node:
            return 0.0
        
        pattern_checks = {
            'recursive_function': lambda: self._has_function_calls(func_node),
            'double_for_loop': lambda: self._has_nested_loops(func_node),
            'while_loop_or_recursion': lambda: self._has_while_loop(func_node) or self._has_function_calls(func_node),
            'for_loop': lambda: self._has_for_loop(func_node),
            'loop': lambda: self._has_loops(func_node),
            'comparison': lambda: self._has_comparisons(func_node),
            'assignment': lambda: self._has_assignments(func_node),
            'arithmetic_operation': lambda: self._has_arithmetic(func_node),
            
            # Sorting specific patterns
            'array_manipulation': lambda: self._has_array_operations(func_node),
            'array_split': lambda: self._has_array_operations(func_node),
            
            # Search specific patterns
            'if_statement': lambda: self._has_conditionals(func_node),
            'return_statement': lambda: True,  # Most functions have returns
            
            # Math specific patterns
            'multiplication': lambda: self._has_specific_operator(func_node, '*'),
            'decrement': lambda: True,  # Handled in text patterns
            'modulo': lambda: self._has_specific_operator(func_node, '%'),
            'division': lambda: self._has_specific_operator(func_node, '/'),
            'loop_or_recursion': lambda: self._has_loops(func_node) or self._has_function_calls(func_node),
            'while_loop': lambda: self._has_while_loop(func_node),
            
            # Additional patterns for our new algorithm types
            'or_operator': lambda: self._has_binary_operator(func_node, '||'),
            'for_in_loop': lambda: self._has_for_in_loop(func_node),
            'property_assignment': lambda: self._has_property_assignment(func_node),
            'function_assignment': lambda: self._has_function_assignment(func_node),
            'prototype_access': lambda: self._has_prototype_access(func_node),
            'object_return': lambda: self._has_object_return(func_node),
            'method_definition': lambda: self._has_method_definition(func_node),
            'switch_statement': lambda: self._has_switch_statement(func_node),
            'promise_call': lambda: self._has_promise_call(func_node),
            'array_assignment': lambda: self._has_array_assignment(func_node),
            'array_access': lambda: self._has_array_access(func_node),
            
            # Cryptographic AST patterns
            'bitwise_operations': lambda: self._has_bitwise_operations(func_node),
            'modulo_operation': lambda: self._has_specific_operator(func_node, '%'),
            'exponentiation': lambda: self._has_exponentiation(func_node),
            'prime_check': lambda: True,  # Text-based check is sufficient
            'array_lookup': lambda: self._has_array_access(func_node),
            'array_constants': lambda: self._has_array_literals(func_node),
            'hash_function_call': lambda: self._has_function_calls(func_node),
            'concatenation': lambda: self._has_string_concatenation(func_node),
            'coordinate_operations': lambda: self._has_multiple_assignments(func_node),
            'substitution': lambda: self._has_array_access(func_node),
            'hmac_call': lambda: self._has_function_calls(func_node)
        }
        
        matched = 0
        for pattern in ast_patterns:
            if pattern in pattern_checks:
                try:
                    if pattern_checks[pattern]():
                        matched += 1
                except:
                    pass
        
        return matched / len(ast_patterns) if ast_patterns else 0.0
    
    def _has_nested_loops(self, node: Any, depth: int = 0) -> bool:
        """Check if node contains nested loops."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            # Check if any child is also a loop
            for child in getattr(node, 'children', []):
                if self._has_loops_at_depth(child, depth + 1):
                    return True
        
        for child in getattr(node, 'children', []):
            if self._has_nested_loops(child, depth):
                return True
        
        return False
    
    def _has_loops_at_depth(self, node: Any, target_depth: int, current_depth: int = 0) -> bool:
        """Check if there are loops at a specific depth."""
        if not node:
            return False
            
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            if current_depth >= target_depth:
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_loops_at_depth(child, target_depth, current_depth):
                return True
        
        return False
    
    def _count_loops(self, node: Any) -> int:
        """Count total number of loops."""
        if not node:
            return 0
            
        count = 0
        loop_types = {'for_statement', 'while_statement', 'do_statement'}
        
        if hasattr(node, 'type') and node.type in loop_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_loops(child)
        
        return count
    
    def _has_recursive_pattern(self, func_text: str, func_node: Any) -> bool:
        """Check for recursive patterns."""
        # Simple heuristic: function calls itself or has multiple function calls
        func_calls = self._count_function_calls(func_node)
        
        # Look for self-referential patterns
        if re.search(r'(\w+)\s*\([^)]*\1[^)]*\)', func_text):
            return True
        
        # Multiple function calls might indicate recursion
        return func_calls >= 2
    
    def _has_decrement_pattern(self, func_text: str) -> bool:
        """Check if function has decrement pattern (i--, i-=1, i = i - 1, etc)."""
        decrement_patterns = [
            r'\w+\s*-=\s*1',       # i -= 1
            r'\w+\s*=\s*\w+\s*-\s*1',  # i = i - 1
            r'\w+--',              # i--
            r'--\w+',              # --i
            r'range\s*\([^,)]+,\s*0',  # range(n, 0, -1) in Python
            r'for.*-1.*:',         # for loops with -1
        ]
        for pattern in decrement_patterns:
            if re.search(pattern, func_text):
                return True
        return False
    
    def _has_loops(self, node: Any) -> bool:
        """Check if node contains any loops."""
        return self._count_loops(node) > 0
    
    def _has_while_loop(self, node: Any) -> bool:
        """Check for while loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'while_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_while_loop(child):
                return True
        
        return False
    
    def _has_for_loop(self, node: Any) -> bool:
        """Check for for loops."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'for_statement':
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_for_loop(child):
                return True
        
        return False
    
    def _has_function_calls(self, node: Any) -> bool:
        """Check if node contains function calls."""
        return self._count_function_calls(node) > 0
    
    def _count_function_calls(self, node: Any) -> int:
        """Count function calls."""
        if not node:
            return 0
            
        count = 0
        call_types = {'call', 'call_expression', 'function_call'}
        
        if hasattr(node, 'type') and node.type in call_types:
            count += 1
        
        for child in getattr(node, 'children', []):
            count += self._count_function_calls(child)
        
        return count
    
    def _has_comparisons(self, node: Any) -> bool:
        """Check for comparison operations."""
        if not node:
            return False
            
        comparison_types = {'comparison', 'binary_operator', 'comparison_operator'}
        
        if hasattr(node, 'type') and node.type in comparison_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_comparisons(child):
                return True
        
        return False
    
    def _has_assignments(self, node: Any) -> bool:
        """Check for assignment operations."""
        if not node:
            return False
            
        assignment_types = {'assignment', 'assignment_expression', '='}
        
        if hasattr(node, 'type') and node.type in assignment_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_assignments(child):
                return True
        
        return False
    
    def _has_arithmetic(self, node: Any) -> bool:
        """Check for arithmetic operations."""
        if not node:
            return False
            
        arithmetic_types = {'binary_operator', 'arithmetic_operation', '+', '-', '*', '/', '%'}
        
        if hasattr(node, 'type') and node.type in arithmetic_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_arithmetic(child):
                return True
        
        return False
    
    def _has_array_operations(self, node: Any) -> bool:
        """Check for array operations like indexing, slicing."""
        if not node:
            return False
            
        array_types = {'subscript', 'array_access', 'index_expression', 'slice'}
        
        if hasattr(node, 'type') and node.type in array_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_array_operations(child):
                return True
        
        return False
    
    def _has_specific_operator(self, node: Any, operator: str) -> bool:
        """Check for specific operator in AST."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'binary_operator':
            if hasattr(node, 'operator') and node.operator == operator:
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_specific_operator(child, operator):
                return True
        
        return False
    
    def _has_bitwise_operations(self, node: Any) -> bool:
        """Check for bitwise operations in AST."""
        if not node:
            return False
            
        bitwise_types = {'binary_operator', 'bitwise_operation', 'shift_operation'}
        bitwise_ops = {'&', '|', '^', '<<', '>>', '~'}
        
        if hasattr(node, 'type') and node.type in bitwise_types:
            return True
            
        if hasattr(node, 'operator') and str(node.operator) in bitwise_ops:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_bitwise_operations(child):
                return True
        
        return False
    
    def _has_exponentiation(self, node: Any) -> bool:
        """Check for exponentiation operations."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type in {'power', 'exponentiation', 'binary_operator'}:
            if hasattr(node, 'operator') and str(node.operator) in {'**', 'pow'}:
                return True
                
        if hasattr(node, 'type') and node.type == 'call':
            # Check for pow() function calls
            for child in getattr(node, 'children', []):
                if hasattr(child, 'type') and child.type == 'identifier':
                    if hasattr(child, 'text') and 'pow' in str(child.text):
                        return True
        
        for child in getattr(node, 'children', []):
            if self._has_exponentiation(child):
                return True
        
        return False
    
    def _has_array_literals(self, node: Any) -> bool:
        """Check for array literal definitions."""
        if not node:
            return False
            
        array_types = {'array', 'list', 'array_literal', 'list_literal', 'array_expression'}
        
        if hasattr(node, 'type') and node.type in array_types:
            return True
        
        for child in getattr(node, 'children', []):
            if self._has_array_literals(child):
                return True
        
        return False
    
    def _has_string_concatenation(self, node: Any) -> bool:
        """Check for string concatenation operations."""
        if not node:
            return False
            
        if hasattr(node, 'type') and node.type == 'binary_operator':
            if hasattr(node, 'operator') and str(node.operator) == '+':
                # Check if operands are strings
                return True
        
        for child in getattr(node, 'children', []):
            if self._has_string_concatenation(child):
                return True
        
        return False
    
    def _has_multiple_assignments(self, node: Any) -> bool:
        """Check for multiple assignment statements."""
        if not node:
            return False
            
        assignment_count = 0
        assignment_types = {'assignment', 'assignment_expression', 'augmented_assignment'}
        
        if hasattr(node, 'type') and node.type in assignment_types:
            assignment_count += 1
        
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and child.type in assignment_types:
                assignment_count += 1
        
        return assignment_count >= 2
    
    def _extract_functions_from_ast(self, ast_tree: Any) -> List[Dict[str, Any]]:
        """Extract functions from AST tree."""
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        self._find_functions_recursive(ast_tree.root, functions, ast_tree.code)
        return functions
    
    def _find_functions_recursive(self, node: Any, functions: List[Dict], code: str):
        """Recursively find function definitions in AST."""
        if not node:
            return
            
        function_types = {
            'function_definition',  # Python
            'function_declaration', # JavaScript, C, Java
            'method_definition',    # Java, JavaScript classes
            'arrow_function',       # JavaScript
            'function_item',        # Rust
            'func_declaration',     # Go
            'function',            # JavaScript function expressions
            'function_expression', # JavaScript/TypeScript
        }
        
        if hasattr(node, 'type') and node.type in function_types:
            func_info = {
                'node': node,
                'type': node.type,
                'start_byte': node.start_byte,
                'end_byte': node.end_byte,
                'text': code[node.start_byte:node.end_byte],
                'name': self._extract_function_name(node, code),
                'lines': self._calculate_lines(node, code)
            }
            functions.append(func_info)
        
        # Also check for assignment patterns like: __assign = function() {...}
        elif hasattr(node, 'type') and node.type in {'assignment', 'assignment_expression', 'variable_declarator'}:
            # Check if any descendant is a function
            var_name = self._extract_assignment_name(node, code)
            self._find_functions_in_descendants(node, functions, code, var_name)
        
        # Recursively search children
        for child in getattr(node, 'children', []):
            self._find_functions_recursive(child, functions, code)
    
    def _extract_function_name(self, func_node: Any, code: str) -> str:
        """Extract function name from function node."""
        try:
            # Different languages have different AST structures
            for child in getattr(func_node, 'children', []):
                if hasattr(child, 'type'):
                    # Python: function name is often direct child with type 'identifier'
                    if child.type in {'identifier', 'function_name', 'name'}:
                        name = code[child.start_byte:child.end_byte].strip()
                        if name and not name.startswith('(') and not name.startswith('def'):
                            return name
                    # Some languages nest the name deeper
                    elif child.type in {'function_declarator', 'function_signature'}:
                        for subchild in getattr(child, 'children', []):
                            if hasattr(subchild, 'type') and subchild.type in {'identifier', 'function_name'}:
                                name = code[subchild.start_byte:subchild.end_byte].strip()
                                if name and not name.startswith('('):
                                    return name
        except (IndexError, AttributeError):
            pass
        return 'anonymous'
    
    def _extract_assignment_name(self, assignment_node: Any, code: str) -> str:
        """Extract variable name from assignment node."""
        # Look for identifier on the left side of assignment
        for child in getattr(assignment_node, 'children', []):
            if hasattr(child, 'type') and child.type == 'identifier':
                return code[child.start_byte:child.end_byte]
        return None
    
    def _find_functions_in_descendants(self, node: Any, functions: List[Dict], code: str, var_name: str = None):
        """Find function nodes in descendants of a node."""
        function_types = {
            'function_definition', 'function_declaration', 'method_definition',
            'arrow_function', 'function_item', 'func_declaration',
            'function', 'function_expression'
        }
        
        # Check direct children
        for child in getattr(node, 'children', []):
            if hasattr(child, 'type') and child.type in function_types:
                func_info = {
                    'node': child,
                    'type': child.type,
                    'start_byte': child.start_byte,
                    'end_byte': child.end_byte,
                    'text': code[child.start_byte:child.end_byte],
                    'name': var_name or self._extract_function_name(child, code),
                    'lines': self._calculate_lines(child, code)
                }
                functions.append(func_info)
            else:
                # Recursively check descendants
                self._find_functions_in_descendants(child, functions, code, var_name)
    
    def _calculate_lines(self, node: Any, code: str) -> Dict[str, int]:
        """Calculate line information for a function."""
        start_line = code[:node.start_byte].count('\n') + 1
        end_line = code[:node.end_byte].count('\n') + 1
        return {
            "start": start_line,
            "end": end_line,
            "total": end_line - start_line + 1
        }
    
    def _create_specific_algorithm_entry(self, func: Dict[str, Any], algo_type: AlgorithmType, 
                                       subtype: str, confidence: float, 
                                       ast_tree: Any, language: str) -> Dict[str, Any]:
        """Create algorithm entry with specific subtype information."""
        # Generate unique ID
        algo_id = f"algo_{uuid.uuid4().hex[:8]}"
        
        # Calculate complexity
        complexity = self._calculate_cyclomatic_complexity(func['node'])
        
        # Generate normalized representation and hashes
        hashes = self._generate_algorithm_hashes(func['node'], func['text'], language)
        
        # Extract mathematical invariants
        invariants = self._extract_mathematical_invariants(func['node'])
        
        return {
            'id': algo_id,
            'type': 'algorithm',
            'name': f"{algo_type.value}_{subtype}_implementation",
            'algorithm_type': algo_type.value,
            'algorithm_subtype': subtype,
            'subtype_classification': subtype,  # Add this for compatibility
            'algorithm_category': self._get_algorithm_category(algo_type),
            'confidence': round(confidence, 3),
            'confidence_score': round(confidence, 3),  # Add this too
            'complexity_metric': complexity,
            'lines': func['lines'],
            'function_info': {  # Add function info
                'name': func['name'],
                'lines': func['lines'],
                'type': func['type']
            },
            'evidence': {
                'pattern_type': self._get_algorithm_category(algo_type),
                'algorithm_type': algo_type.value,
                'control_flow': 'complex' if complexity > 5 else 'linear',
                'ast_signature': hashlib.md5(str(func['node']).encode()).hexdigest()[:16],
                'cyclomatic_complexity': complexity,
                'matched_keywords': self._get_matched_keywords(func['text'], func['name'], algo_type, subtype),
                'pattern_confidence': confidence,
                'matched_subtype': subtype,
                'is_generic': subtype.endswith('_generic'),
                'specificity_score': confidence
            },
            'hashes': hashes,
            'transformation_resistance': self._calculate_transformation_resistance(),
            'ast_representation': {
                'normalized': func['node'].type if hasattr(func['node'], 'type') else 'unknown',
                'original': func['text'][:200] + '...' if len(func['text']) > 200 else func['text']
            },
            'control_flow_graph': f"branches:{complexity-1}_loops:{self._count_loops(func['node'])}_calls:{self._count_function_calls(func['node'])}",
            'mathematical_invariants': invariants
        }
    
    def _calculate_cyclomatic_complexity(self, node: Any) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        decision_types = {
            'if_statement', 'while_statement', 'for_statement',
            'case_statement', 'conditional_expression'
        }
        
        def count_decisions(n):
            count = 0
            if hasattr(n, 'type') and n.type in decision_types:
                count += 1
            for child in getattr(n, 'children', []):
                count += count_decisions(child)
            return count
        
        return complexity + count_decisions(node)
    
    def _generate_algorithm_hashes(self, func_node: Any, func_text: str, language: str) -> Dict[str, Any]:
        """Generate hashes for the algorithm."""
        # Generate normalized representation
        normalized_repr = self.normalizer.normalize_function(func_node, func_text, language)
        
        return {
            "direct": self.direct_hasher.hash_text(normalized_repr),
            "fuzzy": {
                "tlsh": self.fuzzy_hasher.hash_text(normalized_repr),
                "tlsh_threshold": self.config.tlsh_threshold if self.config else 100
            },
            "semantic": {
                "minhash": self.semantic_hasher.generate_minhash(normalized_repr),
                "lsh_bands": self.config.lsh_bands if self.config else 20,
                "simhash": self.semantic_hasher.generate_simhash(normalized_repr)
            },
            "normalized_representation": normalized_repr[:200] + "..." if len(normalized_repr) > 200 else normalized_repr,
            "ast_features": self._extract_ast_features(func_node)
        }
    
    def _extract_mathematical_invariants(self, node: Any) -> List[Dict[str, Any]]:
        """Extract mathematical invariants."""
        # Simplified extraction
        return []
    
    def _calculate_transformation_resistance(self) -> Dict[str, float]:
        """Calculate transformation resistance scores."""
        return {
            'variable_renaming': 0.91,
            'language_translation': 0.71,
            'style_changes': 0.81,
            'framework_adaptation': 0.61
        }
    
    def _extract_ast_features(self, func_node: Any) -> Dict[str, Any]:
        """Extract AST features."""
        return {
            "node_types": [func_node.type] if hasattr(func_node, 'type') else [],
            "depth": 1,
            "branching_factor": 1,
            "leaf_count": 1,
            "control_structures": 0,
            "avg_branching": 0.5,
            "control_density": 0.0
        }
    
    def _get_algorithm_category(self, algo_type: AlgorithmType) -> str:
        """Get algorithm category."""
        category_mapping = {
            AlgorithmType.SORTING_ALGORITHM: "core_algorithms",
            AlgorithmType.SEARCH_ALGORITHM: "core_algorithms",
            AlgorithmType.NUMERICAL_ALGORITHM: "mathematical_algorithms",
            AlgorithmType.COMPRESSION_ALGORITHM: "data_processing",
            AlgorithmType.DYNAMIC_PROGRAMMING: "optimization",
            AlgorithmType.OBJECT_MANIPULATION: "data_structures",
            AlgorithmType.ARRAY_MANIPULATION: "data_structures",
            AlgorithmType.ITERATOR_PATTERN: "design_patterns",
            AlgorithmType.POLYFILL_PATTERN: "runtime_helpers"
        }
        return category_mapping.get(algo_type, "unknown")
    
    def _get_matched_keywords(self, func_text: str, func_name: str, algo_type: AlgorithmType, subtype: str) -> List[str]:
        """Get matched keywords."""
        # Get pattern for this subtype
        type_config = self.patterns.get(algo_type, {})
        subtype_pattern = type_config.get('subtypes', {}).get(subtype, {})
        keywords = subtype_pattern.get('keywords', [])
        
        matched = []
        func_text_lower = func_text.lower()
        func_name_lower = func_name.lower()
        
        for keyword in keywords:
            if keyword in func_name_lower or keyword in func_text_lower:
                matched.append(keyword)
        
        return matched
    
    # Additional helper methods for new patterns
    def _has_binary_operator(self, node: Any, operator: str) -> bool:
        """Check if node contains specific binary operator."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'binary_expression':
            for child in getattr(node, 'children', []):
                if hasattr(child, 'type') and child.type == operator:
                    return True
        for child in getattr(node, 'children', []):
            if self._has_binary_operator(child, operator):
                return True
        return False
    
    def _has_for_in_loop(self, node: Any) -> bool:
        """Check if node contains for-in loop."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'for_in_statement', 'for_of_statement'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_for_in_loop(child):
                return True
        return False
    
    def _has_property_assignment(self, node: Any) -> bool:
        """Check if node contains property assignment."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'member_expression', 'subscript_expression'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_property_assignment(child):
                return True
        return False
    
    def _has_function_assignment(self, node: Any) -> bool:
        """Check if node contains function assignment."""
        return self._has_assignments(node) and self._has_function_expressions(node)
    
    def _has_function_expressions(self, node: Any) -> bool:
        """Check if node contains function expressions."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type in {'function_expression', 'arrow_function'}:
            return True
        for child in getattr(node, 'children', []):
            if self._has_function_expressions(child):
                return True
        return False
    
    def _has_prototype_access(self, node: Any) -> bool:
        """Check if node accesses prototype."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'member_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_prototype_access(child):
                return True
        return False
    
    def _has_object_return(self, node: Any) -> bool:
        """Check if function returns an object."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'return_statement':
            return True
        for child in getattr(node, 'children', []):
            if self._has_object_return(child):
                return True
        return False
    
    def _has_method_definition(self, node: Any) -> bool:
        """Check if node contains method definitions."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'method_definition':
            return True
        for child in getattr(node, 'children', []):
            if self._has_method_definition(child):
                return True
        return False
    
    def _has_switch_statement(self, node: Any) -> bool:
        """Check if node contains switch statement."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'switch_statement':
            return True
        for child in getattr(node, 'children', []):
            if self._has_switch_statement(child):
                return True
        return False
    
    def _has_promise_call(self, node: Any) -> bool:
        """Check if node contains Promise calls."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'call_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_promise_call(child):
                return True
        return False
    
    def _has_array_assignment(self, node: Any) -> bool:
        """Check if node contains array element assignment."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'subscript_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_array_assignment(child):
                return True
        return False
    
    def _has_array_access(self, node: Any) -> bool:
        """Check if node contains array access."""
        if not node:
            return False
        if hasattr(node, 'type') and node.type == 'subscript_expression':
            return True
        for child in getattr(node, 'children', []):
            if self._has_array_access(child):
                return True
        return False