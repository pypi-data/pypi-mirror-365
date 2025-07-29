import numpy as np
import matplotlib.pyplot as plt
from .base import compute_wealth_distribution, ensure_numpy
try:
    from scipy.stats import norm, lognorm
    _has_scipy = True
except ImportError:
    _has_scipy = False

def plot_scatter_knowledge_vs_production(sim, figsize=(10, 8)):
    if 'knowledge' not in sim.dimensions or 'production' not in sim.dimensions:
        raise ValueError("Both 'knowledge' and 'production' dimensions required for scatter plot")
    x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('knowledge')])
    y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('production')])
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, alpha=0.6, s=20)
    ax.set_xlabel('Knowledge Capital')
    ax.set_ylabel('Production Capital')
    ax.set_title(f'Knowledge vs Production Distribution (t={sim.t}, N={sim.N})')
    ax.grid(True, alpha=0.3)
    avg_knowledge = np.mean(x)
    avg_production = np.mean(y)
    ax.text(0.02, 0.98, f'Avg Knowledge: {avg_knowledge:.2f}\nAvg Production: {avg_production:.2f}', 
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    return fig

def plot_scatter_power_vs_knowledge(sim, figsize=(10, 8), ax=None):
    if 'power' not in sim.dimensions or 'knowledge' not in sim.dimensions:
        raise ValueError("Both 'power' and 'knowledge' dimensions required for scatter plot")
    x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('power')])
    y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('knowledge')])
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, alpha=0.6, s=20)
    ax.set_xlabel('Power Capital')
    ax.set_ylabel('Knowledge Capital')
    ax.set_title(f'Power vs Knowledge Distribution (t={sim.t}, N={sim.N})')
    ax.grid(True, alpha=0.3)
    avg_power = np.mean(x)
    avg_knowledge = np.mean(y)
    ax.text(0.02, 0.98, f'Avg Power: {avg_power:.2f}\nAvg Knowledge: {avg_knowledge:.2f}', 
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    if ax is None:
        return fig
    else:
        return ax

def plot_scatter_power_vs_production(sim, figsize=(10, 8), ax=None):
    if 'power' not in sim.dimensions or 'production' not in sim.dimensions:
        raise ValueError("Both 'power' and 'production' dimensions required for scatter plot")
    x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('power')])
    y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index('production')])
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(x, y, alpha=0.6, s=20)
    ax.set_xlabel('Power Capital')
    ax.set_ylabel('Production Capital')
    ax.set_title(f'Power vs Production Distribution (t={sim.t}, N={sim.N})')
    ax.grid(True, alpha=0.3)
    avg_power = np.mean(x)
    avg_production = np.mean(y)
    ax.text(0.02, 0.98, f'Avg Power: {avg_power:.2f}\nAvg Production: {avg_production:.2f}', 
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    if ax is None:
        return fig
    else:
        return ax

def plot_time_series(sim, figsize=(15, 10)):
    if not sim.time_series_data['t']:
        raise ValueError("No time series data available. Run simulation first.")
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes[0, 0].plot(sim.time_series_data['t'], sim.time_series_data['avg_leverage'], 'b-')
    axes[0, 0].set_title('Average Leverage Over Time')
    axes[0, 0].set_xlabel('Time (days)')
    axes[0, 0].set_ylabel('Average Leverage')
    axes[0, 0].grid(True, alpha=0.3)
    for dim_name in sim.dimensions:
        if f'gini_{dim_name}' in sim.time_series_data:
            axes[0, 1].plot(sim.time_series_data['t'], sim.time_series_data[f'gini_{dim_name}'], 
                           label=dim_name.capitalize())
    if 'gini_total' in sim.time_series_data:
        axes[0, 1].plot(sim.time_series_data['t'], sim.time_series_data['gini_total'], 
                       label='Total', linestyle='--')
    axes[0, 1].set_title('Gini Coefficients Over Time')
    axes[0, 1].set_xlabel('Time (days)')
    axes[0, 1].set_ylabel('Gini Coefficient')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)
    if 'production' in sim.dimensions:
        from .time_vector_simulation import TimeVectorSimulation
        sim_temp = TimeVectorSimulation.__new__(TimeVectorSimulation)
        sim_temp.Portfolios = sim.Portfolios
        sim_temp.dimensions = sim.dimensions
        sim_temp.t = sim.t
        sim_temp.N = sim.N
        sim_temp.fit_mode = sim.fit_mode
        sim_temp.xp_module = sim.xp_module
        axes[1, 0].set_title('Current Production Distribution')
        plot_dimension_distribution(sim_temp, 'production', static_plot=True, ax=axes[1, 0])
        axes[1, 0].set_xlabel('Production Capital')
        axes[1, 0].set_ylabel('Probability Density')
        if 'knowledge' in sim.dimensions:
            axes[1, 1].set_title('Current Knowledge Distribution')
            plot_dimension_distribution(sim_temp, 'knowledge', static_plot=True, ax=axes[1, 1])
            axes[1, 1].set_xlabel('Knowledge Capital')
            axes[1, 1].set_ylabel('Probability Density')
    plt.tight_layout()
    return fig

