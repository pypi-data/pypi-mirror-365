# SheetWise

A Python package for encoding spreadsheets for Large Language Models, implementing the SpreadsheetLLM research framework.

[![PyPI version](https://badge.fury.io/py/sheetwise.svg)](https://badge.fury.io/py/sheetwise)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

SheetWise is a Python package that implements the key components from Microsoft Research's SpreadsheetLLM paper for efficiently encoding spreadsheets for use with Large Language Models. The package provides:

- **SheetCompressor**: Efficient encoding framework with three compression modules
- **Chain of Spreadsheet**: Multi-step reasoning approach for spreadsheet analysis
- **Vanilla Encoding**: Traditional cell-by-cell encoding methods
- **Token Optimization**: Significant reduction in token usage for LLM processing

## Key Features

- **Intelligent Compression**: Up to 96% reduction in token usage while preserving semantic information
- **Multi-Table Support**: Handles complex spreadsheets with multiple tables and regions
- **Structural Analysis**: Identifies and preserves important structural elements
- **LLM-Ready Output**: Generates optimized text for direct use with ChatGPT, Claude, etc.
- **Format-Aware**: Preserves data type and formatting information
- **Easy Integration**: Simple API for immediate use

## Installation

### Using pip

```bash
pip install sheetwise
```

### Using Poetry

```bash
poetry add sheetwise
```

### Development Installation

```bash
git clone https://github.com/yourusername/sheetwise.git
cd sheetwise
poetry install
```

## Quick Start

### Basic Usage

```python
import pandas as pd
from sheetwise import SpreadsheetLLM

# Initialize the framework
sllm = SpreadsheetLLM()

# Load your spreadsheet
df = pd.read_excel("your_spreadsheet.xlsx")

# Compress and encode for LLM use
llm_ready_text = sllm.compress_and_encode_for_llm(df)

# Copy and paste this text directly into ChatGPT/Claude
print(llm_ready_text)
```

### Advanced Usage

```python
from sheetwise import SpreadsheetLLM, SheetCompressor

# Using SheetCompressor directly
compressor = SheetCompressor(
    k=2,  # Structural anchor neighborhood size
    use_extraction=True,
    use_translation=True, 
    use_aggregation=True
)

# Compress the spreadsheet
compressed_result = compressor.compress(df)
print(f"Compression ratio: {compressed_result['compression_ratio']:.1f}x")
print(f"Compressed shape: {compressed_result['compressed_df'].shape}")

# Or use with SpreadsheetLLM for full pipeline
sllm = SpreadsheetLLM(compression_params={
    'k': 2,
    'use_extraction': True,
    'use_translation': True, 
    'use_aggregation': True
})

# Get detailed statistics
stats = sllm.get_encoding_stats(df)
print(f"Token reduction: {stats['token_reduction_ratio']:.1f}x")

# Process QA queries
result = sllm.process_qa_query(df, "What was the total revenue in 2023?")
```

### Command Line Interface

```bash
# Compress a spreadsheet file
sheetwise input.xlsx -o output.txt --stats

# Run demo with sample data
sheetwise --demo

# Use vanilla encoding instead of compression
sheetwise input.xlsx --vanilla
```

## Core Components

### 1. SheetCompressor

The main compression framework with three modules:

- **Structural Anchor Extraction**: Identifies and preserves structurally important rows/columns
- **Inverted Index Translation**: Creates efficient value-to-location mappings
- **Data Format Aggregation**: Groups cells by data type and format

### 2. Chain of Spreadsheet

Multi-step reasoning approach:

1. **Table Identification**: Automatically detects table regions
2. **Compression**: Applies SheetCompressor to reduce size
3. **Query Processing**: Identifies relevant regions for specific queries

### 3. Vanilla Encoder

Traditional encoding methods for comparison and compatibility.

## Examples

### Working with Financial Data

```python
from sheetwise import SpreadsheetLLM
from sheetwise.utils import create_realistic_spreadsheet

# Create sample financial spreadsheet
df = create_realistic_spreadsheet()

sllm = SpreadsheetLLM()

# Analyze the data
stats = sllm.get_encoding_stats(df)
print(f"Original size: {stats['original_shape']}")
print(f"Sparsity: {stats['sparsity_percentage']:.1f}% empty cells")
print(f"Compression: {stats['compression_ratio']:.1f}x smaller")

# Generate LLM-ready output
encoded = sllm.compress_and_encode_for_llm(df)
print("\\nReady for LLM:")
print(encoded[:300] + "...")
```

### Custom Compression Pipeline

```python
from sheetwise import SheetCompressor

# Compare different compression strategies
configs = [
    {"name": "Extraction Only", "use_translation": False, "use_aggregation": False},
    {"name": "Translation Only", "use_extraction": False, "use_aggregation": False}, 
    {"name": "All Modules", "use_extraction": True, "use_translation": True, "use_aggregation": True}
]

for config in configs:
    compressor = SheetCompressor(**{k: v for k, v in config.items() if k != "name"})
    result = compressor.compress(df)
    print(f"{config['name']}: {result['compression_ratio']:.1f}x compression")
```

## Performance

SpreadsheetLLM achieves significant improvements over vanilla encoding:

| Metric | Vanilla | SpreadsheetLLM | Improvement |
|--------|---------|----------------|-------------|
| Token Count | ~25,000 | ~1,200 | **96% reduction** |
| Sparsity Handling | Poor | Excellent | **Removes empty regions** |
| Multi-Table Support | Limited | Native | **Preserves structure** |
| Format Preservation | Basic | Advanced | **Type-aware grouping** |

## API Reference

### SpreadsheetLLM Class

The main interface for the framework.

#### Methods

- `compress_and_encode_for_llm(df)`: One-step compression and encoding
- `compress_spreadsheet(df)`: Apply compression pipeline  
- `encode_vanilla(df)`: Traditional encoding
- `get_encoding_stats(df)`: Detailed compression statistics
- `process_qa_query(df, query)`: Chain of Spreadsheet reasoning
- `load_from_file(filepath)`: Load spreadsheet from file

### SheetCompressor Class

Core compression framework.

#### Parameters

- `k`: Structural anchor neighborhood size (default: 4)
- `use_extraction`: Enable structural extraction (default: True)
- `use_translation`: Enable inverted index translation (default: True)
- `use_aggregation`: Enable format aggregation (default: True)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository

git clone https://github.com/yourusername/sheetwise.git
cd sheetwise

# Install development dependencies
poetry install

# Run tests
poetry run pytest

# Run linting
poetry run black src tests
poetry run isort src tests
poetry run flake8 src tests
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src

# Run specific test file
poetry run pytest tests/test_core.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use SpreadsheetLLM in your research, please cite:

```bibtex
@article{spreadsheetllm2024,
  title={SpreadsheetLLM: Encoding Spreadsheets for Large Language Models},
  author={Microsoft Research Team},
  journal={arXiv preprint},
  year={2024}
}
```


## Support

- [Documentation](https://sheetwise.readthedocs.io)
- [Issue Tracker](https://github.com/yourusername/sheetwise/issues)
- [Discussions](https://github.com/yourusername/sheetwise/discussions)
