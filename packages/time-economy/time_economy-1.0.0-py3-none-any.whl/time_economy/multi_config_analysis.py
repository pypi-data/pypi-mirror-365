#!/usr/bin/env python3
"""
Multi-Configuration TimeVectorSimulation Analysis Script

This script runs TimeVectorSimulation with different configurations,
each configuration multiple times, and generates comprehensive comparison plots
and statistical analysis.
"""

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd
from datetime import datetime
import warnings
import signal
import sys
warnings.filterwarnings('ignore')
import copy

# Global variable to store the analysis object for cleanup
_analysis_instance = None

def signal_handler(signum, frame):
    """Handle interrupt signals to ensure plots are closed"""
    print(f"\nReceived signal {signum}. Cleaning up plots...")
    if _analysis_instance is not None:
        _analysis_instance.cleanup_plots()
    plt.close('all')
    sys.exit(1)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Set matplotlib to use non-interactive backend to prevent figure accumulation
import matplotlib
matplotlib.use('Agg')

# Import the simulation class
from .time_vector_simulation import TimeVectorSimulation, TimeVectorSimulationUnleveraged, TimeVectorSimulationDiminishingReturns
import joblib
from . import plotter
from .time_vector_simulation import ensure_numpy, get_gini_coefficients, get_average_leverage
from .base import compute_wealth_distribution


