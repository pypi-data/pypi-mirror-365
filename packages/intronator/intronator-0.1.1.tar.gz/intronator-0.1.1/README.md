# Intronator

A Python package for intron analysis with splice site prediction capabilities.

## Features

- SpliceAI integration for splice site prediction
- Pangolin model support for enhanced predictions
- seqmat compatibility for sequence analysis
- Python 3.10+ support

## Installation

### Basic Installation
```bash
pip install intronator
```

### External Dependencies
The package requires SpliceAI and Pangolin models which must be installed separately:

#### SpliceAI
```bash
pip install spliceai
```

#### Pangolin
```bash
pip install git+https://github.com/tkzeng/Pangolin.git
```

#### Complete Installation (with external dependencies)
```bash
pip install intronator[external]
```

## Quick Start

```python
import intronator

# Check package status
print(intronator.hello_intronator())
print(intronator.check_seqmat_compatibility())
print(intronator.get_model_status())
```

## Requirements

- Python >= 3.10
- seqmat
- torch >= 1.10.0
- tensorflow >= 2.8.0
- SpliceAI (install separately)
- Pangolin (install separately)

## Notes

- SpliceAI and Pangolin models will be automatically loaded when the package is imported
- Model loading may take some time on first import
- GPU acceleration is automatically detected and used when available