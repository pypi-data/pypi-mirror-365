# Semantic Copycat Minner (CopycatM)

A semantic analysis tool for extracting code hashes, algorithms, and structural features for similarity analysis and copyright detection.

## Features

- **Multi-language Support**: Python, JavaScript/TypeScript, Java, C/C++, Go, Rust
- **Semantic Analysis**: AST-based code analysis with tree-sitter parsers
- **Algorithm Detection**: Pattern recognition for common algorithms (sorting, searching, graph algorithms)
- **Fuzzy Hashing**: TLSH for similarity detection across transformed code
- **Semantic Hashing**: MinHash and SimHash for structural similarity
- **Transformation Resistance**: Hash extraction that works across code transformations
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
--min-lines                   Minimum lines for algorithm analysis (default: 20)
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
    "min_lines": 20,
    "confidence_threshold": 0.0
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

The tool can detect various algorithmic patterns:

### Sorting Algorithms
- Quicksort
- Mergesort
- Bubblesort
- Heapsort

### Searching Algorithms
- Binary Search
- Linear Search
- Depth-First Search
- Breadth-First Search

### Graph Algorithms
- Dijkstra's Algorithm
- Bellman-Ford
- Kruskal's Algorithm

### Dynamic Programming
- Fibonacci
- Longest Common Subsequence
- Knapsack Problem

### String Algorithms
- KMP Pattern Matching
- Rabin-Karp

## Hashing Methods

### Direct Hashing
- SHA256: Cryptographic hash for exact matching
- MD5: Fast hash for quick comparisons

### Fuzzy Hashing
- TLSH: Locality-sensitive hashing for similarity detection

### Semantic Hashing
- MinHash: Jaccard similarity for set-based comparison
- SimHash: Hamming distance for structural similarity
- LSH: Locality-sensitive hashing for approximate nearest neighbor search

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