class MultiConfigAnalysis:
    """
    Class to run multiple configurations of TimeVectorSimulation
    and generate comprehensive analysis plots
    """
    
    def __init__(self, base_output_dir="multi_config_results", n_jobs=4, log_to_disk=False):
        """
        Initialize the multi-configuration analysis
        Args:
            base_output_dir: Base directory for all results (relative to current working directory)
            n_jobs: Number of parallel jobs for simulation runs (default: 4 workers)
            log_to_disk: Whether to log simulation state to disk (default: False)
        Note: Each configuration's runs are executed in parallel using joblib.Parallel.
        """
        # Use the provided base_output_dir parameter and make it relative to current working directory
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(exist_ok=True)
        self.n_jobs = n_jobs
        self.log_to_disk = log_to_disk
        
        # Define default configurations to test
        self.default_configurations = {
            'small_population': {
                'N': 1000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Small population (N=1000)',
                'mode': 'original',
            },
            'large_population': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Large population (N=5000)',
                'mode': 'original',
            },
            'very_large_population': {
                'N': 10000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Very large population (N=10000)',
                'mode': 'original',
            },
            'unleveraged_knowledge': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Unleveraged knowledge acquisition',
                'mode': 'unleveraged',
            },
            'diminishing_knowledge': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Diminishing returns on knowledge',
                'mode': 'diminishing',
            },
            'vanilla_limited_sharing': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Original mode + limited knowledge sharing',
                'mode': 'original',
                'c_knowledge_xfer': 0.05,
            },
            'unleveraged_limited_sharing': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Unleveraged + limited knowledge sharing',
                'mode': 'unleveraged',
                'c_knowledge_xfer': 0.05,
            },
            'diminishing_limited_sharing': {
                'N': 5000,
                'dimensions': ['production', 'knowledge'],
                'description': 'Diminishing + limited knowledge sharing',
                'mode': 'diminishing',
                'c_knowledge_xfer': 0.05,
            },
            'power_dynamics': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power'],
                'description': 'Diminishing mode + power dynamics',
                'mode': 'diminishing',
                'enable_power_dynamics': True,
                'c_power_factor': 10,
            },
            'power_and_sharing': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power'],
                'description': 'Diminishing mode + power dynamics + limited knowledge sharing',
                'mode': 'diminishing',
                'c_knowledge_xfer': 0.05,
                'enable_power_dynamics': True,
                'c_power_factor': 10,
            },
            'power_and_sharing_decay': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power'],
                'description': 'Diminishing mode + power dynamics + limited knowledge sharing + decay',
                'mode': 'diminishing',
                'c_knowledge_xfer': 0.05,
                'enable_power_dynamics': True,
                'c_power_factor': 10,
                'base_daily_decay_rate': 0.01,
                'decay_coeffs_map': None,
                'enable_decay': True
            },
            'power_sharing_risk': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power'],
                'description': 'Power + sharing + capital risk',
                'mode': 'diminishing',
                'enable_capital_risk': True,
                'c_knowledge_xfer': 0.05,
                'enable_power_dynamics': True,
                'c_power_factor': 10,
                'base_daily_decay_rate': 0.01,
                'decay_coeffs_map': None,
                'enable_decay': True,
                'savings_mean': 0.05,
                'savings_std': 0.10,
                'risk_mean': 0.1,
                'risk_std': 0.1
            },
            'power_sharing_risk_art': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power', 'Art'],
                'description': 'Power + sharing + risk + Art dimension',
                'mode': 'diminishing',
                'enable_capital_risk': True,
                'c_knowledge_xfer': 0.05,
                'enable_power_dynamics': True,
                'c_power_factor': 10,
                'base_daily_decay_rate': 0.01,
                'decay_coeffs_map': {
                    'production': 2.0,
                    'knowledge': 0.01,
                    'power': 5.0,
                    'Art': 1.0,
                    'default': 1.0
                },
                'enable_decay': True,
                'savings_mean': 0.05,
                'savings_std': 0.10,
                'risk_mean': 0.1,
                'risk_std': 0.1,
                'art_leverage_exponent': 0.6
            },
            'power_sharing_risk_art_pleasure': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power', 'Art', 'pleasure'],
                'description': 'Power + sharing + risk + Art + pleasure (FULL)',
                'mode': 'diminishing',
                'enable_capital_risk': True,
                'enable_power_dynamics': True,
                'enable_decay': True,
                'enable_pleasure': True,
                'c_knowledge_xfer': 0.05,
                'c_power_factor': 10,
                'base_daily_decay_rate': 0.01,
                'decay_coeffs_map': {
                    'production': 2.0,
                    'knowledge': 0.01,
                    'power': 5.0,
                    'Art': 1.0,
                    'pleasure': 7.0,
                    'default': 1.0
                },
                'c_leverage_factor': 0.01,
                'savings_mean': 0.05,
                'savings_std': 0.10,
                'risk_mean': 0.1,
                'risk_std': 0.1,
                'focus_noise_level': 0.05,
                'art_leverage_exponent': 0.6,
                'k_time': 0.1,
                'k_consumption': 0.05,
                'pleasure_time_exponent': 0.5,
                'consumption_factor_mean': 0.01,
                'consumption_factor_std': 0.02,
                'consumption_noise_std': 0.2,
                'use_gpu_if_available': True,
                'log_to_disk': False,
                'plot_interval': 20,
                'random_initial_portfolio': False
            },
            'FULL': {
                'N': 1e5,
                'dimensions': ['production', 'knowledge', 'power', 'Art', 'pleasure'],
                'description': 'All features ON (baseline FULL scenario)',
                'mode': 'diminishing',
                'enable_capital_risk': True,
                'enable_power_dynamics': True,
                'c_knowledge_xfer': 0.05,
                'c_power_factor': 10,
                'base_daily_decay_rate': 0.01,
                'decay_coeffs_map': {
                    'production': 2.0,
                    'knowledge': 0.01,
                    'power': 5.0,
                    'Art': 1.0,
                    'pleasure': 7.0,
                    'default': 1.0
                },
                'c_leverage_factor': 0.01,
                'savings_mean': 0.05,
                'savings_std': 0.10,
                'risk_mean': 0.1,
                'risk_std': 0.1,
                'focus_noise_level': 0.05,
                'art_leverage_exponent': 0.6,
                'k_time': 0.1,
                'k_consumption': 0.05,
                'pleasure_time_exponent': 0.5,
                'consumption_factor_mean': 0.01,
                'consumption_factor_std': 0.02,
                'consumption_noise_std': 0.2,
                'use_gpu_if_available': True,
                'log_to_disk': False,
                'plot_interval': 20,
                'random_initial_portfolio': False
            },
        }
        
        # Add FULL-based sweep configurations
        self._add_full_sweep_configurations()
        
        # Store the full configurations dictionary for external access
        self.all_configurations = self.default_configurations.copy()
        
        # Start with all configurations selected
        self.configurations = self.all_configurations.copy()
        
        # Simulation parameters
        self.simulation_params = {
            'MaxRunTime': 2000,  # 2000 days
            'batch_size': 100,
            'update_rate': 1,   # 1 day per update
            'plot_interval': 50  # Plot every 50 days
        }
        
        # Number of runs per configuration
        self.runs_per_config = 10
        
        # Results storage
        self.results = {}
        self.summary_stats = {}
        
    def _add_full_sweep_configurations(self):
        """Add sweep configurations based on the FULL configuration"""
        full_base = self.default_configurations['FULL']
        
        # Power factor sweeps
        for factor in [1, 3, 5, 7, 9]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + power factor {factor}'
            cfg['c_power_factor'] = factor
            self.default_configurations[f'full_power_factor_0_0{factor}'] = cfg
            
        # Knowledge transfer sweeps
        for xfer in [0.02, 0.05, 0.10, 0.15, 0.20]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + knowledge transfer {xfer}'
            cfg['c_knowledge_xfer'] = xfer
            self.default_configurations[f'full_knowledge_xfer_{xfer:.2f}'.replace('.', '_')] = cfg
            
        # Savings sweeps
        for saving in [0.01, 0.05, 0.10, 0.20, 0.30]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + saving mean {saving}'
            cfg['savings_mean'] = saving
            self.default_configurations[f'full_saving_{saving:.2f}'.replace('.', '_')] = cfg
            
        # Risk sweeps
        for risk in [0.01, 0.05, 0.10, 0.20, 0.30]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + risk mean {risk}'
            cfg['risk_mean'] = risk
            self.default_configurations[f'full_risk_{risk:.2f}'.replace('.', '_')] = cfg
            
        # Decay sweeps
        for decay_power in [1.0, 2.0, 5.0, 10.0, 20.0]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + power decay {decay_power}'
            cfg['decay_coeffs_map'] = copy.deepcopy(full_base['decay_coeffs_map'])
            cfg['decay_coeffs_map']['power'] = decay_power
            self.default_configurations[f'full_decay_power_{decay_power:.1f}'.replace('.', '_')] = cfg
            
        for decay_pleasure in [0.1, 0.5, 1.0, 3.0, 7.0]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + pleasure decay {decay_pleasure}'
            cfg['decay_coeffs_map'] = copy.deepcopy(full_base['decay_coeffs_map'])
            cfg['decay_coeffs_map']['pleasure'] = decay_pleasure
            self.default_configurations[f'full_decay_pleasure_{decay_pleasure:.1f}'.replace('.', '_')] = cfg
            
        # Focus noise sweeps
        for noise in [0.01, 0.03, 0.05, 0.10, 0.20]:
            cfg = copy.deepcopy(full_base)
            cfg['description'] = f'All features ON + focus noise {noise}'
            cfg['focus_noise_level'] = noise
            self.default_configurations[f'full_noise_{noise:.2f}'.replace('.', '_')] = cfg
            
        # Population size variations
        cfg = copy.deepcopy(full_base)
        cfg['description'] = 'All features ON + large population (1M, sequential)'
        cfg['N'] = int(1e6)
        cfg['n_jobs_override'] = 1
        self.default_configurations['full_large_population'] = cfg
        
        cfg = copy.deepcopy(full_base)
        cfg['description'] = 'All features ON + small population (1000)'
        cfg['N'] = 1000
        self.default_configurations['full_small_population'] = cfg
        
        # Random initial portfolio
        cfg = copy.deepcopy(full_base)
        cfg['description'] = 'All features ON + random initial portfolios'
        cfg['random_initial_portfolio'] = True
        self.default_configurations['full_inequal_start'] = cfg
    
    def add_custom_configuration(self, name, config_dict):
        """
        Add a custom configuration to the analysis
        
        Args:
            name: Name of the configuration
            config_dict: Dictionary containing configuration parameters
        """
        if name in self.all_configurations:
            print(f"Warning: Configuration '{name}' already exists. Overwriting.")
        
        # Ensure required fields are present
        required_fields = ['N', 'dimensions', 'description', 'mode']
        for field in required_fields:
            if field not in config_dict:
                raise ValueError(f"Custom configuration '{name}' missing required field: {field}")
        
        self.all_configurations[name] = config_dict
        self.configurations[name] = config_dict
        print(f"Added custom configuration: {name}")
    
    def select_configurations(self, config_names):
        """
        Select specific configurations to run
        
        Args:
            config_names: List of configuration names to run
        """
        self.configurations = {}
        for name in config_names:
            if name in self.all_configurations:
                self.configurations[name] = self.all_configurations[name]
            else:
                print(f"Warning: Configuration '{name}' not found. Available configs:")
                self.list_available_configurations()
                return
        
        print(f"Selected {len(self.configurations)} configurations for analysis")
    
    def select_all_configurations(self):
        """Select all available configurations"""
        self.configurations = self.all_configurations.copy()
        print(f"Selected all {len(self.configurations)} configurations for analysis")
    
    def list_available_configurations(self):
        """List all available configurations"""
        print("\nAvailable Configurations:")
        print("=" * 50)
        for i, (name, config) in enumerate(self.all_configurations.items()):
            print(f"{i+1:3d}. {name:30} - {config['description']}")
        print(f"\nTotal: {len(self.all_configurations)} configurations")
    
    def set_simulation_parameters(self, MaxRunTime=2000, batch_size=100, update_rate=1, plot_interval=50):
        """
        Set simulation parameters
        
        Args:
            MaxRunTime: Maximum simulation time in days
            batch_size: Batch size for simulation updates
            update_rate: Number of days per update
            plot_interval: Plot every N days
        """
        self.simulation_params = {
            'MaxRunTime': MaxRunTime,
            'batch_size': batch_size,
            'update_rate': update_rate,
            'plot_interval': plot_interval
        }
        print(f"Updated simulation parameters: {self.simulation_params}")
    
    def set_runs_per_config(self, runs):
        """
        Set number of runs per configuration
        
        Args:
            runs: Number of runs per configuration
        """
        self.runs_per_config = runs
        print(f"Set runs per configuration to: {runs}")
    
    def set_parallelism(self, n_jobs):
        """
        Set the number of parallel workers
        
        Args:
            n_jobs: Number of parallel jobs (-1 for all CPUs, 1 for sequential)
        """
        self.n_jobs = n_jobs
        print(f"Set parallelism to: {n_jobs} workers")
    
    def cleanup_plots(self):
        """Force cleanup of all matplotlib plots and figures"""
        try:
            plt.close('all')
            # Also try to clear any remaining references
            import gc
            gc.collect()
        except Exception as e:
            print(f"Warning: Error during plot cleanup: {e}")
        
    def run_single_simulation(self, config_name, config_params, run_number):
        """
        Run a single simulation with given configuration
        
        Args:
            config_name: Name of the configuration
            config_params: Configuration parameters
            run_number: Run number for this configuration
            
        Returns:
            Simulation object with results
        """
        print(f"Running {config_name} - Run {run_number + 1}/{self.runs_per_config}")
        
        # Create output directory for this specific run
        run_dir = self.base_output_dir / config_name / f"run_{run_number + 1:02d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize simulation object
        sim = None
        try:
            # Extract parameters
            N = config_params['N']
            dimensions = config_params['dimensions']
            c_leverage_factor = config_params.get('c_leverage_factor', 0.01)  # Default from TimeVectorSimulation
            
            # Determine which simulation class to use
            mode = config_params.get('mode', 'original')
            if mode == 'original':
                sim_class = TimeVectorSimulation
            elif mode == 'unleveraged':
                sim_class = TimeVectorSimulationUnleveraged
            elif mode == 'diminishing':
                sim_class = TimeVectorSimulationDiminishingReturns
            else:
                raise ValueError(f"Unknown simulation mode: {mode}")
            
            c_knowledge_xfer = config_params.get('c_knowledge_xfer', 0.05)
            enable_power_dynamics = config_params.get('enable_power_dynamics', False)
            c_power_factor = config_params.get('c_power_factor', 0.1)
            base_daily_decay_rate = config_params.get('base_daily_decay_rate', 0.01)
            decay_coeffs_map = config_params.get('decay_coeffs_map', None)
            
            sim = sim_class(
                data_folder=str(run_dir),
                N=N,
                dimensions=dimensions,
                use_gpu_if_available=True,
                log_to_disk=self.log_to_disk,
                c_knowledge_xfer=c_knowledge_xfer,
                enable_power_dynamics=enable_power_dynamics,
                c_power_factor=c_power_factor,
                base_daily_decay_rate=base_daily_decay_rate,
                decay_coeffs_map=decay_coeffs_map,
            )
            # Override leverage factor if specified
            sim.c_leverage_factor = c_leverage_factor
            # Run simulation
            sim.run_simulation_static(**self.simulation_params)

            # Save the final portfolios array for detailed scatter plot analysis later
            final_portfolios_path = run_dir / 'final_portfolios.joblib'
            joblib.dump({
                'portfolios': ensure_numpy(sim.Portfolios),
                'dimensions': sim.dimensions
            }, final_portfolios_path)

            # Save simulation object for later analysis
            joblib.dump(sim, run_dir / 'simulation.joblib')
            # Save per-run statistics
            gini_coeffs = sim.get_gini_coefficients()
            avg_leverage = float(sim.get_average_leverage())
            per_dim_means = {dim: float(sim.xp_module.mean(sim.get_dimension_data(dim))) for dim in sim.dimensions}
            stats = {
                'gini_coeffs': gini_coeffs,
                'avg_leverage': avg_leverage,
                'per_dim_means': per_dim_means,
                'time_series_data': {k: ensure_numpy(v) for k, v in sim.time_series_data.items()}
            }
            with open(run_dir / 'statistics.pkl', 'wb') as f:
                pickle.dump(stats, f)
            # Save all original analysis plots for this run
            self.save_all_run_plots(sim, run_dir)
            
        except Exception as e:
            print(f"Error in run_single_simulation for {config_name} run {run_number}: {e}")
            # Ensure plots are closed even if there's an error
            self.cleanup_plots()
            if sim is not None:
                try:
                    sim.close()
                except:
                    pass
            raise e
        finally:
            # ALWAYS close plots and simulation, no matter what happens
            self.cleanup_plots()
            if sim is not None:
                try:
                    sim.close()
                except:
                    pass
                    
        return sim
    
    def run_all_configurations(self):
        """
        Run all configurations multiple times in parallel (per configuration)
        """
        print("Starting multi-configuration analysis...")
        print(f"Total configurations: {len(self.configurations)}")
        print(f"Runs per configuration: {self.runs_per_config}")
        print(f"Total simulations: {len(self.configurations) * self.runs_per_config}")
        print(f"Parallel jobs per configuration: {self.n_jobs}")
        print("WARNING: If you have only one GPU, running many jobs in parallel may cause out-of-memory errors. Set n_jobs=1 if you want to run sequentially on a single GPU.")
        
        for config_name, config_params in self.configurations.items():
            print(f"\n{'='*60}")
            print(f"Running configuration: {config_name}")
            print(f"Description: {config_params['description']}")
            print(f"{'='*60}")
            
            # Ensure plots are closed before starting new configuration
            plt.close('all')
            
            # Parallelize runs for this configuration
            try:
                config_results = joblib.Parallel(n_jobs=self.n_jobs)(
                    joblib.delayed(self.run_single_simulation)(config_name, config_params, run_num)
                    for run_num in range(self.runs_per_config)
                )
                print(f"✓ All runs completed for {config_name}")
            except Exception as e:
                print(f"✗ Parallel execution failed for {config_name}: {e}")
                config_results = []
            finally:
                # ALWAYS clean up figures after each configuration, no matter what
                plt.close('all')
                
            self.results[config_name] = config_results
            print(f"Completed {len(config_results)} successful runs for {config_name}")
            
        print(f"\n{'='*60}")
        print("All simulations completed!")
        print(f"{'='*60}")
        
        # Final cleanup
        self.cleanup_plots()
    
    def calculate_summary_statistics(self):
        """
        Calculate summary statistics for all configurations, dynamically handling all dimensions.
        """
        print("Calculating summary statistics...")
        
        for config_name, config_runs in self.results.items():
            if not config_runs:
                continue
                
            print(f"Processing {config_name} ({len(config_runs)} runs)")
            
            # Use the first run to determine dimensions
            first_run = config_runs[0]
            dimensions = first_run.dimensions
            
            # Initialize collectors dynamically
            final_ginis = {dim: [] for dim in dimensions}
            final_ginis['total'] = []
            final_avgs = {dim: [] for dim in dimensions}
            final_avg_leverage = []
            
            for sim in config_runs:
                gini_coeffs = sim.get_gini_coefficients()
                final_ginis['total'].append(gini_coeffs.get('total', np.nan))
                final_avg_leverage.append(float(sim.get_average_leverage()))
                
                for dim_name in dimensions:
                    final_ginis[dim_name].append(gini_coeffs.get(dim_name, np.nan))
                    final_avgs[dim_name].append(float(sim.xp_module.mean(sim.get_dimension_data(dim_name))))
            
            # Calculate and store summary statistics
            self.summary_stats[config_name] = {}
            
            # Gini stats
            for dim_name, values in final_ginis.items():
                if values:
                    self.summary_stats[config_name][f'gini_{dim_name}'] = {
                        'mean': np.mean(values), 'std': np.std(values),
                        'min': np.min(values), 'max': np.max(values),
                        'values': values
                    }
            
            # Average value stats
            for dim_name, values in final_avgs.items():
                if values:
                    self.summary_stats[config_name][f'avg_{dim_name}'] = {
                        'mean': np.mean(values), 'std': np.std(values),
                        'min': np.min(values), 'max': np.max(values),
                        'values': values
                    }

            # Average leverage stats
            if final_avg_leverage:
                self.summary_stats[config_name]['avg_leverage'] = {
                    'mean': np.mean(final_avg_leverage), 'std': np.std(final_avg_leverage),
                    'min': np.min(final_avg_leverage), 'max': np.max(final_avg_leverage),
                    'values': final_avg_leverage
                }
    
    def create_comparison_plots(self):
        """
        Create comprehensive comparison plots
        """
        try:
            print("Creating comparison plots...")
            
            # Set up plotting style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Create plots directory
            plots_dir = self.base_output_dir / "comparison_plots"
            plots_dir.mkdir(exist_ok=True)
            
            # 1. Gini Coefficient Comparison
            self._plot_gini_comparison(plots_dir)
            
            # 2. Average Leverage Comparison
            self._plot_leverage_comparison(plots_dir)
            
            # 3. Average Values Comparison
            self._plot_average_values_comparison(plots_dir)
            
            # 4. Box plots for all metrics
            self._plot_box_plots(plots_dir)
            
            # 5. Time series comparison (using first run of each config)
            self._plot_time_series_comparison(plots_dir)
            
            # 6. Distribution comparison plots
            self._plot_distribution_comparisons(plots_dir)
            
            # 7. Scatter plot comparisons
            self._plot_scatter_comparisons(plots_dir)
            
            print(f"All comparison plots saved to: {plots_dir}")
            
        except Exception as e:
            print(f"Error in create_comparison_plots: {e}")
            self.cleanup_plots()
            raise e
        finally:
            # Always close plots after comparison plots
            self.cleanup_plots()
    
    def _plot_gini_comparison(self, plots_dir):
        """Plot Gini coefficient comparisons for all dimensions."""
        try:
            # Dynamically find all gini metrics collected
            sample_config = next(iter(self.summary_stats.values()), {})
            metrics = sorted([k for k in sample_config.keys() if k.startswith('gini_')])
            if not metrics:
                return
                
            titles = [m.replace('gini_', '').capitalize() + ' Gini' for m in metrics]
            
            # Determine subplot layout
            n_metrics = len(metrics)
            ncols = min(3, n_metrics)
            nrows = (n_metrics + ncols - 1) // ncols
            fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows), squeeze=False)
            axes = axes.flatten()
            
            for i, (metric, title) in enumerate(zip(metrics, titles)):
                ax = axes[i]
                
                config_names = []
                means = []
                stds = []
                
                for config_name, stats in self.summary_stats.items():
                    if metric in stats:
                        config_names.append(self.configurations[config_name]['description'])
                        means.append(stats[metric]['mean'])
                        stds.append(stats[metric]['std'])
                
                x_pos = np.arange(len(config_names))
                bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
                
                ax.set_title(title)
                ax.set_ylabel('Gini Coefficient')
                ax.set_xticks(x_pos)
                ax.set_xticklabels(config_names, rotation=45, ha='right')
                ax.grid(True, alpha=0.3)
                
                for bar, mean in zip(bars, means):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{mean:.3f}', ha='center', va='bottom', fontsize=8)
            
            # Hide unused subplots
            for j in range(i + 1, len(axes)):
                axes[j].set_visible(False)
                
            plt.tight_layout()
            plt.savefig(plots_dir / 'gini_comparison.png', dpi=300, bbox_inches='tight')
            plt.close()
        except Exception as e:
            print(f"Error in _plot_gini_comparison: {e}")
            self.cleanup_plots()
            raise e
        finally:
            self.cleanup_plots()
    
    def _plot_leverage_comparison(self, plots_dir):
        """Plot average leverage comparison"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        config_names = []
        means = []
        stds = []
        
        for config_name, stats in self.summary_stats.items():
            config_names.append(self.configurations[config_name]['description'])
            means.append(stats['avg_leverage']['mean'])
            stds.append(stats['avg_leverage']['std'])
        
        x_pos = np.arange(len(config_names))
        bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
        
        ax.set_title('Average Leverage Comparison Across Configurations')
        ax.set_ylabel('Average Leverage')
        ax.set_xlabel('Configuration')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(config_names, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for bar, mean in zip(bars, means):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{mean:.4f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(plots_dir / 'leverage_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_average_values_comparison(self, plots_dir):
        """Plot average capital comparisons for all dimensions."""
        
        # Dynamically find all avg metrics collected (excluding leverage)
        sample_config = next(iter(self.summary_stats.values()), {})
        metrics = sorted([k for k in sample_config.keys() if k.startswith('avg_') and k != 'avg_leverage'])
        if not metrics:
            return
            
        titles = [f"Average {m.replace('avg_', '').capitalize()} Capital" for m in metrics]
        
        # Determine subplot layout
        n_metrics = len(metrics)
        ncols = min(3, n_metrics)
        nrows = (n_metrics + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows), squeeze=False)
        axes = axes.flatten()
        
        for i, (metric, title) in enumerate(zip(metrics, titles)):
            ax = axes[i]
            
            config_names = []
            means = []
            stds = []
            
            for config_name, stats in self.summary_stats.items():
                if metric in stats:
                    config_names.append(self.configurations[config_name]['description'])
                    means.append(stats[metric]['mean'])
                    stds.append(stats[metric]['std'])
            
            x_pos = np.arange(len(config_names))
            bars = ax.bar(x_pos, means, yerr=stds, capsize=5, alpha=0.7)
            
            ax.set_title(title)
            ax.set_ylabel('Average Capital')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(config_names, rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            ax.set_yscale('log') # Useful if values vary widely
            
            for bar, mean in zip(bars, means):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{mean:.1f}', ha='center', va='bottom', fontsize=8)
        
        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        plt.savefig(plots_dir / 'average_values_comparison.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_box_plots(self, plots_dir):
        """Create box plots for all metrics"""
        metrics = ['gini_production', 'gini_knowledge', 'gini_total', 'avg_leverage', 'avg_production', 'avg_knowledge']
        metric_labels = ['Production Gini', 'Knowledge Gini', 'Total Gini', 'Avg Leverage', 'Avg Production', 'Avg Knowledge']
        
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        axes = axes.flatten()
        
        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[i]
            
            # Prepare data for box plot
            data = []
            labels = []
            
            for config_name, stats in self.summary_stats.items():
                if metric in stats:
                    data.append(stats[metric]['values'])
                    labels.append(self.configurations[config_name]['description'])
            
            # Create box plot
            bp = ax.boxplot(data, labels=labels, patch_artist=True)
            
            # Color the boxes
            colors = plt.cm.Set3(np.linspace(0, 1, len(bp['boxes'])))
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
            
            ax.set_title(label)
            ax.set_ylabel('Value')
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(plots_dir / 'box_plots.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_time_series_comparison(self, plots_dir):
        """Plot time series comparison using first run of each configuration."""
        
        # --- Plot 1: Average Leverage ---
        fig, ax1 = plt.subplots(figsize=(10, 7))
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]  # Use first run
                if sim.time_series_data['t']:
                    ax1.plot(sim.time_series_data['t'], sim.time_series_data['avg_leverage'], 
                            label=self.configurations[config_name]['description'], linewidth=2)
        ax1.set_title('Average Leverage Over Time')
        ax1.set_xlabel('Time (days)')
        ax1.set_ylabel('Average Leverage')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(plots_dir / 'time_series_leverage_comparison.png', dpi=300, bbox_inches='tight')
        plt.close(fig)

        # --- Plot 2: Gini Coefficients ---
        # Find all gini time series available from the first run of the first config
        first_sim = next((r[0] for r in self.results.values() if r), None)
        if not first_sim:
            return
        
        gini_metrics = sorted([k for k in first_sim.time_series_data.keys() if k.startswith('gini_')])
        n_metrics = len(gini_metrics)
        if n_metrics == 0:
            return

        ncols = min(3, n_metrics)
        nrows = (n_metrics + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(7 * ncols, 5 * nrows), squeeze=False)
        axes = axes.flatten()

        for i, metric in enumerate(gini_metrics):
            ax = axes[i]
            title = f"{metric.replace('gini_', '').capitalize()} Gini Over Time"
            for config_name, config_runs in self.results.items():
                if config_runs:
                    sim = config_runs[0]
                    if sim.time_series_data['t'] and metric in sim.time_series_data:
                        ax.plot(sim.time_series_data['t'], sim.time_series_data[metric], 
                                label=self.configurations[config_name]['description'], linewidth=2)
            ax.set_title(title)
            ax.set_xlabel('Time (days)')
            ax.set_ylabel('Gini Coefficient')
            ax.legend(fontsize='small')
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        plt.tight_layout()
        plt.savefig(plots_dir / 'time_series_gini_comparison.png', dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def _plot_distribution_comparisons(self, plots_dir):
        """Plot distribution comparisons using first run of each configuration"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        
        # Plot production distributions
        ax1 = axes[0, 0]
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]
                if 'production' in sim.dimensions:
                    sim.plot_dimension_distribution_on_axes('production', ax1)
                    ax1.set_title('Production Distribution Comparison')
                    break  # Only plot one for this subplot
        
        # Plot knowledge distributions
        ax2 = axes[0, 1]
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]
                if 'knowledge' in sim.dimensions:
                    sim.plot_dimension_distribution_on_axes('knowledge', ax2)
                    ax2.set_title('Knowledge Distribution Comparison')
                    break
        
        # Plot total wealth distributions
        ax3 = axes[0, 2]
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]
                # Temporarily set AgentWealth to total wealth
                original_wealth = sim.AgentWealth
                sim.AgentWealth = sim.xp_module.sum(sim.Portfolios, axis=1)
                
                # Get distribution data
                (x, y), (X_fit, Y_fit) = compute_wealth_distribution(
                    data=sim.AgentWealth,
                    fit_mode=sim.fit_mode,
                    bins=50,
                    current_xp_module=sim.xp_module
                )
                
                if x is not None and y is not None:
                    ax3.plot(x, y, 'bo-', label='Empirical', markersize=3)
                    if X_fit is not None and Y_fit is not None:
                        ax3.plot(X_fit, Y_fit, 'r--', label=f'{sim.fit_mode} fit', linewidth=2)
                    ax3.set_title("Total Wealth Distribution")
                    ax3.set_xlabel("Total Wealth")
                    ax3.set_ylabel("Probability Density / CCDF")
                    
                    if sim.fit_mode == 'powerlaw':
                        ax3.set_xscale('log')
                        ax3.set_yscale('log')
                    else:
                        ax3.set_xscale('linear')
                        ax3.set_yscale('linear')
                    
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
                
                # Restore original wealth
                sim.AgentWealth = original_wealth
                break
        
        # Create combined distribution plots for all configs
        ax4 = axes[1, 0]
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]
                if 'production' in sim.dimensions:
                    prod_data = sim.get_dimension_data('production')
                    prod_data_np = sim.xp_module.asnumpy(prod_data) if hasattr(sim.xp_module, 'asnumpy') else prod_data
                    # Filter out infinite and NaN values
                    prod_data_clean = prod_data_np[np.isfinite(prod_data_np)]
                    if len(prod_data_clean) > 0:
                        ax4.hist(prod_data_clean, bins=50, alpha=0.5, 
                                label=self.configurations[config_name]['description'], density=True)
        ax4.set_title('Production Distribution Comparison (All Configs)')
        ax4.set_xlabel('Production Capital')
        ax4.set_ylabel('Density')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        ax5 = axes[1, 1]
        for config_name, config_runs in self.results.items():
            if config_runs:
                sim = config_runs[0]
                if 'knowledge' in sim.dimensions:
                    know_data = sim.get_dimension_data('knowledge')
                    know_data_np = sim.xp_module.asnumpy(know_data) if hasattr(sim.xp_module, 'asnumpy') else know_data
                    # Filter out infinite and NaN values
                    know_data_clean = know_data_np[np.isfinite(know_data_np)]
                    if len(know_data_clean) > 0:
                        ax5.hist(know_data_clean, bins=50, alpha=0.5, 
                                label=self.configurations[config_name]['description'], density=True)
        ax5.set_title('Knowledge Distribution Comparison (All Configs)')
        ax5.set_xlabel('Knowledge Capital')
        ax5.set_ylabel('Density')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # Leave last subplot empty for now
        axes[1, 2].text(0.5, 0.5, 'Additional Analysis\nSpace', 
                        transform=axes[1, 2].transAxes, ha='center', va='center')
        axes[1, 2].set_title('Additional Analysis')
        
        plt.tight_layout()
        plt.savefig(plots_dir / 'distribution_comparisons.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def _plot_scatter_comparisons(self, plots_dir):
        """Plot scatter plot comparisons"""
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        
        # Create scatter plots for each configuration
        for i, (config_name, config_runs) in enumerate(self.results.items()):
            if i >= 6:  # Limit to 6 subplots
                break
                
            if config_runs:
                sim = config_runs[0]  # Use first run
                ax = axes[i // 3, i % 3]
                
                try:
                    if 'knowledge' in sim.dimensions and 'production' in sim.dimensions:
                        x = sim.xp_module.asnumpy(sim.Portfolios[:, sim.dimensions.index('knowledge')])
                        y = sim.xp_module.asnumpy(sim.Portfolios[:, sim.dimensions.index('production')])
                        
                        ax.scatter(x, y, alpha=0.6, s=20)
                        ax.set_xlabel('Knowledge Capital')
                        ax.set_ylabel('Production Capital')
                        ax.set_title(f'{self.configurations[config_name]["description"]}\nKnowledge vs Production')
                        ax.grid(True, alpha=0.3)
                        
                        # Use log scale for better visualization
                        ax.set_xscale('log')
                        ax.set_yscale('log')
                        
                        # Add statistics
                        avg_knowledge = np.mean(x)
                        avg_production = np.mean(y)
                        ax.text(0.02, 0.98, f'Avg K: {avg_knowledge:.2f}\nAvg P: {avg_production:.2f}', 
                                transform=ax.transAxes, verticalalignment='top',
                                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error: {str(e)}', 
                           transform=ax.transAxes, ha='center', va='center')
                    ax.set_title(f'{self.configurations[config_name]["description"]}\n(Error)')
        
        plt.tight_layout()
        plt.savefig(plots_dir / 'scatter_comparisons.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    def save_summary_report(self):
        """Save a comprehensive summary report"""
        report_file = self.base_output_dir / "summary_report.txt"
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("MULTI-CONFIGURATION TIMEVECTOR SIMULATION ANALYSIS REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total configurations: {len(self.configurations)}\n")
            f.write(f"Runs per configuration: {self.runs_per_config}\n")
            f.write(f"Total simulations: {len(self.configurations) * self.runs_per_config}\n\n")
            
            f.write("CONFIGURATION DETAILS:\n")
            f.write("-"*50 + "\n")
            for config_name, config_params in self.configurations.items():
                f.write(f"{config_name}:\n")
                f.write(f"  Description: {config_params['description']}\n")
                f.write(f"  N: {config_params['N']}\n")
                f.write(f"  Dimensions: {config_params['dimensions']}\n")
                if 'c_leverage_factor' in config_params:
                    f.write(f"  Leverage Factor: {config_params['c_leverage_factor']}\n")
                f.write("\n")
            
            f.write("SUMMARY STATISTICS:\n")
            f.write("-"*50 + "\n")
            for config_name, stats in self.summary_stats.items():
                f.write(f"\n{self.configurations[config_name]['description']}:\n")
                f.write(f"  Successful runs: {len(stats['gini_total']['values'])}\n")
                
                for metric, metric_stats in stats.items():
                    if 'values' in metric_stats and len(metric_stats['values']) > 0:
                        f.write(f"  {metric}:\n")
                        f.write(f"    Mean: {metric_stats['mean']:.4f}\n")
                        f.write(f"    Std:  {metric_stats['std']:.4f}\n")
                        f.write(f"    Min:  {metric_stats['min']:.4f}\n")
                        f.write(f"    Max:  {metric_stats['max']:.4f}\n")
                f.write("\n")
        
        print(f"Summary report saved to: {report_file}")
    
    def run_complete_analysis(self):
        """
        Run the complete multi-configuration analysis
        """
        try:
            print("Starting complete multi-configuration analysis...")
            print(f"Output directory: {self.base_output_dir}")
            
            # Step 1: Run all simulations
            self.run_all_configurations()
            
            # Step 2: Calculate summary statistics
            self.calculate_summary_statistics()
            
            # Step 3: Create comparison plots
            self.create_comparison_plots()
            
            # Step 4: Save summary report
            self.save_summary_report()
            
            print(f"\n{'='*80}")
            print("ANALYSIS COMPLETE!")
            print(f"{'='*80}")
            print(f"Results saved to: {self.base_output_dir}")
            print(f"Comparison plots: {self.base_output_dir}/comparison_plots/")
            print(f"Summary report: {self.base_output_dir}/summary_report.txt")
            print(f"{'='*80}")
            
        except Exception as e:
            print(f"Error in run_complete_analysis: {e}")
            raise e
        finally:
            # ALWAYS clean up all matplotlib figures at the very end
            self.cleanup_plots()

    def save_all_run_plots(self, sim, run_dir):
        """
        Save all original TimeVectorSimulation analysis plots for a single run to run_dir.
        """
        import itertools
        import os
        
        try:
            dims_no_pleasure = [d for d in sim.dimensions if d != 'pleasure']
            # 1. Distribution for each dimension except 'pleasure'
            for dim_name in dims_no_pleasure:
                try:
                    fig, ax = plt.subplots(figsize=(7, 5))
                    plotter.plot_dimension_distribution_on_axes(sim, dim_name, ax)
                    fig.tight_layout()
                    fig.savefig(os.path.join(run_dir, f'distribution_{dim_name}.png'))
                    plt.close(fig)
                except Exception as e:
                    print(f"Error plotting distribution for {dim_name}: {e}")
                    plt.close('all')
                    
            # 2. Dedicated pleasure plot if present
            if 'pleasure' in sim.dimensions:
                try:
                    fig = plotter.plot_pleasure_distribution(sim)
                    fig.savefig(os.path.join(run_dir, 'distribution_pleasure.png'))
                    plt.close(fig)
                except Exception as e:
                    print(f"Error plotting pleasure distribution: {e}")
                    plt.close('all')
                    
            # 3. Generalized scatter grid for all pairs (including pleasure)
            dims_all = list(sim.dimensions)
            scatter_pairs = list(itertools.combinations(dims_all, 2))
            for dim_x, dim_y in scatter_pairs:
                try:
                    fig, ax = plt.subplots(figsize=(7, 5))
                    x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dim_x)])
                    y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dim_y)])
                    ax.scatter(x, y, alpha=0.6, s=10)
                    ax.set_xlabel(f'{dim_x.capitalize()}')
                    ax.set_ylabel(f'{dim_y.capitalize()}')
                    ax.set_title(f'{dim_x.capitalize()} vs {dim_y.capitalize()}')
                    ax.grid(True, alpha=0.3)
                    ax.set_xscale('log')
                    ax.set_yscale('log')
                    fig.tight_layout()
                    fig.savefig(os.path.join(run_dir, f'scatter_{dim_x}_vs_{dim_y}.png'))
                    plt.close(fig)
                except Exception as e:
                    print(f"Error plotting scatter {dim_x} vs {dim_y}: {e}")
                    plt.close('all')
                    
            # 4. Time series plots
            if sim.time_series_data['t']:
                # Average leverage over time
                try:
                    fig, ax = plt.subplots(figsize=(7, 5))
                    ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data['avg_leverage']), 'b-')
                    ax.set_title('Average Leverage Over Time')
                    ax.set_xlabel('Time (days)')
                    ax.set_ylabel('Average Leverage')
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    fig.savefig(os.path.join(run_dir, 'timeseries_avg_leverage.png'))
                    plt.close(fig)
                except Exception as e:
                    print(f"Error plotting average leverage time series: {e}")
                    plt.close('all')
                    
                # Gini coefficients over time
                try:
                    fig, ax = plt.subplots(figsize=(7, 5))
                    for dim_name in sim.dimensions:
                        if f'gini_{dim_name}' in sim.time_series_data:
                            ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data[f'gini_{dim_name}']), label=dim_name.capitalize())
                    if 'gini_total' in sim.time_series_data:
                        ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data['gini_total']), label='Total', linestyle='--')
                    ax.set_title('Gini Coefficients Over Time')
                    ax.set_xlabel('Time (days)')
                    ax.set_ylabel('Gini Coefficient')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    fig.savefig(os.path.join(run_dir, 'timeseries_gini_coeffs.png'))
                    plt.close(fig)
                except Exception as e:
                    print(f"Error plotting gini coefficients time series: {e}")
                    plt.close('all')
                    
        except Exception as e:
            print(f"Error in save_all_run_plots: {e}")
            self.cleanup_plots()
        finally:
            # ALWAYS close all plots at the end
            self.cleanup_plots()


