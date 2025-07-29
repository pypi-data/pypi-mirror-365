# Time Economy

A comprehensive Python toolkit for time-based economy simulation, focusing on wealth distribution modeling, economic simulations, and multi-agent systems analysis.

## Features

### Core Simulation Models
- **BaseWealthSimulation**: Foundation class for wealth distribution simulations
- **WealthSimulationModel3**: Exponential wealth distribution model  
- **WealthSimulationModel5**: Power law wealth distribution model
- **WealthSimulationModel5_tax**: Power law model with taxation mechanisms
- **TimeVectorSimulation**: Advanced vectorized economy of time simulations

### Analysis & Visualization
- **Multi-configuration Analysis**: Run and compare multiple simulation configurations
- **Statistical Analysis**: Gini coefficient calculations, distribution fitting
- **Advanced Plotting**: Distribution plots, scatter analyses, time series visualization
- **GPU Acceleration**: Optional CuPy support for high-performance computing

### Key Capabilities
- Wealth inequality modeling and analysis
- Economic policy simulation (taxation, redistribution)
- Agent-based modeling with heterogeneous savings behavior
- Power law and exponential distribution analysis
- Real-time animation of simulation dynamics
- Comprehensive statistical reporting

## Installation

```bash
pip install time-economy
```

For GPU acceleration support:
```bash
pip install time-economy[gpu]
```

## Data Storage

**All simulation runs are saved in the directory from which you run the code or in a user-designated location:**

- **Single Simulations**: Data is saved in the `data_folder` parameter you specify when creating simulations
- **Multi-Configuration Analysis**: Results are saved in the `base_output_dir` parameter (defaults to "multi_config_results" in current directory)
- **Default Locations**: If no folder is specified, data is saved in the current working directory

### Examples:
```python
# Save in current directory
sim = WealthSimulationModel5(data_folder="my_results", N=10000, MeanWealth=100.0)

# Save in specific path
sim = TimeVectorSimulation(data_folder="/path/to/my/simulation", N=5000)

# Multi-config analysis with custom output directory
analyzer = MultiConfigAnalysis(base_output_dir="my_analysis_results")
```

## Quick Start

```python
from time_economy import WealthSimulationModel5, TimeVectorSimulation

# Create a power law wealth simulation
sim = WealthSimulationModel5(
    data_folder="results",  # Data will be saved in "results" folder in current directory
    N=10000,
    MeanWealth=100.0,
    MaxLambda=1.0,
    p_0=0.05
)

# Run static simulation
sim.run_simulation_static(MaxRunTime=1000, batch_size=100, update_rate=10)

# Plot results
sim.plot_wealth_distribution(static_plot=True)
```

### Time Vector Simulations

```python
from time_economy import TimeVectorSimulation, run_time_vector, show_run_time_vector_args

# See all available parameters and their default values
show_run_time_vector_args()

# Run a time vector simulation with custom parameters
sim = TimeVectorSimulation(
    data_folder="time_results",  # Data saved in "time_results" folder
    N=5000,
    dimensions=['knowledge', 'production', 'power'],
    use_gpu_if_available=True
)

sim.run_simulation_static(MaxRunTime=500, batch_size=50, update_rate=5)

# Or use the convenience function
sim = run_time_vector(
    data_folder="my_simulation_results",
    N=1000,
    MaxRunTime=100,
    enable_power_dynamics=True
)
```

## Advanced Usage

### Parameter Discovery

The package provides a helper function to discover all available parameters for time vector simulations:

```python
from time_economy import show_run_time_vector_args

# Display all available parameters and their default values
show_run_time_vector_args()
```

This will show you all 25+ parameters that can be configured, including:
- Population size and dimensions
- Economic parameters (savings, risk, knowledge transfer)
- Power dynamics and decay settings
- Simulation control parameters (run time, batch size, etc.)

### Multi-Configuration Analysis

```python
from time_economy.multi_config_analysis import MultiConfigAnalysis

# Create analysis with 4 workers (default)
analyzer = MultiConfigAnalysis(n_jobs=4)

# List all available configurations
analyzer.list_available_configurations()

# Select specific configurations to run
analyzer.select_configurations(['small_population', 'FULL', 'power_dynamics'])

# Add custom configuration
custom_config = {
    'N': 2000,
    'dimensions': ['production', 'knowledge'],
    'description': 'My custom configuration',
    'mode': 'diminishing',
    'c_knowledge_xfer': 0.15,
    'enable_power_dynamics': True
}
analyzer.add_custom_configuration('my_config', custom_config)

# Adjust simulation parameters
analyzer.set_simulation_parameters(MaxRunTime=1000, batch_size=50, update_rate=1, plot_interval=25)

# Set number of runs per configuration
analyzer.set_runs_per_config(5)

# Adjust parallelism
analyzer.set_parallelism(6)

# Run analysis
analyzer.run_complete_analysis()
```

#### Flexible Configuration Management

The multi-configuration analysis now supports:

- **Selective Configuration Running**: Choose any combination of 50+ default configurations
- **Custom Configurations**: Add your own configurations with any parameters
- **Adjustable Parallelism**: Set 1-8+ workers (default: 4)
- **Parameter Sweeps**: Built-in sweeps for power factors, knowledge transfer, savings, risk, decay, and noise
- **Efficient Resource Usage**: Sequential mode for GPU memory constraints, parallel for CPU-bound tasks

#### Available Configuration Types

- **Basic Models**: `small_population`, `large_population`, `very_large_population`
- **Knowledge Models**: `unleveraged_knowledge`, `diminishing_knowledge`
- **Power Dynamics**: `power_dynamics`, `power_and_sharing`, `power_and_sharing_decay`
- **Full Feature Models**: `FULL`, `power_sharing_risk_art_pleasure`
- **Parameter Sweeps**: `full_power_factor_*`, `full_knowledge_xfer_*`, `full_saving_*`, etc.

### Time Vector Simulations

```python
from time_economy import TimeVectorSimulation

sim = TimeVectorSimulation(
    data_folder="time_results",  # Data saved in "time_results" folder
    N=5000,
    dimensions=['knowledge', 'production', 'power'],
    use_gpu_if_available=True
)

sim.run_simulation_static(MaxRunTime=500, batch_size=50, update_rate=5)
```

## Requirements

- Python 3.8+
- NumPy >= 1.20.0
- Matplotlib >= 3.5.0
- Pandas >= 1.3.0
- Seaborn >= 0.11.0
- SciPy >= 1.7.0

## Optional Dependencies

- **CuPy**: For GPU acceleration (recommended for large simulations)
- **Joblib**: For parallel processing in multi-configuration analysis

## Documentation

Detailed documentation and examples are available in the package docstrings and example notebooks.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Citation

If you use this toolkit in your research, please cite:

```
Time Economy: A Python Package for Time-Based Economy Simulation and Economic Modeling
``` 