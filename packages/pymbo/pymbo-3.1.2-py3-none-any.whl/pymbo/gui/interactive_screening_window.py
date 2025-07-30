"""
Interactive SGLBO Screening Execution Window

Provides an interactive interface where users manually input experimental results
and the software suggests the next experiments iteratively.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np

logger = logging.getLogger(__name__)


class InteractiveScreeningWindow:
    """
    Interactive execution window for SGLBO screening optimization.
    Users manually input experimental results and get iterative suggestions.
    """
    
    def __init__(self, parent, screening_optimizer, results_manager, design_generator, config):
        """
        Initialize the interactive screening window.
        
        Args:
            parent: Parent window
            screening_optimizer: SGLBO screening optimizer instance
            results_manager: Screening results manager instance  
            design_generator: Design space generator instance
            config: Screening configuration dictionary
        """
        self.parent = parent
        self.screening_optimizer = screening_optimizer
        self.results_manager = results_manager
        self.design_generator = design_generator
        self.config = config
        
        # Extract configuration for easy access
        self.params_config = config.get("parameters", {})
        self.responses_config = config.get("responses", {})
        self.param_names = list(self.params_config.keys())
        self.response_names = list(self.responses_config.keys())
        
        # State management
        self.current_suggestions = []
        self.current_suggestion_index = 0
        self.experiment_count = 0
        self.is_initial_phase = True
        self.is_converged = False
        
        # UI components
        self.window = None
        self.suggestion_frame = None
        self.input_frame = None
        self.history_text = None
        self.current_suggestion_display = None
        self.response_entries = {}
        
        # Plot components
        self.plot_figure = None
        self.plot_canvas = None
        self.plot_ax = None
        self.experiment_points = []  # Store experiment coordinates for plotting
        # Remove gradient vectors - using contour plot instead
        self.completed_points = set()  # Track which points have results (red)
        self.plot_circles = []  # Store scatter plot objects for color updates
        self.current_contours = []  # Store current contour objects for cleanup
        
        # Response trends plot components
        self.trends_figure = None
        self.trends_canvas = None
        self.trends_ax = None
        self.response_history = {name: [] for name in self.response_names}  # Store response values over time
        
        # Parameter importance plot components
        self.importance_figure = None
        self.importance_canvas = None
        self.importance_ax = None
        
        # Correlation matrix plot components
        self.correlation_figure = None
        self.correlation_canvas = None
        self.correlation_ax = None
        
        # Create the window
        self._create_window()
        
        # Start with initial experiments
        self._generate_initial_suggestions()
        
        logger.info("Interactive screening window initialized")
    
    def _create_window(self):
        """Create the main window and UI components."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Interactive SGLBO Screening")
        self.window.geometry("1000x700")
        self.window.grab_set()  # Make window modal
        
        # Main container with scrollable content
        main_canvas = tk.Canvas(self.window)
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title section
        title_frame = ttk.Frame(scrollable_frame, padding="20")
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="Interactive SGLBO Screening", 
                 font=("Arial", 18, "bold")).pack()
        
        ttk.Label(title_frame, 
                 text="Manual experimental workflow: Suggest → Measure → Input → Next suggestion", 
                 font=("Arial", 10)).pack(pady=(5, 0))
        
        # Configuration summary
        config_frame = ttk.LabelFrame(scrollable_frame, text="Configuration", padding="10")
        config_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        config_text = f"""Parameters: {', '.join(self.param_names)}
Responses: {', '.join(self.response_names)}
Initial Samples: {self.config['sglbo_settings'].get('n_initial_samples', 8)}
Max Iterations: {self.config['sglbo_settings'].get('max_iterations', 20)}"""
        
        ttk.Label(config_frame, text=config_text, justify=tk.LEFT).pack(anchor=tk.W)
        
        # Current suggestion section
        self.suggestion_frame = ttk.LabelFrame(scrollable_frame, text="Current Experiment Suggestion", padding="15")
        self.suggestion_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Suggestion display area
        self.current_suggestion_display = tk.Text(self.suggestion_frame, height=6, wrap=tk.WORD)
        self.current_suggestion_display.pack(fill=tk.X, pady=(0, 10))
        
        # Navigation buttons for multiple suggestions
        nav_frame = ttk.Frame(self.suggestion_frame)
        nav_frame.pack(fill=tk.X)
        
        self.prev_btn = ttk.Button(nav_frame, text="← Previous", command=self._previous_suggestion)
        self.prev_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.suggestion_counter = ttk.Label(nav_frame, text="Suggestion 1 of 1")
        self.suggestion_counter.pack(side=tk.LEFT, padx=10)
        
        self.next_btn = ttk.Button(nav_frame, text="Next →", command=self._next_suggestion)
        self.next_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Copy button for easy parameter copying
        ttk.Button(nav_frame, text="Copy Parameters", 
                  command=self._copy_current_parameters).pack(side=tk.RIGHT)
        
        # Results input section
        self.input_frame = ttk.LabelFrame(scrollable_frame, text="Enter Experimental Results", padding="15")
        self.input_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        # Create input fields for each response
        self._create_response_input_fields()
        
        # Input control buttons
        input_control_frame = ttk.Frame(self.input_frame)
        input_control_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.submit_btn = ttk.Button(input_control_frame, text="Submit Results & Get Next Suggestion", 
                                   command=self._submit_results, style="Accent.TButton")
        self.submit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(input_control_frame, text="Clear Input", 
                  command=self._clear_input).pack(side=tk.LEFT)
        
        # Real-time screening plot section
        plot_frame = ttk.LabelFrame(scrollable_frame, text="Screening Progress Visualization", padding="10")
        plot_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Create notebook for multiple plots
        plot_notebook = ttk.Notebook(plot_frame)
        plot_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Parameter space exploration tab
        param_space_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(param_space_frame, text="Parameter Space")
        self._create_plot(param_space_frame)
        
        # Response trends tab
        trends_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(trends_frame, text="Response Trends")
        self._create_trends_plot(trends_frame)
        
        # Parameter importance tab
        importance_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(importance_frame, text="Parameter Importance")
        self._create_importance_plot(importance_frame)
        
        # Correlation matrix tab
        correlation_frame = ttk.Frame(plot_notebook)
        plot_notebook.add(correlation_frame, text="Correlation Matrix")
        self._create_correlation_plot(correlation_frame)
        
        # Progress and history section
        progress_frame = ttk.LabelFrame(scrollable_frame, text="Progress & History", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        # Progress info
        self.progress_label = ttk.Label(progress_frame, text="Ready to start initial experiments")
        self.progress_label.pack(anchor=tk.W, pady=(0, 5))
        
        # History text area
        self.history_text = tk.Text(progress_frame, height=12, wrap=tk.WORD)
        history_scrollbar = ttk.Scrollbar(progress_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        control_frame = ttk.Frame(scrollable_frame, padding="20")
        control_frame.pack(fill=tk.X)
        
        ttk.Button(control_frame, text="Export Results", 
                  command=self._export_results).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Generate Design Space", 
                  command=self._generate_design_space).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Reset Screening", 
                  command=self._reset_screening).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame, text="Close", 
                  command=self._close_window).pack(side=tk.RIGHT)
        
        # Setup window close protocol
        self.window.protocol("WM_DELETE_WINDOW", self._close_window)
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def _create_plot(self, parent_frame):
        """Create the real-time screening progress plot."""
        try:
            # Create matplotlib figure
            self.plot_figure = Figure(figsize=(8, 6), dpi=80)
            self.plot_ax = self.plot_figure.add_subplot(111)
            
            # Set up the plot
            self.plot_ax.set_title("Screening Progress: Parameter Space Exploration", fontsize=12, fontweight='bold')
            
            # For 2D parameter space (assuming first 2 parameters if more than 2)
            param_names = list(self.params_config.keys())
            if len(param_names) >= 2:
                self.plot_ax.set_xlabel(param_names[0], fontsize=10)
                self.plot_ax.set_ylabel(param_names[1], fontsize=10)
            else:
                self.plot_ax.set_xlabel("Parameter 1", fontsize=10)
                self.plot_ax.set_ylabel("Parameter 2", fontsize=10)
            
            # Set initial plot bounds based on parameter bounds
            self._set_plot_bounds()
            
            # Enable grid
            self.plot_ax.grid(True, alpha=0.3)
            
            # Create canvas and add to frame
            self.plot_canvas = FigureCanvasTkAgg(self.plot_figure, parent_frame)
            self.plot_canvas.draw()
            self.plot_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            instructions_label = ttk.Label(parent_frame, 
                                         text="• Red circles: Experimental data points  • Black arrows: Gradient vectors (after initial phase)",
                                         font=("Arial", 9), foreground="gray")
            instructions_label.pack(pady=(5, 0))
            
            logger.info("Screening progress plot created successfully")
            
        except Exception as e:
            logger.error(f"Error creating plot: {e}")
            # Create fallback label if plot fails
            ttk.Label(parent_frame, text="Plot visualization unavailable", 
                     font=("Arial", 10), foreground="red").pack(pady=20)
    
    def _set_plot_bounds(self):
        """Set plot axis bounds based on parameter configuration."""
        try:
            param_names = list(self.params_config.keys())
            
            if len(param_names) >= 2:
                # Get bounds for first two parameters
                param1_config = self.params_config[param_names[0]]
                param2_config = self.params_config[param_names[1]]
                
                if param1_config["type"] in ["continuous", "discrete"]:
                    x_bounds = param1_config["bounds"]
                    # Add 10% margin
                    x_range = x_bounds[1] - x_bounds[0]
                    x_margin = x_range * 0.1
                    self.plot_ax.set_xlim(x_bounds[0] - x_margin, x_bounds[1] + x_margin)
                
                if param2_config["type"] in ["continuous", "discrete"]:
                    y_bounds = param2_config["bounds"]
                    # Add 10% margin
                    y_range = y_bounds[1] - y_bounds[0]
                    y_margin = y_range * 0.1
                    self.plot_ax.set_ylim(y_bounds[0] - y_margin, y_bounds[1] + y_margin)
            else:
                # Default bounds if insufficient parameters
                self.plot_ax.set_xlim(0, 100)
                self.plot_ax.set_ylim(0, 100)
                
        except Exception as e:
            logger.error(f"Error setting plot bounds: {e}")
            # Default bounds on error
            self.plot_ax.set_xlim(0, 100)
            self.plot_ax.set_ylim(0, 100)
    
    def _create_trends_plot(self, parent_frame):
        """Create the response trends over time plot."""
        try:
            # Create matplotlib figure
            self.trends_figure = Figure(figsize=(8, 6), dpi=80)
            self.trends_ax = self.trends_figure.add_subplot(111)
            
            # Set up the plot
            self.trends_ax.set_title("Response Trends Over Time", fontsize=12, fontweight='bold')
            self.trends_ax.set_xlabel("Experiment Number", fontsize=10)
            self.trends_ax.set_ylabel("Response Values", fontsize=10)
            
            # Enable grid
            self.trends_ax.grid(True, alpha=0.3)
            
            # Create canvas and add to frame
            self.trends_canvas = FigureCanvasTkAgg(self.trends_figure, parent_frame)
            self.trends_canvas.draw()
            self.trends_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            instructions_label = ttk.Label(parent_frame, 
                                         text="• Lines show response value trends • Targets/goals shown as dashed lines",
                                         font=("Arial", 9), foreground="gray")
            instructions_label.pack(pady=(5, 0))
            
            logger.info("Response trends plot created successfully")
            
        except Exception as e:
            logger.error(f"Error creating trends plot: {e}")
            # Create fallback label if plot fails
            ttk.Label(parent_frame, text="Trends plot visualization unavailable", 
                     font=("Arial", 10), foreground="red").pack(pady=20)
    
    def _update_trends_plot(self):
        """Update the response trends plot with new data."""
        try:
            if not self.trends_ax or not self.trends_canvas:
                logger.debug("No trends plot axis or canvas available")
                return
            
            if len(self.screening_optimizer.experimental_data) == 0:
                logger.debug("No experimental data available for trends plot")
                return
            
            # Clear the plot
            self.trends_ax.clear()
            
            # Reset plot settings
            self.trends_ax.set_title("Response Trends Over Time", fontsize=12, fontweight='bold')
            self.trends_ax.set_xlabel("Experiment Number", fontsize=10)
            self.trends_ax.set_ylabel("Response Values", fontsize=10)
            self.trends_ax.grid(True, alpha=0.3)
            
            # Get experimental data
            data = self.screening_optimizer.experimental_data
            experiment_numbers = list(range(1, len(data) + 1))
            
            # Plot trends for each response
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            
            for i, response_name in enumerate(self.response_names):
                if response_name not in data.columns:
                    continue
                
                response_values = data[response_name].values
                color = colors[i % len(colors)]
                
                # Plot the trend line
                self.trends_ax.plot(experiment_numbers, response_values, 
                                  color=color, marker='o', markersize=6, 
                                  linewidth=2, label=response_name, alpha=0.8)
                
                # Add target/goal line if specified
                response_config = self.responses_config.get(response_name, {})
                goal = response_config.get("goal", "None")
                
                if goal == "Target" and "target" in response_config:
                    target_value = response_config["target"]
                    self.trends_ax.axhline(y=target_value, color=color, linestyle='--', 
                                         alpha=0.5, label=f'{response_name} Target')
                
                # Highlight best value so far
                if goal == "Maximize":
                    best_idx = np.argmax(response_values)
                    best_value = response_values[best_idx]
                elif goal == "Minimize":
                    best_idx = np.argmin(response_values)
                    best_value = response_values[best_idx]
                elif goal == "Target":
                    target_value = response_config.get("target", np.mean(response_values))
                    deviations = np.abs(response_values - target_value)
                    best_idx = np.argmin(deviations)
                    best_value = response_values[best_idx]
                else:
                    best_idx = len(response_values) - 1  # Latest value
                    best_value = response_values[best_idx]
                
                # Mark best point with a star
                self.trends_ax.scatter(experiment_numbers[best_idx], best_value, 
                                     marker='*', s=200, color=color, 
                                     edgecolors='black', linewidth=1, zorder=5)
            
            # Add legend
            if len(self.response_names) > 0:
                self.trends_ax.legend(loc='best', fontsize=9)
            
            # Set axis limits with some padding
            if len(experiment_numbers) > 0:
                self.trends_ax.set_xlim(0.5, max(experiment_numbers) + 0.5)
            
            # Add convergence indicators if available
            if hasattr(self, 'is_converged') and self.is_converged:
                # Add vertical line at convergence point
                convergence_point = len(experiment_numbers)
                self.trends_ax.axvline(x=convergence_point, color='red', linestyle=':', 
                                     alpha=0.7, label='Converged')
                self.trends_ax.legend(loc='best', fontsize=9)
            
            # Refresh the plot
            self.trends_canvas.draw()
            
            logger.debug(f"Updated trends plot with {len(experiment_numbers)} data points")
            
        except Exception as e:
            logger.error(f"Error updating trends plot: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_importance_plot(self, parent_frame):
        """Create the parameter importance bar chart plot."""
        try:
            # Create matplotlib figure
            self.importance_figure = Figure(figsize=(8, 6), dpi=80)
            self.importance_ax = self.importance_figure.add_subplot(111)
            
            # Set up the plot
            self.importance_ax.set_title("Parameter Importance Analysis", fontsize=12, fontweight='bold')
            self.importance_ax.set_xlabel("Importance Score", fontsize=10)
            self.importance_ax.set_ylabel("Parameters", fontsize=10)
            
            # Enable grid
            self.importance_ax.grid(True, alpha=0.3, axis='x')
            
            # Create canvas and add to frame
            self.importance_canvas = FigureCanvasTkAgg(self.importance_figure, parent_frame)
            self.importance_canvas.draw()
            self.importance_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            instructions_label = ttk.Label(parent_frame, 
                                         text="• Bar length shows overall parameter importance • Colors indicate significance level",
                                         font=("Arial", 9), foreground="gray")
            instructions_label.pack(pady=(5, 0))
            
            logger.info("Parameter importance plot created successfully")
            
        except Exception as e:
            logger.error(f"Error creating importance plot: {e}")
            # Create fallback label if plot fails
            ttk.Label(parent_frame, text="Parameter importance plot visualization unavailable", 
                     font=("Arial", 10), foreground="red").pack(pady=20)
    
    def _update_importance_plot(self):
        """Update the parameter importance plot with current analysis."""
        try:
            if not self.importance_ax or not self.importance_canvas:
                logger.debug("No importance plot axis or canvas available")
                return
            
            if len(self.screening_optimizer.experimental_data) < 3:
                logger.debug("Need at least 3 data points for parameter importance analysis")
                return
            
            # Get parameter importance analysis from results manager
            param_effects = self.results_manager.analyze_parameter_effects()
            
            if not param_effects or "overall_parameter_importance" not in param_effects:
                logger.debug("No parameter importance data available")
                return
            
            # Clear the plot
            self.importance_ax.clear()
            
            # Reset plot settings
            self.importance_ax.set_title("Parameter Importance Analysis", fontsize=12, fontweight='bold')
            self.importance_ax.set_xlabel("Importance Score", fontsize=10)
            self.importance_ax.set_ylabel("Parameters", fontsize=10)
            self.importance_ax.grid(True, alpha=0.3, axis='x')
            
            # Get importance data
            importance_data = param_effects["overall_parameter_importance"]
            
            if not importance_data:
                self.importance_ax.text(0.5, 0.5, "No parameter importance data available", 
                                      ha='center', va='center', transform=self.importance_ax.transAxes,
                                      fontsize=12, color='gray')
                self.importance_canvas.draw()
                return
            
            # Extract parameter names and importance scores
            param_names = [item["parameter"] for item in importance_data]
            importance_scores = [item["importance_score"] for item in importance_data]
            
            # Determine colors based on importance levels
            max_score = max(importance_scores) if importance_scores else 1.0
            colors = []
            for score in importance_scores:
                if max_score > 0:
                    normalized_score = score / max_score
                    if normalized_score > 0.7:
                        colors.append('#d62728')  # High importance - red
                    elif normalized_score > 0.4:
                        colors.append('#ff7f0e')  # Medium importance - orange
                    else:
                        colors.append('#1f77b4')  # Low importance - blue
                else:
                    colors.append('#1f77b4')  # Default blue
            
            # Create horizontal bar chart
            y_positions = range(len(param_names))
            bars = self.importance_ax.barh(y_positions, importance_scores, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
            
            # Set parameter names on y-axis
            self.importance_ax.set_yticks(y_positions)
            self.importance_ax.set_yticklabels(param_names)
            
            # Add value labels on bars
            for i, (bar, score) in enumerate(zip(bars, importance_scores)):
                width = bar.get_width()
                if width > 0:
                    self.importance_ax.text(width + max_score * 0.01, bar.get_y() + bar.get_height()/2, 
                                          f'{score:.3f}', ha='left', va='center', fontsize=9, fontweight='bold')
            
            # Set x-axis limits with some padding
            if max_score > 0:
                self.importance_ax.set_xlim(0, max_score * 1.15)
            
            # Add color legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#d62728', alpha=0.7, label='High Importance (>70%)'),
                Patch(facecolor='#ff7f0e', alpha=0.7, label='Medium Importance (40-70%)'),
                Patch(facecolor='#1f77b4', alpha=0.7, label='Low Importance (<40%)')
            ]
            self.importance_ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
            
            # Add summary text
            total_params = len(param_names)
            high_importance_params = sum(1 for score in importance_scores if score > 0.7 * max_score)
            
            summary_text = f"Total Parameters: {total_params}  |  High Importance: {high_importance_params}"
            self.importance_ax.text(0.02, 0.98, summary_text, transform=self.importance_ax.transAxes,
                                  fontsize=9, va='top', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.7))
            
            # Refresh the plot
            self.importance_canvas.draw()
            
            logger.debug(f"Updated parameter importance plot with {len(param_names)} parameters")
            
        except Exception as e:
            logger.error(f"Error updating parameter importance plot: {e}")
            import traceback
            traceback.print_exc()
    
    def _create_correlation_plot(self, parent_frame):
        """Create the correlation matrix heatmap plot."""
        try:
            # Create matplotlib figure
            self.correlation_figure = Figure(figsize=(8, 6), dpi=80)
            self.correlation_ax = self.correlation_figure.add_subplot(111)
            
            # Set up the plot
            self.correlation_ax.set_title("Parameter-Response Correlation Matrix", fontsize=12, fontweight='bold')
            
            # Create canvas and add to frame
            self.correlation_canvas = FigureCanvasTkAgg(self.correlation_figure, parent_frame)
            self.correlation_canvas.draw()
            self.correlation_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Add instructions
            instructions_label = ttk.Label(parent_frame, 
                                         text="• Heat map shows correlations between parameters and responses • Red=positive, Blue=negative",
                                         font=("Arial", 9), foreground="gray")
            instructions_label.pack(pady=(5, 0))
            
            logger.info("Correlation matrix plot created successfully")
            
        except Exception as e:
            logger.error(f"Error creating correlation plot: {e}")
            # Create fallback label if plot fails
            ttk.Label(parent_frame, text="Correlation matrix plot visualization unavailable", 
                     font=("Arial", 10), foreground="red").pack(pady=20)
    
    def _update_correlation_plot(self):
        """Update the correlation matrix heatmap with current analysis."""
        try:
            if not self.correlation_ax or not self.correlation_canvas:
                logger.debug("No correlation plot axis or canvas available")
                return
            
            if len(self.screening_optimizer.experimental_data) < 3:
                logger.debug("Need at least 3 data points for correlation analysis")
                return
            
            # Get parameter effects analysis from results manager
            param_effects = self.results_manager.analyze_parameter_effects()
            
            if not param_effects or "correlations" not in param_effects:
                logger.debug("No correlation data available")
                return
            
            # Clear the plot
            self.correlation_ax.clear()
            
            # Get correlation data
            correlations_data = param_effects["correlations"]
            
            if not correlations_data:
                self.correlation_ax.text(0.5, 0.5, "No correlation data available", 
                                       ha='center', va='center', transform=self.correlation_ax.transAxes,
                                       fontsize=12, color='gray')
                self.correlation_canvas.draw()
                return
            
            # Build correlation matrix
            # Rows = parameters, Columns = responses
            param_names = []
            response_names = []
            correlation_matrix = []
            
            # Collect all parameters that have correlations
            all_params = set()
            for response_name, response_corrs in correlations_data.items():
                all_params.update(response_corrs.keys())
                if response_name not in response_names:
                    response_names.append(response_name)
            
            param_names = sorted(list(all_params))
            
            # Build the correlation matrix
            for param_name in param_names:
                row = []
                for response_name in response_names:
                    if (response_name in correlations_data and 
                        param_name in correlations_data[response_name]):
                        correlation = correlations_data[response_name][param_name]
                        row.append(correlation)
                    else:
                        row.append(0.0)  # No correlation data available
                correlation_matrix.append(row)
            
            if not correlation_matrix or not param_names or not response_names:
                self.correlation_ax.text(0.5, 0.5, "Insufficient correlation data", 
                                       ha='center', va='center', transform=self.correlation_ax.transAxes,
                                       fontsize=12, color='gray')
                self.correlation_canvas.draw()
                return
            
            # Convert to numpy array for easier handling
            correlation_array = np.array(correlation_matrix)
            
            # Create heatmap
            import matplotlib.colors as mcolors
            
            # Use RdBu_r colormap (red for positive, blue for negative)
            im = self.correlation_ax.imshow(correlation_array, cmap='RdBu_r', aspect='auto', 
                                          vmin=-1, vmax=1, interpolation='nearest')
            
            # Set ticks and labels
            self.correlation_ax.set_xticks(range(len(response_names)))
            self.correlation_ax.set_xticklabels(response_names, rotation=45, ha='right')
            self.correlation_ax.set_yticks(range(len(param_names)))
            self.correlation_ax.set_yticklabels(param_names)
            
            # Add correlation values as text
            for i in range(len(param_names)):
                for j in range(len(response_names)):
                    correlation_val = correlation_array[i, j]
                    if abs(correlation_val) > 0.001:  # Only show non-zero correlations
                        # Choose text color based on correlation strength
                        text_color = 'white' if abs(correlation_val) > 0.5 else 'black'
                        self.correlation_ax.text(j, i, f'{correlation_val:.2f}', 
                                               ha='center', va='center', 
                                               color=text_color, fontsize=9, fontweight='bold')
            
            # Add colorbar
            if not hasattr(self, '_correlation_colorbar') or self._correlation_colorbar is None:
                try:
                    self._correlation_colorbar = self.correlation_figure.colorbar(im, ax=self.correlation_ax)
                    self._correlation_colorbar.set_label('Correlation Coefficient', rotation=270, labelpad=15)
                except Exception as e:
                    logger.warning(f"Could not create correlation colorbar: {e}")
                    self._correlation_colorbar = None
            else:
                # Update existing colorbar
                try:
                    self._correlation_colorbar.mappable.set_array(correlation_array.ravel())
                    self._correlation_colorbar.mappable.set_clim(vmin=-1, vmax=1)
                    self._correlation_colorbar.update_normal(self._correlation_colorbar.mappable)
                except Exception as e:
                    logger.warning(f"Could not update correlation colorbar: {e}")
            
            # Set title and labels
            self.correlation_ax.set_title("Parameter-Response Correlation Matrix", fontsize=12, fontweight='bold')
            self.correlation_ax.set_xlabel("Response Variables", fontsize=10)
            self.correlation_ax.set_ylabel("Parameters", fontsize=10)
            
            # Add summary statistics
            total_correlations = np.count_nonzero(correlation_array)
            strong_correlations = np.count_nonzero(np.abs(correlation_array) > 0.5)
            max_correlation = np.max(np.abs(correlation_array))
            
            summary_text = f"Total: {total_correlations} | Strong (>0.5): {strong_correlations} | Max: {max_correlation:.2f}"
            self.correlation_ax.text(0.02, 0.98, summary_text, transform=self.correlation_ax.transAxes,
                                   fontsize=9, va='top', 
                                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
            
            # Adjust layout to prevent label cutoff
            self.correlation_figure.tight_layout()
            
            # Refresh the plot
            self.correlation_canvas.draw()
            
            logger.debug(f"Updated correlation matrix plot with {len(param_names)} parameters and {len(response_names)} responses")
            
        except Exception as e:
            logger.error(f"Error updating correlation matrix plot: {e}")
            import traceback
            traceback.print_exc()
    
    def _update_contour_plot(self):
        """Update the contour/heatmap showing the response surface."""
        try:
            if not self.plot_ax or not self.plot_canvas:
                logger.debug("No plot axis or canvas available")
                return
            
            if len(self.screening_optimizer.experimental_data) < 3:
                logger.info("Need at least 3 data points for contour plot")
                return
                
            param_names = list(self.params_config.keys())
            if len(param_names) < 2:
                logger.warning("Need at least 2 parameters for contour plot")
                return
            
            logger.info(f"Updating contour plot with {len(self.screening_optimizer.experimental_data)} data points")
            
            # Get experimental data
            data = self.screening_optimizer.experimental_data
            x_param = param_names[0]
            y_param = param_names[1]
            
            # Get the primary response for visualization
            response_names = list(self.responses_config.keys())
            primary_response = response_names[0]  # Use first response
            
            if primary_response not in data.columns:
                logger.warning(f"Response '{primary_response}' not found in data")
                return
            
            x_data = data[x_param].values
            y_data = data[y_param].values
            z_data = data[primary_response].values
            
            # Create a grid for interpolation
            x_min, x_max = x_data.min(), x_data.max()
            y_min, y_max = y_data.min(), y_data.max()
            
            # Add padding to the grid
            x_range = x_max - x_min
            y_range = y_max - y_min
            x_min -= x_range * 0.1
            x_max += x_range * 0.1
            y_min -= y_range * 0.1
            y_max += y_range * 0.1
            
            # Create grid
            grid_resolution = 50
            xi = np.linspace(x_min, x_max, grid_resolution)
            yi = np.linspace(y_min, y_max, grid_resolution)
            Xi, Yi = np.meshgrid(xi, yi)
            
            # Interpolate data using Gaussian Process prediction if available
            if primary_response in self.screening_optimizer.gp_models:
                gp_model = self.screening_optimizer.gp_models[primary_response]
                
                # Convert grid points to normalized space for GP prediction
                param_handler = self.screening_optimizer.param_handler
                grid_points = []
                for i in range(len(xi)):
                    for j in range(len(yi)):
                        point = {x_param: xi[i], y_param: yi[j]}
                        norm_array = param_handler.params_to_normalized(point)
                        grid_points.append(norm_array)
                
                grid_points = np.array(grid_points)
                
                # Predict using GP model
                predictions, _ = gp_model.predict(grid_points, return_std=True)
                
                # Reshape predictions to grid
                Zi = predictions.reshape(grid_resolution, grid_resolution)
            else:
                # Fallback to simple interpolation
                try:
                    from scipy.interpolate import griddata
                    points = np.column_stack((x_data, y_data))
                    Zi = griddata(points, z_data, (Xi, Yi), method='linear', fill_value=np.nan)
                except ImportError:
                    logger.warning("SciPy not available, using simple grid interpolation")
                    # Very basic interpolation as final fallback
                    Zi = np.full_like(Xi, np.mean(z_data))
            
            # Clear previous contour plots but keep data points (scatter plots)
            # Save scatter plots (data points) 
            scatter_collections = []
            non_scatter_collections = []
            
            for collection in self.plot_ax.collections:
                if type(collection).__name__ == 'PathCollection':
                    scatter_collections.append(collection)
                else:
                    non_scatter_collections.append(collection)
            
            # Remove non-scatter collections (contours)
            for collection in non_scatter_collections:
                try:
                    collection.remove()
                except Exception as e:
                    logger.debug(f"Failed to remove collection: {e}")
            
            if non_scatter_collections:
                logger.info(f"Removed {len(non_scatter_collections)} old contour collections")
            
            # Clear the contour list
            self.current_contours = []
            
            # Create new contour plot
            contour_filled = self.plot_ax.contourf(Xi, Yi, Zi, levels=20, alpha=0.6, cmap='viridis')
            contour_lines = self.plot_ax.contour(Xi, Yi, Zi, levels=10, colors='black', alpha=0.3, linewidths=0.5)
            
            # Store references to new contours for cleanup next time
            self.current_contours = [contour_filled, contour_lines]
            
            # Handle colorbar - create only once, then update
            if not hasattr(self, '_colorbar') or self._colorbar is None:
                # Create colorbar only on first contour plot
                try:
                    self._colorbar = self.plot_figure.colorbar(contour_filled, ax=self.plot_ax)
                    self._colorbar.set_label(f'{primary_response} (Response Values)', rotation=270, labelpad=15)
                    logger.debug(f"Created initial colorbar for {primary_response}")
                except Exception as e:
                    logger.warning(f"Could not create colorbar: {e}")
                    self._colorbar = None
            else:
                # Update existing colorbar with new data range
                try:
                    # Update colorbar mappable to new contour data
                    self._colorbar.mappable.set_array(Zi.ravel())
                    self._colorbar.mappable.set_clim(vmin=Zi.min(), vmax=Zi.max())
                    self._colorbar.update_normal(self._colorbar.mappable)
                    logger.debug(f"Updated colorbar range: {Zi.min():.2f} to {Zi.max():.2f}")
                except Exception as e:
                    logger.warning(f"Could not update colorbar: {e}")
                    # Fallback: try to recreate colorbar
                    try:
                        self._colorbar.remove()
                        self._colorbar = self.plot_figure.colorbar(contour_filled, ax=self.plot_ax)
                        self._colorbar.set_label(f'{primary_response} (Response Values)', rotation=270, labelpad=15)
                        logger.debug("Recreated colorbar as fallback")
                    except Exception as e2:
                        logger.error(f"Colorbar fallback failed: {e2}")
                        self._colorbar = None
            
            # Refresh the plot
            self.plot_canvas.draw()
            
            logger.info(f"Successfully updated contour plot showing response surface")
            
        except Exception as e:
            logger.error(f"Error updating contour plot: {e}")
            import traceback
            traceback.print_exc()
    
    # Gradient vector methods removed - using contour plot instead
    
    def _calculate_design_space_center(self):
        """Calculate the center point of the initial design space from experimental data."""
        try:
            param_names = list(self.params_config.keys())
            center_point = {}
            
            # Calculate center based on actual experimental data points
            if len(self.screening_optimizer.experimental_data) > 0:
                for param_name in param_names:
                    param_values = self.screening_optimizer.experimental_data[param_name].values
                    center_point[param_name] = float(np.mean(param_values))
            else:
                # Fallback to parameter bounds center
                for param_name in param_names:
                    param_config = self.params_config[param_name]
                    if param_config["type"] in ["continuous", "discrete"]:
                        bounds = param_config["bounds"]
                        center_point[param_name] = (bounds[0] + bounds[1]) / 2.0
            
            logger.info(f"Design space center calculated: {center_point}")
            return center_point
            
        except Exception as e:
            logger.error(f"Error calculating design space center: {e}")
            # Return parameter bounds center as fallback
            center_point = {}
            for param_name in self.params_config:
                param_config = self.params_config[param_name]
                if param_config["type"] in ["continuous", "discrete"]:
                    bounds = param_config["bounds"]
                    center_point[param_name] = (bounds[0] + bounds[1]) / 2.0
            return center_point
    
    def _plot_suggested_experiment(self, suggested_experiment):
        """Plot the suggested experiment point and handle plot centering."""
        try:
            if not self.plot_ax or not self.plot_canvas:
                return
            
            param_names = list(self.params_config.keys())
            if len(param_names) < 2:
                return
            
            # Get coordinates for first two parameters
            x_param = param_names[0]
            y_param = param_names[1]
            
            x_val = suggested_experiment.get(x_param, 0)
            y_val = suggested_experiment.get(y_param, 0)
            
            # Store point for later use
            self.experiment_points.append((x_val, y_val))
            
            # Plot the suggested datapoint as blue circle (will turn red when results are entered)
            circle = self.plot_ax.scatter(x_val, y_val, c='blue', s=100, alpha=0.8, edgecolors='darkblue', linewidth=2)
            self.plot_circles.append(circle)  # Store for later color change
            
            # Add point number annotation
            point_num = len(self.experiment_points)
            self.plot_ax.annotate(str(point_num), (x_val, y_val), 
                                xytext=(5, 5), textcoords='offset points',
                                fontsize=8, color='white', weight='bold')
            
            # Auto-zoom to show all points when new ones are added
            # This ensures all data points remain visible
            if len(self.experiment_points) > 1:  # Only zoom if we have multiple points
                self._zoom_to_fit_all_points()
            
            # Refresh the plot
            self.plot_canvas.draw()
            
            logger.info(f"Plotted suggested experiment {point_num}: ({x_val}, {y_val})")
            
        except Exception as e:
            logger.error(f"Error plotting suggested experiment: {e}")
    
    def _center_plot_on_point(self, x_center, y_center):
        """Center the plot on a specific point while maintaining reasonable bounds."""
        try:
            # Get current plot range
            current_x_range = self.plot_ax.get_xlim()[1] - self.plot_ax.get_xlim()[0]
            current_y_range = self.plot_ax.get_ylim()[1] - self.plot_ax.get_ylim()[0]
            
            # Use current range or minimum range, whichever is larger
            param_names = list(self.params_config.keys())
            
            # Get parameter bounds for minimum range calculation
            x_param_bounds = self.params_config[param_names[0]]["bounds"]
            y_param_bounds = self.params_config[param_names[1]]["bounds"]
            
            min_x_range = (x_param_bounds[1] - x_param_bounds[0]) * 1.2  # 20% larger than parameter range
            min_y_range = (y_param_bounds[1] - y_param_bounds[0]) * 1.2
            
            plot_x_range = max(current_x_range, min_x_range)
            plot_y_range = max(current_y_range, min_y_range)
            
            # Center on the new point
            new_x_min = x_center - plot_x_range / 2
            new_x_max = x_center + plot_x_range / 2
            new_y_min = y_center - plot_y_range / 2
            new_y_max = y_center + plot_y_range / 2
            
            self.plot_ax.set_xlim(new_x_min, new_x_max)
            self.plot_ax.set_ylim(new_y_min, new_y_max)
            
            logger.info(f"Centered plot on point ({x_center}, {y_center})")
            
        except Exception as e:
            logger.error(f"Error centering plot on point: {e}")
    
    def _zoom_to_fit_all_points(self):
        """Zoom out the plot to show all data points with some padding."""
        try:
            if len(self.experiment_points) == 0:
                return
            
            param_names = list(self.params_config.keys())
            
            # Get all x and y coordinates
            x_coords = [point[0] for point in self.experiment_points]
            y_coords = [point[1] for point in self.experiment_points]
            
            # Calculate bounds with padding
            x_min, x_max = min(x_coords), max(x_coords)
            y_min, y_max = min(y_coords), max(y_coords)
            
            # Add padding (20% of range on each side)
            x_range = x_max - x_min
            y_range = y_max - y_min
            
            # Ensure minimum range for very close points
            if x_range < 1.0:
                x_range = 1.0
            if y_range < 1.0:
                y_range = 1.0
            
            padding_x = x_range * 0.2
            padding_y = y_range * 0.2
            
            new_x_min = x_min - padding_x
            new_x_max = x_max + padding_x
            new_y_min = y_min - padding_y
            new_y_max = y_max + padding_y
            
            self.plot_ax.set_xlim(new_x_min, new_x_max)
            self.plot_ax.set_ylim(new_y_min, new_y_max)
            
            logger.info(f"Zoomed to fit all {len(self.experiment_points)} points")
            
        except Exception as e:
            logger.error(f"Error zooming to fit all points: {e}")
    
    def _mark_point_completed(self, point_number):
        """Change a point's color from blue to red to indicate completion."""
        try:
            point_index = point_number - 1  # Convert to 0-based index
            
            if 0 <= point_index < len(self.plot_circles):
                # Mark as completed
                self.completed_points.add(point_number)
                
                # Change circle color to red
                circle = self.plot_circles[point_index]
                circle.set_color('red')
                circle.set_edgecolors('darkred')
                
                # Refresh the plot
                self.plot_canvas.draw()
                
                logger.info(f"Marked point {point_number} as completed (changed to red)")
                
        except Exception as e:
            logger.error(f"Error marking point {point_number} as completed: {e}")
    
    def _create_response_input_fields(self):
        """Create input fields for each response variable."""
        self.response_entries = {}
        
        # Create a grid of response inputs
        input_grid_frame = ttk.Frame(self.input_frame)
        input_grid_frame.pack(fill=tk.X, pady=(0, 10))
        
        for i, (response_name, response_config) in enumerate(self.responses_config.items()):
            row = i // 2  # 2 columns
            col = (i % 2) * 2  # Each input takes 2 columns (label + entry)
            
            # Response label
            ttk.Label(input_grid_frame, text=f"{response_name}:").grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            
            # Response entry
            entry = ttk.Entry(input_grid_frame, width=15)
            entry.grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2)
            
            # Add goal information as tooltip/label
            goal = response_config.get("goal", "None")
            if goal != "None":
                goal_label = ttk.Label(input_grid_frame, text=f"({goal})", 
                                     font=("Arial", 8), foreground="gray")
                goal_label.grid(row=row+1, column=col+1, sticky=tk.W, padx=(0, 20))
            
            self.response_entries[response_name] = entry
        
        # Instructions
        ttk.Label(self.input_frame, 
                 text="Enter the measured values from your experiment and click 'Submit Results'", 
                 font=("Arial", 9), foreground="blue").pack(pady=(10, 0))
    
    def _generate_initial_suggestions(self):
        """Generate initial experiment suggestions."""
        try:
            self.current_suggestions = self.screening_optimizer.suggest_initial_experiments()
            self.current_suggestion_index = 0
            self.is_initial_phase = True
            
            self._update_suggestion_display()
            self._update_navigation_buttons()
            
            self._add_to_history(f"Generated {len(self.current_suggestions)} initial experiment suggestions")
            self._add_to_history("Perform these experiments and input the measured results to continue.")
            
            self.progress_label.config(text=f"Initial phase: {len(self.current_suggestions)} experiments to run")
            
        except Exception as e:
            logger.error(f"Error generating initial suggestions: {e}")
            messagebox.showerror("Error", f"Failed to generate initial suggestions: {e}")
    
    def _update_suggestion_display(self):
        """Update the current suggestion display."""
        if not self.current_suggestions:
            self.current_suggestion_display.delete(1.0, tk.END)
            self.current_suggestion_display.insert(1.0, "No suggestions available")
            return
        
        current_suggestion = self.current_suggestions[self.current_suggestion_index]
        
        # Format the suggestion nicely
        suggestion_text = f"Experiment {self.current_suggestion_index + 1}:\n\n"
        
        for param_name, value in current_suggestion.items():
            param_config = self.params_config[param_name]
            if param_config["type"] == "continuous":
                if isinstance(value, (int, float)):
                    suggestion_text += f"{param_name}: {value:.3f}\n"
                else:
                    suggestion_text += f"{param_name}: {value}\n"
            else:
                suggestion_text += f"{param_name}: {value}\n"
        
        suggestion_text += f"\nPerform this experiment and measure the response values.\n"
        suggestion_text += f"Then enter the results below and click 'Submit Results'."
        
        self.current_suggestion_display.delete(1.0, tk.END)
        self.current_suggestion_display.insert(1.0, suggestion_text)
        
        # Plot the suggested experiment datapoint when suggestion is displayed
        self._plot_suggested_experiment(current_suggestion)
    
    def _update_navigation_buttons(self):
        """Update navigation button states."""
        total_suggestions = len(self.current_suggestions)
        current_num = self.current_suggestion_index + 1
        
        self.suggestion_counter.config(text=f"Suggestion {current_num} of {total_suggestions}")
        
        self.prev_btn.config(state=tk.NORMAL if self.current_suggestion_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_suggestion_index < total_suggestions - 1 else tk.DISABLED)
    
    def _previous_suggestion(self):
        """Navigate to previous suggestion."""
        if self.current_suggestion_index > 0:
            self.current_suggestion_index -= 1
            self._update_suggestion_display()
            self._update_navigation_buttons()
    
    def _next_suggestion(self):
        """Navigate to next suggestion."""
        if self.current_suggestion_index < len(self.current_suggestions) - 1:
            self.current_suggestion_index += 1
            self._update_suggestion_display()
            self._update_navigation_buttons()
    
    def _copy_current_parameters(self):
        """Copy current parameters to clipboard."""
        if not self.current_suggestions:
            return
        
        current_suggestion = self.current_suggestions[self.current_suggestion_index]
        
        # Format for copying
        param_text = ""
        for param_name, value in current_suggestion.items():
            param_text += f"{param_name}: {value}\n"
        
        # Copy to clipboard
        self.window.clipboard_clear()
        self.window.clipboard_append(param_text.strip())
        
        messagebox.showinfo("Copied", "Parameters copied to clipboard!")
    
    def _clear_input(self):
        """Clear all response input fields."""
        for entry in self.response_entries.values():
            entry.delete(0, tk.END)
    
    def _submit_results(self):
        """Submit the experimental results and get next suggestion."""
        try:
            # Validate inputs
            if not self.current_suggestions:
                messagebox.showerror("Error", "No current suggestion available")
                return
            
            # Get current suggestion
            current_suggestion = self.current_suggestions[self.current_suggestion_index]
            
            # Collect response values
            response_values = {}
            for response_name, entry in self.response_entries.items():
                value_str = entry.get().strip()
                if not value_str:
                    messagebox.showerror("Input Error", f"Please enter a value for {response_name}")
                    return
                
                try:
                    response_values[response_name] = float(value_str)
                except ValueError:
                    messagebox.showerror("Input Error", f"Invalid numeric value for {response_name}: {value_str}")
                    return
            
            # Create experiment record
            experiment_data = {**current_suggestion, **response_values}
            
            # Add to optimizer and results manager
            data_df = pd.DataFrame([experiment_data])
            self.screening_optimizer.add_experimental_data(data_df)
            
            # Run iteration analysis if not in initial phase
            if not self.is_initial_phase:
                iteration_info = self.screening_optimizer.run_screening_iteration()
                self.results_manager.add_experimental_data(data_df, iteration_info)
            else:
                self.results_manager.add_experimental_data(data_df)
            
            self.experiment_count += 1
            
            # Log the experiment
            self._add_to_history(f"\n--- Experiment {self.experiment_count} Completed ---")
            self._add_to_history(f"Parameters: {current_suggestion}")
            self._add_to_history(f"Results: {response_values}")
            
            # Change the circle color from blue to red to indicate completion
            self._mark_point_completed(self.experiment_count)
            
            # Update contour plot with new data
            if self.experiment_count > 2:  # Need at least 3 points for meaningful contour
                self._update_contour_plot()
            
            # Update trends plot with new data
            self._update_trends_plot()
            
            # Update parameter importance plot with new data (after enough experiments)
            if self.experiment_count >= 3:
                self._update_importance_plot()
                # Update correlation matrix plot with new data
                self._update_correlation_plot()
            
            # Auto-zoom to ensure all points are visible after result submission
            if len(self.experiment_points) > 1:
                self._zoom_to_fit_all_points()
                self.plot_canvas.draw()
            
            # Clear input fields
            self._clear_input()
            
            # Check if we need to continue with initial phase or move to iterative phase
            if self.is_initial_phase:
                # Check if we have more initial suggestions or if we've completed enough
                initial_completed = len(self.screening_optimizer.experimental_data)
                n_initial = self.config['sglbo_settings'].get('n_initial_samples', 8)
                
                if initial_completed >= n_initial or self.current_suggestion_index >= len(self.current_suggestions) - 1:
                    # Move to iterative phase
                    self.is_initial_phase = False
                    self._add_to_history("Initial phase completed. Moving to iterative screening...")
                    self._generate_next_iterative_suggestion()
                else:
                    # Continue with remaining initial suggestions
                    if self.current_suggestion_index < len(self.current_suggestions) - 1:
                        self.current_suggestion_index += 1
                        self._update_suggestion_display()
                        self._update_navigation_buttons()
                    else:
                        # Generate more initial suggestions if needed
                        self._generate_next_iterative_suggestion()
            else:
                # Generate next iterative suggestion
                self._generate_next_iterative_suggestion()
            
            # Update progress
            self._update_progress_display()
            
        except Exception as e:
            logger.error(f"Error submitting results: {e}")
            messagebox.showerror("Error", f"Failed to submit results: {e}")
    
    def _generate_next_iterative_suggestion(self):
        """Generate the next suggestion using SGLBO."""
        try:
            # Check convergence
            convergence_info = self.screening_optimizer.check_convergence()
            
            if convergence_info["converged"]:
                self.is_converged = True
                self._add_to_history(f"\n*** SCREENING CONVERGED ***")
                self._add_to_history(f"Reason: {convergence_info['recommendation']}")
                
                # Get final results
                self._show_final_results()
                return
            
            # Generate next suggestion
            next_suggestion = self.screening_optimizer.suggest_next_experiment()
            
            if next_suggestion:
                self.current_suggestions = [next_suggestion]
                self.current_suggestion_index = 0
                
                self._update_suggestion_display()
                self._update_navigation_buttons()
                
                # Don't add gradient vector yet - wait until user inputs results
                
                self._add_to_history(f"Next suggestion generated (iteration {len(self.screening_optimizer.iteration_history) + 1})")
                
            else:
                self._add_to_history("No more suggestions available. Screening may be complete.")
                messagebox.showinfo("Complete", "No more suggestions available. Consider generating design space.")
        
        except Exception as e:
            logger.error(f"Error generating next suggestion: {e}")
            messagebox.showerror("Error", f"Failed to generate next suggestion: {e}")
    
    def _update_progress_display(self):
        """Update the progress display."""
        total_experiments = len(self.screening_optimizer.experimental_data)
        max_iterations = self.config['sglbo_settings'].get('max_iterations', 20)
        
        if self.is_converged:
            self.progress_label.config(text=f"Screening CONVERGED after {total_experiments} experiments")
        elif self.is_initial_phase:
            n_initial = self.config['sglbo_settings'].get('n_initial_samples', 8)
            self.progress_label.config(text=f"Initial phase: {total_experiments}/{n_initial} experiments completed")
        else:
            iterations = len(self.screening_optimizer.iteration_history)
            self.progress_label.config(text=f"Iterative phase: {total_experiments} experiments, {iterations} iterations, max {max_iterations}")
    
    def _show_final_results(self):
        """Show final screening results."""
        try:
            # Get best parameters and responses
            best_params, best_responses = self.results_manager.get_best_parameters()
            
            # Generate analysis
            param_effects = self.results_manager.analyze_parameter_effects()
            recommendations = self.results_manager.generate_optimization_recommendations()
            
            # Display results
            self._add_to_history(f"\n=== FINAL SCREENING RESULTS ===")
            self._add_to_history(f"Total Experiments: {len(self.screening_optimizer.experimental_data)}")
            self._add_to_history(f"Best Parameters: {best_params}")
            self._add_to_history(f"Best Responses: {best_responses}")
            
            if "overall_parameter_importance" in param_effects:
                self._add_to_history(f"\nParameter Importance Ranking:")
                for rank in param_effects["overall_parameter_importance"][:3]:  # Top 3
                    self._add_to_history(f"  {rank['parameter']}: {rank['importance_score']:.3f}")
            
            self._add_to_history(f"\nReady for design space generation and detailed optimization!")
            
            # Enable design space generation
            messagebox.showinfo("Screening Complete", 
                              "Screening optimization completed successfully!\n\n" +
                              "You can now generate a design space around the optimal region " +
                              "for detailed Bayesian optimization.")
            
        except Exception as e:
            logger.error(f"Error showing final results: {e}")
            self._add_to_history(f"Error generating final results: {e}")
    
    def _add_to_history(self, message):
        """Add a message to the history display."""
        timestamp = time.strftime("%H:%M:%S")
        self.history_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.history_text.see(tk.END)
    
    def _export_results(self):
        """Export screening results to file."""
        try:
            # Ask user for file location
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[
                    ("JSON files", "*.json"),
                    ("Excel files", "*.xlsx"),
                    ("All files", "*.*")
                ],
                title="Export Screening Results"
            )
            
            if file_path:
                # Determine format from extension
                if file_path.endswith('.xlsx'):
                    format_type = "excel"
                else:
                    format_type = "json"
                
                # Export results
                success = self.results_manager.export_results(file_path, format=format_type)
                
                if success:
                    messagebox.showinfo("Export Successful", 
                                      f"Results exported successfully to:\\n{file_path}")
                    self._add_to_history(f"Results exported to {file_path}")
                else:
                    messagebox.showerror("Export Failed", 
                                       "Failed to export results. Check the log for details.")
                    
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            messagebox.showerror("Export Error", f"Error exporting results: {e}")
    
    def _generate_design_space(self):
        """Generate design space around the best parameters."""
        try:
            # Get best parameters
            best_params, best_responses = self.results_manager.get_best_parameters()
            
            if not best_params:
                messagebox.showwarning("No Results", "No experimental results available for design space generation.")
                return
            
            # Generate design space
            design_points = self.design_generator.generate_central_composite_design(
                center_point=best_params,
                design_radius=0.15,
                include_center=True,
                include_axial=True,
                include_factorial=True
            )
            
            if design_points:
                # Show design space window or export
                result = messagebox.askyesno("Design Space Generated", 
                                           f"Generated {len(design_points)} design points around optimal region.\n\n" +
                                           f"Would you like to export them to CSV for use in detailed optimization?")
                
                if result:
                    # Export design points
                    file_path = filedialog.asksaveasfilename(
                        defaultextension=".csv",
                        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                        title="Export Design Space"
                    )
                    
                    if file_path:
                        design_df = pd.DataFrame(design_points)
                        design_df.to_csv(file_path, index=False)
                        messagebox.showinfo("Export Successful", f"Design space exported to:\\n{file_path}")
                        self._add_to_history(f"Design space ({len(design_points)} points) exported to {file_path}")
                
                self._add_to_history(f"Generated design space with {len(design_points)} points around best parameters")
            
        except Exception as e:
            logger.error(f"Error generating design space: {e}")
            messagebox.showerror("Design Space Error", f"Failed to generate design space: {e}")
    
    def _reset_screening(self):
        """Reset the screening to start over."""
        result = messagebox.askyesno("Reset Screening", 
                                   "Are you sure you want to reset the screening?\n\n" +
                                   "This will clear all experimental data and start over.")
        
        if result:
            try:
                # Reset optimizer and results manager
                self.screening_optimizer.experimental_data = pd.DataFrame()
                self.screening_optimizer.iteration_history = []
                self.screening_optimizer.gp_models = {}
                self.screening_optimizer.current_best_params = None
                self.screening_optimizer.current_best_response = None
                self.screening_optimizer.converged = False
                
                # Reset results manager
                self.results_manager.experimental_data = pd.DataFrame()
                self.results_manager.iteration_history = []
                
                # Reset UI state
                self.experiment_count = 0
                self.is_initial_phase = True
                self.is_converged = False
                self.experiment_points = []
                self.completed_points = set()
                self.plot_circles = []
                self.current_contours = []
                self.response_history = {name: [] for name in self.response_names}
                
                # Clear displays
                self.history_text.delete(1.0, tk.END)
                self._clear_input()
                
                # Clear plots
                if self.plot_ax:
                    self.plot_ax.clear()
                    self._set_plot_bounds()
                    self.plot_ax.grid(True, alpha=0.3)
                    if self.plot_canvas:
                        self.plot_canvas.draw()
                
                if self.trends_ax:
                    self.trends_ax.clear()
                    self.trends_ax.set_title("Response Trends Over Time", fontsize=12, fontweight='bold')
                    self.trends_ax.set_xlabel("Experiment Number", fontsize=10)
                    self.trends_ax.set_ylabel("Response Values", fontsize=10)
                    self.trends_ax.grid(True, alpha=0.3)
                    if self.trends_canvas:
                        self.trends_canvas.draw()
                
                if self.importance_ax:
                    self.importance_ax.clear()
                    self.importance_ax.set_title("Parameter Importance Analysis", fontsize=12, fontweight='bold')
                    self.importance_ax.set_xlabel("Importance Score", fontsize=10)
                    self.importance_ax.set_ylabel("Parameters", fontsize=10)
                    self.importance_ax.grid(True, alpha=0.3, axis='x')
                    if self.importance_canvas:
                        self.importance_canvas.draw()
                
                if self.correlation_ax:
                    self.correlation_ax.clear()
                    self.correlation_ax.set_title("Parameter-Response Correlation Matrix", fontsize=12, fontweight='bold')
                    if self.correlation_canvas:
                        self.correlation_canvas.draw()
                
                # Generate new initial suggestions
                self._generate_initial_suggestions()
                
                self._add_to_history("Screening reset successfully. Ready to start over.")
                
            except Exception as e:
                logger.error(f"Error resetting screening: {e}")
                messagebox.showerror("Reset Error", f"Failed to reset screening: {e}")
    
    def _close_window(self):
        """Close the interactive screening window."""
        if self.experiment_count > 0 and not self.is_converged:
            result = messagebox.askyesno("Confirm Close", 
                                       f"You have completed {self.experiment_count} experiments.\n\n" +
                                       f"Are you sure you want to close the screening window?")
            if not result:
                return
        
        self.window.destroy()


def show_interactive_screening_window(parent, screening_optimizer, results_manager, design_generator, config):
    """
    Show the interactive screening execution window.
    
    Args:
        parent: Parent window
        screening_optimizer: SGLBO screening optimizer instance
        results_manager: Screening results manager instance  
        design_generator: Design space generator instance
        config: Screening configuration dictionary
    """
    return InteractiveScreeningWindow(parent, screening_optimizer, results_manager, design_generator, config)