def main():
    """Main function to run the analysis with flexible configuration selection"""
    global _analysis_instance
    analysis = None
    try:
        # Create analysis instance with default 4 workers
        analysis = MultiConfigAnalysis(n_jobs=4)
        _analysis_instance = analysis  # Set global reference for signal handler
        
        # List all available configurations
        analysis.list_available_configurations()
        
        # Example: Run only a few specific configurations
        # You can modify this list to run different configurations
        selected_configs = [
            'power_dynamics',
            'FULL',
            'full_power_factor_0_05'
        ]
        
        print(f"\nRunning selected configurations: {selected_configs}")
        analysis.select_configurations(selected_configs)
        
        # Or run all configurations (uncomment the line below)
        # analysis.select_all_configurations()
        
        # Optional: Adjust simulation parameters
        # analysis.set_simulation_parameters(MaxRunTime=1000, batch_size=50, update_rate=1, plot_interval=25)
        
        # Optional: Adjust number of runs per configuration
        # analysis.set_runs_per_config(5)
        
        # Optional: Adjust parallelism
        # analysis.set_parallelism(2)
        
        # Run complete analysis for selected configs
        analysis.run_complete_analysis()
        
    except Exception as e:
        print(f"Fatal error in main: {e}")
        raise e
    finally:
        # ALWAYS close all plots at the very end, no matter what
        if analysis is not None:
            analysis.cleanup_plots()
        _analysis_instance = None  # Clear global reference
        plt.close('all')


if __name__ == "__main__":
    main() 