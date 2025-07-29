# t.py

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import animation
from IPython.display import HTML # Keep for notebook compatibility if animation is run there

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
    cp = None  # Define cp as None when not available
    if not _gpu_message_printed:
        print("CuPy not found, using NumPy (CPU).")
        sys.modules['time_economy.base']._gpu_message_printed = True

# --- Global Variables ---
# data_folder is now set when instantiating simulations
# animation_ffmpeg_path is now an attribute of BaseWealthSimulation

# --- Helper Functions ---
def ensure_numpy(array):
    """Ensures an array is a NumPy array, converting from CuPy if necessary."""
    if xp_is_cupy and isinstance(array, cp.ndarray):
        return cp.asnumpy(array)
    return np.asarray(array) # Ensure it's a numpy array even if xp is numpy

def ensure_xp(array, current_xp_module):
    """Ensures an array is of the type used by the current xp module (cupy or numpy)."""
    if current_xp_module is cp and not isinstance(array, cp.ndarray):
        return cp.asarray(array)
    elif current_xp_module is np and not isinstance(array, np.ndarray):
        # This case might happen if loading numpy data and xp is numpy
        return np.asarray(array)
    return array

def custom_ecdf(data):
    """
    Custom ECDF implementation to replace statsmodels dependency
    """
    sorted_data = np.sort(data)
    n = len(sorted_data)
    # Create ECDF: F(x) = (number of values <= x) / n
    ecdf_values = np.arange(1, n + 1) / n
    return sorted_data, ecdf_values

def compute_wealth_distribution(data, fit_mode, bins=50, current_xp_module=None):
    '''computes distribution

        returns two pairs of variables:
            (x,y) for empirical distribution
            (X,Y) for lognormal PDF fit.
    '''
    if current_xp_module is None:
        current_xp_module = xp # Default to global xp

    # Ensure data is on CPU for certain operations or if it's simpler
    data_np = ensure_numpy(data)
    if len(data_np) == 0 or data_np.max() == data_np.min(): # Handle empty or all-same-value data
        return (None, None), (None, None)

    if fit_mode == 'lognormal':
        y_np, x_edges_np = np.histogram(data_np, bins=np.linspace(data_np.min(), data_np.max(), bins))
        x_np = x_edges_np[:-1] + np.diff(x_edges_np) / 2
        
        valid_indices = y_np > 0
        x_np = x_np[valid_indices]
        y_np = y_np[valid_indices]
        if y_np.sum() == 0: return (None, None), (None, None) # Avoid division by zero
        y_np = y_np / y_np.sum()

        mu_np = data_np.mean()
        sigma_np = data_np.std()

        # Convert back to xp arrays for calculation if desired, though PDF usually small
        X_fit = current_xp_module.asarray(x_np)
        Y_fit_np = np.zeros_like(x_np)

        if (mu_np != 0) and (sigma_np != 0) and len(X_fit) > 0 : # check X_fit not empty
             # Formula for lognormal PDF:
             # 1 / (x * sigma * sqrt(2 * pi)) * exp(- (ln(x) - mu)^2 / (2 * sigma^2))
             # The parameters mu and sigma here are for the underlying normal distribution
             # of log(data). We need to estimate them from data_np.
            log_data_np = np.log(data_np[data_np > 0]) # Avoid log(0)
            if len(log_data_np) > 1:
                mu_log = log_data_np.mean()
                sigma_log = log_data_np.std()
                if sigma_log > 0: # Check for zero standard deviation in log space
                    # Use the definition of lognormal PDF based on parameters of the log data
                    Y_fit_np = 1.0 / (x_np * sigma_log * np.sqrt(2 * np.pi)) * \
                               np.exp(-(np.log(x_np) - mu_log)**2 / (2 * sigma_log**2))
                    if Y_fit_np.sum() > 0: # Avoid division by zero if all Y_fit_np are zero
                        Y_fit_np = Y_fit_np / Y_fit_np.sum()
                    else:
                        Y_fit_np = np.zeros_like(x_np) # Or handle as appropriate
                else: # If sigma_log is 0, it's a degenerate distribution
                    Y_fit_np = np.zeros_like(x_np) # Fallback, or assign to empirical
            else: # Not enough data points for lognormal fit
                Y_fit_np = np.zeros_like(x_np)
        else: # Fallback if mu or sigma is zero or X_fit is empty
            X_fit_np, Y_fit_np = x_np, y_np
            X_fit = current_xp_module.asarray(X_fit_np) # Ensure X_fit is xp array

        return (x_np, y_np), (ensure_numpy(X_fit), Y_fit_np)


    elif fit_mode == 'exponential':
        y_np, x_edges_np = np.histogram(data_np, bins=np.linspace(data_np.min(), data_np.max(), bins))
        x_np = x_edges_np[:-1] + np.diff(x_edges_np) / 2

        valid_indices = y_np > 0
        x_np = x_np[valid_indices]
        y_np = y_np[valid_indices]
        if y_np.sum() == 0: return (None, None), (None, None)
        y_np = y_np / y_np.sum()

        mu_np = data_np.mean()
        X_fit_np = x_np
        Y_fit_np = np.zeros_like(x_np)

        if mu_np > 0 and len(X_fit_np) > 0: # mu must be positive for exponential
            Y_fit_np = (1.0 / mu_np) * np.exp(-X_fit_np / mu_np)
            if Y_fit_np.sum() > 0:
                 Y_fit_np = Y_fit_np / Y_fit_np.sum()
            else:
                Y_fit_np = np.zeros_like(x_np)
        else:
            Y_fit_np = y_np # Fallback to empirical if mu is not positive or X_fit is empty

        return (x_np, y_np), (X_fit_np, Y_fit_np)

    elif fit_mode == 'powerlaw':
        if len(np.unique(data_np)) > 1:
            # Replace statsmodels ECDF with custom implementation
            try:
                # Try statsmodels first (if available)
                from statsmodels.distributions.empirical_distribution import ECDF
                ecdf = ECDF(data_np)
                x_ecdf_np, y_ecdf_np = ecdf.x, ecdf.y
            except ImportError:
                # Fallback to custom ECDF implementation
                x_ecdf_np, y_ecdf_np = custom_ecdf(data_np)
            
            # Ensure ecdf.x and ecdf.y have more than 2 elements for slicing [1:-1]
            if len(x_ecdf_np) <= 2 or len(y_ecdf_np) <= 2:
                return (None, None), (None, None)

            x_ecdf_np, y_ecdf_complement_np = x_ecdf_np[1:-1], 1 - y_ecdf_np[1:-1]
            
            # Filter out non-positive values for log and ensure y_ecdf_complement_np is also positive
            valid_fit_indices = (x_ecdf_np > 0) & (y_ecdf_complement_np > 0) & (x_ecdf_np >= data_np.mean())
            
            if np.sum(valid_fit_indices) < 2:  # Need at least 2 points for polyfit
                # Fallback or return no fit
                if len(x_ecdf_np) > 0 and len(y_ecdf_complement_np) > 0:
                    return (x_ecdf_np, y_ecdf_complement_np), (x_ecdf_np, y_ecdf_complement_np)  # Return empirical as fit
                else:
                    return (None, None), (None, None)

            log_x_fit_np = np.log10(x_ecdf_np[valid_fit_indices])
            log_y_fit_np = np.log10(y_ecdf_complement_np[valid_fit_indices])
            
            P_np = np.polyfit(log_x_fit_np, log_y_fit_np, 1)

            # For plotting the fit, use the range of x_ecdf_np where x > 0
            X_fit_np = x_ecdf_np[x_ecdf_np > 0]
            if len(X_fit_np) == 0:  # if no x values for fit
                return (x_ecdf_np, y_ecdf_complement_np), (None, None)

            Y_fit_np = 10**np.polyval(P_np, np.log10(X_fit_np))
            # Normalize Y_fit for CCDF interpretation, though often plotted as is for power law
            # For consistency with other modes, if we want PDF-like sum:
            # if Y_fit_np.sum() > 0: Y_fit_np = Y_fit_np / Y_fit_np.sum()

            return (x_ecdf_np, y_ecdf_complement_np), (X_fit_np, Y_fit_np)
        else:
            return (None, None), (None, None)
    return (None,None), (None,None)


