
"""
Targeted Comparison Plotter for TimeVectorSimulation Results

This script loads pre-computed simulation results from the `multi_config_results`
directory and generates specific, targeted comparison plots as requested.
"""

import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='seaborn')

# --- Configuration Section ---

# Import the configurations dictionary from multi_config_analysis
from .multi_config_analysis import MultiConfigAnalysis

# Get the FULL configurations dictionary (not the filtered subset)
temp_analyzer = MultiConfigAnalysis()
ALL_CONFIGURATIONS = temp_analyzer.all_configurations


class TargetedAnalysis:
    """
    Loads simulation results and creates specific comparison plots.
    """
    def __init__(self, results_dir="multi_config_results"):
        # Use the provided results_dir parameter (relative to current working directory)
        self.results_dir = Path(results_dir)
        if not self.results_dir.exists():
            raise FileNotFoundError(f"Results directory not found: {self.results_dir}")

        self.output_dir = self.results_dir / "targeted_comparison_plots"
        self.output_dir.mkdir(exist_ok=True)
        print(f"Saving plots to: {self.output_dir}")

        self.summary_df = None
        self.timeseries_df = None

        # Define the specific comparison groups based on your request
        self.comparison_groups = {
            'population_size': ['small_population', 'large_population'],
            'knowledge_modes': ['large_population', 'unleveraged_knowledge', 'diminishing_knowledge'],
            'diminishing_vs_sharing': ['diminishing_knowledge', 'diminishing_limited_sharing'],
            'power_vs_original': ['large_population', 'power_dynamics'],
            'feature_stack': ['power_dynamics', 'power_and_sharing', 'power_and_sharing_decay', 'power_sharing_risk', 'power_sharing_risk_art'],
            'art_vs_pleasure': ['power_sharing_risk_art', 'power_sharing_risk_art_pleasure'],
            'pleasure_vs_full': ['power_sharing_risk_art_pleasure', 'FULL'],
            'full pop sizes': ['full_small_population', 'full_large_population', 'FULL'],
        }

        # Define sweep comparisons relative to the 'FULL' baseline
        self.sweep_groups = {
            'power_factor_sweep': {
                'configs': ['full_power_factor_0_01', 'full_power_factor_0_03', 'full_power_factor_0_05', 'full_power_factor_0_07', 'full_power_factor_0_09', 'FULL'],
                'param': 'c_power_factor',
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('c_power_factor', 'N/A')
            },
            'knowledge_xfer_sweep': {
                'configs': ['full_knowledge_xfer_0_02', 'FULL', 'full_knowledge_xfer_0_10', 'full_knowledge_xfer_0_15', 'full_knowledge_xfer_0_20'],
                'param': 'c_knowledge_xfer',
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('c_knowledge_xfer', 'N/A')
            },
            'savings_sweep': {
                'configs': ['full_saving_0_01', 'FULL', 'full_saving_0_10', 'full_saving_0_20', 'full_saving_0_30'],
                'param': 'savings_mean',
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('savings_mean', 'N/A')
            },
            'risk_sweep': {
                'configs': ['full_risk_0_01', 'full_risk_0_05', 'FULL', 'full_risk_0_20', 'full_risk_0_30'],
                'param': 'risk_mean',
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('risk_mean', 'N/A')
            },
            'power_decay_sweep': {
                'configs': ['full_decay_power_1_0', 'full_decay_power_2_0', 'FULL', 'full_decay_power_10_0', 'full_decay_power_20_0'],
                'param': "decay_coeffs_map['power']",
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('decay_coeffs_map', {}).get('power', 'N/A')
            },
            'pleasure_decay_sweep': {
                'configs': ['full_decay_pleasure_0_1', 'full_decay_pleasure_0_5', 'full_decay_pleasure_1_0', 'full_decay_pleasure_3_0', 'FULL'],
                'param': "decay_coeffs_map['pleasure']",
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('decay_coeffs_map', {}).get('pleasure', 'N/A')
            },
            'focus_noise_sweep': {
                'configs': ['full_noise_0_01', 'full_noise_0_03', 'FULL', 'full_noise_0_10', 'full_noise_0_20'],
                'param': 'focus_noise_level',
                'baseline_val': ALL_CONFIGURATIONS['FULL'].get('focus_noise_level', 'N/A')
            },
        }

    def load_data(self):
        """Load all statistics.pkl files into pandas DataFrames."""
        all_summaries = []
        all_timeseries = []

        print("Loading data from result directories...")
        found_configs = set()
        for pkl_path in self.results_dir.glob('**/statistics.pkl'):
            config_name = pkl_path.parts[-3]
            run_name = pkl_path.parts[-2]
            found_configs.add(config_name)

            if config_name not in ALL_CONFIGURATIONS:
                continue

            with open(pkl_path, 'rb') as f:
                stats = pickle.load(f)

            # Process summary stats (final values)
            for metric, value in stats['gini_coeffs'].items():
                all_summaries.append({'config_name': config_name, 'run': run_name, 'metric': f'gini_{metric}', 'value': value})
            all_summaries.append({'config_name': config_name, 'run': run_name, 'metric': 'avg_leverage', 'value': stats['avg_leverage']})
            for dim, value in stats['per_dim_means'].items():
                all_summaries.append({'config_name': config_name, 'run': run_name, 'metric': f'avg_{dim}', 'value': value})

            # Process time series data
            ts_data = stats['time_series_data']
            if ts_data and len(ts_data['t']) > 0:
                df = pd.DataFrame(ts_data)
                df['config_name'] = config_name
                df['run'] = run_name
                df_long = df.melt(id_vars=['config_name', 'run', 't'], var_name='metric', value_name='value')
                all_timeseries.append(df_long)

        if not all_summaries:
            raise ValueError("No summary statistics found. Did the simulations run correctly?")
        
        self.summary_df = pd.DataFrame(all_summaries)
        self.timeseries_df = pd.concat(all_timeseries, ignore_index=True)

        # Add readable descriptions for plotting
        desc_map = {k: v['description'] for k, v in ALL_CONFIGURATIONS.items()}
        self.summary_df['description'] = self.summary_df['config_name'].map(desc_map)
        self.timeseries_df['description'] = self.timeseries_df['config_name'].map(desc_map)
        
        print("Data loading complete.")

    def _plot_group(self, group_name, df_summary, df_timeseries):
        """Generic plotting function for a comparison group."""
        group_output_dir = self.output_dir / group_name
        group_output_dir.mkdir(exist_ok=True)

        # --- Plot 1: Boxplots of final summary metrics ---
        metrics_to_plot = sorted(df_summary['metric'].unique())
        n_metrics = len(metrics_to_plot)
        ncols = 3
        nrows = (n_metrics + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, nrows * 5), squeeze=False)
        axes = axes.flatten()

        for i, metric in enumerate(metrics_to_plot):
            ax = axes[i]
            metric_df = df_summary[df_summary['metric'] == metric]
            sns.boxplot(data=metric_df, x='description', y='value', ax=ax)
            ax.set_title(f'Final {metric.replace("_", " ").title()}')
            ax.set_xlabel('')
            ax.set_ylabel('Value')
            ax.tick_params(axis='x', rotation=45)
            plt.setp(ax.get_xticklabels(), ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

        for j in range(i + 1, len(axes)):
            axes[j].set_visible(False)

        fig.suptitle(f'Comparison: {group_name.replace("_", " ").title()}', fontsize=16, y=1.02)
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(group_output_dir / 'summary_boxplots.png', dpi=150)
        plt.close(fig)

        # --- Plot 2: Time series comparison ---
        ts_metrics = sorted(df_timeseries['metric'].unique())
        n_ts_metrics = len(ts_metrics)
        ncols_ts = 2
        nrows_ts = (n_ts_metrics + ncols_ts - 1) // ncols_ts
        fig_ts, axes_ts = plt.subplots(nrows_ts, ncols_ts, figsize=(ncols_ts * 8, nrows_ts * 5), squeeze=False, sharex=True)
        axes_ts = axes_ts.flatten()

        for i, metric in enumerate(ts_metrics):
            ax = axes_ts[i]
            metric_df = df_timeseries[df_timeseries['metric'] == metric]
            sns.lineplot(data=metric_df, x='t', y='value', hue='description', ax=ax, errorbar='sd')
            ax.set_title(f'{metric.replace("_", " ").title()} Over Time')
            ax.set_xlabel('Time (days)')
            ax.set_ylabel('Value')
            ax.legend(title='Configuration')
            ax.grid(True, linestyle='--', alpha=0.7)

        for j in range(i + 1, len(axes_ts)):
            axes_ts[j].set_visible(False)
            
        fig_ts.suptitle(f'Time Series Comparison: {group_name.replace("_", " ").title()}', fontsize=16, y=1.02)
        plt.tight_layout(rect=[0, 0, 1, 0.98])
        plt.savefig(group_output_dir / 'timeseries_comparison.png', dpi=150)
        plt.close(fig_ts)
        print(f"  -> Plots for '{group_name}' saved.")

    def generate_all_plots(self):
        """Generate all defined comparison plots."""
        if self.summary_df is None or self.timeseries_df is None:
            print("Data not loaded. Call load_data() first.")
            return

        # Generate plots for standard comparison groups
        for group_name, config_list in self.comparison_groups.items():
            df_s = self.summary_df[self.summary_df['config_name'].isin(config_list)]
            df_t = self.timeseries_df[self.timeseries_df['config_name'].isin(config_list)]
            if df_s.empty or df_t.empty:
                print(f"  -> Skipping '{group_name}', no data found for specified configs.")
                continue
            self._plot_group(group_name, df_s, df_t)
            
        # Generate plots for sweep groups
        for group_name, group_info in self.sweep_groups.items():
            config_list = group_info['configs']
            df_s = self.summary_df[self.summary_df['config_name'].isin(config_list)]
            df_t = self.timeseries_df[self.timeseries_df['config_name'].isin(config_list)]
            if df_s.empty or df_t.empty:
                print(f"  -> Skipping '{group_name}', no data found for specified configs.")
                continue

            # Override the plot function to add baseline info
            # We can do this by modifying the title of the generic plot
            def _plot_sweep_group(gn, dfs, dft):
                original_title = f'Comparison: {gn.replace("_", " ").title()}'
                sweep_title = f"{original_title}\n(Baseline '{group_info['param']}': {group_info['baseline_val']})"
                
                # Re-run the generic plot function but with a modified group name for the title
                self._plot_group(gn, dfs, dft)
                # This is a simple approach. A more complex one would pass the title to _plot_group.
                # For now, let's just print the context.
                print(f"  Plotting sweep '{gn}' with baseline '{group_info['param']}': {group_info['baseline_val']}")

            _plot_sweep_group(group_name, df_s, df_t)
            
        print("\nAll targeted plots generated successfully.")


if __name__ == "__main__":
    try:
        # Use default results directory in current working directory
        plotter = TargetedAnalysis(results_dir="multi_config_results")
        plotter.load_data()
        plotter.generate_all_plots()
    except (FileNotFoundError, ValueError) as e:
        print(f"\nERROR: Could not run analysis. {e}")
        print("Please ensure you have run 'multi_config_analysis.py' first and that the 'multi_config_results' directory exists.")