def plot_dimension_distribution(sim, dimension_name, static_plot=False, ax=None):
    if dimension_name == 'pleasure':
        # Exclude pleasure from general distribution plot
        return
    dim_data = ensure_numpy(sim.get_dimension_data(dimension_name))
    (x, y), (X_fit, Y_fit) = compute_wealth_distribution(
        data=dim_data,
        fit_mode=sim.fit_mode,
        bins=50,
        current_xp_module=sim.xp_module
    )
    if ax is None and hasattr(sim, 'ax'):
        ax = sim.ax
    if x is not None and y is not None:
        if static_plot:
            ax.clear()
            ax.plot(x, y, 'bo-', label='Empirical')
            if X_fit is not None and Y_fit is not None:
                ax.plot(X_fit, Y_fit, 'r--', label=f'{sim.fit_mode} fit')
            # --- Gaussian overlay ---
            mu = float(np.mean(dim_data))
            sigma = float(np.std(dim_data))
            if sigma > 0:
                x_gauss = np.linspace(np.min(ensure_numpy(x)), np.max(ensure_numpy(x)), 200)
                if _has_scipy:
                    y_gauss = norm.pdf(x_gauss, mu, sigma)
                else:
                    y_gauss = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_gauss - mu)/sigma)**2)
                y_gauss = y_gauss / np.sum(y_gauss) * np.sum(y)  # scale to empirical
                ax.plot(x_gauss, y_gauss, 'g-', label='Gaussian')
            # --- Log-Gaussian overlay ---
            log_data = np.log(dim_data[dim_data > 0])
            if len(log_data) > 1:
                mu_log = float(np.mean(log_data))
                sigma_log = float(np.std(log_data))
                x_log = ensure_numpy(x[x > 0]) if np.any(x > 0) else np.linspace(1e-3, np.max(ensure_numpy(x)), 200)
                if _has_scipy:
                    s = sigma_log
                    scale = np.exp(mu_log)
                    y_log_gauss = lognorm.pdf(x_log, s=s, scale=scale)
                else:
                    y_log_gauss = (1/(x_log * sigma_log * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(x_log) - mu_log)/sigma_log)**2)
                y_log_gauss = y_log_gauss / np.sum(y_log_gauss) * np.sum(y[x > 0])
                ax.plot(x_log, y_log_gauss, 'm-', label='Log-Gaussian')
            ax.set_title(f"{dimension_name.capitalize()} Distribution at t={sim.t} (N={sim.N})")
            ax.set_xlabel(dimension_name.capitalize())
            ax.set_ylabel("Probability Density / CCDF")
            if sim.fit_mode == 'powerlaw':
                ax.set_xscale('log')
                ax.set_yscale('log')
            else:
                ax.set_xscale('linear')
                ax.set_yscale('linear')
            ax.legend()
        else:
            if sim.line_data is None or sim.line_fit is None:
                sim.line_data, = ax.plot([], [], 'bo-', label='Empirical')
                sim.line_fit, = ax.plot([], [], 'r--', label=f'{sim.fit_mode} fit')
                ax.legend()
            sim.line_data.set_data(x, y)
            if X_fit is not None and Y_fit is not None:
                sim.line_fit.set_data(X_fit, Y_fit)
            else:
                sim.line_fit.set_data([], [])
            # Overlay Gaussian and log-Gaussian for dynamic plots as well
            mu = float(np.mean(dim_data))
            sigma = float(np.std(dim_data))
            if sigma > 0:
                x_gauss = np.linspace(np.min(ensure_numpy(x)), np.max(ensure_numpy(x)), 200)
                if _has_scipy:
                    y_gauss = norm.pdf(x_gauss, mu, sigma)
                else:
                    y_gauss = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_gauss - mu)/sigma)**2)
                y_gauss = y_gauss / np.sum(y_gauss) * np.sum(y)
                ax.plot(x_gauss, y_gauss, 'g-', label='Gaussian')
            log_data = np.log(dim_data[dim_data > 0])
            if len(log_data) > 1:
                mu_log = float(np.mean(log_data))
                sigma_log = float(np.std(log_data))
                x_log = ensure_numpy(x[x > 0]) if np.any(x > 0) else np.linspace(1e-3, np.max(ensure_numpy(x)), 200)
                if _has_scipy:
                    s = sigma_log
                    scale = np.exp(mu_log)
                    y_log_gauss = lognorm.pdf(x_log, s=s, scale=scale)
                else:
                    y_log_gauss = (1/(x_log * sigma_log * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(x_log) - mu_log)/sigma_log)**2)
                y_log_gauss = y_log_gauss / np.sum(y_log_gauss) * np.sum(y[x > 0])
                ax.plot(x_log, y_log_gauss, 'm-', label='Log-Gaussian')
            all_y = ensure_numpy(y)
            all_x = ensure_numpy(x)
            if Y_fit is not None:
                all_y = np.concatenate((all_y, ensure_numpy(Y_fit)))
            if X_fit is not None:
                all_x = np.concatenate((all_x, ensure_numpy(X_fit)))
            all_y_clean = all_y[np.isfinite(all_y) & (all_y > 0)]
            all_x_clean = all_x[np.isfinite(all_x) & (all_x > 0)]
            if sim.fit_mode == 'powerlaw':
                ax.set_xscale('log')
                ax.set_yscale('log')
                y_min_lim = np.min(all_y_clean) * 0.9 if len(all_y_clean) > 0 else 1e-5
                y_max_lim = np.max(all_y_clean) * 1.1 if len(all_y_clean) > 0 else 1
                x_min_lim = np.min(all_x_clean) * 0.9 if len(all_x_clean) > 0 else 1e-2
                x_max_lim = np.max(all_x_clean) * 1.1 if len(all_x_clean) > 0 else 100
                ax.set_ylim((max(1e-9, y_min_lim), y_max_lim))
                ax.set_xlim((max(1e-9, x_min_lim), x_max_lim))
            else:
                ax.set_xscale('linear')
                ax.set_yscale('linear')
                ax.set_ylim((np.min(all_y)*0.9 if len(all_y)>0 else 0, 
                            np.max(all_y)*1.1 if len(all_y)>0 else 1))
                ax.set_xlim((np.min(all_x)*0.9 if len(all_x)>0 else 0, 
                            np.max(all_x)*1.1 if len(all_x)>0 else 1))
    else:
        if static_plot:
            ax.clear()
            ax.set_title(f"No data to plot for {dimension_name} at t={sim.t}")
        elif hasattr(sim, 'line_data') and sim.line_data is not None:
            sim.line_data.set_data([], [])
            sim.line_fit.set_data([], [])

