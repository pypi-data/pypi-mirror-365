# ml-graphy

A Python package for plotting machine learning training metrics with automatic detection of validation data and clean, publication-ready visualizations.

## Features

- 📊 Automatic detection of training and validation metrics
- 🎨 Clean, publication-ready plots using seaborn styling
- 📈 Support for loss and accuracy metrics
- 🔍 Automatic handling of missing data
- 📋 Training summary statistics

## Installation

```bash
pip install ml-graphy
```

This will automatically install all required dependencies:
- `numpy>=1.20.0`
- `matplotlib>=3.5.0` 
- `seaborn>=0.11.0`

### Development Installation
```bash
git clone https://github.com/Prasoon-Rai/Graphy.git
cd Graphy
pip install -e ".[dev]"
```

## Quick Start

```python
from graphy import plot_metrics

# Assuming you have a trained model with history
# model.history = {
#     'loss': [0.5, 0.4, 0.3, 0.2],
#     'accuracy': [0.8, 0.85, 0.9, 0.95],
#     'val_loss': [0.6, 0.45, 0.35, 0.25],
#     'val_accuracy': [0.75, 0.8, 0.85, 0.9]
# }

plot_metrics(model)
```

This will automatically:
- Detect available metrics (loss, accuracy)
- Check for validation data
- Create side-by-side plots
- Display training summary statistics

## Publishing to PyPI

This package uses GitHub releases for automated publishing. See [RELEASE.md](RELEASE.md) for instructions.

### Quick Release Process
1. Update version in `pyproject.toml`
2. Commit and push changes
3. Create a GitHub release
4. GitHub Actions automatically publishes to PyPI

## Requirements

- Python >= 3.8
- numpy >= 1.20.0
- matplotlib >= 3.5.0
- seaborn >= 0.11.0

All dependencies are automatically installed when you install ml-graphy.

## Testing

Test the package after installation:
```python
from graphy import plot_metrics

# Create a mock model with training history
class MockModel:
    def __init__(self):
        self.history = {
            'loss': [0.8, 0.6, 0.4, 0.3, 0.2],
            'accuracy': [0.6, 0.7, 0.8, 0.85, 0.9],
            'val_loss': [0.9, 0.7, 0.5, 0.4, 0.3],
            'val_accuracy': [0.55, 0.65, 0.75, 0.8, 0.85]
        }

model = MockModel()
plot_metrics(model)
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Development

For development, install with:
```bash
pip install -e ".[dev]"
```

This includes additional tools:
- pytest for testing
- black for code formatting
- flake8 for linting
- mypy for type checking
