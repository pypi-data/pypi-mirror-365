"""
Time Economy

A comprehensive toolkit for time-based economy simulation, focusing on wealth 
distribution modeling, economic simulations, and multi-agent systems analysis.
"""

__version__ = "1.0.0"
__author__ = "Double-N-A"

# Core simulation classes
from .base import (
    BaseWealthSimulation,
    WealthSimulationModel3,
    WealthSimulationModel5,
    WealthSimulationModel5_tax,
    ensure_numpy,
    ensure_xp,
    compute_wealth_distribution,
    gini_coefficient,
)

from .time_vector_simulation import (
    TimeVectorSimulation,
    TimeVectorSimulationUnleveraged,
    TimeVectorSimulationDiminishingReturns,
    run_time_vector,
    show_run_time_vector_args,
)

# Analysis and visualization modules
from . import plotter
from . import utils
from . import comparison_plotter

# Multi-configuration analysis
try:
    from .multi_config_analysis import MultiConfigAnalysis
except ImportError:
    # Handle case where some dependencies might not be available
    MultiConfigAnalysis = None

# Define what gets imported with "from time_economy import *"
__all__ = [
    # Core classes
    "BaseWealthSimulation",
    "WealthSimulationModel3", 
    "WealthSimulationModel5",
    "WealthSimulationModel5_tax",
    "TimeVectorSimulation",
    "TimeVectorSimulationUnleveraged",
    "TimeVectorSimulationDiminishingReturns",
    # Analysis classes
    "MultiConfigAnalysis",
    # Utility functions
    "ensure_numpy",
    "ensure_xp", 
    "compute_wealth_distribution",
    "gini_coefficient",
    # Time vector functions
    "run_time_vector",
    "show_run_time_vector_args",
    # Modules
    "plotter",
    "utils",
    "comparison_plotter",
] 