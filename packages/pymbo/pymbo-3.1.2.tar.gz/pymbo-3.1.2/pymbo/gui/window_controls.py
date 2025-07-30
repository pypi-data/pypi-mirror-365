"""
Window Controls Module
Separate window implementation of plot control panels
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable

logger = logging.getLogger(__name__)


class WindowPlotControlPanel:
    """Plot control panel in a separate window"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        self.axis_ranges = {}
        
        # Initialize default axis ranges
        self.axis_ranges = {
            'x_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'x_max': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_min': {'var': tk.StringVar(value='auto'), 'auto': True},
            'y_max': {'var': tk.StringVar(value='auto'), 'auto': True}
        }
        
        logger.info(f"Window plot control panel created for {plot_type}")
    
    def create_window(self):
        """Create the control panel window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ {self.plot_type.replace('_', ' ').title()} Controls")
        self.window.geometry("350x450")
        self.window.resizable(False, False)
        
        # Set window icon (if available)
        try:
            self.window.iconbitmap(default='')
        except:
            pass
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title with icon
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = ttk.Label(title_frame, text=f"📊 {self.plot_type.replace('_', ' ').title()} Controls", 
                               font=('Arial', 14, 'bold'))
        title_label.pack()
        
        # Create notebook for organized controls
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Axis tab
        axis_tab = ttk.Frame(notebook)
        notebook.add(axis_tab, text="Axis Settings")
        self._create_window_axis_controls(axis_tab)
        
        # Appearance tab
        appearance_tab = ttk.Frame(notebook)
        notebook.add(appearance_tab, text="Appearance")
        self._create_appearance_controls(appearance_tab)
        
        # Export tab
        export_tab = ttk.Frame(notebook)
        notebook.add(export_tab, text="Export")
        self._create_export_controls(export_tab)
        
        # Action buttons
        self._create_window_buttons(main_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"Control window created for {self.plot_type}")
    
    def _create_window_axis_controls(self, parent):
        """Create comprehensive axis range controls"""
        # X-axis section
        x_frame = ttk.LabelFrame(parent, text="X-Axis Configuration")
        x_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # X-axis range
        x_range_frame = ttk.Frame(x_frame)
        x_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(x_range_frame, text="Range:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(x_range_frame, text="Min:").grid(row=0, column=1, sticky='w')
        x_min_entry = ttk.Entry(x_range_frame, textvariable=self.axis_ranges['x_min']['var'], width=12)
        x_min_entry.grid(row=0, column=2, padx=(5, 10), sticky='ew')
        
        ttk.Label(x_range_frame, text="Max:").grid(row=0, column=3, sticky='w')
        x_max_entry = ttk.Entry(x_range_frame, textvariable=self.axis_ranges['x_max']['var'], width=12)
        x_max_entry.grid(row=0, column=4, padx=(5, 0), sticky='ew')
        
        x_range_frame.columnconfigure(2, weight=1)
        x_range_frame.columnconfigure(4, weight=1)
        
        # Y-axis section
        y_frame = ttk.LabelFrame(parent, text="Y-Axis Configuration")
        y_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Y-axis range  
        y_range_frame = ttk.Frame(y_frame)
        y_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(y_range_frame, text="Range:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Label(y_range_frame, text="Min:").grid(row=0, column=1, sticky='w')
        y_min_entry = ttk.Entry(y_range_frame, textvariable=self.axis_ranges['y_min']['var'], width=12)
        y_min_entry.grid(row=0, column=2, padx=(5, 10), sticky='ew')
        
        ttk.Label(y_range_frame, text="Max:").grid(row=0, column=3, sticky='w')
        y_max_entry = ttk.Entry(y_range_frame, textvariable=self.axis_ranges['y_max']['var'], width=12)
        y_max_entry.grid(row=0, column=4, padx=(5, 0), sticky='ew')
        
        y_range_frame.columnconfigure(2, weight=1)
        y_range_frame.columnconfigure(4, weight=1)
        
        # Auto scale section
        auto_frame = ttk.Frame(parent)
        auto_frame.pack(fill=tk.X, padx=10, pady=10)
        
        auto_button = ttk.Button(auto_frame, text="🔄 Auto Scale Both Axes", 
                                command=self._auto_scale, style='Accent.TButton')
        auto_button.pack()
    
    def _create_appearance_controls(self, parent):
        """Create appearance control options"""
        # Grid options
        grid_frame = ttk.LabelFrame(parent, text="Grid Options")
        grid_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_grid_var = tk.BooleanVar(value=True)
        grid_check = ttk.Checkbutton(grid_frame, text="Show Grid", 
                                    variable=self.show_grid_var)
        grid_check.pack(anchor='w', padx=10, pady=5)
        
        # Legend options
        legend_frame = ttk.LabelFrame(parent, text="Legend Options")
        legend_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.show_legend_var = tk.BooleanVar(value=True)
        legend_check = ttk.Checkbutton(legend_frame, text="Show Legend", 
                                      variable=self.show_legend_var)
        legend_check.pack(anchor='w', padx=10, pady=5)
        
        # Color scheme
        color_frame = ttk.LabelFrame(parent, text="Color Scheme")
        color_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.color_scheme_var = tk.StringVar(value="default")
        ttk.Radiobutton(color_frame, text="Default", variable=self.color_scheme_var, 
                       value="default").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(color_frame, text="Colorblind Friendly", variable=self.color_scheme_var, 
                       value="colorblind").pack(anchor='w', padx=10, pady=2)
        ttk.Radiobutton(color_frame, text="High Contrast", variable=self.color_scheme_var, 
                       value="high_contrast").pack(anchor='w', padx=10, pady=2)
    
    def _create_export_controls(self, parent):
        """Create export control options"""
        export_frame = ttk.LabelFrame(parent, text="Export Settings")
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # DPI settings
        dpi_frame = ttk.Frame(export_frame)
        dpi_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(dpi_frame, text="Resolution (DPI):").pack(side=tk.LEFT)
        self.dpi_var = tk.StringVar(value="300")
        dpi_combo = ttk.Combobox(dpi_frame, textvariable=self.dpi_var, 
                                values=["150", "300", "600", "1200"], width=10)
        dpi_combo.pack(side=tk.RIGHT)
        
        # Format settings
        format_frame = ttk.Frame(export_frame)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="PNG")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["PNG", "PDF", "SVG", "JPG"], width=10)
        format_combo.pack(side=tk.RIGHT)
        
        # Export button
        export_btn = ttk.Button(export_frame, text="💾 Export Plot", 
                               command=self._export_plot)
        export_btn.pack(pady=10)
    
    def _create_window_buttons(self, parent):
        """Create action buttons for window"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side buttons
        refresh_button = ttk.Button(button_frame, text="🔄 Refresh Plot", 
                                   command=self._refresh_plot, style='Accent.TButton')
        refresh_button.pack(side=tk.LEFT)
        
        apply_button = ttk.Button(button_frame, text="✓ Apply Settings", 
                                 command=self._apply_settings)
        apply_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # Right side buttons
        close_button = ttk.Button(button_frame, text="✕ Close", command=self.hide)
        close_button.pack(side=tk.RIGHT)
        
        reset_button = ttk.Button(button_frame, text="↺ Reset", command=self._reset_settings)
        reset_button.pack(side=tk.RIGHT, padx=(0, 5))
    
    def _auto_scale(self):
        """Reset axis ranges to auto"""
        for axis in self.axis_ranges:
            self.axis_ranges[axis]['var'].set('auto')
            self.axis_ranges[axis]['auto'] = True
        logger.info(f"Auto scale applied for {self.plot_type}")
    
    def _refresh_plot(self):
        """Refresh the plot with current settings"""
        logger.info(f"Plot refresh requested for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Update callback executed for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error calling update callback for {self.plot_type}: {e}")
    
    def _apply_settings(self):
        """Apply current settings to the plot"""
        logger.info(f"Settings applied for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"Settings applied and plot updated for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error applying settings for {self.plot_type}: {e}")
    
    def _reset_settings(self):
        """Reset all settings to defaults"""
        self._auto_scale()
        self.show_grid_var.set(True)
        self.show_legend_var.set(True)
        self.color_scheme_var.set("default")
        self.dpi_var.set("300")
        self.format_var.set("PNG")
        logger.info(f"Settings reset for {self.plot_type}")
    
    def _export_plot(self):
        """Export the plot with current settings"""
        logger.info(f"Plot export requested for {self.plot_type} "
                   f"(Format: {self.format_var.get()}, DPI: {self.dpi_var.get()})")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        logger.info(f"Control window shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info(f"Control window hidden for {self.plot_type}")
    
    def get_axis_ranges(self):
        """Get current axis range settings"""
        ranges = {}
        for axis_name, axis_data in self.axis_ranges.items():
            value = axis_data['var'].get()
            is_auto = value.lower() == 'auto'
            try:
                numeric_value = float(value) if not is_auto else None
            except ValueError:
                numeric_value = None
                is_auto = True
            ranges[axis_name] = (numeric_value, numeric_value, is_auto)
        return ranges


def create_window_plot_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                    responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> WindowPlotControlPanel:
    """Factory function to create a window plot control panel"""
    try:
        # Check for specialized plot types
        if plot_type == 'surface_3d' or '3d' in plot_type.lower() or 'surface' in plot_type.lower():
            try:
                from .surface_3d_controls import create_surface_3d_control_panel
                return create_surface_3d_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("3D Surface controls not available, using standard controls")
        
        elif plot_type == 'gp_uncertainty' or 'uncertainty' in plot_type.lower():
            try:
                from .gp_uncertainty_controls import create_gp_uncertainty_control_panel
                return create_gp_uncertainty_control_panel(parent, plot_type, params_config, responses_config, update_callback)
            except ImportError:
                logger.warning("GP Uncertainty controls not available, using standard controls")
        
        # Default to standard window controls
        control_panel = WindowPlotControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created window plot control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating window plot control panel for {plot_type}: {e}")
        raise