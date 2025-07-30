"""
Enhanced algorithm detection with better subtype classification.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from .algorithm_types import AlgorithmType


class EnhancedAlgorithmDetector:
    """Enhanced algorithm detector with reduced generic classifications."""
    
    def __init__(self, config=None):
        # Initialize detection patterns with specificity scores
        self.detection_patterns = self._initialize_detection_patterns()
        self.config = config
        
        # Context patterns for better classification
        self.context_patterns = {
            'sorting_context': ['sort', 'order', 'arrange', 'compare', 'swap'],
            'search_context': ['find', 'search', 'locate', 'lookup', 'query'],
            'graph_context': ['node', 'edge', 'vertex', 'graph', 'path', 'tree'],
            'crypto_context': ['encrypt', 'decrypt', 'hash', 'key', 'cipher', 'secure', 
                             'cryptographic', 'primality', 'miller', 'rabin', 'elliptic', 
                             'curve', 'modular', 'exponentiation', 'witness'],
            'math_context': ['calculate', 'compute', 'solve', 'equation', 'formula'],
            'audio_context': ['audio', 'pcm', 'codec', 'sample', 'encode', 'decode', 
                            'channels', 'bitrate', 'format', 'frame', 'buffer', 'sound', 
                            'frequency', 'amplitude', 'waveform', 'spectrum'],
            'video_context': ['video', 'frame', 'pixel', 'yuv', 'rgb', 'motion', 
                            'macroblock', 'slice', 'gop', 'bitstream', 'resolution',
                            'chroma', 'luma', 'intra', 'inter', 'prediction']
        }
    
    def detect_algorithm_type(self, func_text: str, func_name: str, 
                            ast_node: Any = None, language: str = None) -> Tuple[AlgorithmType, str, float]:
        """Detect algorithm type with enhanced subtype classification."""
        
        # Normalize text for analysis
        normalized_text = func_text.lower()
        normalized_name = func_name.lower()
        
        # Extract features for classification
        features = self._extract_features(normalized_text, normalized_name, ast_node)
        
        # Score each algorithm type and subtype
        scores = defaultdict(lambda: defaultdict(float))
        
        for algo_type, patterns in self.detection_patterns.items():
            for subtype, pattern_data in patterns.items():
                score = self._calculate_pattern_score(features, pattern_data)
                if score > 0:
                    scores[algo_type][subtype] = score
        
        # Apply context boosting
        context_boosts = self._calculate_context_boosts(features)
        for context_type, boost in context_boosts.items():
            if context_type in scores:
                for subtype in scores[context_type]:
                    scores[context_type][subtype] *= (1 + boost)
        
        # Find best match
        best_type = None
        best_subtype = "unknown"
        best_score = 0.0
        
        for algo_type, subtypes in scores.items():
            for subtype, score in subtypes.items():
                if score > best_score:
                    best_score = score
                    best_type = algo_type
                    best_subtype = subtype
        
        # Avoid generic classification if specific pattern found
        if best_subtype.endswith('_generic') and best_score < 0.7:
            # Try to find more specific subtype
            specific_subtype = self._find_specific_subtype(features, best_type)
            if specific_subtype:
                best_subtype = specific_subtype
                best_score *= 1.2  # Boost confidence for specific match
        
        # Special check for quicksort based on name and patterns
        if ('quicksort' in normalized_name or 'qsort' in normalized_name or 
            ('partition' in normalized_name and 'pivot' in features['patterns'])):
            # Override if we have strong quicksort indicators
            if features['operations']['function_call'] >= 1:
                best_type = AlgorithmType.SORTING_ALGORITHM
                best_subtype = 'quicksort'
                best_score = max(best_score, 0.8)
        
        # Codec-specific prioritization - prefer specific codecs over generic PCM
        if best_type in [AlgorithmType.AUDIO_CODEC, AlgorithmType.VIDEO_CODEC]:
            # Check for codec names in function/text
            codec_hints = {
                'mp3': 'mp3_codec',
                'aac': 'aac_codec', 
                'opus': 'opus',
                'flac': 'flac',
                'vorbis': 'vorbis',
                'h264': 'h264',
                'h265': 'h265',
                'hevc': 'h265',
                'vp8': 'vp8',
                'vp9': 'vp9',
                'av1': 'av1'
            }
            
            for hint, codec_type in codec_hints.items():
                if hint in normalized_name or hint in normalized_text[:200]:  # Check name and beginning of text
                    if codec_type in scores.get(best_type, {}):
                        # Boost this codec's score
                        hint_score = scores[best_type][codec_type]
                        if hint_score > best_score * 0.5:  # If it has reasonable score
                            best_subtype = codec_type
                            best_score = max(hint_score * 1.2, best_score)
                            break
            
            # If still PCM, check for more specific match
            if best_subtype == 'pcm_codec':
                # Check if we have a more specific codec match
                for subtype, score in scores.get(best_type, {}).items():
                    if subtype != 'pcm_codec' and score > best_score * 0.7:  # Within 30% of PCM score
                        # Prefer the more specific codec
                        best_subtype = subtype
                        best_score = score * 1.1  # Slight boost for being specific
                        break
        
        # Final confidence adjustment
        confidence = min(best_score, 1.0)
        
        # If no algorithm type detected, return None with special handling
        if best_type is None:
            return None, "unknown", 0.0
        
        return best_type, best_subtype, confidence
    
    def _extract_features(self, text: str, name: str, ast_node: Any = None) -> Dict[str, Any]:
        """Extract comprehensive features for classification."""
        features = {
            'text': text,
            'name': name,
            'keywords': set(),
            'operations': defaultdict(int),
            'patterns': set(),
            'complexity': {},
            'ast_features': set()
        }
        
        # Extract keywords
        keywords = re.findall(r'\b\w{3,}\b', text)
        features['keywords'] = set(keywords)
        
        # Extract operations
        operations = {
            'comparison': len(re.findall(r'[<>=!]=?', text)),
            'arithmetic': len(re.findall(r'[+\-*/]', text)),
            'assignment': len(re.findall(r'\w+\s*=\s*', text)),
            'array_access': len(re.findall(r'\[\s*\w+\s*\]', text)),
            'function_call': len(re.findall(r'\w+\s*\(', text)),
            'loop': len(re.findall(r'\b(for|while|do)\b', text)),
            'conditional': len(re.findall(r'\b(if|else|elif|switch|case)\b', text))
        }
        features['operations'] = operations
        
        # Extract specific patterns
        patterns = {
            # Sorting patterns
            'swap': bool(re.search(r'(\w+)\s*,\s*(\w+)\s*=\s*\2\s*,\s*\1|temp\s*=|swap', text)),
            'pivot': bool(re.search(r'pivot|partition', text)),
            'merge': bool(re.search(r'merge|combine', text)),
            'heap': bool(re.search(r'heap|heapify', text)),
            'bubble': bool(re.search(r'bubble|adjacent', text)),
            
            # Search patterns
            'binary_search': bool(re.search(r'(left|low|mid|right|high)\s*[+\-=]', text)),
            'linear_search': bool(re.search(r'for.*if.*return', text)),
            'hash_lookup': bool(re.search(r'hash|dict|map\[', text)),
            
            # Graph patterns
            'graph_traversal': bool(re.search(r'visit|visited|traverse', text)),
            'queue_based': bool(re.search(r'queue|enqueue|dequeue', text)),
            'stack_based': bool(re.search(r'stack|push|pop(?!\()', text)),
            'adjacency': bool(re.search(r'adjacen|neighbor|edge', text)),
            
            # Math patterns
            'recursion': bool(re.search(rf'\b{name}\s*\(', text)),
            'fibonacci': bool(re.search(r'fib|n-1.*n-2', text)),
            'factorial': bool(re.search(r'fact|n\s*\*.*n-1', text)),
            'modulo': bool(re.search(r'%|mod\b', text)),
            
            # Crypto patterns
            'bitwise': bool(re.search(r'[&|^~]|<<|>>', text)),
            'xor': bool(re.search(r'\^|xor', text)),
            'rounds': bool(re.search(r'round|iteration', text)),
            'key_operation': bool(re.search(r'key|encrypt|decrypt', text)),
            
            # Audio/Video patterns
            'audio_processing': bool(re.search(r'audio|pcm|sample|channel|codec|decode|encode|frame', text.lower())),
            'video_processing': bool(re.search(r'video|frame|pixel|yuv|rgb|h264|h265|vp[89]|av1', text.lower()))
        }
        features['patterns'] = {k for k, v in patterns.items() if v}
        
        # Calculate complexity metrics
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        features['complexity'] = {
            'lines': len(non_empty_lines),
            'cyclomatic': operations['conditional'] + operations['loop'] + 1,
            'nesting': self._calculate_nesting_depth(text)
        }
        
        # Extract AST features if available
        if ast_node:
            features['ast_features'] = self._extract_ast_features(ast_node)
        
        return features
    
    def _calculate_pattern_score(self, features: Dict, pattern_data: Dict) -> float:
        """Calculate score for a specific pattern."""
        score = 0.0
        
        # Keyword matching - require at least one keyword match
        if 'keywords' in pattern_data:
            keyword_matches = sum(1 for kw in pattern_data['keywords'] 
                                if kw in features['text'] or kw in features['name'])
            if keyword_matches == 0:
                return 0.0  # No keyword matches = no detection
            score += 0.3 * (keyword_matches / len(pattern_data['keywords']))
        
        # Required patterns - must have patterns if specified
        if 'required_patterns' in pattern_data and pattern_data['required_patterns']:
            pattern_matches = sum(1 for p in pattern_data['required_patterns'] 
                                if p in features['patterns'])
            if pattern_matches >= len(pattern_data['required_patterns']) * 0.7:
                score += 0.4
            else:
                return 0.0  # Required patterns not met
        
        # Operation requirements
        if 'required_operations' in pattern_data:
            op_score = 0
            for op, min_count in pattern_data['required_operations'].items():
                if features['operations'].get(op, 0) >= min_count:
                    op_score += 1
            if op_score > 0:
                score += 0.2 * (op_score / len(pattern_data['required_operations']))
        
        # Complexity requirements
        if 'complexity_range' in pattern_data:
            comp_range = pattern_data['complexity_range']
            if comp_range[0] <= features['complexity']['cyclomatic'] <= comp_range[1]:
                score += 0.1
        
        # Apply specificity bonus
        if pattern_data.get('specificity', 0) > 0:
            score *= (1 + pattern_data['specificity'] * 0.2)
        
        return score
    
    def _calculate_context_boosts(self, features: Dict) -> Dict[str, float]:
        """Calculate context-based boosts for algorithm types."""
        boosts = {}
        
        for context_type, context_words in self.context_patterns.items():
            context_score = sum(1 for word in context_words 
                              if word in features['text'] or word in features['name'])
            if context_score > 0:
                # Map context to algorithm type
                if context_type == 'sorting_context':
                    boosts[AlgorithmType.SORTING_ALGORITHM] = context_score * 0.1
                elif context_type == 'search_context':
                    boosts[AlgorithmType.SEARCH_ALGORITHM] = context_score * 0.1
                elif context_type == 'graph_context':
                    boosts[AlgorithmType.GRAPH_TRAVERSAL] = context_score * 0.15
                elif context_type == 'crypto_context':
                    boosts[AlgorithmType.CRYPTOGRAPHIC_ALGORITHM] = context_score * 0.3
                elif context_type == 'math_context':
                    boosts[AlgorithmType.NUMERICAL_ALGORITHM] = context_score * 0.1
                elif context_type == 'audio_context':
                    boosts[AlgorithmType.AUDIO_CODEC] = context_score * 0.25
                elif context_type == 'video_context':
                    boosts[AlgorithmType.VIDEO_CODEC] = context_score * 0.25
        
        return boosts
    
    def _find_specific_subtype(self, features: Dict, algo_type: AlgorithmType) -> Optional[str]:
        """Try to find a more specific subtype based on detailed analysis."""
        
        if algo_type == AlgorithmType.SEARCH_ALGORITHM:
            # Check for specific search patterns
            if 'binary_search' in features['patterns'] and features['operations']['comparison'] > 2:
                return 'binary_search'
            elif 'hash_lookup' in features['patterns']:
                return 'hash_search'
            elif features['operations']['loop'] > 0 and features['operations']['conditional'] > 0:
                return 'linear_search'
        
        elif algo_type == AlgorithmType.SORTING_ALGORITHM:
            # Check for specific sort patterns
            if 'pivot' in features['patterns']:
                return 'quicksort'
            elif 'merge' in features['patterns']:
                return 'merge_sort'
            elif 'heap' in features['patterns']:
                return 'heap_sort'
            elif 'bubble' in features['patterns'] or 'swap' in features['patterns']:
                return 'bubble_sort'
            elif features['operations']['comparison'] > 3:
                return 'selection_sort'
        
        elif algo_type == AlgorithmType.GRAPH_TRAVERSAL:
            # Check for specific graph algorithms
            if 'queue_based' in features['patterns']:
                return 'bfs'
            elif 'stack_based' in features['patterns'] or 'recursion' in features['patterns']:
                return 'dfs'
            elif 'adjacency' in features['patterns'] and 'distance' in features['text']:
                return 'dijkstra'
        
        elif algo_type == AlgorithmType.NUMERICAL_ALGORITHM:
            # Check for specific mathematical algorithms
            if 'fibonacci' in features['patterns']:
                return 'fibonacci'
            elif 'factorial' in features['patterns']:
                return 'factorial'
            elif 'modulo' in features['patterns'] and features['operations']['loop'] > 0:
                return 'gcd'
            elif 'prime' in features['text']:
                return 'prime_check'
        
        elif algo_type == AlgorithmType.CRYPTOGRAPHIC_ALGORITHM:
            # Check for specific crypto algorithms
            if 'rounds' in features['patterns'] and 'xor' in features['patterns']:
                return 'block_cipher'
            elif 'key_operation' in features['patterns'] and 'bitwise' in features['patterns']:
                return 'stream_cipher'
            elif 'hash' in features['text']:
                return 'hash_function'
            elif 'modulo' in features['patterns'] and 'power' in features['text']:
                return 'rsa'
        
        elif algo_type == AlgorithmType.AUDIO_CODEC:
            # Check for specific audio codec patterns
            text_lower = features['text'].lower()
            name_lower = features['name'].lower()
            
            # Check function name and content for codec identification
            if 'mp3' in text_lower or 'mp3' in name_lower or 'layer3' in text_lower or 'psychoacoustic' in text_lower:
                return 'mp3_codec'
            elif 'opus' in text_lower or 'opus' in name_lower or 'silk' in text_lower or 'celt' in text_lower:
                return 'opus'
            elif 'flac' in text_lower or 'flac' in name_lower or 'lpc' in text_lower or 'rice' in text_lower:
                return 'flac'
            elif 'aac' in text_lower or 'aac' in name_lower or 'advanced_audio' in text_lower:
                return 'aac_codec'
            elif 'vorbis' in text_lower or 'vorbis' in name_lower or 'ogg' in text_lower:
                return 'vorbis'
            elif 'alaw' in text_lower or 'ulaw' in text_lower or 'g711' in text_lower:
                return 'alaw_ulaw'
            elif 'wma' in text_lower or 'windows_media_audio' in text_lower:
                return 'wma'
            elif 'g722' in text_lower or 'g729' in text_lower:
                return 'g722' if 'g722' in text_lower else 'g729'
            elif 'ac3' in text_lower or 'dolby' in text_lower:
                return 'ac3'
            elif 'dts' in text_lower or 'dca' in text_lower:
                return 'dts'
            elif 'pcm' in text_lower or 'raw_audio' in text_lower:
                return 'pcm_codec'
                
        elif algo_type == AlgorithmType.VIDEO_CODEC:
            # Check for specific video codec patterns
            text_lower = features['text'].lower()
            if 'h264' in text_lower or 'avc' in text_lower:
                return 'h264'
            elif 'h265' in text_lower or 'hevc' in text_lower:
                return 'h265'
            elif 'h266' in text_lower or 'vvc' in text_lower:
                return 'h266'
            elif 'vp8' in text_lower:
                return 'vp8'
            elif 'vp9' in text_lower:
                return 'vp9'
            elif 'av1' in text_lower or 'aomedia' in text_lower:
                return 'av1'
            elif 'mpeg2' in text_lower or 'mpeg_2' in text_lower:
                return 'mpeg2'
            elif 'mpeg4' in text_lower or 'divx' in text_lower or 'xvid' in text_lower:
                return 'mpeg4'
            elif 'theora' in text_lower:
                return 'theora'
            elif 'wmv' in text_lower or 'vc1' in text_lower:
                return 'wmv'
            elif 'prores' in text_lower:
                return 'prores'
            elif 'motion_vector' in text_lower or 'motion_estimation' in text_lower:
                return 'motion_estimation'
            elif 'dct' in text_lower or 'discrete_cosine' in text_lower:
                return 'dct_transform'
        
        return None
    
    def _calculate_nesting_depth(self, text: str) -> int:
        """Calculate maximum nesting depth in code."""
        max_depth = 0
        current_depth = 0
        
        for char in text:
            if char in '{([':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in '})]':
                current_depth = max(0, current_depth - 1)
        
        # Also check indentation for Python
        lines = text.split('\n')
        indent_depth = 0
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_depth = max(indent_depth, indent // 4)
        
        return max(max_depth, indent_depth)
    
    def _extract_ast_features(self, ast_node: Any) -> set:
        """Extract features from AST node."""
        features = set()
        
        # This would be implemented based on actual AST structure
        # For now, return empty set
        return features
    
    def _initialize_detection_patterns(self) -> Dict[AlgorithmType, Dict[str, Dict]]:
        """Initialize comprehensive detection patterns."""
        patterns = {
            AlgorithmType.SORTING_ALGORITHM: {
                'quicksort': {
                    'keywords': ['quicksort', 'quick_sort', 'qsort', 'partition', 'pivot'],
                    'required_patterns': ['pivot'],  # Only require pivot, not swap
                    'required_operations': {'comparison': 1, 'function_call': 1},
                    'specificity': 0.9
                },
                'merge_sort': {
                    'keywords': ['mergesort', 'merge_sort', 'merge', 'divide'],
                    'required_patterns': ['merge'],
                    'required_operations': {'function_call': 2, 'array_access': 3},
                    'specificity': 0.85
                },
                'heap_sort': {
                    'keywords': ['heapsort', 'heap_sort', 'heapify', 'heap'],
                    'required_patterns': ['heap'],
                    'required_operations': {'comparison': 3, 'swap': 2},
                    'specificity': 0.85
                },
                'bubble_sort': {
                    'keywords': ['bubblesort', 'bubble_sort', 'bubble'],
                    'required_patterns': ['swap', 'bubble'],
                    'required_operations': {'loop': 2, 'comparison': 2},
                    'specificity': 0.8
                },
                'selection_sort': {
                    'keywords': ['selectionsort', 'selection_sort', 'select', 'minimum'],
                    'required_operations': {'loop': 2, 'comparison': 3},
                    'specificity': 0.75
                },
                'insertion_sort': {
                    'keywords': ['insertionsort', 'insertion_sort', 'insert'],
                    'required_operations': {'loop': 2, 'comparison': 1, 'assignment': 2},
                    'specificity': 0.75
                }
            },
            
            AlgorithmType.SEARCH_ALGORITHM: {
                'binary_search': {
                    'keywords': ['binary', 'bsearch', 'bisect'],
                    'required_patterns': ['binary_search'],
                    'required_operations': {'comparison': 2, 'arithmetic': 1},
                    'complexity_range': (2, 5),
                    'specificity': 0.9
                },
                'linear_search': {
                    'keywords': ['linear', 'sequential', 'find', 'search'],
                    'required_patterns': ['linear_search'],
                    'required_operations': {'loop': 1, 'comparison': 1},
                    'specificity': 0.7
                },
                'hash_search': {
                    'keywords': ['hash', 'lookup', 'dictionary', 'map'],
                    'required_patterns': ['hash_lookup'],
                    'specificity': 0.8
                },
                'interpolation_search': {
                    'keywords': ['interpolation', 'probe'],
                    'required_operations': {'arithmetic': 3, 'comparison': 2},
                    'specificity': 0.85
                }
            },
            
            AlgorithmType.GRAPH_TRAVERSAL: {
                'dfs': {
                    'keywords': ['dfs', 'depth', 'deep', 'stack'],
                    'required_patterns': ['graph_traversal'],
                    'required_operations': {'function_call': 1},
                    'specificity': 0.9
                },
                'bfs': {
                    'keywords': ['bfs', 'breadth', 'queue', 'level'],
                    'required_patterns': ['graph_traversal', 'queue_based'],
                    'specificity': 0.9
                },
                'dijkstra': {
                    'keywords': ['dijkstra', 'shortest', 'distance', 'path'],
                    'required_patterns': ['graph_traversal'],
                    'required_operations': {'comparison': 3, 'assignment': 3},
                    'specificity': 0.95
                },
                'a_star': {
                    'keywords': ['astar', 'a*', 'heuristic', 'manhattan'],
                    'required_patterns': ['graph_traversal'],
                    'specificity': 0.95
                }
            },
            
            AlgorithmType.CRYPTOGRAPHIC_ALGORITHM: {
                'miller_rabin': {
                    'keywords': ['miller', 'rabin', 'primality', 'witness', 'composite'],
                    'required_patterns': ['modulo'],
                    'required_operations': {'loop': 1, 'arithmetic': 2},
                    'specificity': 0.95
                },
                'elliptic_curve': {
                    'keywords': ['elliptic', 'curve', 'point', 'addition', 'ecc'],
                    'required_patterns': ['modulo'],
                    'required_operations': {'arithmetic': 3},
                    'specificity': 0.95
                },
                'aes': {
                    'keywords': ['aes', 'rijndael', 'subbytes', 'shiftrows'],
                    'required_patterns': ['rounds', 'xor'],
                    'specificity': 0.95
                },
                'rsa': {
                    'keywords': ['rsa', 'modexp', 'public_key', 'private_key', 'exponentiation'],
                    'required_patterns': ['modulo'],
                    'specificity': 0.95
                },
                'sha': {
                    'keywords': ['sha', 'sha256', 'sha512', 'digest'],
                    'required_patterns': ['rounds', 'bitwise'],
                    'specificity': 0.9
                },
                'hmac': {
                    'keywords': ['hmac', 'mac', 'authentication'],
                    'required_patterns': ['xor', 'key_operation'],
                    'specificity': 0.9
                },
                'modular_arithmetic': {
                    'keywords': ['modular', 'mod', 'prime', 'gcd', 'inverse'],
                    'required_patterns': ['modulo'],
                    'specificity': 0.85
                }
            },
            
            AlgorithmType.AUDIO_CODEC: {
                # Uncompressed formats
                'pcm_codec': {
                    'keywords': ['pcm', 'audio_format_pcm', 'pcm_s16', 'pcm_s24', 'pcm_s32', 'pcm_f32', 'raw_audio', 'uncompressed', 'linear_pcm'],
                    'required_patterns': ['audio_processing'],  # Must have audio context
                    'required_operations': {'assignment': 2, 'array_access': 1},  # More strict
                    'specificity': 0.75  # Lower priority than specific codecs
                },
                # Classic telephony codecs
                'alaw_ulaw': {
                    'keywords': ['alaw', 'ulaw', 'g711', 'g711a', 'g711u', 'companding', 'quantization', 'mu_law', 'a_law'],
                    'required_patterns': ['bitwise'],
                    'specificity': 0.95
                },
                'g722': {
                    'keywords': ['g722', 'adpcm', 'sub_band', 'qmf', 'quadrature_mirror'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'g729': {
                    'keywords': ['g729', 'acelp', 'cs_acelp', 'conjugate_structure', 'algebraic_celp'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Modern lossy codecs
                'mp3_codec': {
                    'keywords': ['mp3', 'mpeg', 'layer3', 'layer_3', 'psychoacoustic', 'mdct', 'huffman_decode', 'bit_reservoir', 'granule', 'xing', 'vbri'],
                    'required_patterns': ['audio_processing'],  # Must have audio context
                    'required_operations': {'function_call': 1},  # MP3 has function calls
                    'specificity': 0.98
                },
                'aac_codec': {
                    'keywords': ['aac', 'advanced_audio', 'm4a', 'spectral', 'tns', 'pns', 'sbr', 'ps', 'he_aac', 'aac_lc', 'mpeg4_audio'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'vorbis': {
                    'keywords': ['vorbis', 'ogg', 'xiph', 'floor', 'residue', 'codebook', 'mdct_vorbis'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'opus': {
                    'keywords': ['opus', 'silk', 'celt', 'hybrid_codec', 'opus_encode', 'opus_decode', 'silk_encode', 'celt_encode'],
                    'required_patterns': [],
                    'specificity': 0.98
                },
                'ac3': {
                    'keywords': ['ac3', 'dolby', 'a52', 'bsi', 'mantissa', 'exponent', 'bit_allocation'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'dts': {
                    'keywords': ['dts', 'dca', 'coherent_acoustics', 'subband', 'qmf_dts'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Lossless codecs
                'flac': {
                    'keywords': ['flac', 'free_lossless', 'rice', 'golomb', 'lpc', 'flac_encode', 'linear_predictive'],
                    'required_patterns': [],
                    'specificity': 0.98
                },
                'alac': {
                    'keywords': ['alac', 'apple_lossless', 'rice_coding', 'adaptive_golomb'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'ape': {
                    'keywords': ['ape', 'monkey', 'monkeys_audio', 'range_coding', 'predictor_ape'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Speech codecs
                'amr': {
                    'keywords': ['amr', 'amr_nb', 'amr_wb', 'acelp', 'adaptive_multi_rate'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'speex': {
                    'keywords': ['speex', 'celp', 'wideband', 'narrowband', 'ultra_wideband'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'gsm': {
                    'keywords': ['gsm', 'rpeltp', 'gsm_fr', 'gsm_efr', 'gsm_hr'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Proprietary/specialized
                'wma': {
                    'keywords': ['wma', 'windows_media_audio', 'wmapro', 'wmalossless'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'atrac': {
                    'keywords': ['atrac', 'adaptive_transform', 'sony', 'minidisc', 'qmf_atrac'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'aptx': {
                    'keywords': ['aptx', 'apt_x', 'qmf', 'adpcm_aptx', 'bluetooth_audio'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'ldac': {
                    'keywords': ['ldac', 'sony_ldac', 'hybrid_codec', 'bluetooth_hires'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                }
            },
            
            AlgorithmType.VIDEO_CODEC: {
                # H.26x family
                'h264': {
                    'keywords': ['h264', 'avc', 'cabac', 'cavlc', 'intra_prediction', 'deblocking_filter', 'nal_unit', 'macroblock', 'motion_estimation', 'h264_encode'],
                    'required_patterns': [],
                    'specificity': 0.98
                },
                'h265': {
                    'keywords': ['h265', 'hevc', 'ctu', 'coding_tree_unit', 'sao', 'sample_adaptive_offset', 'pu', 'tu', 'prediction_unit', 'transform_unit'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'h266': {
                    'keywords': ['h266', 'vvc', 'versatile_video', 'alf', 'adaptive_loop_filter', 'mts', 'multiple_transform'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # VP family
                'vp8': {
                    'keywords': ['vp8', 'golden_frame', 'altref', 'bool_coder', 'dct_vp8', 'loop_filter_vp8'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'vp9': {
                    'keywords': ['vp9', 'superblock', 'compound_prediction', 'vp9_decode', 'partition', 'loop_restoration', 'inter_prediction'],
                    'required_patterns': [],
                    'specificity': 0.98
                },
                'av1': {
                    'keywords': ['av1', 'aomedia', 'cdef', 'restoration_filter', 'film_grain', 'warped_motion', 'av1_encode', 'palette_mode'],
                    'required_patterns': [],
                    'specificity': 0.98
                },
                # MPEG family
                'mpeg2': {
                    'keywords': ['mpeg2', 'mpeg_2', 'gop', 'group_of_pictures', 'dct_8x8', 'field_picture', 'frame_picture'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'mpeg4': {
                    'keywords': ['mpeg4', 'mpeg_4', 'divx', 'xvid', 'simple_profile', 'advanced_simple', 'quarter_pixel'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Legacy/specialized
                'theora': {
                    'keywords': ['theora', 'xiph_video', 'vp3', 'golden_frame_theora', 'hilbert_curve'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'wmv': {
                    'keywords': ['wmv', 'windows_media_video', 'vc1', 'vc_1', 'intensity_compensation', 'range_reduction'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'rv': {
                    'keywords': ['realvideo', 'rv40', 'rv30', 'real_video', 'h263_plus'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Motion estimation patterns
                'motion_estimation': {
                    'keywords': ['motion_vector', 'mv', 'sad', 'sum_absolute_difference', 'motion_search', 'me', 'diamond_search', 'hexagon_search'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                # Transform coding
                'dct_transform': {
                    'keywords': ['dct', 'discrete_cosine', 'idct', 'transform_coefficients', 'quantization_matrix', 'zigzag_scan'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                'wavelet_transform': {
                    'keywords': ['wavelet', 'dwt', 'lifting_scheme', 'haar', 'daubechies', 'subband_decomposition'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                # Entropy coding
                'cabac': {
                    'keywords': ['cabac', 'context_adaptive_binary', 'arithmetic_coding', 'context_model', 'bypass_coding'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                'cavlc': {
                    'keywords': ['cavlc', 'context_adaptive_vlc', 'coeff_token', 'total_zeros', 'run_before'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                # Professional/RAW formats
                'prores': {
                    'keywords': ['prores', 'apple_prores', 'dct_prores', 'slice_based', 'chroma_subsampling'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'dnxhd': {
                    'keywords': ['dnxhd', 'dnxhr', 'avid', 'vc3', 'smpte_vc3'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'cineform': {
                    'keywords': ['cineform', 'wavelet_cineform', 'cfhd', 'gopro_codec'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                # Screen capture/lossless
                'screen_codec': {
                    'keywords': ['screen_capture', 'screen_codec', 'zlib', 'deflate', 'rgb_compression', 'desktop_capture'],
                    'required_patterns': ['loop'],
                    'specificity': 0.9
                },
                'huffyuv': {
                    'keywords': ['huffyuv', 'huffman_yuv', 'lossless_video', 'median_prediction'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                },
                'ffv1': {
                    'keywords': ['ffv1', 'ffmpeg_video1', 'range_coder', 'context_model_ffv1'],
                    'required_patterns': ['loop'],
                    'specificity': 0.95
                }
            },
            
            AlgorithmType.NUMERICAL_ALGORITHM: {
                'fibonacci': {
                    'keywords': ['fibonacci', 'fib'],
                    'required_patterns': ['fibonacci'],
                    'specificity': 0.95
                },
                'factorial': {
                    'keywords': ['factorial', 'fact'],
                    'required_patterns': ['factorial'],
                    'specificity': 0.95
                },
                'gcd': {
                    'keywords': ['gcd', 'greatest', 'common', 'divisor', 'euclidean'],
                    'required_patterns': ['modulo'],
                    'required_operations': {'loop': 1, 'arithmetic': 1},
                    'specificity': 0.9
                },
                'prime_check': {
                    'keywords': ['prime', 'isprime', 'primality'],
                    'required_patterns': ['modulo'],
                    'required_operations': {'loop': 1, 'comparison': 1},
                    'specificity': 0.85
                },
                'matrix_multiplication': {
                    'keywords': ['matrix', 'matmul', 'multiply'],
                    'required_operations': {'loop': 3, 'arithmetic': 2},
                    'specificity': 0.9
                }
            }
        }
        
        return patterns
    
    def detect(self, ast_tree: Any, language: str, line_count: int = 0) -> List[Dict[str, Any]]:
        """
        Main detection method matching the original AlgorithmDetector interface.
        
        Args:
            ast_tree: The parsed AST tree
            language: Programming language
            line_count: Number of lines in the file
            
        Returns:
            List of detected algorithms with their metadata
        """
        detected_algorithms = []
        
        # Extract functions from AST based on language
        functions = self._extract_functions_from_ast(ast_tree, language)
        
        for func_node, func_name, func_text in functions:
            # Skip very small functions (less than 3 lines of actual code)
            func_lines = [l for l in func_text.split('\n') if l.strip() and not l.strip().startswith('#')]
            if len(func_lines) < 3:
                continue
            
            # Detect algorithm type using enhanced detection
            algo_type, subtype, confidence = self.detect_algorithm_type(
                func_text, func_name, func_node, language
            )
            
            # Skip if no algorithm detected or confidence is too low
            if algo_type is None:
                continue
                
            min_confidence = getattr(self.config, 'confidence_threshold', 0.0)
            if confidence < min_confidence:
                continue
            
            # Build algorithm metadata
            algorithm_info = {
                "algorithm_type": algo_type.value,
                "algorithm_subtype": subtype,
                "confidence": confidence,
                "function_info": {
                    "name": func_name,
                    "start_line": getattr(func_node, 'start_point', (0, 0))[0] + 1,
                    "end_line": getattr(func_node, 'end_point', (0, 0))[0] + 1,
                    "lines_of_code": len(func_lines)
                },
                "transformation_resistance": {
                    "variable_renaming": 0.8 if confidence > 0.7 else 0.6,
                    "code_reformatting": 0.9,
                    "comment_modification": 1.0,
                    "function_extraction": 0.7
                }
            }
            
            detected_algorithms.append(algorithm_info)
        
        # Check for unknown complex algorithms in large files
        if line_count >= 50 and not detected_algorithms:
            # Add a file-level unknown algorithm marker
            detected_algorithms.append({
                "algorithm_type": "unknown_complex_algorithm",
                "algorithm_subtype": "complex_implementation",
                "confidence": 0.5,
                "function_info": {
                    "name": "file_level_complexity",
                    "start_line": 1,
                    "end_line": line_count,
                    "lines_of_code": line_count
                },
                "transformation_resistance": {
                    "variable_renaming": 0.5,
                    "code_reformatting": 0.6,
                    "comment_modification": 1.0,
                    "function_extraction": 0.4
                }
            })
        
        return detected_algorithms
    
    def _extract_functions_from_ast(self, ast_tree: Any, language: str) -> List[Tuple[Any, str, str]]:
        """
        Extract functions from AST tree.
        
        Returns:
            List of tuples (ast_node, function_name, function_text)
        """
        if not hasattr(ast_tree, 'root'):
            return []
            
        functions = []
        self._find_functions_recursive(ast_tree.root, functions, ast_tree.code)
        
        # Convert to expected format
        result = []
        for func_info in functions:
            result.append((
                func_info['node'],
                func_info['name'],
                func_info['text']
            ))
        
        return result
    
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
                
    def _calculate_lines(self, node: Any, code: str) -> int:
        """Calculate number of lines for a node."""
        if not node:
            return 0
        try:
            start_line = code[:node.start_byte].count('\n') + 1
            end_line = code[:node.end_byte].count('\n') + 1
            return end_line - start_line + 1
        except:
            return 0