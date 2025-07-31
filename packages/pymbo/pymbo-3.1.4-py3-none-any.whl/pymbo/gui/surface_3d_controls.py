"""
3D Surface Plot Controls Module
Specialized control panels for 3D surface plots with extensive customization options
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Dict, Any, Callable
import matplotlib.pyplot as plt
from matplotlib import cm

logger = logging.getLogger(__name__)


class Surface3DControlPanel:
    """Specialized control panel for 3D surface plots with extensive options"""
    
    def __init__(self, parent, plot_type: str, params_config: Dict[str, Any] = None, 
                 responses_config: Dict[str, Any] = None, update_callback: Callable = None):
        self.parent = parent
        self.plot_type = plot_type
        self.params_config = params_config or {}
        self.responses_config = responses_config or {}
        self.update_callback = update_callback
        self.window = None
        
        # 3D Surface specific settings
        self.surface_settings = {
            # Axis ranges
            'x_min': tk.StringVar(value='auto'),
            'x_max': tk.StringVar(value='auto'),
            'y_min': tk.StringVar(value='auto'),
            'y_max': tk.StringVar(value='auto'),
            'z_min': tk.StringVar(value='auto'),
            'z_max': tk.StringVar(value='auto'),
            
            # Surface appearance
            'colormap': tk.StringVar(value='viridis'),
            'alpha': tk.DoubleVar(value=0.8),
            'wireframe': tk.BooleanVar(value=False),
            'surface_fill': tk.BooleanVar(value=True),
            'edge_color': tk.StringVar(value='black'),
            'edge_alpha': tk.DoubleVar(value=0.3),
            'antialiased': tk.BooleanVar(value=True),
            
            # Mesh resolution
            'x_resolution': tk.IntVar(value=50),
            'y_resolution': tk.IntVar(value=50),
            'interpolation_method': tk.StringVar(value='linear'),
            
            # Lighting and shading
            'lighting_enabled': tk.BooleanVar(value=True),
            'light_elevation': tk.DoubleVar(value=45),
            'light_azimuth': tk.DoubleVar(value=45),
            'shade': tk.BooleanVar(value=True),
            'norm_colors': tk.BooleanVar(value=True),
            
            # View angle
            'elevation': tk.DoubleVar(value=30),
            'azimuth': tk.DoubleVar(value=45),
            'roll': tk.DoubleVar(value=0),
            'distance': tk.DoubleVar(value=10),
            
            # Contour options
            'show_contours': tk.BooleanVar(value=False),
            'contour_levels': tk.IntVar(value=10),
            'contour_offset': tk.DoubleVar(value=-0.1),
            'contour_alpha': tk.DoubleVar(value=0.6),
            
            # Color bar
            'show_colorbar': tk.BooleanVar(value=True),
            'colorbar_position': tk.StringVar(value='right'),
            'colorbar_shrink': tk.DoubleVar(value=0.8),
            'colorbar_aspect': tk.IntVar(value=20),
            
            # Data points
            'show_data_points': tk.BooleanVar(value=False),
            'data_point_size': tk.DoubleVar(value=30),
            'data_point_color': tk.StringVar(value='red'),
            'data_point_alpha': tk.DoubleVar(value=0.8),
            
            # Grid and axes
            'show_grid': tk.BooleanVar(value=True),
            'grid_alpha': tk.DoubleVar(value=0.3),
            'axes_visible': tk.BooleanVar(value=True),
            'tick_density': tk.StringVar(value='medium'),
            
            # Labels and title
            'x_label': tk.StringVar(value='X Parameter'),
            'y_label': tk.StringVar(value='Y Parameter'),
            'z_label': tk.StringVar(value='Response'),
            'title': tk.StringVar(value='3D Surface Plot'),
            'title_size': tk.IntVar(value=12),
            'label_size': tk.IntVar(value=10),
        }
        
        logger.info(f"3D Surface control panel created for {plot_type}")
    
    def create_window(self):
        """Create the comprehensive 3D surface control window"""
        if self.window is not None:
            self.show()
            return
            
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"🎛️ 3D Surface Plot Controls - {self.plot_type.replace('_', ' ').title()}")
        self.window.geometry("1275x550")
        self.window.resizable(False, False)
        
        # Create main frame with scrollable content
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(main_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create tabbed interface for organized controls
        notebook = ttk.Notebook(scrollable_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Configure notebook to use wider space efficiently
        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[20, 5])
        
        # Create all control tabs
        self._create_axes_tab(notebook)
        self._create_appearance_tab(notebook)
        self._create_mesh_tab(notebook)
        self._create_lighting_tab(notebook)
        self._create_view_tab(notebook)
        self._create_contours_tab(notebook)
        self._create_colorbar_tab(notebook)
        self._create_data_points_tab(notebook)
        self._create_labels_tab(notebook)
        
        # Action buttons at the bottom
        self._create_action_buttons(scrollable_frame)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Center the window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (self.window.winfo_width() // 2)
        y = (self.window.winfo_screenheight() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
        logger.info(f"3D Surface control window created for {self.plot_type}")
    
    def _create_axes_tab(self, notebook):
        """Create axes and ranges tab"""
        axes_tab = ttk.Frame(notebook)
        notebook.add(axes_tab, text="📊 Axes & Ranges")
        
        # X-axis section
        x_frame = ttk.LabelFrame(axes_tab, text="X-Axis Configuration")
        x_frame.pack(fill=tk.X, padx=10, pady=5)
        
        x_range_frame = ttk.Frame(x_frame)
        x_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(x_range_frame, text="Range:").grid(row=0, column=0, sticky='w')
        ttk.Label(x_range_frame, text="Min:").grid(row=0, column=1, sticky='w', padx=(10, 0))
        ttk.Entry(x_range_frame, textvariable=self.surface_settings['x_min'], width=10).grid(row=0, column=2, padx=5)
        ttk.Label(x_range_frame, text="Max:").grid(row=0, column=3, sticky='w', padx=(10, 0))
        ttk.Entry(x_range_frame, textvariable=self.surface_settings['x_max'], width=10).grid(row=0, column=4, padx=5)
        
        # Y-axis section
        y_frame = ttk.LabelFrame(axes_tab, text="Y-Axis Configuration")
        y_frame.pack(fill=tk.X, padx=10, pady=5)
        
        y_range_frame = ttk.Frame(y_frame)
        y_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(y_range_frame, text="Range:").grid(row=0, column=0, sticky='w')
        ttk.Label(y_range_frame, text="Min:").grid(row=0, column=1, sticky='w', padx=(10, 0))
        ttk.Entry(y_range_frame, textvariable=self.surface_settings['y_min'], width=10).grid(row=0, column=2, padx=5)
        ttk.Label(y_range_frame, text="Max:").grid(row=0, column=3, sticky='w', padx=(10, 0))
        ttk.Entry(y_range_frame, textvariable=self.surface_settings['y_max'], width=10).grid(row=0, column=4, padx=5)
        
        # Z-axis section
        z_frame = ttk.LabelFrame(axes_tab, text="Z-Axis Configuration")
        z_frame.pack(fill=tk.X, padx=10, pady=5)
        
        z_range_frame = ttk.Frame(z_frame)
        z_range_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(z_range_frame, text="Range:").grid(row=0, column=0, sticky='w')
        ttk.Label(z_range_frame, text="Min:").grid(row=0, column=1, sticky='w', padx=(10, 0))
        ttk.Entry(z_range_frame, textvariable=self.surface_settings['z_min'], width=10).grid(row=0, column=2, padx=5)
        ttk.Label(z_range_frame, text="Max:").grid(row=0, column=3, sticky='w', padx=(10, 0))
        ttk.Entry(z_range_frame, textvariable=self.surface_settings['z_max'], width=10).grid(row=0, column=4, padx=5)
        
        # Auto scale button
        ttk.Button(axes_tab, text="🔄 Auto Scale All Axes", command=self._auto_scale_all).pack(pady=10)
    
    def _create_appearance_tab(self, notebook):
        """Create surface appearance tab"""
        appearance_tab = ttk.Frame(notebook)
        notebook.add(appearance_tab, text="🎨 Appearance")
        
        # Colormap section
        colormap_frame = ttk.LabelFrame(appearance_tab, text="Color Mapping")
        colormap_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(colormap_frame, text="Colormap:").pack(anchor='w', padx=10, pady=2)
        colormap_combo = ttk.Combobox(colormap_frame, textvariable=self.surface_settings['colormap'],
                                     values=['viridis', 'plasma', 'inferno', 'magma', 'coolwarm', 
                                            'RdYlBu', 'seismic', 'terrain', 'ocean', 'gist_earth',
                                            'rainbow', 'jet', 'hot', 'cool', 'spring', 'summer',
                                            'autumn', 'winter', 'bone', 'copper', 'pink', 'gray'])
        colormap_combo.pack(fill=tk.X, padx=10, pady=2)
        
        # Surface properties
        surface_frame = ttk.LabelFrame(appearance_tab, text="Surface Properties")
        surface_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Alpha control
        alpha_frame = ttk.Frame(surface_frame)
        alpha_frame.pack(fill=tk.X, padx=10, pady=2)
        ttk.Label(alpha_frame, text="Surface Alpha:").grid(row=0, column=0, sticky='w', padx=(0, 10))
        ttk.Scale(alpha_frame, from_=0.0, to=1.0, variable=self.surface_settings['alpha'],
                 orient=tk.HORIZONTAL, length=200).grid(row=0, column=1, sticky='ew')
        alpha_frame.columnconfigure(1, weight=1)
        
        # Checkboxes in two columns
        checkbox_frame = ttk.Frame(surface_frame)
        checkbox_frame.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Checkbutton(checkbox_frame, text="Show Wireframe", 
                       variable=self.surface_settings['wireframe']).grid(row=0, column=0, sticky='w', padx=(0, 20))
        ttk.Checkbutton(checkbox_frame, text="Fill Surface", 
                       variable=self.surface_settings['surface_fill']).grid(row=0, column=1, sticky='w')
        ttk.Checkbutton(checkbox_frame, text="Antialiased", 
                       variable=self.surface_settings['antialiased']).grid(row=1, column=0, sticky='w', padx=(0, 20), pady=(2, 0))
        
        # Edge properties
        edge_frame = ttk.LabelFrame(appearance_tab, text="Edge Properties")
        edge_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(edge_frame, text="Edge Color:").pack(anchor='w', padx=10, pady=2)
        edge_color_combo = ttk.Combobox(edge_frame, textvariable=self.surface_settings['edge_color'],
                                       values=['black', 'white', 'gray', 'red', 'blue', 'green', 'none'])
        edge_color_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(edge_frame, text="Edge Alpha:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(edge_frame, from_=0.0, to=1.0, variable=self.surface_settings['edge_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_mesh_tab(self, notebook):
        """Create mesh resolution tab"""
        mesh_tab = ttk.Frame(notebook)
        notebook.add(mesh_tab, text="🔲 Mesh & Resolution")
        
        # Resolution settings
        resolution_frame = ttk.LabelFrame(mesh_tab, text="Mesh Resolution")
        resolution_frame.pack(fill=tk.X, padx=10, pady=5)
        
        res_grid = ttk.Frame(resolution_frame)
        res_grid.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(res_grid, text="X Resolution:").grid(row=0, column=0, sticky='w')
        ttk.Spinbox(res_grid, from_=10, to=200, textvariable=self.surface_settings['x_resolution'],
                   width=10).grid(row=0, column=1, padx=5)
        
        ttk.Label(res_grid, text="Y Resolution:").grid(row=1, column=0, sticky='w', pady=(5, 0))
        ttk.Spinbox(res_grid, from_=10, to=200, textvariable=self.surface_settings['y_resolution'],
                   width=10).grid(row=1, column=1, padx=5, pady=(5, 0))
        
        # Interpolation method
        interp_frame = ttk.LabelFrame(mesh_tab, text="Interpolation")
        interp_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(interp_frame, text="Method:").pack(anchor='w', padx=10, pady=2)
        interp_combo = ttk.Combobox(interp_frame, textvariable=self.surface_settings['interpolation_method'],
                                   values=['linear', 'cubic', 'nearest', 'quintic'])
        interp_combo.pack(fill=tk.X, padx=10, pady=2)
        
        # Preset buttons
        preset_frame = ttk.Frame(mesh_tab)
        preset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(preset_frame, text="Low Quality (Fast)", 
                  command=lambda: self._set_resolution_preset('low')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="Medium Quality", 
                  command=lambda: self._set_resolution_preset('medium')).pack(side=tk.LEFT, padx=2)
        ttk.Button(preset_frame, text="High Quality (Slow)", 
                  command=lambda: self._set_resolution_preset('high')).pack(side=tk.LEFT, padx=2)
    
    def _create_lighting_tab(self, notebook):
        """Create lighting and shading tab"""
        lighting_tab = ttk.Frame(notebook)
        notebook.add(lighting_tab, text="💡 Lighting & Shading")
        
        # Lighting controls
        lighting_frame = ttk.LabelFrame(lighting_tab, text="Lighting Settings")
        lighting_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(lighting_frame, text="Enable Lighting", 
                       variable=self.surface_settings['lighting_enabled']).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(lighting_frame, text="Light Elevation:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(lighting_frame, from_=0, to=90, variable=self.surface_settings['light_elevation'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(lighting_frame, text="Light Azimuth:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(lighting_frame, from_=0, to=360, variable=self.surface_settings['light_azimuth'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Shading options
        shading_frame = ttk.LabelFrame(lighting_tab, text="Shading Options")
        shading_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(shading_frame, text="Enable Shading", 
                       variable=self.surface_settings['shade']).pack(anchor='w', padx=10, pady=2)
        ttk.Checkbutton(shading_frame, text="Normalize Colors", 
                       variable=self.surface_settings['norm_colors']).pack(anchor='w', padx=10, pady=2)
    
    def _create_view_tab(self, notebook):
        """Create view angle tab"""
        view_tab = ttk.Frame(notebook)
        notebook.add(view_tab, text="👁️ View Angle")
        
        # View angle controls
        view_frame = ttk.LabelFrame(view_tab, text="3D View Settings")
        view_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(view_frame, text="Elevation (vertical):").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=-90, to=90, variable=self.surface_settings['elevation'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(view_frame, text="Azimuth (horizontal):").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=0, to=360, variable=self.surface_settings['azimuth'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(view_frame, text="Roll:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=-180, to=180, variable=self.surface_settings['roll'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(view_frame, text="Distance (zoom):").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(view_frame, from_=1, to=20, variable=self.surface_settings['distance'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Preset view buttons in a grid
        preset_frame = ttk.Frame(view_tab)
        preset_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(preset_frame, text="Top View", width=12,
                  command=lambda: self._set_view_preset('top')).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(preset_frame, text="Side View", width=12,
                  command=lambda: self._set_view_preset('side')).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(preset_frame, text="Isometric", width=12,
                  command=lambda: self._set_view_preset('iso')).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(preset_frame, text="Reset", width=12,
                  command=lambda: self._set_view_preset('default')).grid(row=1, column=1, padx=2, pady=2)
    
    def _create_contours_tab(self, notebook):
        """Create contour options tab"""
        contours_tab = ttk.Frame(notebook)
        notebook.add(contours_tab, text="📈 Contours")
        
        # Contour settings
        contour_frame = ttk.LabelFrame(contours_tab, text="Contour Settings")
        contour_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(contour_frame, text="Show Contour Lines", 
                       variable=self.surface_settings['show_contours']).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(contour_frame, text="Number of Levels:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(contour_frame, from_=5, to=50, textvariable=self.surface_settings['contour_levels'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(contour_frame, text="Contour Offset:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(contour_frame, from_=-1.0, to=1.0, variable=self.surface_settings['contour_offset'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(contour_frame, text="Contour Alpha:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(contour_frame, from_=0.0, to=1.0, variable=self.surface_settings['contour_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
    
    def _create_colorbar_tab(self, notebook):
        """Create colorbar options tab"""
        colorbar_tab = ttk.Frame(notebook)
        notebook.add(colorbar_tab, text="🌈 Color Bar")
        
        # Colorbar settings
        colorbar_frame = ttk.LabelFrame(colorbar_tab, text="Color Bar Settings")
        colorbar_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(colorbar_frame, text="Show Color Bar", 
                       variable=self.surface_settings['show_colorbar']).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(colorbar_frame, text="Position:").pack(anchor='w', padx=10, pady=2)
        position_combo = ttk.Combobox(colorbar_frame, textvariable=self.surface_settings['colorbar_position'],
                                     values=['right', 'left', 'top', 'bottom'])
        position_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(colorbar_frame, text="Size (shrink):").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(colorbar_frame, from_=0.1, to=1.0, variable=self.surface_settings['colorbar_shrink'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(colorbar_frame, text="Aspect Ratio:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(colorbar_frame, from_=5, to=50, textvariable=self.surface_settings['colorbar_aspect'],
                   width=10).pack(anchor='w', padx=10, pady=2)
    
    def _create_data_points_tab(self, notebook):
        """Create data points overlay tab"""
        points_tab = ttk.Frame(notebook)
        notebook.add(points_tab, text="📍 Data Points")
        
        # Data points settings
        points_frame = ttk.LabelFrame(points_tab, text="Data Points Overlay")
        points_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(points_frame, text="Show Original Data Points", 
                       variable=self.surface_settings['show_data_points']).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(points_frame, text="Point Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(points_frame, from_=1, to=100, variable=self.surface_settings['data_point_size'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(points_frame, text="Point Color:").pack(anchor='w', padx=10, pady=2)
        color_combo = ttk.Combobox(points_frame, textvariable=self.surface_settings['data_point_color'],
                                  values=['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'black', 'white'])
        color_combo.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(points_frame, text="Point Alpha:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(points_frame, from_=0.0, to=1.0, variable=self.surface_settings['data_point_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        # Grid and axes
        grid_frame = ttk.LabelFrame(points_tab, text="Grid & Axes")
        grid_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Checkbutton(grid_frame, text="Show Grid", 
                       variable=self.surface_settings['show_grid']).pack(anchor='w', padx=10, pady=2)
        ttk.Checkbutton(grid_frame, text="Show Axes", 
                       variable=self.surface_settings['axes_visible']).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(grid_frame, text="Grid Alpha:").pack(anchor='w', padx=10, pady=2)
        ttk.Scale(grid_frame, from_=0.0, to=1.0, variable=self.surface_settings['grid_alpha'],
                 orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(grid_frame, text="Tick Density:").pack(anchor='w', padx=10, pady=2)
        tick_combo = ttk.Combobox(grid_frame, textvariable=self.surface_settings['tick_density'],
                                 values=['low', 'medium', 'high'])
        tick_combo.pack(fill=tk.X, padx=10, pady=2)
    
    def _create_labels_tab(self, notebook):
        """Create labels and title tab"""
        labels_tab = ttk.Frame(notebook)
        notebook.add(labels_tab, text="🏷️ Labels & Title")
        
        # Labels section
        labels_frame = ttk.LabelFrame(labels_tab, text="Axis Labels")
        labels_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(labels_frame, text="X-Axis Label:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.surface_settings['x_label']).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(labels_frame, text="Y-Axis Label:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.surface_settings['y_label']).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(labels_frame, text="Z-Axis Label:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(labels_frame, textvariable=self.surface_settings['z_label']).pack(fill=tk.X, padx=10, pady=2)
        
        # Title section
        title_frame = ttk.LabelFrame(labels_tab, text="Plot Title")
        title_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(title_frame, text="Title:").pack(anchor='w', padx=10, pady=2)
        ttk.Entry(title_frame, textvariable=self.surface_settings['title']).pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(title_frame, text="Title Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(title_frame, from_=8, to=24, textvariable=self.surface_settings['title_size'],
                   width=10).pack(anchor='w', padx=10, pady=2)
        
        ttk.Label(title_frame, text="Label Size:").pack(anchor='w', padx=10, pady=2)
        ttk.Spinbox(title_frame, from_=6, to=18, textvariable=self.surface_settings['label_size'],
                   width=10).pack(anchor='w', padx=10, pady=2)
    
    def _create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Left side buttons
        ttk.Button(button_frame, text="🔄 Apply & Refresh", 
                  command=self._apply_and_refresh, style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="📋 Copy Settings", 
                  command=self._copy_settings).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, text="📁 Save Preset", 
                  command=self._save_preset).pack(side=tk.LEFT, padx=2)
        
        # Right side buttons
        ttk.Button(button_frame, text="✕ Close", command=self.hide).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(button_frame, text="↺ Reset All", 
                  command=self._reset_all_settings).pack(side=tk.RIGHT, padx=2)
        
        ttk.Button(button_frame, text="📤 Export Plot", 
                  command=self._export_plot).pack(side=tk.RIGHT, padx=2)
    
    def _auto_scale_all(self):
        """Auto scale all axes"""
        for axis in ['x_min', 'x_max', 'y_min', 'y_max', 'z_min', 'z_max']:
            self.surface_settings[axis].set('auto')
        logger.info(f"Auto scale applied to all axes for {self.plot_type}")
    
    def _set_resolution_preset(self, preset):
        """Set resolution preset"""
        presets = {
            'low': (25, 25),
            'medium': (50, 50),
            'high': (100, 100)
        }
        if preset in presets:
            x_res, y_res = presets[preset]
            self.surface_settings['x_resolution'].set(x_res)
            self.surface_settings['y_resolution'].set(y_res)
            logger.info(f"Resolution preset '{preset}' applied for {self.plot_type}")
    
    def _set_view_preset(self, preset):
        """Set view angle preset"""
        presets = {
            'top': (90, 0, 0),
            'side': (0, 0, 0),
            'iso': (30, 45, 0),
            'default': (30, 45, 0)
        }
        if preset in presets:
            elev, azim, roll = presets[preset]
            self.surface_settings['elevation'].set(elev)
            self.surface_settings['azimuth'].set(azim)
            self.surface_settings['roll'].set(roll)
            logger.info(f"View preset '{preset}' applied for {self.plot_type}")
    
    def _apply_and_refresh(self):
        """Apply settings and refresh plot"""
        logger.info(f"Applying 3D surface settings for {self.plot_type}")
        if self.update_callback:
            try:
                self.update_callback()
                logger.info(f"3D surface plot updated for {self.plot_type}")
            except Exception as e:
                logger.error(f"Error updating 3D surface plot for {self.plot_type}: {e}")
    
    def _copy_settings(self):
        """Copy current settings to clipboard"""
        logger.info(f"Settings copied for {self.plot_type}")
    
    def _save_preset(self):
        """Save current settings as preset"""
        logger.info(f"Preset saved for {self.plot_type}")
    
    def _reset_all_settings(self):
        """Reset all settings to defaults"""
        # Reset to default values
        defaults = {
            'x_min': 'auto', 'x_max': 'auto', 'y_min': 'auto', 'y_max': 'auto', 'z_min': 'auto', 'z_max': 'auto',
            'colormap': 'viridis', 'alpha': 0.8, 'wireframe': False, 'surface_fill': True,
            'edge_color': 'black', 'edge_alpha': 0.3, 'antialiased': True,
            'x_resolution': 50, 'y_resolution': 50, 'interpolation_method': 'linear',
            'lighting_enabled': True, 'light_elevation': 45, 'light_azimuth': 45, 'shade': True, 'norm_colors': True,
            'elevation': 30, 'azimuth': 45, 'roll': 0, 'distance': 10,
            'show_contours': False, 'contour_levels': 10, 'contour_offset': -0.1, 'contour_alpha': 0.6,
            'show_colorbar': True, 'colorbar_position': 'right', 'colorbar_shrink': 0.8, 'colorbar_aspect': 20,
            'show_data_points': False, 'data_point_size': 30, 'data_point_color': 'red', 'data_point_alpha': 0.8,
            'show_grid': True, 'grid_alpha': 0.3, 'axes_visible': True, 'tick_density': 'medium',
            'x_label': 'X Parameter', 'y_label': 'Y Parameter', 'z_label': 'Response', 
            'title': '3D Surface Plot', 'title_size': 12, 'label_size': 10
        }
        
        for key, value in defaults.items():
            if key in self.surface_settings:
                self.surface_settings[key].set(value)
        
        logger.info(f"All settings reset to defaults for {self.plot_type}")
    
    def _export_plot(self):
        """Export the plot"""
        logger.info(f"Export requested for {self.plot_type}")
    
    def show(self):
        """Show the control panel window"""
        if self.window is None:
            self.create_window()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        logger.info(f"3D Surface control window shown for {self.plot_type}")
    
    def hide(self):
        """Hide the control panel window"""
        if self.window:
            self.window.withdraw()
        logger.info(f"3D Surface control window hidden for {self.plot_type}")
    
    def get_surface_settings(self):
        """Get all current 3D surface settings"""
        settings = {}
        for key, var in self.surface_settings.items():
            try:
                settings[key] = var.get()
            except:
                settings[key] = None
        return settings
    
    def get_axis_ranges(self):
        """Get axis ranges for 3D plotting in the format expected by GUI"""
        try:
            def parse_range_value(value_str):
                """Parse range value, return None for 'auto'"""
                if value_str == 'auto' or value_str == '':
                    return None
                try:
                    return float(value_str)
                except (ValueError, TypeError):
                    return None
            
            # Parse individual range values
            x_min = parse_range_value(self.surface_settings['x_min'].get())
            x_max = parse_range_value(self.surface_settings['x_max'].get())
            y_min = parse_range_value(self.surface_settings['y_min'].get())
            y_max = parse_range_value(self.surface_settings['y_max'].get())
            z_min = parse_range_value(self.surface_settings['z_min'].get())
            z_max = parse_range_value(self.surface_settings['z_max'].get())
            
            # Determine if each axis is auto-scaled
            x_is_auto = (x_min is None or x_max is None)
            y_is_auto = (y_min is None or y_max is None)
            z_is_auto = (z_min is None or z_max is None)
            
            # Return in the format expected by GUI: {axis_name: (min_val, max_val, is_auto)}
            ranges = {
                'x_axis': (x_min, x_max, x_is_auto),
                'y_axis': (y_min, y_max, y_is_auto),
                'z_axis': (z_min, z_max, z_is_auto)
            }
            
            logger.debug(f"Retrieved axis ranges for {self.plot_type}: {ranges}")
            return ranges
            
        except Exception as e:
            logger.error(f"Error getting axis ranges for {self.plot_type}: {e}")
            # Return default ranges (auto-scale)
            return {
                'x_axis': (None, None, True),
                'y_axis': (None, None, True),
                'z_axis': (None, None, True)
            }


def create_surface_3d_control_panel(parent, plot_type: str, params_config: Dict[str, Any] = None, 
                                   responses_config: Dict[str, Any] = None, update_callback: Callable = None) -> Surface3DControlPanel:
    """Factory function to create a 3D surface control panel"""
    try:
        control_panel = Surface3DControlPanel(parent, plot_type, params_config, responses_config, update_callback)
        logger.info(f"Created 3D surface control panel for {plot_type}")
        return control_panel
    except Exception as e:
        logger.error(f"Error creating 3D surface control panel for {plot_type}: {e}")
        raise