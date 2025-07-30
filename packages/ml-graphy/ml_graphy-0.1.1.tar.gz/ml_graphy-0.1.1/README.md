# ml-graphy

A simple and elegant Python package for visualizing machine learning training metrics. `ml-graphy` automatically detects training and validation data to generate clean, publication-ready plots with just one line of code.

## Key Features

- **Automatic Metric Detection**: Intelligently finds `loss`, `accuracy`, `val_loss`, and `val_accuracy` in your model's history.
- **Publication-Ready Plots**: Creates beautiful, clean plots using Seaborn styling.
- **Simple API**: Generate insightful visualizations with a single function call.
- **Training Summary**: Prints a concise summary of final training and validation metrics.

## Installation

Install `ml-graphy` directly from PyPI:

```bash
pip install ml-graphy
```

This will automatically install the required dependencies: `matplotlib` and `seaborn`.

## Quick Start

Using `ml-graphy` is straightforward. Just import the `plot_metrics` function and pass it your trained model object that contains a `history` attribute.

```python
from mlgraphy.plotting import plot_metrics

# Create a mock model with a history attribute
class MockModel:
    def __init__(self):
        self.history = {
            'loss': [0.8, 0.6, 0.4, 0.3, 0.2],
            'accuracy': [0.6, 0.7, 0.8, 0.85, 0.9],
            'val_loss': [0.9, 0.7, 0.5, 0.4, 0.3],
            'val_accuracy': [0.55, 0.65, 0.75, 0.8, 0.85]
        }

# Create an instance and plot the metrics
model = MockModel()
plot_metrics(model)
```

This will generate and display side-by-side plots for loss and accuracy.

## What's Next?

The current version of `ml-graphy` focuses on simplicity and core functionality. Future releases will introduce more advanced features to provide greater flexibility and insight into your model's performance. We are actively working on expanding the library's capabilities to support a wider range of visualization needs.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
