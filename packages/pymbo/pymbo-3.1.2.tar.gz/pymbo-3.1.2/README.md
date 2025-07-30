# PyMBO - Python Multi-objective Bayesian Optimization

A comprehensive multi-objective Bayesian optimization framework with advanced visualization and screening capabilities.

## Features

- **Multi-objective Bayesian optimization** with PyTorch/BoTorch backend
- **Real-time acquisition function heatmap visualization**
- **Interactive plot controls** with fixed aspect ratios
- **SGLBO screening module** for efficient parameter space exploration
- **Comprehensive logging and error handling**
- **Enhanced reporting capabilities**
- **Scientific utilities** for data validation and analysis

## Installation

### Requirements

- Python 3.8+
- PyTorch
- BoTorch
- Matplotlib
- Tkinter
- NumPy
- Pandas
- SciPy
- scikit-learn

### Setup

1. Clone the repository:
```bash
git clone https://github.com/jakub-jagielski/pymbo.git
cd pymbo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Usage

The application provides a graphical interface for:

1. **Parameter Configuration**: Define continuous, discrete, or categorical parameters
2. **Objective Setup**: Configure single or multi-objective optimization goals
3. **Optimization Execution**: Run Bayesian optimization with real-time visualization
4. **Results Analysis**: Generate detailed reports and export data

### Quick Start

```python
from pymbo import EnhancedMultiObjectiveOptimizer, SimpleController

# Create optimizer instance
optimizer = EnhancedMultiObjectiveOptimizer(
    bounds=[(0, 10), (0, 10)],
    objectives=['maximize']
)

# Run optimization
controller = SimpleController(optimizer)
controller.run_optimization()
```

## Architecture

The codebase is organized into four main modules:

- **`core/`**: Core optimization algorithms and controllers
- **`gui/`**: Graphical user interface components  
- **`utils/`**: Utility functions for plotting, reporting, and scientific calculations
- **`screening/`**: SGLBO screening optimization module

## Screening Module (SGLBO)

The Stochastic Gradient Line Bayesian Optimization (SGLBO) module provides efficient parameter space screening:

```python
from pymbo.screening import ScreeningOptimizer

optimizer = ScreeningOptimizer(
    params_config=config["parameters"],
    responses_config=config["responses"]
)
```

## License and Academic Use

PyMBO is licensed under the **CC BY-NC-ND 4.0 license**.

We want to explicitly clarify the "NonCommercial" clause for the academic community. The use of PyMBO for academic research and the publication of your results in scientific journals, theses, or conference proceedings is **fully permitted and strongly encouraged**.

Please see the `LICENSE` file for full details.

## How to Cite

If you use PyMBO in your research, please cite it as follows:

> Jakub Jagielski. (2025). *PyMBO: A Python library for multivariate Bayesian optimization and stochastic Bayesian screening*. Version 3.1.2. Retrieved from https://github.com/jakub-jagielski/pymbo

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request