class BaseWealthSimulation():
    def __init__(self, data_folder, N, fit_mode, use_gpu_if_available=True, log_to_disk=False):
        '''
            data_folder - the name of the folder in which the model run will be logged.
        '''
        self.xp_module = cp if xp_is_cupy and use_gpu_if_available else np
        self.using_gpu = self.xp_module is cp and cp is not None

        # %matplotlib inline # This is an IPython magic, not needed in .py, handled by calling script/notebook
        # import os, matplotlib.pyplot as plt, numpy as np # Already imported

        self.data_folder = data_folder
        if self.data_folder and not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder, exist_ok=True)

        self.N = N
        self.t = 0
        self.AgentWealth = None # To be initialized by child as xp_module array

        self.fit_mode = fit_mode
        self.log_file_name = None # The name is simulation-specific, set by child

        # Initialize figure for animations (if used)
        self.fig, self.ax = plt.subplots(figsize=(9, 9))
        self.line_data = None
        self.line_fit = None

        self.animation = None
        # User-provided path for ffmpeg
        self.animation_ffmpeg_path = r"C:\Users\mikin\anaconda3\envs\keras_env\Library\bin\ffmpeg.exe"
        # self.animation_ffmpeg_path = r"c:\Program Files\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe" # Original path

        self.logged_data = None # For replaying logs
        self.log_to_disk = log_to_disk

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

    def log_wealth_distribution(self):
        '''
            Writes another line into the log file.
            Every update is stored as a tuple: (time, numpy array of wealth).
        '''
        if not self.log_to_disk:
            return
        if self.log_file_name is not None:
            if (self.t == 0) and (os.path.isfile(self.log_file_name)):
                try:
                    os.remove(self.log_file_name)
                except OSError as e:
                    print(f"Warning: Could not remove existing log file {self.log_file_name}: {e}")

            # Ensure AgentWealth is a NumPy array for pickling
            agent_wealth_np = ensure_numpy(self.AgentWealth)
            try:
                with open(self.log_file_name, 'ab') as f:
                    pickle.dump((self.t, agent_wealth_np), f)
            except Exception as e:
                print(f"Error writing to log file {self.log_file_name}: {e}")


    def plot_wealth_distribution(self, static_plot=False):
        # AgentWealth can be CuPy or NumPy, compute_wealth_distribution handles conversion
        (x,y), (X_fit,Y_fit) = compute_wealth_distribution(
            data=self.AgentWealth, 
            fit_mode=self.fit_mode, 
            bins=50,
            current_xp_module=self.xp_module
        )

        if x is not None and y is not None : # Check if empirical data is valid
            if static_plot: # For non-animation plotting
                self.ax.clear() # Clear previous static plot content
                self.ax.plot(x, y, 'bo-', label='Empirical')
                if X_fit is not None and Y_fit is not None:
                    self.ax.plot(X_fit, Y_fit, 'r--', label=f'{self.fit_mode} fit')
                self.ax.set_title(f"Wealth Distribution at t={self.t} (N={self.N})")
                self.ax.set_xlabel("Wealth")
                self.ax.set_ylabel("Probability Density / CCDF")
                if self.fit_mode == 'powerlaw':
                    self.ax.set_xscale('log')
                    self.ax.set_yscale('log')
                else: # reset scales if not powerlaw
                    self.ax.set_xscale('linear')
                    self.ax.set_yscale('linear')

                # Set limits carefully, handling potential empty arrays or single points
                y_min_val = np.min(y) if len(y)>0 else 0
                y_max_val = np.max(y) if len(y)>0 else 1
                x_min_val = np.min(x) if len(x)>0 else 0
                x_max_val = np.max(x) if len(x)>0 else 1

                if Y_fit is not None and len(Y_fit)>0:
                    y_min_val = np.min([y_min_val, np.min(Y_fit)])
                    y_max_val = np.max([y_max_val, np.max(Y_fit)])
                if X_fit is not None and len(X_fit)>0:
                    x_min_val = np.min([x_min_val, np.min(X_fit)])
                    x_max_val = np.max([x_max_val, np.max(X_fit)])
                
                # Add small buffer to avoid tight limits, ensure min < max
                y_buffer = (y_max_val - y_min_val) * 0.05 if (y_max_val - y_min_val) > 1e-9 else 0.1
                x_buffer = (x_max_val - x_min_val) * 0.05 if (x_max_val - x_min_val) > 1e-9 else 0.1

                # For log scale, ensure positive limits
                if self.fit_mode == 'powerlaw':
                    y_min_lim = max(1e-9, y_min_val - y_buffer)
                    x_min_lim = max(1e-9, x_min_val - x_buffer)
                    self.ax.set_ylim((y_min_lim, y_max_val + y_buffer if y_max_val > 0 else 0.1))
                    self.ax.set_xlim((x_min_lim, x_max_val + x_buffer if x_max_val > 0 else 0.1))
                else:
                    self.ax.set_ylim((max(0, y_min_val - y_buffer), y_max_val + y_buffer if y_max_val > 0 else 0.1))
                    self.ax.set_xlim((max(0, x_min_val - x_buffer), x_max_val + x_buffer if x_max_val > 0 else 0.1))
                self.ax.legend()
                # For static plot, fig might need to be returned or shown by caller
            else: # For animation
                if self.line_data is None or self.line_fit is None: # Initialize lines if not done
                     self.line_data, = self.ax.plot([], [], 'bo-', label='Empirical')
                     self.line_fit, = self.ax.plot([], [], 'r--', label=f'{self.fit_mode} fit')
                     self.ax.legend()


                self.line_data.set_data(x, y)
                if X_fit is not None and Y_fit is not None:
                    self.line_fit.set_data(X_fit, Y_fit)
                else: # Clear fit line if no fit data
                    self.line_fit.set_data([],[])


                # Dynamic axis scaling for animations
                all_y = ensure_numpy(y)
                all_x = ensure_numpy(x)
                if Y_fit is not None: all_y = np.concatenate((all_y, ensure_numpy(Y_fit)))
                if X_fit is not None: all_x = np.concatenate((all_x, ensure_numpy(X_fit)))
                
                all_y_clean = all_y[np.isfinite(all_y) & (all_y > 0)] # filter out non-positives for log scale
                all_x_clean = all_x[np.isfinite(all_x) & (all_x > 0)]

                if self.fit_mode == 'powerlaw':
                    self.ax.set_xscale('log')
                    self.ax.set_yscale('log')
                    # For log scale, ensure limits are positive
                    y_min_lim = np.min(all_y_clean) * 0.9 if len(all_y_clean) > 0 else 1e-5
                    y_max_lim = np.max(all_y_clean) * 1.1 if len(all_y_clean) > 0 else 1
                    x_min_lim = np.min(all_x_clean) * 0.9 if len(all_x_clean) > 0 else 1e-2
                    x_max_lim = np.max(all_x_clean) * 1.1 if len(all_x_clean) > 0 else 100
                    self.ax.set_ylim((max(1e-9, y_min_lim), y_max_lim)) # Avoid zero or negative for log
                    self.ax.set_xlim((max(1e-9, x_min_lim), x_max_lim))
                else:
                    self.ax.set_xscale('linear')
                    self.ax.set_yscale('linear')
                    self.ax.set_ylim((np.min(all_y)*0.9 if len(all_y)>0 else 0, np.max(all_y)*1.1 if len(all_y)>0 else 1))
                    self.ax.set_xlim((np.min(all_x)*0.9 if len(all_x)>0 else 0, np.max(all_x)*1.1 if len(all_x)>0 else 1))
        else: # No valid data to plot
            if static_plot:
                self.ax.clear()
                self.ax.set_title(f"No data to plot at t={self.t}")
            elif self.line_data is not None: # Clear animation lines
                self.line_data.set_data([],[])
                self.line_fit.set_data([],[])


    def initialize_wealth_distribution(self):
        # This method MUST be implemented by the child class.
        # It should initialize self.AgentWealth as an self.xp_module array.
        raise NotImplementedError("Child class must implement initialize_wealth_distribution.")

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        # This method MUST be implemented by the child class.
        # It should update self.AgentWealth (an self.xp_module array) and self.t.
        raise NotImplementedError("Child class must implement update_wealth_distribution.")

    def init_simulation_animation(self): # Renamed to avoid conflict if a static init is needed
        self.initialize_wealth_distribution()
        if self.log_to_disk:
            self.log_wealth_distribution()
        self.line_data, = self.ax.plot([], [], 'bo-', label='Empirical') # note the comma for Line2D
        self.line_fit, = self.ax.plot([], [], 'r--', label=f'{self.fit_mode} fit')
        self.ax.legend()
        if self.fit_mode == 'powerlaw': # Set scales initially
            self.ax.set_xscale('log')
            self.ax.set_yscale('log')
        return (self.line_data, self.line_fit)

    def update_simulation_animation(self, batch_index, update_rate, batch_size): # Renamed
        self.update_wealth_distribution(batch_index, update_rate, batch_size) # Implemented by child
        if self.log_to_disk:
            self.log_wealth_distribution()
        self.plot_wealth_distribution(static_plot=False) # Call animation plotting
        self.ax.set_title(f"t={self.t}, N={self.N}, GPU={'Yes' if self.using_gpu else 'No'}")
        return (self.line_data, self.line_fit)

    def run_simulation_animation(self, MaxRunTime, batch_size, update_rate):
        if plt.get_backend() == 'agg': # If running in a non-GUI backend, animation won't show
            print("Warning: Matplotlib backend is 'agg'. Animation will not be displayed interactively.")
            print("Consider running in a Jupyter Notebook or a script with interactive backend for live animation.")

        # Ensure ffmpeg path is set for saving animations
        plt.rcParams['animation.ffmpeg_path'] = self.animation_ffmpeg_path
        if not os.path.exists(self.animation_ffmpeg_path):
             print(f"Warning: FFMPEG not found at {self.animation_ffmpeg_path}. Saving animation will fail.")


        self.animation = animation.FuncAnimation(self.fig,
                                                 self.update_simulation_animation,
                                                 init_func=self.init_simulation_animation,
                                                 fargs=(update_rate, batch_size),
                                                 frames=int(MaxRunTime / update_rate),
                                                 interval=200, blit=False, repeat=True) # Blit=False often more stable
        return self.display_animation() # display_animation handles HTML conversion for notebooks

    def run_simulation_static(self, MaxRunTime, batch_size, update_rate, plot_interval=None):
        """Runs simulation and logs data. Optionally plots final state or at intervals."""
        self.initialize_wealth_distribution()
        if self.log_to_disk:
            self.log_wealth_distribution()

        if plot_interval is None: # Default: plot only at the end
            plot_interval = MaxRunTime + 1 # Effectively never plot during run

        num_updates = int(MaxRunTime / update_rate)
        for i in range(num_updates):
            self.update_wealth_distribution(i, update_rate, batch_size) # Child implements this
            if self.log_to_disk:
                self.log_wealth_distribution()
            if (i + 1) * update_rate % plot_interval == 0 or i == num_updates -1 :
                print(f"Static run: t={self.t}")
                # self.plot_wealth_distribution(static_plot=True) # Optionally plot snapshot
                # plt.pause(0.1) # For brief display if in interactive mode

        print(f"Simulation finished at t={self.t}. Final distribution logged.")
        self.plot_wealth_distribution(static_plot=True) # Plot final state
        # plt.show() # Caller should handle plt.show() if running .py script

    def display_animation(self):
        # %matplotlib inline # Handled by notebook environment
        # import matplotlib.pyplot as plt # Already imported
        plt.rcParams['animation.ffmpeg_path'] = self.animation_ffmpeg_path
        # from IPython.display import HTML # Already imported
        if self.animation is not None:
            try:
                return HTML(self.animation.to_html5_video())
            except Exception as e:
                print(f"Error generating HTML5 video for animation: {e}")
                print("Ensure ffmpeg is correctly installed and configured.")
                return None
        return None

    def load_log_data(self):
        if self.log_file_name and os.path.isfile(self.log_file_name):
            file_size = os.path.getsize(self.log_file_name)
            if file_size == 0:
                print(f"Log file {self.log_file_name} is empty.")
                self.logged_data = None
                return False

            self.logged_data = {}
            try:
                with open(self.log_file_name, 'rb') as in_file:
                    while in_file.tell() < file_size:
                        try:
                            data_entry = pickle.load(in_file)
                            self.logged_data[data_entry[0]] = data_entry[1] # data_entry[1] is already numpy
                        except EOFError:
                            print(f"Warning: Reached EOF unexpectedly while reading {self.log_file_name}. Log might be incomplete.")
                            break
                        except Exception as e:
                            print(f"Error loading entry from log file {self.log_file_name}: {e}")
                            continue # Try to load next entry
                if not self.logged_data: # if dict is still empty after trying
                    print(f"No valid data loaded from {self.log_file_name}.")
                    return False

                self.t = 0 # Reset internal time for replay
                # AgentWealth is set from logged_data (NumPy) and converted to xp_module type
                self.AgentWealth = ensure_xp(self.logged_data[self.t], self.xp_module)
                return True
            except Exception as e:
                print(f"Failed to load log data from {self.log_file_name}: {e}")
                self.logged_data = None
                return False
        else:
            print(f"Log file {self.log_file_name} not found.")
            return False


    def init_log_replay_animation(self): # Renamed
        self.line_data, = self.ax.plot([], [], 'bo-', label='Empirical')
        self.line_fit, = self.ax.plot([], [], 'r--', label=f'{self.fit_mode} fit')
        self.ax.legend()
        if self.fit_mode == 'powerlaw': # Set scales initially
            self.ax.set_xscale('log')
            self.ax.set_yscale('log')
        return (self.line_data, self.line_fit)

    def update_log_replay_animation(self, t_key): # Renamed, t_key is a key from logged_data
        self.t = t_key
        # Logged data is NumPy, convert to current xp_module type
        self.AgentWealth = ensure_xp(self.logged_data[self.t], self.xp_module)
        self.plot_wealth_distribution(static_plot=False) # Animation plot
        self.ax.set_title(f"Replay: t={self.t}, N={self.N}, GPU={'Yes' if self.using_gpu else 'No'}")
        return (self.line_data, self.line_fit)

    def replay_animation_from_log(self):
        plt.rcParams['animation.ffmpeg_path'] = self.animation_ffmpeg_path
        if not os.path.exists(self.animation_ffmpeg_path):
             print(f"Warning: FFMPEG not found at {self.animation_ffmpeg_path}. Saving animation will fail.")

        if self.load_log_data():
            if not self.logged_data: # Check if logged_data actually got populated
                print("No data in log to replay.")
                return None
            ts = sorted(self.logged_data.keys())
            if not ts:
                print("No time steps in logged data to replay.")
                return None

            self.animation = animation.FuncAnimation(self.fig,
                                                     self.update_log_replay_animation,
                                                     init_func=self.init_log_replay_animation,
                                                     frames=ts, interval=200, blit=False, repeat=True)
            return self.display_animation()
        else:
            return None

    def show_simulation_animation(self, MaxRunTime, batch_size, update_rate):
        # Tries to replay. If log doesn't exist or fails, runs the simulation.
        print(f"Attempting to replay animation from log: {self.log_file_name}")
        anim_obj = self.replay_animation_from_log()
        if anim_obj is None:
            print(f"Log replay failed or log not found. Running new simulation animation...")
            anim_obj = self.run_simulation_animation(MaxRunTime, batch_size, update_rate)
        return anim_obj


