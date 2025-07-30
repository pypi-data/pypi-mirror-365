# Semantic Copycat Minner (CopycatM)

A semantic analysis tool for extracting code hashes, algorithms, and structural features for similarity analysis and copyright detection.

## Features

- **Multi-language Support**: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust
- **Semantic Analysis**: AST-based code analysis with tree-sitter parsers
- **Algorithm Detection**: Pattern recognition for 40+ algorithm types across 8 categories
- **Unknown Algorithm Detection**: Structural complexity analysis to identify novel algorithms (v1.2.0+)
- **Cross-Language Consistency**: 100% MinHash similarity for same algorithms across languages (v1.4.0+)
- **Transformation Resistance**: 86.8% average resistance to code transformations (v1.4.0+)
- **Audio/Video Codec Detection**: Comprehensive detection of 40+ multimedia codecs (v1.4.0+)
  - Successfully tested on FFmpeg source code
  - Detects MP3, AAC, Opus, FLAC, PCM audio codecs
  - Detects H.264, H.265, VP8/9, AV1 video codecs
- **Fuzzy Hashing**: TLSH with optimized preprocessing for code similarity
- **Semantic Hashing**: MinHash and SimHash for structural similarity
- **CLI Interface**: Easy-to-use command-line tool with batch processing
- **JSON Output**: Structured output for integration with other tools

## Installation

### From PyPI

```bash
pip install semantic-copycat-minner
```

### From Source

```bash
git clone https://github.com/username/semantic-copycat-minner
cd semantic-copycat-minner
pip install -e .
```

## Quick Start

### Analyze a Single File

```bash
copycatm src/algorithm.py -o results.json
```

### Analyze a Directory

```bash
copycatm ./codebase -o results.json
```

### Custom Configuration

```bash
copycatm algorithm.py --complexity-threshold 5 --min-lines 50 -o results.json
```

## CLI Usage

### Basic Commands

```bash
# Single file analysis
copycatm <file_path> [options]

# Batch directory analysis
copycatm <directory_path> [options]
```

### Options

```bash
# Core options
--output, -o           Output JSON file path (default: stdout)
--verbose, -v          Verbose output (can be repeated: -v, -vv, -vvv)
--quiet, -q           Suppress all output except errors
--debug               Enable debug mode with intermediate representations

# Analysis configuration
--complexity-threshold, -c    Cyclomatic complexity threshold (default: 3)
--min-lines                   Minimum lines for algorithm analysis (default: 20, recommend 2 for utility libraries)
--include-intermediates       Include AST and control flow graphs in output
--languages                   Comma-separated list of languages to analyze

# Hash configuration
--hash-algorithms            Comma-separated hash types (default: sha256,tlsh,minhash)
--tlsh-threshold            TLSH similarity threshold (default: 100)
--lsh-bands                 LSH band count for similarity detection (default: 20)

# Output filtering
--only-algorithms           Only output algorithmic signatures
--only-metadata            Only output file metadata
--confidence-threshold     Minimum confidence score to include (0.0-1.0)

# Performance
--parallel, -p             Number of parallel workers (default: CPU count)
--chunk-size              Files per chunk for batch processing (default: 100)
```

## Library API

The library provides different levels of API access, with `CopycatAnalyzer` as the main entry point for most use cases.

### Main Entry Point: CopycatAnalyzer

`CopycatAnalyzer` is the primary interface that orchestrates all analysis components including parsing, algorithm detection, hashing, and complexity analysis.

```python
from semantic_copycat_minner import CopycatAnalyzer, AnalysisConfig

# Create analyzer with default configuration
analyzer = CopycatAnalyzer()

# Analyze a file (auto-detect language from extension)
result = analyzer.analyze_file("src/algorithm.py")

# Force specific language (useful for non-standard extensions)
result = analyzer.analyze_file("script.txt", force_language="python")

# Analyze code string directly
result = analyzer.analyze_code(code, "python", "algorithm.py")

# Analyze directory
results = analyzer.analyze_directory("./codebase")
```

### Lower-Level Components