def plot_dimension_distribution_on_axes(sim, dimension_name, ax):
    if dimension_name == 'pleasure':
        # Exclude pleasure from general distribution plot
        return
    dim_data = ensure_numpy(sim.get_dimension_data(dimension_name))
    (x, y), (X_fit, Y_fit) = compute_wealth_distribution(
        data=dim_data,
        fit_mode=sim.fit_mode,
        bins=50,
        current_xp_module=sim.xp_module
    )
    ax.clear()
    if x is not None and y is not None:
        ax.plot(x, y, 'bo-', label='Empirical', markersize=3)
        if X_fit is not None and Y_fit is not None:
            ax.plot(X_fit, Y_fit, 'r--', label=f'{sim.fit_mode} fit', linewidth=2)
        # --- Gaussian overlay ---
        mu = float(np.mean(dim_data))
        sigma = float(np.std(dim_data))
        if sigma > 0:
            x_gauss = np.linspace(np.min(ensure_numpy(x)), np.max(ensure_numpy(x)), 200)
            if _has_scipy:
                y_gauss = norm.pdf(x_gauss, mu, sigma)
            else:
                y_gauss = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_gauss - mu)/sigma)**2)
            y_gauss = y_gauss / np.sum(y_gauss) * np.sum(y)
            ax.plot(x_gauss, y_gauss, 'g-', label='Gaussian')
        # --- Log-Gaussian overlay ---
        log_data = np.log(dim_data[dim_data > 0])
        if len(log_data) > 1:
            mu_log = float(np.mean(log_data))
            sigma_log = float(np.std(log_data))
            x_log = ensure_numpy(x[x > 0]) if np.any(x > 0) else np.linspace(1e-3, np.max(ensure_numpy(x)), 200)
            if _has_scipy:
                s = sigma_log
                scale = np.exp(mu_log)
                y_log_gauss = lognorm.pdf(x_log, s=s, scale=scale)
            else:
                y_log_gauss = (1/(x_log * sigma_log * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((np.log(x_log) - mu_log)/sigma_log)**2)
            y_log_gauss = y_log_gauss / np.sum(y_log_gauss) * np.sum(y[x > 0])
            ax.plot(x_log, y_log_gauss, 'm-', label='Log-Gaussian')
        ax.set_title(f"{dimension_name.capitalize()} Distribution")
        ax.set_xlabel(dimension_name.capitalize())
        ax.set_ylabel("Probability Density / CCDF")
        if sim.fit_mode == 'powerlaw':
            ax.set_xscale('log')
            ax.set_yscale('log')
        else:
            ax.set_xscale('linear')
            ax.set_yscale('linear')
        ax.legend()
        ax.grid(True, alpha=0.3)
        if len(x) > 0 and len(y) > 0:
            x_min, x_max = np.min(x), np.max(x)
            y_min, y_max = np.min(y), np.max(y)
            if Y_fit is not None and len(Y_fit) > 0:
                y_min = min(y_min, np.min(Y_fit))
                y_max = max(y_max, np.max(Y_fit))
            if X_fit is not None and len(X_fit) > 0:
                x_min = min(x_min, np.min(X_fit))
                x_max = max(x_max, np.max(X_fit))
            x_buffer = (x_max - x_min) * 0.1 if x_max > x_min else 0.1
            y_buffer = (y_max - y_min) * 0.1 if y_max > y_min else 0.1
            if sim.fit_mode == 'powerlaw':
                x_min_lim = max(1e-9, x_min - x_buffer)
                y_min_lim = max(1e-9, y_min - y_buffer)
                ax.set_xlim(x_min_lim, x_max + x_buffer)
                ax.set_ylim(y_min_lim, y_max + y_buffer)
            else:
                ax.set_xlim(x_min - x_buffer, x_max + x_buffer)
                ax.set_ylim(max(0, y_min - y_buffer), y_max + y_buffer)
    else:
        ax.text(0.5, 0.5, f'No data for {dimension_name}', 
               transform=ax.transAxes, ha='center', va='center')
        ax.set_title(f"{dimension_name.capitalize()} Distribution")

def plot_pleasure_distribution(sim, ax=None):
    """
    Plot the distribution of the 'pleasure' dimension, with x-axis capped between 0 and 1.
    Only activates if 'pleasure' is in sim.dimensions.
    """
    if 'pleasure' not in sim.dimensions:
        raise ValueError("'pleasure' dimension not found in simulation.")
    dim_data = ensure_numpy(sim.get_dimension_data('pleasure'))
    (x, y), (X_fit, Y_fit) = compute_wealth_distribution(
        data=dim_data,
        fit_mode=sim.fit_mode,
        bins=50,
        current_xp_module=sim.xp_module
    )
    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))
    else:
        fig = None
    ax.clear()
    if x is not None and y is not None:
        ax.plot(x, y, 'bo-', label='Empirical', markersize=3)
        if X_fit is not None and Y_fit is not None:
            ax.plot(X_fit, Y_fit, 'r--', label=f'{sim.fit_mode} fit', linewidth=2)
        mu = float(np.mean(dim_data))
        sigma = float(np.std(dim_data))
        if sigma > 0:
            x_gauss = np.linspace(0, 1, 200)
            if _has_scipy:
                from scipy.stats import norm
                y_gauss = norm.pdf(x_gauss, mu, sigma)
            else:
                y_gauss = (1/(sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_gauss - mu)/sigma)**2)
            y_gauss = y_gauss / np.sum(y_gauss) * np.sum(y)
            ax.plot(x_gauss, y_gauss, 'g-', label='Gaussian')
        ax.set_title(f"Pleasure Distribution at t={sim.t} (N={sim.N})")
        ax.set_xlabel("Pleasure")
        ax.set_ylabel("Probability Density / CCDF")
        ax.set_xlim(0, 1)
        # Force linear scale for pleasure distribution
        ax.set_xscale('linear')
        ax.legend()
        ax.grid(True, alpha=0.3)
    else:
        ax.text(0.5, 0.5, 'No data for pleasure', transform=ax.transAxes, ha='center', va='center')
        ax.set_title("Pleasure Distribution")
        ax.set_xlim(0, 1)
        # Force linear scale even for empty data
        ax.set_xscale('linear')
    if fig is not None:
        plt.tight_layout()
        return fig
    else:
        return ax