# --- Model Implementations ---

class WealthSimulationModel3(BaseWealthSimulation):
    def __init__(self, data_folder, N, MeanWealth, Lambda, use_gpu_if_available=True):
        super().__init__(data_folder, N, fit_mode='exponential', use_gpu_if_available=use_gpu_if_available)
        self.MeanWealth = MeanWealth
        self.Lambda = Lambda # This is a scalar
        log_fn = f"WealthDistM3_N{self.N:08d}_MW{self.MeanWealth:0.2f}_L{self.Lambda:0.2f}.log.pickle"
        self.log_file_name = os.path.join(self.data_folder, log_fn) if self.data_folder else None
        print(f"Model 3 log file: {self.log_file_name}")


    def initialize_wealth_distribution(self):
        self.AgentWealth = self.xp_module.full(shape=(self.N,), fill_value=self.MeanWealth, dtype=np.float32)
        self.t = 0 # Reset time on initialization

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        # In this model, batch_index isn't directly used in the loop logic itself,
        # but is standard for FuncAnimation. update_rate determines sim steps per anim frame.
        for _ in range(update_rate): # Simulate `update_rate` steps
            if self.N < 2 : continue # Need at least 2 agents

            # Ensure batch_size is not larger than N/2 if replace=False for pairs
            actual_batch_size = min(batch_size, self.N // 2)
            if actual_batch_size <=0: continue


            ids_indices = self.xp_module.random.choice(self.N, size=(actual_batch_size, 2), replace=False)
            
            # Ensure ids_indices is correctly shaped if xp_module is cupy, cupy.random.choice might behave differently
            # For CuPy, if N is small, it might return fewer than requested if replace=False.
            if ids_indices.shape[0] == 0: continue # No pairs selected

            agents_i_wealth = self.AgentWealth[ids_indices[:, 0]]
            agents_j_wealth = self.AgentWealth[ids_indices[:, 1]]

            epsilon = self.xp_module.random.uniform(low=0.0, high=1.0, size=(ids_indices.shape[0],))

            newWealth_i = self.Lambda * agents_i_wealth + \
                          (1 - self.Lambda) * epsilon * (agents_i_wealth + agents_j_wealth)
            newWealth_j = self.Lambda * agents_j_wealth + \
                          (1 - self.Lambda) * (1 - epsilon) * (agents_i_wealth + agents_j_wealth)

            self.AgentWealth[ids_indices[:, 0]] = newWealth_i
            self.AgentWealth[ids_indices[:, 1]] = newWealth_j
            self.t += 1


class WealthSimulationModel5(BaseWealthSimulation):
    def __init__(self, data_folder, N, MeanWealth, MaxLambda=1.0, p_0=0.05, use_gpu_if_available=True):
        super().__init__(data_folder, N, fit_mode='powerlaw', use_gpu_if_available=use_gpu_if_available)
        self.MeanWealth = MeanWealth
        self.MaxLambda = MaxLambda
        self.p_0 = p_0

        self.Lambda_dist = self.xp_module.zeros(shape=(self.N,), dtype=np.float32)
        num_saving_agents = int(np.round(self.N * self.p_0))
        
        if num_saving_agents > 0 and self.N > 0:
            # Use numpy for choice if N is small and xp_module is cupy to ensure correct behavior with replace=False
            # or handle potential smaller array from cupy.random.choice.
            # For simplicity, using numpy for this selection part.
            saving_user_indices_np = np.random.choice(np.arange(self.N), num_saving_agents, replace=False).astype(np.int32)
            saving_user_indices = self.xp_module.asarray(saving_user_indices_np)
            
            self.Lambda_dist[saving_user_indices] = self.xp_module.random.uniform(low=0, high=self.MaxLambda,
                                                                             size=saving_user_indices.shape)
        
        log_fn = f"WealthDistM5_N{self.N:08d}_MW{self.MeanWealth:0.2f}_MaxL{self.MaxLambda:0.2f}_p0_{self.p_0:0.3f}.log.pickle"
        self.log_file_name = os.path.join(self.data_folder, log_fn) if self.data_folder else None
        print(f"Model 5 log file: {self.log_file_name}")

        # Specific plot styling for powerlaw from notebook
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')
        # Initial limits might need adjustment based on typical data ranges for powerlaw
        # These are illustrative, plot_wealth_distribution will try to set them dynamically
        # self.ax.set_xlim([1e-1, 1e3]) 
        # self.ax.set_ylim([1e-5, 1])


    def initialize_wealth_distribution(self):
        self.AgentWealth = self.xp_module.full(shape=(self.N,), fill_value=self.MeanWealth, dtype=np.float32)
        self.t = 0 # Reset time

    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        for _ in range(update_rate):
            if self.N < 2: continue
            actual_batch_size = min(batch_size, self.N // 2)
            if actual_batch_size <=0: continue

            ids_indices = self.xp_module.random.choice(self.N, size=(actual_batch_size, 2), replace=False)
            if ids_indices.shape[0] == 0: continue


            agents_i_indices = ids_indices[:, 0]
            agents_j_indices = ids_indices[:, 1]

            agents_i_wealth = self.AgentWealth[agents_i_indices]
            agents_j_wealth = self.AgentWealth[agents_j_indices]
            lambda_i = self.Lambda_dist[agents_i_indices]
            lambda_j = self.Lambda_dist[agents_j_indices]

            epsilon = self.xp_module.random.uniform(low=0.0, high=1.0, size=(ids_indices.shape[0],))
            
            # Original formula from notebook:
            # dx = (1-epsilon)*(1-self.Lambda[ ids[:,0] ])*self.AgentWealth[ ids[:,0] ] - epsilon*(1-self.Lambda[ ids[:,1] ])*self.AgentWealth[ ids[:,1] ]
            # self.AgentWealth[ ids[:,0] ] = self.AgentWealth[ ids[:,0] ]  - dx
            # self.AgentWealth[ ids[:,1] ] = self.AgentWealth[ ids[:,1] ]  + dx
            # This dx is change in agent i's wealth from non-saved part of j, and vice versa.
            
            # Let's re-verify the update rule for model 5 (heterogenous savings)
            # From notebook: "x_i` = lambda_i * x_i + epsilon * [ (1-lambda_i)x_i + (1-lambda_j)x_j]"
            # This seems to be the intended one rather than the dx formulation for conserved sum.
            # The dx formulation implies:
            # x_i' = x_i - [(1-eps)(1-lam_i)x_i - eps(1-lam_j)x_j]
            #      = eps(1-lam_i)x_i + lam_i x_i + eps(1-lam_j)x_j
            # x_j' = x_j + [(1-eps)(1-lam_i)x_i - eps(1-lam_j)x_j]
            #      = (1-eps)(1-lam_i)x_i + (1-eps)(1-lam_j)x_j + lam_j x_j + eps x_j
            # This looks a bit complex and the sum (x_i' + x_j') is conserved if all terms match.
            # Let's use the dx from the notebook code for model 4/5, which is:
            # dx = (1-epsilon) * (1-lambda_i) * agents_i_wealth - epsilon * (1-lambda_j) * agents_j_wealth
            # This means agent i gives (1-epsilon)*(1-lambda_i)*agents_i_wealth and receives epsilon*(1-lambda_j)*agents_j_wealth
            # No, dx is the net amount agent i *loses* to agent j from the shared pot.
            # Shared pot = (1-lambda_i)x_i + (1-lambda_j)x_j
            # Agent i gets: lambda_i*x_i + epsilon * Shared_pot
            # Agent j gets: lambda_j*x_j + (1-epsilon) * Shared_pot
            # This is the standard formulation.
            # The notebook's dx formulation:
            # dx = (1-epsilon)*(1-lambda_i)*X_i - epsilon*(1-lambda_j)*X_j
            # X_i' = X_i - dx
            # X_j' = X_j + dx
            # Sum X_i' + X_j' = X_i + X_j (conserved)
            # This means that the amount (1-lambda_i)*X_i from agent i and (1-lambda_j)*X_j from agent j
            # are pooled. From this pool, agent i effectively gets epsilon fraction of j's contribution
            # and keeps epsilon fraction of its own contribution.
            # Let's stick to the notebook's dx formulation for WealthSimulationModel4 and 5 as it's explicitly coded.
            
            dx = (1 - epsilon) * (1 - lambda_i) * agents_i_wealth - \
                 epsilon * (1 - lambda_j) * agents_j_wealth

            self.AgentWealth[agents_i_indices] = agents_i_wealth - dx
            self.AgentWealth[agents_j_indices] = agents_j_wealth + dx
            self.t += 1
            
            
def gini_coefficient(wealth_array, current_xp_module=None):
    """Calculates the Gini coefficient for a wealth array."""
    if current_xp_module is None:
        current_xp_module = xp # Use global xp if not specified
    
    # Ensure array is numpy and 1D for Gini calculation
    wealth_np = ensure_numpy(wealth_array).flatten()
    
    if len(wealth_np) == 0:
        return np.nan
    
    # Values must be non-negative for Gini; clamp if necessary
    if np.any(wealth_np < 0):
        # print("Warning: Gini calculation received negative wealth values. Clamping to 0.")
        wealth_np = np.maximum(wealth_np, 0)

    # Gini requires sorted data
    sorted_wealth = np.sort(wealth_np) # Use numpy for sorting after conversion
    n = len(sorted_wealth)
    
    if n == 0: return np.nan
        
    cumulative_wealth_sum = np.sum(sorted_wealth)
    if cumulative_wealth_sum == 0: # All wealth is zero or no wealth
        return 0.0 
    
    # Using the direct formula for sorted array:
    # Gini = (sum_{i=1 to n} (2*i - n - 1) * x_i) / (n * sum(x_i))
    index = np.arange(1, n + 1) # Create index array using numpy
    gini = (np.sum((2 * index - n - 1) * sorted_wealth)) / (n * cumulative_wealth_sum)
    return gini

class WealthSimulationModel5_tax(BaseWealthSimulation):
    def __init__(self, data_folder, N, MeanWealth, MaxLambda=1.0, p_0=0.05, 
                 use_gpu_if_available=True,
                 # Taxation parameters
                 tax_rate=0.0,  # e.g., 0.05 for 5%
                 tax_rich_threshold_percentile=99.0, # Percentile to define "rich" (e.g., 99 means top 1%)
                 tax_distribute_poor_percentile=20.0, # Percentile to define "poor" (e.g., 20 means bottom 20%)
                 tax_frequency=0): # How often to apply tax (e.g., every 100 sim steps 't'. 0 = no tax)
        
        super().__init__(data_folder, N, fit_mode='powerlaw', use_gpu_if_available=use_gpu_if_available)
        self.MeanWealth = MeanWealth
        self.MaxLambda = MaxLambda
        self.p_0 = p_0

        # Lambda distribution (heterogenous savings)
        self.Lambda_dist = self.xp_module.zeros(shape=(self.N,), dtype=np.float32)
        num_saving_agents = int(np.round(self.N * self.p_0))
        if num_saving_agents > 0 and self.N > 0:
            saving_user_indices_np = np.random.choice(np.arange(self.N), num_saving_agents, replace=False).astype(np.int32)
            saving_user_indices = self.xp_module.asarray(saving_user_indices_np)
            self.Lambda_dist[saving_user_indices] = self.xp_module.random.uniform(
                low=0, high=self.MaxLambda, size=saving_user_indices.shape
            )
        
        # Store taxation parameters
        self.tax_rate = tax_rate
        self.tax_rich_threshold_percentile = tax_rich_threshold_percentile
        self.tax_distribute_poor_percentile = tax_distribute_poor_percentile
        self.tax_frequency = tax_frequency

        # Update log file name to include tax parameters if taxation is active
        log_fn_base = f"WealthDistM5_N{self.N:08d}_MW{self.MeanWealth:0.2f}_MaxL{self.MaxLambda:0.2f}_p0_{self.p_0:0.3f}"
        if self.tax_rate > 0 and self.tax_frequency > 0:
            log_fn_tax = (f"_TaxR{self.tax_rate:.3f}_RichP{self.tax_rich_threshold_percentile:.0f}_"
                          f"PoorP{self.tax_distribute_poor_percentile:.0f}_TFreq{self.tax_frequency}")
            log_fn_base += log_fn_tax
        log_fn = f"{log_fn_base}.log.pickle"
        self.log_file_name = os.path.join(self.data_folder, log_fn) if self.data_folder else None
        # print(f"Model 5 log file: {self.log_file_name}") # Moved to run_analysis for clarity

        # Plot styling for powerlaw (from BaseWealthSimulation or here)
        self.ax.set_xscale('log')
        self.ax.set_yscale('log')

    def initialize_wealth_distribution(self):
        self.AgentWealth = self.xp_module.full(shape=(self.N,), fill_value=self.MeanWealth, dtype=np.float32)
        self.t = 0

    def _apply_taxation(self):
        if self.N == 0 or self.tax_rate == 0: return

        # Work on a copy for percentile calculations to reflect state before this step's taxation
        # However, sequential application is also valid. For simplicity, operate on self.AgentWealth.
        
        # Determine rich threshold (wealth value above which agents are taxed)
        # Ensure AgentWealth is 1D for percentile
        rich_wealth_threshold = self.xp_module.percentile(self.AgentWealth, self.tax_rich_threshold_percentile)
        
        rich_agents_mask = (self.AgentWealth >= rich_wealth_threshold)
        rich_agents_indices = self.xp_module.where(rich_agents_mask)[0]
        
        total_tax_collected = self.xp_module.array(0.0, dtype=np.float32)

        if len(rich_agents_indices) > 0:
            wealth_of_rich_agents = self.AgentWealth[rich_agents_indices]
            tax_from_each_rich_agent = wealth_of_rich_agents * self.tax_rate
            total_tax_collected = self.xp_module.sum(tax_from_each_rich_agent)
            
            # Apply tax
            self.AgentWealth[rich_agents_indices] -= tax_from_each_rich_agent
        
        if total_tax_collected > 0:
            # Determine poor threshold (wealth value below which agents receive tax benefits)
            # Use current wealth distribution *after* taxing the rich for identifying poor
            poor_wealth_threshold = self.xp_module.percentile(self.AgentWealth, self.tax_distribute_poor_percentile)
            
            poor_agents_mask = (self.AgentWealth <= poor_wealth_threshold)
            poor_agents_indices = self.xp_module.where(poor_agents_mask)[0]

            num_poor_agents = len(poor_agents_indices)
            if num_poor_agents > 0:
                tax_share_per_poor_agent = total_tax_collected / num_poor_agents
                self.AgentWealth[poor_agents_indices] += tax_share_per_poor_agent
            # else:
                # If no "poor" agents found by this definition, the collected tax effectively
                # reduces the total wealth in the system (like government spending outside this model).
                # This is an acceptable interpretation of "taxation".

        # Ensure wealth doesn't go negative
        self.AgentWealth = self.xp_module.maximum(self.AgentWealth, 0)


    def update_wealth_distribution(self, batch_index, update_rate, batch_size):
        for _ in range(update_rate): # Simulate `update_rate` micro-steps
            if self.N < 2: continue
            actual_batch_size = min(batch_size, self.N // 2)
            if actual_batch_size <= 0: continue

            ids_indices = self.xp_module.random.choice(self.N, size=(actual_batch_size, 2), replace=False)
            if ids_indices.shape[0] == 0: continue

            agents_i_indices = ids_indices[:, 0]
            agents_j_indices = ids_indices[:, 1]

            agents_i_wealth = self.AgentWealth[agents_i_indices]
            agents_j_wealth = self.AgentWealth[agents_j_indices]
            lambda_i = self.Lambda_dist[agents_i_indices]
            lambda_j = self.Lambda_dist[agents_j_indices]

            epsilon = self.xp_module.random.uniform(low=0.0, high=1.0, size=(ids_indices.shape[0],))
            
            dx = (1 - epsilon) * (1 - lambda_i) * agents_i_wealth - \
                 epsilon * (1 - lambda_j) * agents_j_wealth

            self.AgentWealth[agents_i_indices] = agents_i_wealth - dx
            self.AgentWealth[agents_j_indices] = agents_j_wealth + dx
            
            self.t += 1 # Increment global simulation time

            # Apply taxation periodically
            if self.tax_rate > 0 and self.tax_frequency > 0 and self.t > 0 and self.t % self.tax_frequency == 0:
                self._apply_taxation()