For advanced use cases, you can access individual components directly:

```python
from semantic_copycat_minner import AlgorithmDetector
from semantic_copycat_minner.parsers import TreeSitterParser

# Direct algorithm detection with flexible input
detector = AlgorithmDetector()

# Option 1: Provide raw content (convenience method)
algorithms = detector.detect_algorithms_from_input(content, "python")

# Option 2: Provide pre-parsed AST (for reuse across components)
parser = TreeSitterParser()
ast_tree = parser.parse(content, "python")
algorithms = detector.detect_algorithms_from_input(ast_tree, "python")

# Option 3: Use original method (backward compatible)
algorithms = detector.detect_algorithms(ast_tree, "python")
```

### Custom Configuration

```python
from semantic_copycat_minner import CopycatAnalyzer, AnalysisConfig

# Create custom configuration
config = AnalysisConfig(
    complexity_threshold=5,
    min_lines=50,
    include_intermediates=True,
    hash_algorithms=["sha256", "tlsh", "minhash"],
    confidence_threshold=0.8
)

analyzer = CopycatAnalyzer(config)
result = analyzer.analyze_file("src/algorithm.py")
```

## Output Format

The tool outputs structured JSON with the following components:

### File Metadata

```json
{
  "file_metadata": {
    "file_name": "algorithm.py",
    "language": "python",
    "line_count": 85,
    "is_source_code": true,
    "analysis_timestamp": "2025-07-25T10:30:00Z"
  }
}
```

### Algorithm Detection

```json
{
  "algorithms": [
    {
      "id": "algo_001",
      "type": "algorithm",
      "name": "quicksort_implementation",
      "confidence": 0.92,
      "complexity_metric": 8,
      "evidence": {
        "pattern_type": "divide_and_conquer",
        "control_flow": "recursive_partition"
      },
      "hashes": {
        "direct": {"sha256": "abc123..."},
        "fuzzy": {"tlsh": "T1A2B3C4..."},
        "semantic": {"minhash": "123456789abcdef"}
      },
      "transformation_resistance": {
        "variable_renaming": 0.95,
        "language_translation": 0.85
      }
    }
  ]
}
```

### Unknown Algorithm Detection (v1.2.0+)

For complex code that doesn't match known algorithm patterns, CopycatM performs structural complexity analysis to identify unknown algorithms. This feature automatically activates for files with 50+ lines to optimize performance.

```json
{
  "algorithms": [
    {
      "id": "unknown_a1b2c3d4",
      "algorithm_type": "unknown_complex_algorithm",
      "subtype_classification": "bitwise_manipulation_algorithm",
      "confidence_score": 0.79,
      "evidence": {
        "complexity_score": 0.79,
        "cyclomatic_complexity": 33,
        "nesting_depth": 5,
        "operation_density": 4.2,
        "unique_operations": 25,
        "structural_hash": "abc123def456",
        "algorithmic_fingerprint": "ALG-E66468BA743C"
      },
      "transformation_resistance": {
        "structural_hash": 0.9,
        "operation_patterns": 0.85,
        "complexity_metrics": 0.95
      }
    }
  ]
}
```

Unknown algorithms are classified into subtypes based on their dominant characteristics:
- `complex_iteration_pattern` - Nested loops and complex iteration
- `bitwise_manipulation_algorithm` - Heavy use of bitwise operations
- `mathematical_computation` - Dense mathematical operations
- `complex_decision_logic` - High conditional complexity
- `data_transformation_algorithm` - Complex data flow patterns
- `deeply_nested_algorithm` - Extreme nesting depth
- `unclassified_complex_pattern` - Other complex patterns

### Mathematical Invariants

```json
{
  "mathematical_invariants": [
    {
      "id": "inv_001",
      "type": "mathematical_expression",
      "confidence": 0.78,
      "evidence": {
        "expression_type": "arithmetic_calculation"
      }
    }
  ]
}
```

## Configuration

### Configuration File

Create `copycatm.json` in your project directory:

```json
{
  "analysis": {
    "complexity_threshold": 3,
    "min_lines": 2,  // Recommended: 2 for utility libraries, 20 for general code
    "confidence_threshold": 0.0,
    "unknown_algorithm_threshold": 50  // Line count threshold for unknown algorithm detection
  },
  "languages": {
    "enabled": ["python", "javascript", "java", "c", "cpp", "go", "rust"]
  },
  "hashing": {
    "algorithms": ["sha256", "tlsh", "minhash"],
    "tlsh_threshold": 100,
    "lsh_bands": 20
  },
  "performance": {
    "parallel_workers": null,
    "chunk_size": 100
  },
  "output": {
    "include_intermediates": false
  }
}
```

## Supported Languages

- **Python**: `.py`, `.pyx`, `.pyi`
- **JavaScript**: `.js`, `.jsx`
- **TypeScript**: `.ts`, `.tsx`
- **Java**: `.java`
- **C/C++**: `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`
- **Go**: `.go`
- **Rust**: `.rs`

## Algorithm Detection

The tool can detect 40+ algorithmic patterns across 8 major categories:

### Core CS Algorithms
- **Sorting**: Quicksort, Mergesort, Bubblesort, Heapsort, Radix Sort
- **Searching**: Binary Search, Linear Search, DFS, BFS, A*, Jump Search
- **Graph Algorithms**: Dijkstra's, Bellman-Ford, Kruskal's, Prim's, Floyd-Warshall
- **Dynamic Programming**: Fibonacci, LCS, Knapsack, Edit Distance

### Security & Cryptography
- **Encryption**: AES, RSA, DES, ChaCha20, Elliptic Curve
- **Hashing**: SHA family, MD5, bcrypt, Argon2
- **Security**: Anti-tampering, obfuscation, authentication

### Media Processing
- **Audio Codecs**: MP3, AAC, Opus, FLAC, Vorbis, PCM, AC3, DTS
- **Video Codecs**: H.264, H.265/HEVC, VP8/9, AV1, MPEG-2, ProRes
- **Image Processing**: JPEG, PNG compression, filters, transforms

### System Level
- **Drivers**: Device drivers, kernel modules
- **Firmware**: Bootloaders, embedded systems
- **Low-level**: Memory management, interrupt handlers

### Domain Specific
- **Machine Learning**: Neural networks, gradient descent, k-means
- **Graphics**: Ray tracing, rasterization, shaders
- **Financial**: Options pricing, risk models
- **Medical**: Image reconstruction, signal processing
- **Automotive**: Control systems, sensor fusion

### Cross-Language Support (v1.4.0+)
- Same algorithms detected consistently across Python, JavaScript, C/C++, Java
- 100% MinHash similarity for identical algorithms in different languages
- Language-agnostic normalization for true semantic matching

## Hashing Methods

### Direct Hashing
- SHA256: Cryptographic hash for exact matching
- MD5: Fast hash for quick comparisons

### Fuzzy Hashing (Enhanced in v1.4.0)
- **TLSH**: Optimized preprocessing for code similarity
  - Algorithm-focused normalization
  - Smart padding for short functions
  - 15% transformation resistance (vs 5% standard)
- **ssdeep**: Primary fallback for code similarity
- **Enhanced Fallback**: Multi-component hashing when libraries unavailable

### Semantic Hashing (Cross-Language Support in v1.4.0)
- **MinHash**: 100% cross-language similarity with normalization
  - Language-agnostic code representation
  - Structural shingle extraction
  - 96.9% uniqueness (up from 61.9%)
- **SimHash**: Hamming distance for structural similarity
- **LSH**: Locality-sensitive hashing for approximate nearest neighbor search

## Development

### Setup Development Environment

```bash
git clone https://github.com/oscarvalenzuelab/semantic-copycat-minner
cd semantic-copycat-minner
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

## License

GNU Affero General Public License v3.0 - see LICENSE file for details.

## Acknowledgments

- Tree-sitter for robust parsing
- TLSH for fuzzy hashing
- DataSketch for MinHash implementation
- Radon for cyclomatic complexity analysis