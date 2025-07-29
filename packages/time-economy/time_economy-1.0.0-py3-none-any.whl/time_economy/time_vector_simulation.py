# TimeVectorSimulation.py
# Vectorized "Economy of Time" Simulation

import sys
import os

import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML

# Import the base simulation class and helper functions
from .base import BaseWealthSimulation, ensure_numpy, ensure_xp, compute_wealth_distribution, gini_coefficient
from . import plotter
from .utils import (
    get_dimension_data,
    get_leverage_data,
    get_focus_data,
    get_gini_coefficients,
    get_average_leverage,
)

# --- GPU Configuration ---
# Use a global flag to ensure GPU message is printed only once
import sys
_gpu_message_printed = hasattr(sys.modules['time_economy.base'], '_gpu_message_printed')

try:
    import cupy as cp
    xp = cp
    xp_is_cupy = True
    if not _gpu_message_printed:
        print("CuPy found, using GPU.")
        sys.modules['time_economy.base']._gpu_message_printed = True
except ImportError:
    xp = np
    xp_is_cupy = False
    if not _gpu_message_printed:
        print("CuPy not found, using NumPy (CPU).")
        sys.modules['time_economy.base']._gpu_message_printed = True


class TimeVectorSimulation(BaseWealthSimulation):
    """
    Vectorized "Economy of Time" Simulation
    
    This simulation models an economy where agents allocate time between production
    and knowledge acquisition, with knowledge providing leverage on production.
    All operations are vectorized for GPU performance.
    """
    
    def __init__(self, data_folder, N, dimensions=None, use_gpu_if_available=True, log_to_disk=False,
                 c_knowledge_xfer=0.05, enable_power_dynamics=False,
                 c_power_factor=0.1, base_daily_decay_rate=0.001, decay_coeffs_map=None,
                 enable_capital_risk=False,
                 savings_mean=0.20, savings_std=0.10, risk_mean=0.01, risk_std=0.02,
                 focus_noise_level=0.0, k_time=0.1, k_consumption=0.05, pleasure_time_exponent=0.5,
                 consumption_factor_mean=0.01, consumption_factor_std=0.02, consumption_noise_std=0.2,
                 plot_interval=20, art_leverage_exponent=1.0,
                 random_initial_portfolio=False):
        """
        Initialize the Time Vector Simulation
        
        Args:
            data_folder: Folder to store simulation logs
            N: Number of agents
            dimensions: List of dimension names (default: ['production', 'knowledge'])
            use_gpu_if_available: Whether to use GPU if available
            log_to_disk: Whether to log simulation state to disk (default: False)
            c_knowledge_xfer: Knowledge transfer efficiency (default: 0.05)
            savings_mean: Mean for daily savings rate (default 0.20)
            savings_std: Std for daily savings rate (default 0.10)
            risk_mean: Mean for risked capital rate (default 0.01)
            risk_std: Std for risked capital rate (default 0.02)
            focus_noise_level: Magnitude of daily focus fluctuation (default: 0.0)
            k_time: Coefficient for time's effect on pleasure (default: 0.1)
            k_consumption: Coefficient for consumption's effect on pleasure (default: 0.05)
            pleasure_time_exponent: Exponent for time's diminishing returns on pleasure (0-1, default: 0.5)
            consumption_factor_mean: Mean of the base consumption factor distribution (default: 0.01)
            consumption_factor_std: Std dev of the base consumption factor distribution (default: 0.02)
            consumption_noise_std: Std dev of the daily noise on the consumption factor (default: 0.2)
            plot_interval: How often to update time series data (default: 20)
            random_initial_portfolio: If True, initialize each agent's portfolio randomly (pleasure capped between 0 and 1)
        """
        # Set default dimensions if not provided
        if dimensions is None:
            dimensions = ['production', 'knowledge']
        
        self.dimensions = dimensions
        self.D = len(self.dimensions)  # Number of dimensions
        # Convert N to int to avoid CuPy type issues
        N = int(N)
        self.N = N
        # Initialize with 'powerlaw' fit mode for wealth distribution analysis
        super().__init__(data_folder, N, fit_mode='powerlaw', use_gpu_if_available=use_gpu_if_available, log_to_disk=log_to_disk)
        self._init_dimension_masks()  # Initialize vectorized masks for dimension categories
        
        # Constants for the time economy
        self.T_budget = 24.0  # Total time budget per day
        self.c_leverage_factor = 0.01  # Knowledge leverage coefficient
        # Automatically set enable_knowledge_sharing based on c_knowledge_xfer
        self.enable_knowledge_sharing = c_knowledge_xfer > 0
        self.c_knowledge_xfer = c_knowledge_xfer  # Knowledge transfer efficiency
        self.enable_power_dynamics = enable_power_dynamics
        self.c_power_factor = c_power_factor  # Power effect on split
        # Automatically set enable_decay based on base_daily_decay_rate
        self.enable_decay = base_daily_decay_rate > 0
        self.enable_capital_risk = enable_capital_risk  # <--- NEW ATTRIBUTE
        self.base_daily_decay_rate = base_daily_decay_rate
        self.savings_mean = savings_mean
        self.savings_std = savings_std
        self.risk_mean = risk_mean
        self.risk_std = risk_std
        self.focus_noise_level = focus_noise_level
        # Permanent per-agent savings rate for the run
        self.savings_rate = None
        # Precompute lognormal parameters for risk (mu, sigma) using the current backend
        xp = self.xp_module
        mean = self.risk_mean
        std = self.risk_std
        sigma2 = xp.log((std**2 / mean**2) + 1)
        self.risk_lognorm_mu = float(xp.log(mean) - 0.5 * sigma2)
        self.risk_lognorm_sigma = float(xp.sqrt(sigma2))
        # Default decay coefficients map
        if decay_coeffs_map is None:
            self.decay_coeffs_map = {
                'production': 1.0,
                'knowledge': 0.1,
                'power': 2.0,
                'default': 1.0
            }
        else:
            self.decay_coeffs_map = decay_coeffs_map
        self.decay_coeffs_list = [self.decay_coeffs_map.get(dim, self.decay_coeffs_map.get('default', 1.0)) for dim in (dimensions if dimensions is not None else ['production', 'knowledge', 'power'])]
        self.DecayMultiplier = None
        
        # Initialize data structures
        self.Portfolios = None  # Will be (N, D) array
        self.T_sustain = None   # Will be (N,) array
        self.BaseFocus = None   # RENAMED from self.Focus
        
        # Pre-allocated temporary arrays for the simulation loop
        self._tmp_DailyCrystals = None
        self._tmp_shuffled_indices = None
        self._tmp_DailyCrystals_shuffled = None
        self._tmp_CombinedCrystals = None
        self._tmp_epsilon = None
        self._tmp_Gain_for_original = None
        self._tmp_Gain_for_shuffled = None
        self._tmp_Total_Gains = None
        self._tmp_indices = None
        
        # Time series tracking for analysis
        self.time_series_data = {
            'avg_leverage': [],
            'gini_total': [],
            't': []
        }
        
        # Initialize dimension-specific Gini tracking
        for dim_name in self.dimensions:
            self.time_series_data[f'gini_{dim_name}'] = []
        
        # --- PLEASURE ATTRIBUTES ---
        self.k_time = k_time
        self.k_consumption = k_consumption
        self.pleasure_time_exponent = pleasure_time_exponent
        self.consumption_noise_std = consumption_noise_std
        self.base_consumption_factor = None # Initialized later
        # Automatically set enable_pleasure based on dimensions
        self.enable_pleasure = 'pleasure' in self.dimensions
        self.plot_interval = plot_interval
        self.art_leverage_exponent = art_leverage_exponent
        # Precompute lognormal parameters for base consumption factor
        xp = self.xp_module
        mean_cf = consumption_factor_mean
        std_cf = consumption_factor_std
        sigma2_cf = xp.log((std_cf**2 / mean_cf**2) + 1)
        self.cf_lognorm_mu = float(xp.log(mean_cf) - 0.5 * sigma2_cf)
        self.cf_lognorm_sigma = float(xp.sqrt(sigma2_cf))
        
        # Store random_initial_portfolio as instance variable
        self.random_initial_portfolio = random_initial_portfolio
        
        # Set log file name
        log_fn = f"TimeVector_N{int(self.N):08d}_D{self.D}.log.pickle"
        self.log_file_name = os.path.join(self.data_folder, log_fn) if self.data_folder else None
        print(f"Time Vector Simulation log file: {self.log_file_name}")
        
        # Plot styling for powerlaw
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')
    
    def __getstate__(self):
        """
        Custom pickling method to exclude xp_module and other non-picklable objects
        """
        state = self.__dict__.copy()
        # Remove xp_module from state (it will be reconstructed on unpickling)
        if 'xp_module' in state:
            del state['xp_module']
        # Remove matplotlib figure and axes (they can't be pickled)
        if 'fig' in state:
            del state['fig']
        if 'ax' in state:
            del state['ax']
        if 'line_data' in state:
            del state['line_data']
        if 'line_fit' in state:
            del state['line_fit']
        if 'animation' in state:
            del state['animation']
        return state
    
    def __setstate__(self, state):
        """
        Custom unpickling method to reconstruct xp_module and other objects
        """
        self.__dict__.update(state)
        # Reconstruct xp_module
        try:
            import cupy as cp
            self.xp_module = cp
            self.using_gpu = True
        except ImportError:
            import numpy as np
            self.xp_module = np
            self.using_gpu = False
        # Reconstruct matplotlib objects
        import matplotlib.pyplot as plt
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        self.line_data = None
        self.line_fit = None
        self.animation = None
        # Reconstruct plot styling
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')
    
    def _init_simulation_arrays(self):
        """
        Initialize and pre-allocate temporary arrays for the simulation loop
        to avoid repeated allocation on the GPU.
        """
        xp = self.xp_module
        # These arrays are used inside the update_wealth_distribution loop
        self._tmp_DailyCrystals = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_DailyCrystals_shuffled = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_CombinedCrystals = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_Gain_for_original = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_Gain_for_shuffled = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_Total_Gains = xp.zeros((self.N, self.D), dtype=np.float32)
        self._tmp_epsilon = xp.zeros((self.N, 1), dtype=np.float32)
        self._tmp_indices = xp.arange(self.N)
        self._tmp_shuffled_indices = xp.copy(self._tmp_indices)
    
    def _init_dimension_masks(self):
        """
        Initialize boolean masks for rivalrous, shared, and private goods dimensions.
        This is done once at initialization for vectorized operations.
        """
        rivalrous_mask = np.zeros(self.D, dtype=bool)
        shared_mask = np.zeros(self.D, dtype=bool)
        private_mask = np.zeros(self.D, dtype=bool)
        dim_map = {
            'production': rivalrous_mask,
            'knowledge': shared_mask,
            'power': rivalrous_mask,
            'pleasure': private_mask,
        }
        default_mask = rivalrous_mask
        for i, dim in enumerate(self.dimensions):
            # Allow for partial matches like 'pleasure_1', 'pleasure_2'
            main_dim_type = dim.split('_')[0]
            mask_to_update = dim_map.get(main_dim_type, default_mask)
            mask_to_update[i] = True
        self.rivalrous_mask = self.xp_module.asarray(rivalrous_mask)
        self.shared_mask = self.xp_module.asarray(shared_mask)
        self.private_mask = self.xp_module.asarray(private_mask)
    
    def initialize_wealth_distribution(self):
        """
        Initialize the simulation state with vectorized arrays
        """
        xp = self.xp_module
        if self.random_initial_portfolio:
            # Random initialization for each agent's portfolio
            self.Portfolios = (xp.random.lognormal(mean=0.0, sigma=1.0, size=(self.N, self.D)) * 10000).astype(np.float32)
            # If pleasure is present, cap between 0 and 1
            if self.enable_pleasure and 'pleasure' in self.dimensions:
                pleasure_idx = self.dimensions.index('pleasure')
                self.Portfolios[:, pleasure_idx] = xp.clip(self.Portfolios[:, pleasure_idx], 0.0, 1.0)
        else:
            # Default: all zeros, except pleasure if present
            self.Portfolios = xp.zeros((self.N, self.D), dtype=np.float32)
            if self.enable_pleasure and 'pleasure' in self.dimensions:
                pleasure_idx = self.dimensions.index('pleasure')
                self.Portfolios[:, pleasure_idx] = 0.5
        
        # Initialize sustain times: normal distribution around 12 hours
        self.T_sustain = self.xp_module.random.normal(loc=12.0, scale=2.0, size=self.N).astype(np.float32)
        # Ensure sustain times are within reasonable bounds
        self.T_sustain = self.xp_module.clip(self.T_sustain, 6.0, 20.0)
        
        # Initialize focus vectors: random allocation between dimensions
        # Each agent's focus vector must sum to 1
        # Focus is permanent per agent for the run
        if self.D == 2:
            # For 2D case, use simple random allocation
            r = self.xp_module.random.rand(self.N, 1).astype(np.float32)
            focus_prod = r
            focus_know = 1.0 - r
            self.BaseFocus = self.xp_module.hstack([focus_prod, focus_know])
        else:
            # For higher dimensions, use Dirichlet distribution
            # Generate random values and normalize
            random_focus = self.xp_module.random.rand(self.N, self.D).astype(np.float32)
            row_sums = self.xp_module.sum(random_focus, axis=1, keepdims=True)
            self.BaseFocus = random_focus / row_sums
        
        # Pre-allocate temporary arrays
        self._init_simulation_arrays()
        
        # Set AgentWealth to total embodied time for compatibility with base class
        self.AgentWealth = self.xp_module.sum(self.Portfolios, axis=1)
        self.t = 0
    
        # Initialize time series data
        self.time_series_data = {
            'avg_leverage': [],
            'gini_total': [],
            't': []
        }
        
        # Initialize dimension-specific Gini tracking
        for dim_name in self.dimensions:
            self.time_series_data[f'gini_{dim_name}'] = []
        
        # --- DecayMultiplier setup ---
        coeffs_array = self.xp_module.array(self.decay_coeffs_list, dtype=np.float32)
        actual_decay_rates = self.base_daily_decay_rate * coeffs_array
        self.DecayMultiplier = 1.0 - actual_decay_rates
        self.DecayMultiplier = self.DecayMultiplier.reshape(1, self.D)
        
        # Permanent per-agent savings rate
        self.savings_rate = self.xp_module.random.normal(loc=self.savings_mean, scale=self.savings_std, size=(self.N, 1)).astype(np.float32)
        self.savings_rate = self.xp_module.clip(self.savings_rate, 0.0, 1.0)

        # --- PLEASURE: Initialize base consumption factor ---
        if self.enable_pleasure and 'pleasure' in self.dimensions and 'production' in self.dimensions:
            self.base_consumption_factor = self.xp_module.random.lognormal(
                self.cf_lognorm_mu, self.cf_lognorm_sigma, size=self.N
            ).astype('float32')
    
    def _sigmoid(self, x):
        """Vectorized sigmoid function."""
        return 1 / (1 + self.xp_module.exp(-x))

    def _apply_capital_risk_and_savings(self, DailyCrystals, Total_Gains):
        """
        Apply capital risk and savings mechanism to DailyCrystals and Total_Gains.
        Returns a modified TransactionPot (copy of DailyCrystals) and updates Total_Gains in-place.
        Uses self.savings_rate (permanent per agent), and a long-tailed (lognormal) distribution for daily risk factor.
        """
        xp = self.xp_module
        TransactionPot = xp.copy(DailyCrystals)
        if self.enable_capital_risk and xp.any(self.rivalrous_mask):
            # A. Agents save a portion of their daily rivalrous production (permanent per agent)
            savings_rate = self.savings_rate
            saved_crystals = TransactionPot[:, self.rivalrous_mask] * savings_rate
            Total_Gains[:, self.rivalrous_mask] += saved_crystals  # Risk-free savings
            TransactionPot[:, self.rivalrous_mask] -= saved_crystals  # Remove from pot
            # B. Agents bring a portion of their accumulated rivalrous wealth to the table
            # Use a long-tailed lognormal distribution for risk factor (conversion done in __init__)
            wealth_to_risk_rate = xp.random.lognormal(self.risk_lognorm_mu, self.risk_lognorm_sigma, size=(self.N, 1)).astype('float32')
            wealth_to_risk_rate = xp.clip(wealth_to_risk_rate, 0.0, 0.15)
            wealth_to_risk = self.Portfolios[:, self.rivalrous_mask] * wealth_to_risk_rate
            self.Portfolios[:, self.rivalrous_mask] -= wealth_to_risk  # Subtract from portfolios NOW
            TransactionPot[:, self.rivalrous_mask] += wealth_to_risk  # Add to transaction pot
        return TransactionPot

    def _apply_focus_noise(self):
        """
        Applies random noise to the base focus and re-normalizes.
        This creates a temporary, daily focus distribution for agents.
        Returns:
            xp.ndarray: The daily focus matrix of shape (N, D).
        """
        xp = self.xp_module
        if self.focus_noise_level <= 0:
            return self.BaseFocus
        # Generate noise centered around 0 (from -1 to 1)
        noise = xp.random.uniform(-1, 1, size=self.BaseFocus.shape).astype(np.float32)
        # Apply scaled noise to the agent's core strategy
        noisy_focus = self.BaseFocus + noise * self.focus_noise_level
        # Clip to ensure focus values are non-negative
        noisy_focus = xp.clip(noisy_focus, 0, None)
        # Re-normalize so each agent's focus vector sums to 1
        row_sums = xp.sum(noisy_focus, axis=1, keepdims=True)
        # Avoid division by zero for rows that might sum to 0 after clipping
        row_sums[row_sums == 0] = 1.0
        daily_focus = noisy_focus / row_sums
        return daily_focus

    def _update_pleasure_dimension(self, T_productive):
        """
        Vectorized update for the 'pleasure' dimension.
        This process is non-rivalrous and private. Pleasure is gained from two sources:
        1. Time invested, with gentle diminishing returns.
        2. Production capital consumed, with strong diminishing returns.
        Capital consumed for pleasure is permanently removed from the 'production' portfolio.
        """
        if not self.enable_pleasure:
            return
        xp = self.xp_module
        try:
            pleasure_idx = self.dimensions.index('pleasure')
            production_idx = self.dimensions.index('production')
        except ValueError:
            # If pleasure or production dimensions don't exist, do nothing.
            return
        # 1. Consumption of Production Capital
        # Add daily noise to the base consumption factor
        noise = xp.random.normal(loc=1.0, scale=self.consumption_noise_std, size=self.N).astype('float32')
        daily_consumption_factor = self.base_consumption_factor * noise
        # Calculate capital to be consumed
        production_capital = self.Portfolios[:, production_idx]
        C_amount = daily_consumption_factor * production_capital
        C_amount = xp.clip(C_amount, 0, production_capital) # Cannot consume more than you have
        # Permanently remove consumed capital from production portfolio
        self.Portfolios[:, production_idx] -= C_amount
        # 2. Time Invested in Pleasure
        focus_on_pleasure = self.BaseFocus[:, pleasure_idx]
        T_pleasure = T_productive * focus_on_pleasure
        # 3. Calculate Pleasure Gain
        current_pleasure = self.Portfolios[:, pleasure_idx]
        gain_potential = 1.0 - current_pleasure
        # Calculate effect from time (power function for gentler diminishing returns)
        time_effect = self.k_time * (T_pleasure ** self.pleasure_time_exponent)
        # Calculate effect from consumption (log function for strong diminishing returns)
        consumption_effect = self.k_consumption * xp.log1p(C_amount)
        # Total change in pleasure is limited by the gain potential
        delta_pleasure = gain_potential * (time_effect + consumption_effect)
        # 4. Update and Clip Pleasure Portfolio
        self.Portfolios[:, pleasure_idx] += delta_pleasure
        self.Portfolios[:, pleasure_idx] = xp.clip(self.Portfolios[:, pleasure_idx], 0.0, 1.0)

    def _apply_art_leverage(self, DailyCrystals, Time_on_dims, k_leverage):
        """
        Helper to apply special diminishing returns for 'art' leverage if enabled.
        Modifies DailyCrystals in-place if art_leverage_exponent < 1.0 and 'art' is present.
        """
        if self.art_leverage_exponent < 1.0:
            try:
                art_idx = self.dimensions.index('art')
                art_leverage = self.xp_module.power(k_leverage, self.art_leverage_exponent)
                time_spent_on_art = Time_on_dims[:, art_idx]
                DailyCrystals[:, art_idx] = art_leverage * time_spent_on_art
            except ValueError:
                pass
        return DailyCrystals

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        """
        Fully vectorized simulation update step
        """
        for _ in range(update_rate):  # Simulate multiple days per animation frame
            if self.N < 2:
                continue
            
            # Use pre-allocated arrays
            xp = self.xp_module
            Total_Gains = self._tmp_Total_Gains
            Total_Gains.fill(0) # Reset gains for the day

            # Determine daily focus, applying noise if enabled
            daily_focus = self._apply_focus_noise()
            
            # Phase 1: Calculate Productive Time (for all agents)
            T_productive = self.T_budget - self.T_sustain  # (N,) array
            
            # Phase 2: Calculate Leverage (for all agents)
            try:
                knowledge_idx = self.dimensions.index('knowledge')
                knowledge_capital = self.Portfolios[:, knowledge_idx]  # (N,) array
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital  # (N,) array
            except ValueError:
                # If 'knowledge' dimension doesn't exist, use first dimension as leverage source
                knowledge_capital = self.Portfolios[:, 0]
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital
            
            # Phase 3: Produce the "Daily Crystals" (for all agents)
            # Time Allocation: reshape T_productive to (N, 1) for broadcasting
            Time_on_dims = T_productive[:, self.xp_module.newaxis] * daily_focus  # (N, D) array
            
            # Value Production: apply leverage to time allocation
            DailyCrystals = k_leverage[:, self.xp_module.newaxis] * Time_on_dims  # (N, D) array
            
            if self.enable_pleasure:
                self._update_pleasure_dimension(T_productive)

            # Phase 4: Vectorized Interaction Phase
            # Randomly pair every agent with another
            shuffled_indices = self._tmp_shuffled_indices
            # xp.random.permutation does not support 'out' argument, so we assign it
            shuffled_indices[:] = xp.random.permutation(self._tmp_indices)
            
            # Use pre-allocated arrays for calculations
            DailyCrystals_shuffled = DailyCrystals[shuffled_indices]
            CombinedCrystals = self._tmp_CombinedCrystals
            xp.add(DailyCrystals, DailyCrystals_shuffled, out=CombinedCrystals)
            
            # Random split factor for each pair
            epsilon = self._tmp_epsilon
            epsilon[:] = xp.random.rand(self.N, 1)
            
            # Calculate gains for original and shuffled agents
            Gain_for_original = self._tmp_Gain_for_original
            Gain_for_shuffled = self._tmp_Gain_for_shuffled
            xp.multiply(epsilon, CombinedCrystals, out=Gain_for_original)
            
            # Calculate (1-epsilon) into a temporary variable to avoid in-place modification issues
            one_minus_epsilon = 1.0 - epsilon
            xp.multiply(one_minus_epsilon, CombinedCrystals, out=Gain_for_shuffled)
            
            # Distribute gains using scatter-add
            Total_Gains.fill(0) # Ensure it's zeroed before use
            Total_Gains += Gain_for_original  # Add gains for original agents
            
            # Add gains for shuffled agents using scatter-add
            xp.add.at(Total_Gains, shuffled_indices, Gain_for_shuffled)
            
            # Update portfolios
            self.Portfolios += Total_Gains
            
            # Update AgentWealth for compatibility with base class
            self.AgentWealth = self.xp_module.sum(self.Portfolios, axis=1)

            self.t += 1
            # Update time series data periodically, not every step
            if self.t > 0 and self.t % self.plot_interval == 0:
                self._update_time_series()
            
            # --- Apply decay at the end of each day if enabled ---
            if self.enable_decay:
                self.Portfolios *= self.DecayMultiplier
    
    def _update_time_series(self):
        """
        Update time series data for analysis
        """
        # Calculate current metrics
        avg_leverage = get_average_leverage(self.Portfolios, self.dimensions, self.c_leverage_factor, self.xp_module)
        if hasattr(avg_leverage, 'get'):
            avg_leverage = float(avg_leverage.get())
        else:
            avg_leverage = float(avg_leverage)
        gini_coeffs = get_gini_coefficients(self.Portfolios, self.AgentWealth, self.dimensions, self.xp_module)
        for k in gini_coeffs:
            if hasattr(gini_coeffs[k], 'get'):
                gini_coeffs[k] = float(gini_coeffs[k].get())
            else:
                gini_coeffs[k] = float(gini_coeffs[k])
        # Store in time series
        self.time_series_data['t'].append(self.t)
        self.time_series_data['avg_leverage'].append(avg_leverage)
        # Store Gini coefficients for each dimension
        for dim_name in self.dimensions:
            if dim_name in gini_coeffs:
                self.time_series_data[f'gini_{dim_name}'].append(gini_coeffs[dim_name])
        # Store total wealth Gini
        if 'total' in gini_coeffs:
            self.time_series_data['gini_total'].append(gini_coeffs['total'])
    
    def log_simulation_state(self):
        """
        Log additional simulation state beyond just wealth
        """
        if self.log_file_name is not None:
            # Log the full simulation state
            state_data = {
                't': self.t,
                'portfolios': ensure_numpy(self.Portfolios),
                't_sustain': ensure_numpy(self.T_sustain),
                'focus': ensure_numpy(self.BaseFocus),  # Use BaseFocus
                'agent_wealth': ensure_numpy(self.AgentWealth),
                'gini_coefficients': get_gini_coefficients(self.Portfolios, self.AgentWealth, self.dimensions, self.xp_module),
                'avg_leverage': float(get_average_leverage(self.Portfolios, self.dimensions, self.c_leverage_factor, self.xp_module)),
                'time_series_data': self.time_series_data
            }
            try:
                with open(self.log_file_name, 'ab') as f:
                    pickle.dump((self.t, state_data), f)
            except Exception as e:
                print(f"Error writing to log file {self.log_file_name}: {e}")
    
    def log_wealth_distribution(self):
        """
        Override to log full simulation state
        """
        self.log_simulation_state()

    def _vectorized_wealth_update(self, DailyCrystals, shuffled_indices):
        """
        Fully vectorized wealth update using precomputed masks for rivalrous, shared, and private goods.
        This version correctly handles rivalrous goods in separate "markets" and fixes private goods handling for 'pleasure'.
        Returns the calculated gains instead of updating portfolios directly.
        """
        xp = self.xp_module
        Interaction_Gains = xp.zeros_like(self.Portfolios)
        DailyCrystals_shuffled = DailyCrystals[shuffled_indices]
        
        # --- 1. Handle Rivalrous & Pooled Goods (CORRECTED LOGIC) ---
        # Find the indices of all dimensions marked as rivalrous
        rivalrous_indices = xp.where(self.rivalrous_mask)[0]

        # Process each rivalrous dimension independently
        for dim_idx in rivalrous_indices:
            # Extract the single dimension's daily production for all agents
            my_production_dim = DailyCrystals[:, dim_idx]
            partner_production_dim = DailyCrystals_shuffled[:, dim_idx]

            # Combine the pot for this specific dimension
            combined_dim = my_production_dim + partner_production_dim

            # Determine the split factor (power dynamics or random)
            power_idx = self.dimensions.index('power') if 'power' in self.dimensions else -1
            if self.enable_power_dynamics and power_idx != -1:
                power_original = self.Portfolios[:, power_idx]
                power_shuffled = self.Portfolios[shuffled_indices, power_idx]
                power_diff = (power_original - power_shuffled) / (power_original + power_shuffled + 1e-9)
                epsilon = self._sigmoid(self.c_power_factor * power_diff)
            else:
                # Epsilon must be (N,) to match the shape of combined_dim
                epsilon = xp.random.rand(self.N).astype(np.float32)

            # Calculate gains and add them to the correct column in Interaction_Gains
            gains_for_original = epsilon * combined_dim
            gains_for_shuffled = (1.0 - epsilon) * combined_dim

            Interaction_Gains[:, dim_idx] += gains_for_original
            xp.add.at(Interaction_Gains[:, dim_idx], shuffled_indices, gains_for_shuffled)

        # --- 2. Handle Non-Rivalrous & Shared Goods (Knowledge) ---
        if xp.any(self.shared_mask):
            my_production = DailyCrystals[:, self.shared_mask]
            partner_production = DailyCrystals_shuffled[:, self.shared_mask]
            final_gains = my_production + self.c_knowledge_xfer * partner_production
            Interaction_Gains[:, self.shared_mask] += final_gains
            
        # --- 3. Handle Non-Rivalrous & Private Goods ---
        if xp.any(self.private_mask):
            # We need to exclude any private goods that have special handling, like 'pleasure'.
            # 'pleasure' is handled in _update_pleasure_dimension and shouldn't gain wealth here.
            # Let's create a mask for private goods that AREN'T pleasure.
            private_non_special_mask = self.private_mask.copy()
            if 'pleasure' in self.dimensions:
                pleasure_idx = self.dimensions.index('pleasure')
                private_non_special_mask[pleasure_idx] = False

            if xp.any(private_non_special_mask):
                 final_gains = DailyCrystals[:, private_non_special_mask]
                 Interaction_Gains[:, private_non_special_mask] += final_gains

        # --- 4. Return the calculated gains instead of updating portfolios ---
        return Interaction_Gains

    def get_dimension_data(self, dimension_name):
        from .utils import get_dimension_data
        return get_dimension_data(self.Portfolios, self.dimensions, dimension_name)

    def get_leverage_data(self):
        from .utils import get_leverage_data
        return get_leverage_data(self.Portfolios, self.dimensions, self.c_leverage_factor, self.xp_module)

    def get_focus_data(self, dimension_name):
        from .utils import get_focus_data
        return get_focus_data(self.BaseFocus, self.dimensions, dimension_name)

    def get_gini_coefficients(self):
        from .utils import get_gini_coefficients
        return get_gini_coefficients(self.Portfolios, self.AgentWealth, self.dimensions, self.xp_module)

    def get_average_leverage(self):
        from .utils import get_average_leverage
        return get_average_leverage(self.Portfolios, self.dimensions, self.c_leverage_factor, self.xp_module)