def plot_wealth_distribution(sim, static_plot=False):
    sim.AgentWealth = sim.xp_module.sum(sim.Portfolios, axis=1)
    if hasattr(sim, 'super_plot_wealth_distribution'):
        sim.super_plot_wealth_distribution(static_plot)
    else:
        from .base import plot_wealth_distribution as base_plot_wealth_distribution
        base_plot_wealth_distribution(sim, static_plot) 

def plot_all_scatter_pairs(sim, axes=None):
    """
    Plot scatter plots for every unique pair of dimensions (including 'pleasure').
    If axes is provided, use it as a grid; otherwise, create a new figure and axes.
    Returns the figure.
    """
    dims = [d for d in sim.dimensions]  # include all dims, including 'pleasure'
    n = len(dims)
    from math import comb
    n_pairs = n * (n - 1) // 2
    if axes is None:
        ncols = 3
        nrows = (n_pairs + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 5, nrows * 4))
        axes = axes.flatten()
    else:
        fig = None
        axes = axes.flatten()
    idx = 0
    for i in range(n):
        for j in range(i+1, n):
            if idx >= len(axes):
                break
            x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dims[i])])
            y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dims[j])])
            ax = axes[idx]
            ax.scatter(x, y, alpha=0.6, s=10)
            ax.set_xlabel(f'{dims[i].capitalize()}')
            ax.set_ylabel(f'{dims[j].capitalize()}')
            ax.set_title(f'{dims[i].capitalize()} vs {dims[j].capitalize()}')
            ax.grid(True, alpha=0.3)
            ax.set_xscale('log')
            ax.set_yscale('log')
            idx += 1
    # Hide unused axes
    for k in range(idx, len(axes)):
        axes[k].set_visible(False)
    if fig is not None:
        plt.tight_layout()
        return fig
    else:
        return axes 