class TimeVectorSimulationUnleveraged(TimeVectorSimulation):
    """
    Simulation where knowledge acquisition is unleveraged (Solution 1 from enh1.md).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __getstate__(self):
        """
        Custom pickling method to exclude xp_module and other non-picklable objects
        """
        state = self.__dict__.copy()
        # Remove xp_module from state (it will be reconstructed on unpickling)
        if 'xp_module' in state:
            del state['xp_module']
        # Remove matplotlib figure and axes (they can't be pickled)
        if 'fig' in state:
            del state['fig']
        if 'ax' in state:
            del state['ax']
        if 'line_data' in state:
            del state['line_data']
        if 'line_fit' in state:
            del state['line_fit']
        if 'animation' in state:
            del state['animation']
        return state
    
    def __setstate__(self, state):
        """
        Custom unpickling method to reconstruct xp_module and other objects
        """
        self.__dict__.update(state)
        # Reconstruct xp_module
        try:
            import cupy as cp
            self.xp_module = cp
            self.using_gpu = True
        except ImportError:
            import numpy as np
            self.xp_module = np
            self.using_gpu = False
        # Reconstruct matplotlib objects
        import matplotlib.pyplot as plt
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        self.line_data = None
        self.line_fit = None
        self.animation = None
        # Reconstruct plot styling
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        for _ in range(update_rate):
            if self.N < 2:
                continue
            daily_focus = self._apply_focus_noise()
            T_productive = self.T_budget - self.T_sustain
            try:
                knowledge_idx = self.dimensions.index('knowledge')
                knowledge_capital = self.Portfolios[:, knowledge_idx]
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital
            except ValueError:
                knowledge_capital = self.Portfolios[:, 0]
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital
            Time_on_dims = T_productive[:, self.xp_module.newaxis] * daily_focus
            DailyCrystals = self.xp_module.copy(Time_on_dims)
            # Apply the standard linear leverage to all dimensions first
            DailyCrystals *= k_leverage[:, self.xp_module.newaxis]
            # Use helper for art leverage
            DailyCrystals = self._apply_art_leverage(DailyCrystals, Time_on_dims, k_leverage)
            indices = self.xp_module.arange(self.N)
            shuffled_indices = self.xp_module.random.permutation(indices)
            # --- Capital Risk & Savings Mechanism ---
            Total_Gains = self.xp_module.zeros_like(self.Portfolios)
            if self.enable_capital_risk:
                DailyCrystals = self._apply_capital_risk_and_savings(DailyCrystals, Total_Gains)
            if self.enable_knowledge_sharing:
                # Get the returned gains and add them to the accumulator
                interaction_gains = self._vectorized_wealth_update(DailyCrystals, shuffled_indices)
                Total_Gains += interaction_gains
            else:
                DailyCrystals_shuffled = DailyCrystals[shuffled_indices]
                CombinedCrystals = DailyCrystals + DailyCrystals_shuffled
                epsilon = self.xp_module.random.rand(self.N, 1).astype(np.float32)
                Gain_for_original = epsilon * CombinedCrystals
                Gain_for_shuffled = (1.0 - epsilon) * CombinedCrystals
                Total_Gains += Gain_for_original
                self.xp_module.add.at(Total_Gains, shuffled_indices, Gain_for_shuffled)
            
            # Apply the combined gains (savings + interaction) to portfolios
            self.Portfolios += Total_Gains
            self.AgentWealth = self.xp_module.sum(self.Portfolios, axis=1)
            
            self.t += 1
            # Update time series data periodically
            if self.t > 0 and self.t % self.plot_interval == 0:
                self._update_time_series()

            # --- Apply decay at the end of each day if enabled ---
            if self.enable_decay:
                self.Portfolios *= self.DecayMultiplier

class TimeVectorSimulationDiminishingReturns(TimeVectorSimulation):
    """
    Simulation where knowledge acquisition has diminishing returns (Solution 2 from enh1.md).
    Art leverage also has diminishing returns from knowledge.
    """
    def __init__(self, *args, research_factor=0.05, **kwargs):
        super().__init__(*args, **kwargs)
        self.research_factor = research_factor

    def __getstate__(self):
        """
        Custom pickling method to exclude xp_module and other non-picklable objects
        """
        state = self.__dict__.copy()
        # Remove xp_module from state (it will be reconstructed on unpickling)
        if 'xp_module' in state:
            del state['xp_module']
        # Remove matplotlib figure and axes (they can't be pickled)
        if 'fig' in state:
            del state['fig']
        if 'ax' in state:
            del state['ax']
        if 'line_data' in state:
            del state['line_data']
        if 'line_fit' in state:
            del state['line_fit']
        if 'animation' in state:
            del state['animation']
        return state
    
    def __setstate__(self, state):
        """
        Custom unpickling method to reconstruct xp_module and other objects
        """
        self.__dict__.update(state)
        # Reconstruct xp_module
        try:
            import cupy as cp
            self.xp_module = cp
            self.using_gpu = True
        except ImportError:
            import numpy as np
            self.xp_module = np
            self.using_gpu = False
        # Reconstruct matplotlib objects
        import matplotlib.pyplot as plt
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        self.line_data = None
        self.line_fit = None
        self.animation = None
        # Reconstruct plot styling
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        c_research_factor = self.research_factor
        for _ in range(update_rate):
            if self.N < 2:
                continue
            daily_focus = self._apply_focus_noise()
            T_productive = self.T_budget - self.T_sustain
            if self.enable_pleasure:
                self._update_pleasure_dimension(T_productive)
            try:
                knowledge_idx = self.dimensions.index('knowledge')
                knowledge_capital = self.Portfolios[:, knowledge_idx]
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital
            except ValueError:
                knowledge_capital = self.Portfolios[:, 0]
                k_leverage = 1.0 + self.c_leverage_factor * knowledge_capital
            Time_on_dims = T_productive[:, self.xp_module.newaxis] * daily_focus
            DailyCrystals = self.xp_module.copy(Time_on_dims)
            # Apply the standard linear leverage to all dimensions first
            DailyCrystals *= k_leverage[:, self.xp_module.newaxis]
            # Use helper for art leverage
            DailyCrystals = self._apply_art_leverage(DailyCrystals, Time_on_dims, k_leverage)
            try:
                # Diminishing returns for knowledge acquisition
                research_leverage = c_research_factor * self.xp_module.log1p(k_leverage - 1.0) + 1.0
                time_spent_on_knowledge = Time_on_dims[:, knowledge_idx]
                new_knowledge_value = research_leverage * time_spent_on_knowledge
                DailyCrystals[:, knowledge_idx] = new_knowledge_value
            except Exception:
                pass
            indices = self.xp_module.arange(self.N)
            shuffled_indices = self.xp_module.random.permutation(indices)
            # --- Capital Risk & Savings Mechanism ---
            Total_Gains = self.xp_module.zeros_like(self.Portfolios)
            if self.enable_capital_risk:
                DailyCrystals = self._apply_capital_risk_and_savings(DailyCrystals, Total_Gains)
            if self.enable_knowledge_sharing:
                # Get the returned gains and add them to the accumulator
                interaction_gains = self._vectorized_wealth_update(DailyCrystals, shuffled_indices)
                Total_Gains += interaction_gains
            else:
                DailyCrystals_shuffled = DailyCrystals[shuffled_indices]
                CombinedCrystals = DailyCrystals + DailyCrystals_shuffled
                epsilon = self.xp_module.random.rand(self.N, 1).astype(np.float32)
                Gain_for_original = epsilon * CombinedCrystals
                Gain_for_shuffled = (1.0 - epsilon) * CombinedCrystals
                Total_Gains += Gain_for_original
                self.xp_module.add.at(Total_Gains, shuffled_indices, Gain_for_shuffled)
            
            # Apply the combined gains (savings + interaction) to portfolios
            self.Portfolios += Total_Gains
            self.AgentWealth = self.xp_module.sum(self.Portfolios, axis=1)

            self.t += 1
            # Update time series data periodically
            if self.t > 0 and self.t % self.plot_interval == 0:
                self._update_time_series()
            
            # --- Apply decay at the end of each day if enabled ---
            if self.enable_decay:
                self.Portfolios *= self.DecayMultiplier

def show_run_time_vector_args():
    """
    Display all available arguments for run_time_vector function and their default values.
    
    This function helps users understand what parameters they can configure
    when running time vector simulations.
    """
    import inspect
    
    # Get the function signature
    sig = inspect.signature(run_time_vector)
    
    print("run_time_vector Function Arguments:")
    print("=" * 50)
    print("Function: run_time_vector(data_folder, N, dimensions, ...)")
    print()
    print("Available Arguments and Default Values:")
    print("-" * 40)
    
    # Get the docstring to extract parameter descriptions
    doc = run_time_vector.__doc__
    
    # Parse the docstring to get parameter descriptions
    param_descriptions = {}
    if doc:
        lines = doc.split('\n')
        current_param = None
        for line in lines:
            line = line.strip()
            if line.startswith('Args:'):
                continue
            if line.startswith('data_folder (str):'):
                current_param = 'data_folder'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('N (int):'):
                current_param = 'N'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('dimensions (list):'):
                current_param = 'dimensions'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('enable_power_dynamics (bool):'):
                current_param = 'enable_power_dynamics'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('enable_capital_risk (bool):'):
                current_param = 'enable_capital_risk'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('savings_mean (float):'):
                current_param = 'savings_mean'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('savings_std (float):'):
                current_param = 'savings_std'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('risk_mean (float):'):
                current_param = 'risk_mean'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('risk_std (float):'):
                current_param = 'risk_std'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('c_knowledge_xfer (float):'):
                current_param = 'c_knowledge_xfer'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('base_daily_decay_rate (float):'):
                current_param = 'base_daily_decay_rate'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('decay_coeffs_map (dict):'):
                current_param = 'decay_coeffs_map'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('research_factor (float):'):
                current_param = 'research_factor'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('art_leverage_exponent (float):'):
                current_param = 'art_leverage_exponent'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('focus_noise_level (float):'):
                current_param = 'focus_noise_level'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('k_time (float):'):
                current_param = 'k_time'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('k_consumption (float):'):
                current_param = 'k_consumption'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('pleasure_time_exponent (float):'):
                current_param = 'pleasure_time_exponent'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('consumption_factor_mean (float):'):
                current_param = 'consumption_factor_mean'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('consumption_factor_std (float):'):
                current_param = 'consumption_factor_std'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('consumption_noise_std (float):'):
                current_param = 'consumption_noise_std'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('use_gpu_if_available (bool):'):
                current_param = 'use_gpu_if_available'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('log_to_disk (bool):'):
                current_param = 'log_to_disk'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('c_power_factor (float):'):
                current_param = 'c_power_factor'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('MaxRunTime (int):'):
                current_param = 'MaxRunTime'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('batch_size (int):'):
                current_param = 'batch_size'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('update_rate (int):'):
                current_param = 'update_rate'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('plot_interval (int):'):
                current_param = 'plot_interval'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
            elif line.startswith('random_initial_portfolio (bool):'):
                current_param = 'random_initial_portfolio'
                param_descriptions[current_param] = line.split(':', 1)[1].strip()
    
    # Display parameters with their defaults and descriptions
    for param_name, param in sig.parameters.items():
        default_value = param.default
        if default_value == inspect.Parameter.empty:
            default_str = "Required"
        else:
            default_str = repr(default_value)
        
        description = param_descriptions.get(param_name, "No description available")
        
        print(f"{param_name:25} = {default_str}")
        print(f"{'':25}   {description}")
        print()

def run_time_vector(
    data_folder="time_vector_results",
    N=1e6,
    dimensions=None,
    enable_power_dynamics=True,
    enable_capital_risk=True,
    savings_mean=0,
    savings_std=0,
    risk_mean=0.1,
    risk_std=0.1,
    c_knowledge_xfer=0.01,
    base_daily_decay_rate=0.01,
    decay_coeffs_map=None,
    research_factor=0.01,
    art_leverage_exponent=0.6,
    focus_noise_level=0.05,
    k_time=0.1,
    k_consumption=0.05,
    pleasure_time_exponent=0.5,
    consumption_factor_mean=0.01,
    consumption_factor_std=0.02,
    consumption_noise_std=0.2,
    use_gpu_if_available=True,
    log_to_disk=False,
    c_power_factor=10,
    # Simulation run parameters
    MaxRunTime=2000,
    batch_size=100,
    update_rate=1,
    plot_interval=20,
    random_initial_portfolio=False
):
    """
    Run the Time Vector Simulation with optional parameters.
    All parameters are optional and default to the current example values.
    
    Args:
        data_folder (str): Folder to store simulation logs. Defaults to "time_vector_results" 
                          in the current working directory.
        N (int): Number of agents.
        dimensions (list): List of dimension names.
        enable_power_dynamics (bool): Enable power dynamics.
        enable_capital_risk (bool): Enable capital risk.
        savings_mean (float): Mean for daily savings rate.
        savings_std (float): Std for daily savings rate.
        risk_mean (float): Mean for risked capital rate.
        risk_std (float): Std for risked capital rate.
        c_knowledge_xfer (float): Knowledge transfer efficiency.
        base_daily_decay_rate (float): Base daily decay rate.
        decay_coeffs_map (dict): Decay coefficients per dimension.
        research_factor (float): Diminishing returns factor for knowledge.
        focus_noise_level (float): Magnitude of daily focus fluctuation.
        k_time (float): Coefficient for time's effect on pleasure.
        k_consumption (float): Coefficient for consumption's effect on pleasure.
        pleasure_time_exponent (float): Exponent for time's diminishing returns on pleasure.
        consumption_factor_mean (float): Mean of the base consumption factor distribution.
        consumption_factor_std (float): Std dev of the base consumption factor distribution.
        consumption_noise_std (float): Std dev of the daily noise on the consumption factor.
        use_gpu_if_available (bool): Use GPU if available.
        log_to_disk (bool): Log simulation state to disk.
        c_power_factor (float): Power effect on split.
        MaxRunTime (int): Number of days to run the simulation.
        batch_size (int): Batch size for simulation updates.
        update_rate (int): Number of days per update.
        plot_interval (int): Plot every N days.
        random_initial_portfolio (bool): If True, initialize each agent's portfolio randomly (pleasure capped between 0 and 1).
    """
    if dimensions is None:
        dimensions = ['production', 'knowledge', 'power']
    if decay_coeffs_map is None:
        decay_coeffs_map = {
            'production': 5.0,
            'knowledge': 0.01,
            'power': 5.0,
            'art': 2.0,
            'pleasure': 7.0,
            'default': 1.0,
        }
    sim = TimeVectorSimulationDiminishingReturns(
        data_folder=data_folder,
        N=N,
        dimensions=dimensions,
        enable_power_dynamics=enable_power_dynamics,
        enable_capital_risk=enable_capital_risk,
        savings_mean=savings_mean,
        savings_std=savings_std,
        risk_mean=risk_mean,
        risk_std=risk_std,
        c_knowledge_xfer=c_knowledge_xfer,
        base_daily_decay_rate=base_daily_decay_rate,
        decay_coeffs_map=decay_coeffs_map,
        research_factor=research_factor,
        art_leverage_exponent=art_leverage_exponent, 
        focus_noise_level=focus_noise_level,
        k_time=k_time,
        k_consumption=k_consumption,
        pleasure_time_exponent=pleasure_time_exponent,
        consumption_factor_mean=consumption_factor_mean,
        consumption_factor_std=consumption_factor_std,
        consumption_noise_std=consumption_noise_std,
        use_gpu_if_available=use_gpu_if_available,
        log_to_disk=log_to_disk,
        c_power_factor=c_power_factor,
        plot_interval=plot_interval,
        random_initial_portfolio=random_initial_portfolio
    )
    print("Running Time Vector Simulation...")
    sim.run_simulation_static(
        MaxRunTime=MaxRunTime,
        batch_size=batch_size,
        update_rate=update_rate,
        plot_interval=plot_interval
    )
    
    # Print final statistics
    print("\nFinal Statistics:")
    gini_coeffs = get_gini_coefficients(sim.Portfolios, sim.AgentWealth, sim.dimensions, sim.xp_module)
    for dim, gini in gini_coeffs.items():
        print(f"Gini coefficient for {dim}: {gini:.4f}")
    
    print(f"Average leverage: {get_average_leverage(sim.Portfolios, sim.dimensions, sim.c_leverage_factor, sim.xp_module):.4f}")

    # --- Create comprehensive and dynamic analysis plots ---
    n_dims = len(sim.dimensions)
    dims_no_pleasure = [d for d in sim.dimensions if d != 'pleasure']
    plot_tasks = []

    # 1. Distribution for each dimension except 'pleasure'
    for dim_name in dims_no_pleasure:
        plot_tasks.append(('dimension', dim_name))
    # 2. Dedicated pleasure plot if present
    if 'pleasure' in sim.dimensions:
        plot_tasks.append(('pleasure', None))
    # 3. Generalized scatter grid for all pairs (including pleasure)
    dims_all = list(sim.dimensions)
    n_pairs = len(dims_all) * (len(dims_all) - 1) // 2
    scatter_pairs = []
    for i in range(len(dims_all)):
        for j in range(i+1, len(dims_all)):
            scatter_pairs.append((dims_all[i], dims_all[j]))
    # Instead of a single scatter_pairs task, add one per pair
    for pair in scatter_pairs:
        plot_tasks.append(('scatter_pair', pair))
    # 4. Time series plots
    if sim.time_series_data['t']:
        plot_tasks.append(('avg_leverage', None))
        plot_tasks.append(('gini_coeffs', None))

    # Split into batches of 9
    max_plots_per_window = 9
    i = 0
    while i < len(plot_tasks):
        batch = plot_tasks[i:i+max_plots_per_window]
        n_plots = len(batch)
        ncols = 3
        nrows = (n_plots + ncols - 1) // ncols
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, nrows * 5))
        axes = axes.flatten()
        plot_idx = 0
        for task in batch:
            if plot_idx >= len(axes):
                break
            ax = axes[plot_idx]
            if task[0] == 'dimension':
                plotter.plot_dimension_distribution_on_axes(sim, task[1], ax)
            elif task[0] == 'pleasure':
                plotter.plot_pleasure_distribution(sim, ax=ax)
            elif task[0] == 'scatter_pair':
                dim_x, dim_y = task[1]
                x = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dim_x)])
                y = ensure_numpy(sim.Portfolios[:, sim.dimensions.index(dim_y)])
                ax.scatter(x, y, alpha=0.6, s=10)
                ax.set_xlabel(f'{dim_x.capitalize()}')
                ax.set_ylabel(f'{dim_y.capitalize()}')
                ax.set_title(f'{dim_x.capitalize()} vs {dim_y.capitalize()}')
                ax.grid(True, alpha=0.3)
                ax.set_xscale('log')
                ax.set_yscale('log')
            elif task[0] == 'avg_leverage':
                ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data['avg_leverage']), 'b-')
                ax.set_title('Average Leverage Over Time'); ax.set_xlabel('Time (days)')
                ax.set_ylabel('Average Leverage'); ax.grid(True, alpha=0.3)
            elif task[0] == 'gini_coeffs':
                for dim_name in sim.dimensions:
                    if f'gini_{dim_name}' in sim.time_series_data:
                        ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data[f'gini_{dim_name}']), label=dim_name.capitalize())
                if 'gini_total' in sim.time_series_data:
                    ax.plot(ensure_numpy(sim.time_series_data['t']), ensure_numpy(sim.time_series_data['gini_total']), label='Total', linestyle='--')
                ax.set_title('Gini Coefficients Over Time'); ax.set_xlabel('Time (days)')
                ax.set_ylabel('Gini Coefficient'); ax.legend(); ax.grid(True, alpha=0.3)
            plot_idx += 1
        # Hide any unused subplots
        for j in range(plot_idx, len(axes)):
            axes[j].set_visible(False)
        plt.tight_layout()
        plt.show(block=False)
        i += max_plots_per_window
    plt.show()
    return sim


if __name__ == "__main__":
    # Run example if script is executed directly
    sim = run_time_vector() 