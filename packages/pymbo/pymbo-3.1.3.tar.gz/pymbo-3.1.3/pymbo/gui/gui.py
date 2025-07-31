"""
simple_gui_fixed.py

CORRECTED - Simplified GUI with proper parameter goal selection and suggestion display
Replace the original simple_gui.py with this file
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, font
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json

# Import screening execution windows
try:
    from .interactive_screening_window import show_interactive_screening_window
    INTERACTIVE_SCREENING_AVAILABLE = True
except ImportError:
    INTERACTIVE_SCREENING_AVAILABLE = False
    print("Interactive screening window not available")

try:
    from .screening_execution_window import show_screening_execution_window
    SCREENING_WINDOW_AVAILABLE = True
except ImportError:
    SCREENING_WINDOW_AVAILABLE = False
    print("Screening execution window not available - using basic interface")

# Import enhanced plot controls
try:
    from .plot_controls import (
        create_plot_control_panel,
        EnhancedPlotControlPanel,
    )
    from .compact_controls import (
        create_compact_plot_control_panel,
        CompactPlotControlPanel,
    )
    from .movable_controls import (
        create_movable_plot_control_panel,
        MovablePlotControlPanel,
    )
    from .window_controls import (
        create_window_plot_control_panel,
        WindowPlotControlPanel,
    )

    ENHANCED_CONTROLS_AVAILABLE = True
    COMPACT_CONTROLS_AVAILABLE = True
    MOVABLE_CONTROLS_AVAILABLE = True
    WINDOW_CONTROLS_AVAILABLE = True
except ImportError:
    ENHANCED_CONTROLS_AVAILABLE = False
    COMPACT_CONTROLS_AVAILABLE = False
    MOVABLE_CONTROLS_AVAILABLE = False
    WINDOW_CONTROLS_AVAILABLE = False
    print("Enhanced plot controls not available - using basic controls")

# Configuration constants
APP_TITLE = "Multi-Objective Optimization Laboratory v3.0"
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 800
DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

# Color scheme
COLOR_PRIMARY = "#1976D2"
COLOR_SECONDARY = "#424242"
COLOR_SUCCESS = "#4CAF50"
COLOR_WARNING = "#FF9800"
COLOR_ERROR = "#F44336"
COLOR_BACKGROUND = "#FAFAFA"
COLOR_SURFACE = "#FFFFFF"

# Initialize logger for GUI module
logger = logging.getLogger(__name__)


class ModernTheme:
    """Modern color scheme and styling constants for the application"""

    # Color Palette - Modern Material Design inspired
    PRIMARY = "#1976D2"  # Professional blue
    PRIMARY_DARK = "#1565C0"  # Darker blue for hover states
    PRIMARY_LIGHT = "#E3F2FD"  # Light blue for backgrounds

    SECONDARY = "#FF6F00"  # Orange accent
    SECONDARY_DARK = "#E65100"  # Darker orange
    SECONDARY_LIGHT = "#FFF3E0"  # Light orange

    SUCCESS = "#2E7D32"  # Green for success states
    SUCCESS_LIGHT = "#E8F5E8"  # Light green

    WARNING = "#F57C00"  # Amber for warnings
    WARNING_LIGHT = "#FFF8E1"  # Light amber

    ERROR = "#C62828"  # Red for errors
    ERROR_LIGHT = "#FFEBEE"  # Light red

    # Neutral colors
    SURFACE = "#FFFFFF"  # White surface
    BACKGROUND = "#FAFAFA"  # Light gray background
    CARD = "#F5F7FA"  # Card background
    BORDER = "#E0E0E0"  # Border color
    DIVIDER = "#EEEEEE"  # Divider color

    # Text colors
    TEXT_PRIMARY = "#212121"  # Primary text
    TEXT_SECONDARY = "#757575"  # Secondary text
    TEXT_DISABLED = "#BDBDBD"  # Disabled text
    TEXT_HINT = "#9E9E9E"  # Hint text

    # Modern fonts with fallbacks
    @staticmethod
    def get_font(size=10, weight="normal", family="system"):
        """Get appropriate font for the system"""
        font_families = {
            "system": ["Segoe UI", "SF Pro Display", "Roboto", "Arial", "sans-serif"],
            "mono": ["Cascadia Code", "SF Mono", "Consolas", "Monaco", "monospace"],
            "serif": ["Georgia", "Times New Roman", "serif"],
        }

        for font_name in font_families.get(family, font_families["system"]):
            try:
                return (font_name, size, weight)
            except:
                continue
        return ("Arial", size, weight)

    # Common styles
    BUTTON_STYLE = {
        "relief": "flat",
        "borderwidth": 0,
        "pady": 8,
        "padx": 16,
        "cursor": "hand2",
    }

    CARD_STYLE = {"relief": "flat", "borderwidth": 1, "pady": 16, "padx": 16}

    INPUT_STYLE = {"relief": "solid", "borderwidth": 1, "pady": 8, "padx": 12}


class SimpleOptimizerApp(tk.Tk):
    """
    Main application class for the Multi-Objective Optimization Laboratory GUI.
    It handles the user interface, interacts with the controller, and displays
    optimization results and plots.
    """

    def __init__(self):
        """
        Initializes the main application window and its components with modern styling.
        """
        super().__init__()

        # Configure modern window appearance
        self.title("Multi-Objective Optimization Laboratory v3.0")
        self.geometry("1600x1000")  # Larger default size for better content visibility
        self.minsize(1200, 800)  # Increased minimum size
        self.configure(bg=ModernTheme.BACKGROUND)

        # Center window on screen
        self._center_window()

        # Configure modern styling
        self._configure_modern_style()

        # Initialize enhanced controls storage
        self.enhanced_controls = {}
        # Initialize window configurations for lazy creation
        self.window_configs = {}

        # Set window icon if available
        try:
            # You can add an icon file here if available
            # self.iconbitmap("icon.ico")
            pass
        except:
            pass

        # Initialize controller and state variables.
        self.controller: Optional[Any] = None
        self.param_rows: List[Dict[str, Any]] = []
        self.response_rows: List[Dict[str, Any]] = []
        self.suggestion_labels: Dict[str, tk.Label] = {}
        self.results_entries: Dict[str, tk.Entry] = {}
        self.best_solution_labels: Dict[str, Dict[str, Any]] = {
            "params": {},
            "responses": {},
        }
        self.current_suggestion: Dict[str, Any] = {}
        self.initial_sampling_method_var: tk.StringVar = tk.StringVar(
            value="Random"
        )  # Default to Random

        # Figures and canvases for various plots.
        self.pareto_fig: Optional[Figure] = None
        self.pareto_canvas: Optional[FigureCanvasTkAgg] = None
        self.progress_fig: Optional[Figure] = None
        self.progress_canvas: Optional[FigureCanvasTkAgg] = None
        self.gp_slice_fig: Optional[Figure] = None
        self.gp_slice_canvas: Optional[FigureCanvasTkAgg] = None
        self.surface_3d_fig: Optional[Figure] = None
        self.surface_3d_canvas: Optional[FigureCanvasTkAgg] = None
        self.parallel_coords_fig: Optional[Figure] = None
        self.parallel_coords_canvas: Optional[FigureCanvasTkAgg] = None
        self.gp_uncertainty_map_fig: Optional[Figure] = None
        self.gp_uncertainty_map_canvas: Optional[FigureCanvasTkAgg] = None
        self.parity_fig: Optional[Figure] = None
        self.parity_canvas: Optional[FigureCanvasTkAgg] = None
        self.residuals_fig: Optional[Figure] = None
        self.residuals_canvas: Optional[FigureCanvasTkAgg] = None
        self.sensitivity_fig: Optional[Figure] = None
        self.sensitivity_canvas: Optional[FigureCanvasTkAgg] = None

        # Status variables for display.
        self.status_var: tk.StringVar = tk.StringVar()
        self.data_count_var: tk.StringVar = tk.StringVar()
        self.plot_manager: Optional[Any] = None

        # Initialize the GUI layout.
        self._setup_main_window()

    def _center_window(self):
        """Center the window on the screen"""
        self.update_idletasks()
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{pos_x}+{pos_y}")

    def _configure_modern_style(self):
        """Configure modern TTK styles for the application"""
        style = ttk.Style()

        # Configure modern button style
        style.configure(
            "Modern.TButton",
            background=ModernTheme.PRIMARY,
            foreground="white",
            font=ModernTheme.get_font(10, "normal"),
            borderwidth=0,
            focuscolor="none",
            padding=(16, 8),
        )

        style.map(
            "Modern.TButton",
            background=[
                ("active", ModernTheme.PRIMARY_DARK),
                ("pressed", ModernTheme.PRIMARY_DARK),
            ],
        )

        # Configure secondary button style
        style.configure(
            "Secondary.TButton",
            background=ModernTheme.SURFACE,
            foreground=ModernTheme.PRIMARY,
            font=ModernTheme.get_font(10, "normal"),
            borderwidth=1,
            focuscolor="none",
            padding=(16, 8),
        )

        style.map(
            "Secondary.TButton",
            background=[
                ("active", ModernTheme.PRIMARY_LIGHT),
                ("pressed", ModernTheme.PRIMARY_LIGHT),
            ],
            bordercolor=[
                ("active", ModernTheme.PRIMARY),
                ("pressed", ModernTheme.PRIMARY),
            ],
        )

        # Configure modern notebook style
        style.configure(
            "Modern.TNotebook", background=ModernTheme.BACKGROUND, borderwidth=0
        )

        style.configure(
            "Modern.TNotebook.Tab",
            background=ModernTheme.SURFACE,
            foreground=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
            padding=(20, 12),
            borderwidth=0,
        )

        style.map(
            "Modern.TNotebook.Tab",
            background=[
                ("selected", ModernTheme.PRIMARY),
                ("active", ModernTheme.PRIMARY_LIGHT),
            ],
            foreground=[("selected", "white"), ("active", ModernTheme.PRIMARY)],
        )

        # Configure modern entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground=ModernTheme.SURFACE,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            padding=(12, 8),
        )

        style.map(
            "Modern.TEntry",
            bordercolor=[
                ("focus", ModernTheme.PRIMARY),
                ("active", ModernTheme.BORDER),
            ],
        )

        # Configure modern combobox style
        style.configure(
            "Modern.TCombobox",
            fieldbackground=ModernTheme.SURFACE,
            foreground=ModernTheme.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor="none",
            padding=(12, 8),
        )

        # Configure modern label styles
        style.configure(
            "Title.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(24, "bold"),
        )

        style.configure(
            "Heading.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(16, "bold"),
        )

        style.configure(
            "Body.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(10, "normal"),
        )

        style.configure(
            "Caption.TLabel",
            background=ModernTheme.BACKGROUND,
            foreground=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(9, "normal"),
        )

    def create_modern_button(
        self, parent, text, command=None, style="primary", **kwargs
    ):
        """Create a modern styled button with hover effects"""
        if style == "primary":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.PRIMARY,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.PRIMARY_DARK,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "secondary":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.PRIMARY,
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.PRIMARY_LIGHT,
                activeforeground=ModernTheme.PRIMARY,
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "success":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.SUCCESS,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.SUCCESS,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )
        elif style == "warning":
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=ModernTheme.WARNING,
                fg="white",
                font=ModernTheme.get_font(10, "normal"),
                activebackground=ModernTheme.WARNING,
                activeforeground="white",
                **ModernTheme.BUTTON_STYLE,
                **kwargs,
            )

        # Add hover effects
        def on_enter(e):
            if style == "primary":
                btn.config(bg=ModernTheme.PRIMARY_DARK)
            elif style == "secondary":
                btn.config(bg=ModernTheme.PRIMARY_LIGHT)

        def on_leave(e):
            if style == "primary":
                btn.config(bg=ModernTheme.PRIMARY)
            elif style == "secondary":
                btn.config(bg=ModernTheme.SURFACE)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)

        return btn

    def create_modern_card(self, parent, **kwargs):
        """Create a modern card-style frame"""
        return tk.Frame(
            parent,
            bg=ModernTheme.SURFACE,
            relief="flat",
            borderwidth=1,
            highlightbackground=ModernTheme.BORDER,
            highlightthickness=1,
            **kwargs,
        )

    def set_plot_manager(self, plot_manager: Any) -> None:
        """Sets the plot manager instance for the GUI to use."""
        self.plot_manager = plot_manager
        logger.info("Plot manager set for optimizer app")

    def _setup_main_window(self) -> None:
        """
        Sets up the main window of the application with modern layout and styling.
        """
        # Main container frame with modern background
        self.main_frame = tk.Frame(self, bg=ModernTheme.BACKGROUND, padx=0, pady=0)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a top header bar for branding and navigation
        self._create_header_bar()

        # Create main content area
        self.content_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))

        # Display the welcome screen when the application starts.
        self._show_welcome_screen()

        # Create and pack the status bar at the bottom of the window.
        self._create_status_bar()

    def _create_header_bar(self):
        """Create a modern header bar with branding"""
        header_frame = tk.Frame(
            self.main_frame,
            bg=ModernTheme.SURFACE,
            height=60,
            relief="flat",
            borderwidth=0,
        )
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Add a subtle shadow effect with a separator
        separator = tk.Frame(self.main_frame, bg=ModernTheme.DIVIDER, height=1)
        separator.pack(fill=tk.X)

        # Header content
        header_content = tk.Frame(header_frame, bg=ModernTheme.SURFACE)
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=0)

        # Application title
        title_label = tk.Label(
            header_content,
            text="Multi-Objective Optimization Laboratory",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(18, "bold"),
        )
        title_label.pack(side=tk.LEFT, pady=16)

        # Version badge
        version_label = tk.Label(
            header_content,
            text="v3.0",
            bg=ModernTheme.PRIMARY_LIGHT,
            fg=ModernTheme.PRIMARY,
            font=ModernTheme.get_font(10, "bold"),
            padx=8,
            pady=4,
        )
        version_label.pack(side=tk.LEFT, padx=(12, 0), pady=16)

        # Add status indicator (will be updated based on application state)
        self.status_indicator = tk.Label(
            header_content,
            text="●",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
            font=ModernTheme.get_font(12, "bold"),
        )
        self.status_indicator.pack(side=tk.RIGHT, pady=16)

        self.status_text = tk.Label(
            header_content,
            text="Ready",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        self.status_text.pack(side=tk.RIGHT, padx=(0, 8), pady=16)

    def _clear_content_frame(self):
        """Clear the content frame for new content"""
        # Check if content_frame exists and is valid
        if hasattr(self, 'content_frame') and self.content_frame.winfo_exists():
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    def _show_welcome_screen(self) -> None:
        """
        Displays a modern welcome screen with improved layout and styling.
        """
        # Ensure main frame is recreated if it was destroyed
        if not hasattr(self, 'main_frame') or not self.main_frame.winfo_exists():
            self._create_main_layout()
        
        # Ensure content frame exists before clearing
        if not hasattr(self, 'content_frame') or not self.content_frame.winfo_exists():
            self.content_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
            self.content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        # Clear the content frame and create the welcome frame.
        self._clear_content_frame()

        # Main welcome container with card styling
        welcome_container = self.create_modern_card(self.content_frame, padx=0, pady=0)
        welcome_container.pack(fill=tk.BOTH, expand=True)

        # Welcome content with proper spacing
        welcome_content = tk.Frame(welcome_container, bg=ModernTheme.SURFACE)
        welcome_content.pack(fill=tk.BOTH, expand=True, padx=48, pady=48)

        # Hero section with icon and title
        hero_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        hero_frame.pack(fill=tk.X, pady=(0, 32))

        # Modern title with better hierarchy
        title_label = tk.Label(
            hero_frame,
            text="Multi-Objective Optimization Laboratory",
            font=ModernTheme.get_font(28, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        title_label.pack(pady=(0, 12))

        # Enhanced subtitle with features
        subtitle_label = tk.Label(
            hero_frame,
            text="Advanced Bayesian optimization with uncertainty quantification\nand interactive visualization for scientific research",
            font=ModernTheme.get_font(14, "normal"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            justify=tk.CENTER,
        )
        subtitle_label.pack(pady=(0, 40))

        # Features highlight section
        features_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        features_frame.pack(fill=tk.X, pady=(0, 40))

        features_title = tk.Label(
            features_frame,
            text="Key Features",
            font=ModernTheme.get_font(16, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        features_title.pack(pady=(0, 16))

        # Feature cards grid
        features_grid = tk.Frame(features_frame, bg=ModernTheme.SURFACE)
        features_grid.pack(fill=tk.X)

        features = [
            (
                "🎯",
                "Multi-Objective Optimization",
                "Simultaneous optimization of multiple conflicting objectives",
            ),
            (
                "🔬",
                "Uncertainty Quantification",
                "GP prediction uncertainty and data density analysis",
            ),
            (
                "📊",
                "Interactive Visualization",
                "Real-time plots, 3D surfaces, and acquisition heatmaps",
            ),
            (
                "🤖",
                "Bayesian Learning",
                "Intelligent experiment suggestion using Gaussian processes",
            ),
        ]

        for i, (icon, title, desc) in enumerate(features):
            row = i // 2
            col = i % 2

            feature_card = self.create_modern_card(features_grid, padx=16, pady=12)
            feature_card.grid(row=row, column=col, padx=12, pady=8, sticky="ew")

            features_grid.columnconfigure(col, weight=1)

            # Feature icon
            icon_label = tk.Label(
                feature_card,
                text=icon,
                font=ModernTheme.get_font(24, "normal"),
                bg=ModernTheme.SURFACE,
            )
            icon_label.pack(pady=(8, 4))

            # Feature title
            title_label = tk.Label(
                feature_card,
                text=title,
                font=ModernTheme.get_font(12, "bold"),
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.TEXT_PRIMARY,
            )
            title_label.pack(pady=(0, 4))

            # Feature description
            desc_label = tk.Label(
                feature_card,
                text=desc,
                font=ModernTheme.get_font(9, "normal"),
                bg=ModernTheme.SURFACE,
                fg=ModernTheme.TEXT_SECONDARY,
                wraplength=200,
                justify=tk.CENTER,
            )
            desc_label.pack(pady=(0, 8))

        # Action buttons section
        actions_frame = tk.Frame(welcome_content, bg=ModernTheme.SURFACE)
        actions_frame.pack(fill=tk.X, pady=(40, 0))

        # Primary action button
        new_project_btn = self.create_modern_button(
            actions_frame,
            text="🚀 Start New Optimization",
            command=self._start_setup_wizard,
            style="primary",
        )
        new_project_btn.pack(pady=(0, 16))

        # SGLBO Screening button (new primary option)
        screening_btn = self.create_modern_button(
            actions_frame,
            text="🎯 SGLBO Screening",
            command=self._start_screening_wizard,
            style="secondary",
        )
        # Apply custom styling after creation
        screening_btn.config(
            bg=ModernTheme.SECONDARY,
            activebackground=ModernTheme.SECONDARY_DARK,
            fg="white"
        )
        
        # Fix hover effects for custom styling
        def screening_on_enter(e):
            screening_btn.config(bg=ModernTheme.SECONDARY_DARK)
            
        def screening_on_leave(e):
            screening_btn.config(bg=ModernTheme.SECONDARY)
            
        # Remove default hover handlers and add custom ones
        screening_btn.unbind("<Enter>")
        screening_btn.unbind("<Leave>")
        screening_btn.bind("<Enter>", screening_on_enter)
        screening_btn.bind("<Leave>", screening_on_leave)
        
        screening_btn.pack(pady=(0, 16))

        # Secondary actions in a row
        secondary_actions = tk.Frame(actions_frame, bg=ModernTheme.SURFACE)
        secondary_actions.pack()

        load_project_btn = self.create_modern_button(
            secondary_actions,
            text="📂 Load Study",
            command=self._load_existing_study,
            style="secondary",
        )
        load_project_btn.pack(side=tk.LEFT, padx=(0, 16))

        import_btn = self.create_modern_button(
            secondary_actions,
            text="📊 Import Data",
            command=self._import_experimental_data,
            style="secondary",
        )
        import_btn.pack(side=tk.LEFT)

    def _start_setup_wizard(self) -> None:
        """
        Initiates the optimization setup wizard, clearing the main frame
        and preparing the interface for parameter and response definition.
        """
        # Clear the main frame to remove the welcome screen.
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset lists that hold references to parameter and response input rows.
        self.param_rows = []
        self.response_rows = []

        # Build the setup interface where users define their optimization problem.
        self._create_setup_interface()

    def _create_setup_interface(self) -> None:
        """
        Creates the graphical interface for setting up a new optimization study.
        This includes tabs for defining parameters and responses, and controls
        for selecting initial sampling methods.
        """
        setup_frame = tk.Frame(self.main_frame, bg="white")
        setup_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header for the setup section.
        header_label = tk.Label(
            setup_frame,
            text="Optimization Setup",
            font=("Arial", 18, "bold"),
            bg="white",
            fg="#2c3e50",
        )
        header_label.pack(pady=(0, 20))

        # Notebook widget to organize Parameters and Responses tabs.
        notebook = ttk.Notebook(setup_frame, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True)

        # Parameters tab creation and addition to the notebook.
        params_tab = tk.Frame(notebook, bg="white")
        notebook.add(params_tab, text="Parameters")

        # Responses tab creation and addition to the notebook.
        responses_tab = tk.Frame(notebook, bg="white")
        notebook.add(responses_tab, text="Responses")

        # Populate the content of the Parameters tab.
        self._build_parameters_tab(params_tab)

        # Populate the content of the Responses tab.
        self._build_responses_tab(responses_tab)

        # Frame for action buttons (Start Optimization, Back).
        action_frame = tk.Frame(setup_frame, bg="white")
        action_frame.pack(fill=tk.X, pady=(20, 0))

        # Section for selecting the initial sampling method.
        sampling_frame = ttk.LabelFrame(action_frame, text="Initial Sampling Method")
        sampling_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(
            sampling_frame, text="Select method for initial experiments:", bg="white"
        ).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(
            sampling_frame,
            textvariable=self.initial_sampling_method_var,
            values=["Random", "LHS"],  # Options for initial sampling.
            state="readonly",
            width=10,
        ).pack(side=tk.LEFT, padx=5, pady=5)

        # Frame to hold the main action buttons.
        btn_frame = tk.Frame(action_frame, bg="white")
        btn_frame.pack()

        # Button to start the optimization process.
        start_btn = tk.Button(
            btn_frame,
            text="Start Optimization",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            command=self._start_optimization,
        )
        start_btn.pack(side=tk.LEFT, padx=10)

        # Button to go back to the welcome screen.
        back_btn = tk.Button(
            btn_frame,
            text="Back",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            padx=30,
            pady=10,
            command=self._show_welcome_screen,
        )
        back_btn.pack(side=tk.LEFT, padx=10)

    def _build_parameters_tab(self, parent: tk.Frame) -> None:
        """
        Builds the user interface for configuring optimization parameters.
        Allows users to define parameter names, types, bounds/values, and optimization goals.

        Args:
            parent (tk.Frame): The parent Tkinter frame to which this tab will be added.
        """
        # Header section for the parameters tab.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header_frame,
            text="Define Optimization Parameters",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Parameters are the variables you can control. You can also define optimization goals for them.",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", pady=(5, 0))

        # Column headers for the parameter table.
        headers_frame = tk.Frame(parent, bg="#f8f9fa")
        headers_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            headers_frame,
            text="Name",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=15,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Type",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Bounds/Values",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=20,
        ).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Goal",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Target",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=4, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Action",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=8,
        ).grid(row=0, column=5, padx=5, pady=5)

        # Scrollable area for parameter input rows.
        params_container = tk.Frame(parent, bg="white")
        params_container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(params_container, bg="white")
        scrollbar = ttk.Scrollbar(
            params_container, orient="vertical", command=canvas.yview
        )
        self.params_frame = tk.Frame(canvas, bg="white")

        self.params_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.params_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button to add a new parameter row.
        add_btn = tk.Button(
            params_container,
            text="Add Parameter",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self._add_parameter_row,
        )
        add_btn.pack(pady=10)

        # Add an initial parameter row when the tab is built.
        self._add_parameter_row()

    def _build_responses_tab(self, parent: tk.Frame) -> None:
        """
        Builds the user interface for configuring optimization responses (objectives).
        Allows users to define response names, optimization goals, units, and target values.

        Args:
            parent (tk.Frame): The parent Tkinter frame to which this tab will be added.
        """
        # Header section for the responses tab.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            header_frame,
            text="Define Optimization Responses",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w")

        tk.Label(
            header_frame,
            text="Responses are the outputs you measure and want to optimize.",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", pady=(5, 0))

        # Column headers for the response table.
        headers_frame = tk.Frame(parent, bg="#f8f9fa")
        headers_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(
            headers_frame,
            text="Name",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=15,
        ).grid(row=0, column=0, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Goal",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=12,
        ).grid(row=0, column=1, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Target",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=2, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Units",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=10,
        ).grid(row=0, column=3, padx=5, pady=5)
        tk.Label(
            headers_frame,
            text="Action",
            font=("Arial", 10, "bold"),
            bg="#f8f9fa",
            width=8,
        ).grid(row=0, column=4, padx=5, pady=5)

        # Scrollable area for response input rows.
        responses_container = tk.Frame(parent, bg="white")
        responses_container.pack(fill=tk.BOTH, expand=True, padx=20)

        canvas = tk.Canvas(responses_container, bg="white")
        scrollbar = ttk.Scrollbar(
            responses_container, orient="vertical", command=canvas.yview
        )
        self.responses_frame = tk.Frame(canvas, bg="white")

        self.responses_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.responses_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Button to add a new response row.
        add_btn = tk.Button(
            responses_container,
            text="Add Response",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self._add_response_row,
        )
        add_btn.pack(pady=10)

        # Add an initial response row when the tab is built.
        self._add_response_row()

    def _add_parameter_row(self) -> None:
        """
        Adds a new row to the parameter configuration table, allowing the user to
        define a new optimization parameter with its name, type, bounds/values,
        optimization goal, and an optional target value.
        """
        row_frame = tk.Frame(
            self.params_frame, bg="#f8f9fa", relief="solid", borderwidth=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=5)

        widgets = {}

        # Entry for parameter name.
        widgets["name"] = tk.Entry(row_frame, width=15)
        widgets["name"].grid(row=0, column=0, padx=5, pady=5)
        widgets["name"].insert(0, f"Parameter_{len(self.param_rows) + 1}")

        # Combobox for parameter type (continuous, discrete, categorical).
        widgets["type"] = ttk.Combobox(
            row_frame,
            values=["continuous", "discrete", "categorical"],
            width=12,
            state="readonly",
        )
        widgets["type"].grid(row=0, column=1, padx=5, pady=5)
        widgets["type"].set("continuous")
        # Bind an event to update bounds/values field based on type selection.
        widgets["type"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_param_type_change(widgets)
        )

        # Entry for parameter bounds or categorical values.
        widgets["bounds"] = tk.Entry(row_frame, width=20)
        widgets["bounds"].grid(row=0, column=2, padx=5, pady=5)
        widgets["bounds"].insert(0, "[0, 100]")

        # Combobox for parameter optimization goal (None, Maximize, Minimize, Target).
        widgets["goal"] = ttk.Combobox(
            row_frame,
            values=["None", "Maximize", "Minimize", "Target"],
            width=12,
            state="readonly",
        )
        widgets["goal"].grid(row=0, column=3, padx=5, pady=5)
        widgets["goal"].set("None")
        # Bind an event to enable/disable target field based on goal selection.
        widgets["goal"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_param_goal_change(widgets)
        )

        # Entry for target/ideal value (initially disabled).
        widgets["target"] = tk.Entry(row_frame, width=10)
        widgets["target"].grid(row=0, column=4, padx=5, pady=5)
        widgets["target"].config(state="disabled")

        # Button to remove this parameter row.
        remove_btn = tk.Button(
            row_frame,
            text="Remove",
            bg="#e74c3c",
            fg="white",
            command=lambda: self._remove_row(row_frame, widgets, self.param_rows),
        )
        remove_btn.grid(row=0, column=5, padx=5, pady=5)

        # Add the new row's widgets to the list of parameter rows.
        self.param_rows.append(widgets)

    def _add_response_row(self) -> None:
        """
        Adds a new row to the response configuration table, allowing the user to
        define a new optimization response with its name, optimization goal,
        an optional target value, and units.
        """
        row_frame = tk.Frame(
            self.responses_frame, bg="#f8f9fa", relief="solid", borderwidth=1
        )
        row_frame.pack(fill=tk.X, padx=5, pady=5)

        widgets = {}

        # Entry for response name.
        widgets["name"] = tk.Entry(row_frame, width=15)
        widgets["name"].grid(row=0, column=0, padx=5, pady=5)
        widgets["name"].insert(0, f"Response_{len(self.response_rows) + 1}")

        # Combobox for response optimization goal (Maximize, Minimize, Target, Range).
        widgets["goal"] = ttk.Combobox(
            row_frame,
            values=["Maximize", "Minimize", "Target", "Range"],
            width=12,
            state="readonly",
        )
        widgets["goal"].grid(row=0, column=1, padx=5, pady=5)
        widgets["goal"].set("Maximize")
        # Bind an event to enable/disable target field based on goal selection.
        widgets["goal"].bind(
            "<<ComboboxSelected>>", lambda e: self._on_response_goal_change(widgets)
        )

        # Entry for target/ideal value or range (initially disabled).
        widgets["target"] = tk.Entry(row_frame, width=10)
        widgets["target"].grid(row=0, column=2, padx=5, pady=5)
        widgets["target"].config(state="disabled")

        # Entry for units.
        widgets["units"] = tk.Entry(row_frame, width=10)
        widgets["units"].grid(row=0, column=3, padx=5, pady=5)
        widgets["units"].insert(0, "%")

        # Button to remove this response row.
        remove_btn = tk.Button(
            row_frame,
            text="Remove",
            bg="#e74c3c",
            fg="white",
            command=lambda: self._remove_row(row_frame, widgets, self.response_rows),
        )
        remove_btn.grid(row=0, column=4, padx=5, pady=5)

        # Add the new row's widgets to the list of response rows.
        self.response_rows.append(widgets)

    def _on_param_type_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a parameter's type is changed in the setup interface.
        Adjusts the placeholder text in the 'Bounds/Values' entry field based on the selected type.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current parameter row.
        """
        param_type = widgets["type"].get()
        widgets["bounds"].delete(0, tk.END)
        if param_type == "categorical":
            widgets["bounds"].insert(0, "Value1, Value2, Value3")
        elif param_type == "discrete":
            widgets["bounds"].insert(0, "[0, 10]")
        else:  # continuous
            widgets["bounds"].insert(0, "[0.0, 100.0]")

    def _on_param_goal_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a parameter's optimization goal is changed.
        Enables or disables the 'Target' entry field based on the selected goal.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current parameter row.
        """
        goal = widgets["goal"].get()
        if goal in ["Target"]:
            widgets["target"].config(state="normal")
        else:
            widgets["target"].config(state="disabled")
            widgets["target"].delete(0, tk.END)

    def _on_response_goal_change(self, widgets: Dict[str, Any]) -> None:
        """
        Handles the event when a response's optimization goal is changed.
        Enables or disables the 'Target' entry field based on the selected goal.

        Args:
            widgets (Dict[str, Any]): A dictionary containing the Tkinter widgets for the current response row.
        """
        goal = widgets["goal"].get()
        if goal in ["Target", "Range"]:
            widgets["target"].config(state="normal")
            if goal == "Range":
                widgets["target"].delete(0, tk.END)
                widgets["target"].insert(0, "[0.0, 1.0]")  # Placeholder for range
        else:
            widgets["target"].config(state="disabled")
            widgets["target"].delete(0, tk.END)

    def _remove_row(
        self,
        frame: tk.Frame,
        widgets: Dict[str, Any],
        widgets_list: List[Dict[str, Any]],
    ) -> None:
        """
        Removes a parameter or response configuration row from the GUI.

        Args:
            frame (tk.Frame): The Tkinter frame representing the row to be removed.
            widgets (Dict[str, Any]): The dictionary of widgets associated with the row.
            widgets_list (List[Dict[str, Any]]): The list from which the widgets dictionary should be removed.
        """
        frame.destroy()
        if widgets in widgets_list:
            widgets_list.remove(widgets)

    def _start_optimization(self) -> None:
        """
        Collects the defined parameters and responses from the setup interface,
        validates them, and initiates a new optimization session via the controller.
        Displays error messages if the configuration is invalid.
        """
        try:
            # Collect parameter configurations from the GUI.
            params_config = {}
            for row in self.param_rows:
                name = row["name"].get().strip()
                # Skip rows that haven't been named or are still default placeholders.
                if not name or name.startswith("Parameter_"):
                    continue

                param_type = row["type"].get()
                bounds_str = row["bounds"].get().strip()
                goal = row["goal"].get()
                target_str = row["target"].get().strip()

                config = {"type": param_type, "goal": goal}

                # Parse bounds/values based on parameter type.
                if param_type in ["continuous", "discrete"]:
                    try:
                        bounds = json.loads(bounds_str)
                        if not isinstance(bounds, list) or len(bounds) != 2:
                            raise ValueError("Bounds must be a list of two numbers.")
                        config["bounds"] = bounds
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"Invalid JSON format for bounds of '{name}': {bounds_str}"
                        )
                    except ValueError as ve:
                        raise ValueError(f"Invalid bounds for '{name}': {ve}")
                elif param_type == "categorical":
                    try:
                        values = [x.strip() for x in bounds_str.split(",")]
                        if not values or all(not v for v in values):
                            raise ValueError("Categorical values cannot be empty.")
                        config["values"] = values
                    except Exception:
                        raise ValueError(
                            f"Invalid comma-separated values format for '{name}': {bounds_str}"
                        )

                # Add target/ideal value if the goal requires it.
                if goal == "Target" and target_str:
                    try:
                        config["ideal"] = float(target_str)
                    except ValueError:
                        raise ValueError(
                            f"Invalid target value for '{name}': '{target_str}' is not a number."
                        )

                params_config[name] = config

            # Collect response configurations from the GUI.
            responses_config = {}
            for row in self.response_rows:
                name = row["name"].get().strip()
                # Skip rows that haven't been named or are still default placeholders.
                if not name or name.startswith("Response_"):
                    continue

                goal = row["goal"].get()
                target_str = row["target"].get().strip()
                units = row["units"].get().strip()

                config = {"goal": goal, "units": units if units else None}

                # Add target/range value if the goal requires it.
                if goal in ["Target", "Range"] and target_str:
                    try:
                        if goal == "Target":
                            config["ideal"] = float(target_str)
                        elif goal == "Range":
                            range_vals = json.loads(target_str)
                            if not isinstance(range_vals, list) or len(range_vals) != 2:
                                raise ValueError("Range must be a list of two numbers.")
                            config["range"] = range_vals
                    except json.JSONDecodeError:
                        raise ValueError(
                            f"Invalid JSON format for target/range of '{name}': {target_str}"
                        )
                    except ValueError as ve:
                        raise ValueError(f"Invalid target/range for '{name}': {ve}")

                responses_config[name] = config

            # Perform basic validation on the collected configurations.
            if not params_config:
                raise ValueError(
                    "At least one parameter must be defined to start optimization."
                )
            if not responses_config:
                raise ValueError(
                    "At least one response must be defined to start optimization."
                )

            # Check if at least one parameter or response has an optimization goal.
            has_objective = False
            for conf in list(params_config.values()) + list(responses_config.values()):
                if conf.get("goal") in ["Maximize", "Minimize", "Target", "Range"]:
                    has_objective = True
                    break

            if not has_objective:
                raise ValueError(
                    "At least one parameter or response must have an optimization goal (Maximize, Minimize, Target, or Range) to define the optimization problem."
                )

            # If all validations pass, start the optimization via the controller.
            if self.controller:
                initial_sampling_method = self.initial_sampling_method_var.get()
                self.controller.start_new_optimization(
                    params_config, responses_config, [], initial_sampling_method
                )
            else:
                messagebox.showerror(
                    "Initialization Error",
                    "Controller not initialized. Please restart the application.",
                )

        except ValueError as ve:  # Catch specific validation errors.
            messagebox.showerror("Configuration Error", str(ve))
        except Exception as e:  # Catch any other unexpected errors.
            logger.error(
                f"An unexpected error occurred during optimization setup: {e}",
                exc_info=True,
            )
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def create_main_interface(
        self, params_config: Dict[str, Any], responses_config: Dict[str, Any]
    ) -> None:
        """
        Creates the main optimization interface after a study has been started or loaded.
        This involves clearing the setup interface and building the control and plotting panels.

        Args:
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Clear any existing widgets from the main frame (e.g., setup wizard).
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Build the main layout for the active optimization session.
        self._create_main_layout(params_config, responses_config)

    def _create_main_layout(
        self, params_config: Dict[str, Any], responses_config: Dict[str, Any]
    ) -> None:
        """
        Creates the overall layout for the main optimization interface, dividing it
        into a left control panel and a right plotting panel using a PanedWindow.

        Args:
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the main application interface.
        header_frame = tk.Frame(self.main_frame, bg="#34495e", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(
            False
        )  # Prevent frame from resizing to fit content.

        tk.Label(
            header_frame,
            text="Multi-Objective Optimization - Active Session",
            font=("Arial", 16, "bold"),
            bg="#34495e",
            fg="white",
        ).pack(pady=20)

        # Content area that will hold the control and plot panels.
        content_frame = tk.Frame(self.main_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # PanedWindow to allow resizing of left and right panels.
        paned = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Left panel for experiment controls.
        left_panel = tk.Frame(paned, bg="white", relief="solid", borderwidth=1)
        paned.add(left_panel, weight=1)

        # Right panel for data visualizations.
        right_panel = tk.Frame(paned, bg="white", relief="solid", borderwidth=1)
        paned.add(right_panel, weight=2)

        # Populate the left and right panels.
        self._build_control_panel(left_panel, params_config, responses_config)
        self._build_plot_panel(right_panel, params_config, responses_config)

    def _build_control_panel(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the left-hand control panel of the main interface.
        This panel contains sections for experiment suggestions, result submission,
        and displaying the best compromise solution.

        Args:
            parent (tk.Frame): The parent Tkinter frame for the control panel.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the control panel.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))

        tk.Label(
            header_frame,
            text="Experiment Control",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side=tk.LEFT, anchor="w")

        # Button to save the current optimization study.
        save_btn = tk.Button(
            header_frame,
            text="Save Optimization",
            font=("Arial", 10),
            bg="#28a745",
            fg="white",
            command=self._save_current_study,
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Button to generate a comprehensive report.
        report_btn = tk.Button(
            header_frame,
            text="Generate Report",
            font=("Arial", 10),
            bg="#007bff",
            fg="white",
            command=self._on_generate_report,
        )
        report_btn.pack(side=tk.RIGHT, padx=5)

        # Notebook widget to organize different control sections.
        notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Tab for displaying next experiment suggestions.
        suggestions_tab = tk.Frame(notebook, bg="white")
        notebook.add(suggestions_tab, text="Next Experiment")

        # Tab for submitting experimental results.
        results_tab = tk.Frame(notebook, bg="white")
        notebook.add(results_tab, text="Submit Results")

        # Tab for displaying the best compromise solution found so far.
        best_tab = tk.Frame(notebook, bg="white")
        notebook.add(best_tab, text="Best Solution")

        # Populate the content of each control tab.
        self._build_suggestions_tab(suggestions_tab, params_config)
        self._build_results_tab(results_tab, responses_config)
        self._build_best_solution_tab(best_tab, params_config, responses_config)

    def _build_suggestions_tab(
        self, parent: tk.Frame, params_config: Dict[str, Any]
    ) -> None:
        """
        Builds the 'Next Experiment' tab, which displays the optimizer's suggested
        parameter values for the next experiment and provides controls for batch
        suggestion generation and export.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
        """
        # Header for the suggestions section.
        tk.Label(
            parent,
            text="Recommended Parameters",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Instructions for the user.
        tk.Label(
            parent,
            text="Use these parameter values for your next experiment:",
            font=("Arial", 10),
            bg="white",
            fg="#7f8c8d",
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Frame to display individual parameter suggestions.
        params_frame = tk.LabelFrame(
            parent, text="Parameter Values", font=("Arial", 10), bg="white"
        )
        params_frame.pack(fill=tk.X, padx=15, pady=10)

        # Clear existing labels to prepare for new suggestions.
        self.suggestion_labels = {}

        # Create a label for each parameter to display its suggested value.
        for name in params_config:
            param_frame = tk.Frame(params_frame, bg="white")
            param_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                param_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                param_frame,
                text="Calculating...",  # Placeholder text while suggestion is being generated.
                font=("Arial", 11, "bold"),
                bg="#e8f5e8",
                fg="#2d5a3d",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=3,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.suggestion_labels[name] = value_label

        # Button to manually refresh the single experiment suggestion.
        refresh_btn = tk.Button(
            parent,
            text="Get New Suggestion",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self._refresh_suggestion,
        )
        refresh_btn.pack(pady=10)

        # Section for generating and managing batch suggestions.
        batch_frame = tk.LabelFrame(
            parent, text="Batch Suggestions", font=("Arial", 10), bg="white"
        )
        batch_frame.pack(fill=tk.X, padx=15, pady=10)

        # Input field for the number of batch suggestions.
        tk.Label(batch_frame, text="Number of Suggestions:", bg="white").pack(
            side=tk.LEFT, padx=5, pady=5
        )
        self.num_suggestions_entry = tk.Entry(batch_frame, width=5)
        self.num_suggestions_entry.insert(0, "10")  # Default to 10 suggestions.
        self.num_suggestions_entry.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to generate a batch of suggestions.
        generate_batch_btn = tk.Button(
            batch_frame,
            text="Generate Batch",
            font=("Arial", 10),
            bg="#28a745",
            fg="white",
            command=self._generate_batch_suggestions,
        )
        generate_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to download the generated batch suggestions as a CSV file.
        download_batch_btn = tk.Button(
            batch_frame,
            text="Download CSV",
            font=("Arial", 10),
            bg="#007bff",
            fg="white",
            command=self._download_batch_suggestions_csv,
        )
        download_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Button to upload experimental data from a CSV file.
        upload_batch_btn = tk.Button(
            batch_frame,
            text="Upload CSV",
            font=("Arial", 10),
            bg="#6f42c1",
            fg="white",
            command=self._upload_batch_suggestions_csv,
        )
        upload_batch_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # ScrolledText widget to display the generated batch suggestions.
        self.batch_suggestions_text = scrolledtext.ScrolledText(
            parent, height=10, wrap=tk.WORD
        )
        self.batch_suggestions_text.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.batch_suggestions_text.insert(
            tk.END, "Batch suggestions will appear here."
        )
        self.batch_suggestions_text.config(state=tk.DISABLED)  # Make it read-only.

        # List to store generated batch suggestions internally.
        self.generated_batch_suggestions = []

    def _build_results_tab(
        self, parent: tk.Frame, responses_config: Dict[str, Any]
    ) -> None:
        """
        Builds the 'Submit Results' tab, allowing users to input experimental
        results for each response variable.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Header for the results submission section.
        tk.Label(
            parent,
            text="Enter Experimental Results",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to contain entry fields for response values.
        results_frame = tk.LabelFrame(
            parent, text="Response Values", font=("Arial", 10), bg="white"
        )
        results_frame.pack(fill=tk.X, padx=15, pady=10)

        # Clear existing entry widgets.
        self.results_entries = {}

        # Create an entry field for each response variable.
        for name, config in responses_config.items():
            result_frame = tk.Frame(results_frame, bg="white")
            result_frame.pack(fill=tk.X, padx=10, pady=5)

            tk.Label(
                result_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            entry = tk.Entry(result_frame, font=("Arial", 10), width=15)
            entry.pack(side=tk.LEFT, padx=(10, 5))

            units = config.get("units", "")
            if units:
                tk.Label(
                    result_frame,
                    text=units,
                    font=("Arial", 9),
                    bg="white",
                    fg="#7f8c8d",
                ).pack(side=tk.LEFT)

            self.results_entries[name] = entry

        # Button to submit the entered results.
        submit_btn = tk.Button(
            parent,
            text="Submit Results",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            padx=30,
            pady=10,
            command=self._submit_results,
        )
        submit_btn.pack(pady=20)

    def _build_best_solution_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Best Solution' tab, which displays the optimal parameter values
        and their predicted response values as determined by the optimizer.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters for the current study.
            responses_config (Dict[str, Any]): The configuration of responses for the current study.
        """
        # Header for optimal parameters section.
        tk.Label(
            parent,
            text="Optimal Parameter Values",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to display optimal parameter values.
        params_frame = tk.LabelFrame(
            parent, text="Parameters", font=("Arial", 10), bg="white"
        )
        params_frame.pack(fill=tk.X, padx=15, pady=5)

        # Create labels for each parameter to display its optimal value.
        for name in params_config:
            param_frame = tk.Frame(params_frame, bg="white")
            param_frame.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                param_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                param_frame,
                text="Not available",  # Placeholder until data is updated.
                font=("Arial", 10),
                bg="#ecf0f1",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=2,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.best_solution_labels["params"][name] = value_label

        # Header for predicted response values section.
        tk.Label(
            parent,
            text="Predicted Response Values",
            font=("Arial", 12, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # Frame to display predicted response values.
        responses_frame = tk.LabelFrame(
            parent, text="Responses", font=("Arial", 10), bg="white"
        )
        responses_frame.pack(fill=tk.X, padx=15, pady=5)

        # Create labels for each response to display its predicted mean and confidence interval.
        for name in responses_config:
            response_frame = tk.Frame(responses_frame, bg="white")
            response_frame.pack(fill=tk.X, padx=10, pady=3)

            tk.Label(
                response_frame,
                text=f"{name}:",
                font=("Arial", 10, "bold"),
                bg="white",
                width=15,
                anchor="w",
            ).pack(side=tk.LEFT)

            value_label = tk.Label(
                response_frame,
                text="Not available",  # Placeholder until data is updated.
                font=("Arial", 10),
                bg="#ecf0f1",
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=2,
            )
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

            self.best_solution_labels["responses"][name] = {
                "mean": value_label,
                "ci": None,  # Placeholder for confidence interval label.
            }

            ci_label = tk.Label(
                response_frame,
                text="",  # Confidence interval text.
                font=("Arial", 8),
                bg="#ecf0f1",
                fg="#7f8c8d",
                padx=5,
                pady=1,
            )
            ci_label.pack(side=tk.LEFT, padx=(5, 0))
            self.best_solution_labels["responses"][name]["ci"] = ci_label

    def _build_plot_panel(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the right-hand plotting panel of the main interface.
        This panel contains a notebook with various tabs for different types of plots
        (Pareto front, progress, GP slice, 3D surface, parallel coordinates, GP uncertainty, and model diagnostics).

        Args:
            parent (tk.Frame): The parent Tkinter frame for the plotting panel.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Header for the visualization section with control buttons.
        header_frame = tk.Frame(parent, bg="white")
        header_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        # Title on the left
        tk.Label(
            header_frame,
            text="Data Visualization",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#2c3e50",
        ).pack(side=tk.LEFT, anchor="w")
        
        # Single control button on the right
        self.single_control_btn = tk.Button(
            header_frame,
            text="⚙ Open Controls",
            font=("Segoe UI", 9, "bold"),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._open_active_tab_controls,
        )
        self.single_control_btn.pack(side=tk.RIGHT, anchor="e", padx=(10, 0))
        
        # Add hover effect
        def on_enter(e):
            self.single_control_btn.config(bg="#1565C0")

        def on_leave(e):
            self.single_control_btn.config(bg="#1976D2")

        self.single_control_btn.bind("<Enter>", on_enter)
        self.single_control_btn.bind("<Leave>", on_leave)

        # Notebook widget to organize different plot tabs.
        self.plot_notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.plot_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.plot_notebook.bind(
            "<<NotebookTabChanged>>", lambda event: self.update_all_plots()
        )
        
        # Create mapping from tab index to plot type for single button functionality
        self.tab_to_plot_type = {}

        # Create and add each plot tab to the notebook.
        pareto_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(pareto_tab, text="Pareto Front")
        self.tab_to_plot_type[0] = "pareto"

        progress_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(progress_tab, text="Progress")
        self.tab_to_plot_type[1] = "progress"

        gp_slice_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(gp_slice_tab, text="GP Slice")
        self.tab_to_plot_type[2] = "gp_slice"

        surface_3d_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(surface_3d_tab, text="3D Surface")
        self.tab_to_plot_type[3] = "3d_surface"

        parallel_coords_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(parallel_coords_tab, text="Parallel Coordinates")
        self.tab_to_plot_type[4] = "parallel_coordinates"

        gp_uncertainty_map_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(gp_uncertainty_map_tab, text="GP Uncertainty Map")
        self.tab_to_plot_type[5] = "gp_uncertainty"

        model_diagnostics_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(model_diagnostics_tab, text="Model Diagnostics")
        self.tab_to_plot_type[6] = "parity"  # Model diagnostics contains parity tab

        sensitivity_analysis_tab = tk.Frame(self.plot_notebook, bg="white")
        self.plot_notebook.add(sensitivity_analysis_tab, text="Sensitivity Analysis")
        self.tab_to_plot_type[7] = "sensitivity_analysis"

        # Populate the content of each plot tab.
        self._build_pareto_tab(pareto_tab, responses_config, params_config)
        self._build_progress_tab(progress_tab)
        self._build_gp_slice_tab(gp_slice_tab, params_config, responses_config)
        self._build_3d_surface_tab(surface_3d_tab, params_config, responses_config)
        self._build_parallel_coordinates_tab(
            parallel_coords_tab, params_config, responses_config
        )
        self._build_gp_uncertainty_map_tab(
            gp_uncertainty_map_tab, params_config, responses_config
        )
        self._build_model_diagnostics_tab(
            model_diagnostics_tab, params_config, responses_config
        )
        self._build_sensitivity_analysis_tab(
            sensitivity_analysis_tab, params_config, responses_config
        )

    def _build_pareto_tab(
        self,
        parent: tk.Frame,
        responses_config: Dict[str, Any],
        params_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Pareto Front' tab, which displays a 2D Pareto front plot.
        Allows users to select which objectives to plot on the X and Y axes.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            responses_config (Dict[str, Any]): The configuration of responses.
            params_config (Dict[str, Any]): The configuration of parameters.
        """
        # Initialize variables for Pareto plot (controls now handled by separate panels)
        objectives = []
        for name, conf in params_config.items():
            if conf.get("goal") in ["Maximize", "Minimize", "Target"]:
                objectives.append(name)
        for name, conf in responses_config.items():
            if conf.get("goal") in ["Maximize", "Minimize", "Target"]:
                objectives.append(name)

        self.pareto_x_var = tk.StringVar(value=objectives[0] if objectives else "")
        self.pareto_y_var = tk.StringVar(
            value=objectives[1] if len(objectives) > 1 else ""
        )

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="pareto",
            fig_attr="pareto_fig",
            canvas_attr="pareto_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

    def _build_progress_tab(self, parent: tk.Frame) -> None:
        """
        Builds the 'Progress' tab, which displays the optimization progress plot
        (e.g., Hypervolume Indicator over iterations).

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
        """
        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="progress",
            fig_attr="progress_fig",
            canvas_attr="progress_canvas",
            figsize=(8, 8),  # Square aspect ratio
        )

    def _build_gp_slice_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'GP Slice' tab, which displays a 2D slice of the Gaussian Process
        model's prediction for a response, varying one parameter while fixing others.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for GP Slice plot (controls now handled by separate panels)
        self.gp_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.gp_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.gp_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )
        self.gp_fixed_value_var = tk.DoubleVar(value=0.5)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="gp_slice",
            fig_attr="gp_slice_fig",
            canvas_attr="gp_slice_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

    def _build_parallel_coordinates_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the 'Parallel Coordinates' tab, which displays a parallel coordinates plot.
        Allows users to select which parameters and responses to include in the plot.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for Parallel Coordinates plot (controls now handled by separate panels)
        all_variables = list(params_config.keys()) + list(responses_config.keys())
        self.parallel_coords_vars = {}
        for var_name in all_variables:
            var = tk.BooleanVar(value=True)  # Default to including all variables
            self.parallel_coords_vars[var_name] = var

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="parallel_coordinates",
            fig_attr="parallel_coords_fig",
            canvas_attr="parallel_coords_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

    def _build_3d_surface_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the '3D Surface' tab, which displays a 3D response surface plot.
        Allows users to select a response and two parameters to visualize the surface.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for 3D Surface plot (controls now handled by separate panels)
        self.surface_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.surface_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.surface_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="3d_surface",
            fig_attr="surface_3d_fig",
            canvas_attr="surface_3d_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

    def _build_gp_uncertainty_map_tab(
        self,
        parent: tk.Frame,
        params_config: Dict[str, Any],
        responses_config: Dict[str, Any],
    ) -> None:
        """
        Builds the enhanced 'GP Uncertainty Map' tab, which displays a 2D heatmap of the
        Gaussian Process model's uncertainty across two parameters with advanced controls.

        Args:
            parent (tk.Frame): The parent Tkinter frame for this tab.
            params_config (Dict[str, Any]): The configuration of parameters.
            responses_config (Dict[str, Any]): The configuration of responses.
        """
        # Initialize variables for GP Uncertainty plot (controls now handled by separate panels)
        self.gp_uncertainty_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        self.gp_uncertainty_param1_var = tk.StringVar(
            value=list(params_config.keys())[0] if params_config else ""
        )
        self.gp_uncertainty_param2_var = tk.StringVar(
            value=(
                list(params_config.keys())[1]
                if len(params_config) > 1
                else list(params_config.keys())[0] if params_config else ""
            )
        )
        self.gp_uncertainty_plot_style_var = tk.StringVar(value="heatmap")
        self.gp_uncertainty_metric_var = tk.StringVar(value="data_density")
        self.gp_uncertainty_colormap_var = tk.StringVar(value="Reds")
        self.gp_uncertainty_resolution_var = tk.StringVar(value="70")
        self.gp_uncertainty_show_data_var = tk.BooleanVar(value=True)

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="gp_uncertainty",
            fig_attr="gp_uncertainty_map_fig",
            canvas_attr="gp_uncertainty_map_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )
        logger.debug("Enhanced GP Uncertainty Map tab built with advanced controls.")

    def _build_model_diagnostics_tab(self, parent, params_config, responses_config):
        """Build Model Diagnostics plot tab with sub-tabs for Parity and Residuals plots."""
        # Notebook for sub-tabs
        self.diagnostics_notebook = ttk.Notebook(parent, style="Modern.TNotebook")
        self.diagnostics_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Parity Plot tab
        parity_tab = tk.Frame(self.diagnostics_notebook, bg="white")
        self.diagnostics_notebook.add(parity_tab, text="Parity Plot")

        # Residuals Plot tab
        residuals_tab = tk.Frame(self.diagnostics_notebook, bg="white")
        self.diagnostics_notebook.add(residuals_tab, text="Residuals Plot")

        # Initialize variables for Parity plot (controls now handled by separate panels)
        self.parity_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )

        # Create plot with compact controls using helper method (in parity_tab)
        self._create_plot_with_compact_controls(
            parent=parity_tab,
            plot_type="parity",
            fig_attr="parity_fig",
            canvas_attr="parity_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

        # Initialize residuals response variable for automatic updates
        self.residuals_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )

        # Create plot with compact controls using helper method (in residuals_tab)
        self._create_plot_with_compact_controls(
            parent=residuals_tab,
            plot_type="residuals",
            fig_attr="residuals_fig",
            canvas_attr="residuals_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )
        
        # Draw initial plot - either with existing data or placeholder
        if hasattr(self, "residuals_fig"):
            # Check if we have data and can create the actual plot
            if (hasattr(self, 'controller') and self.controller and 
                hasattr(self.controller, 'plot_manager') and self.controller.plot_manager):
                try:
                    # Try to create the actual residuals plot with existing data
                    response_name = self.residuals_response_var.get()
                    if response_name:
                        self.controller.plot_manager.create_residuals_plot(
                            self.residuals_fig, self.residuals_canvas, response_name
                        )
                        self.residuals_canvas.draw()
                    else:
                        # No response selected, show placeholder
                        self._draw_residuals_placeholder()
                except Exception as e:
                    # If plot creation fails (no data), show placeholder
                    logger.debug(f"Could not create initial residuals plot: {e}")
                    self._draw_residuals_placeholder()
            else:
                # No controller/plot_manager available, show placeholder
                self._draw_residuals_placeholder()
    
    def _draw_residuals_placeholder(self):
        """Draw placeholder for residuals plot when no data is available"""
        if hasattr(self, "residuals_fig"):
            self.residuals_fig.clear()  # Clear any existing content
            ax = self.residuals_fig.add_subplot(111)
            ax.text(0.5, 0.5, "Residuals Plot\n(Data will appear when optimization data is available)", 
                   ha='center', va='center', transform=ax.transAxes, 
                   fontsize=12, color='gray')
            ax.set_title("Model Residuals Analysis")
            self.residuals_canvas.draw()

    def _build_sensitivity_analysis_tab(self, parent, params_config, responses_config):
        """Build Enhanced Sensitivity Analysis plot tab with method selection."""
        # Initialize variables for Sensitivity Analysis plot (controls now handled by separate panels)
        self.sensitivity_response_var = tk.StringVar(
            value=list(responses_config.keys())[0] if responses_config else ""
        )
        
        sensitivity_methods = [
            ("Variance-based", "variance"),
            ("Morris Elementary Effects", "morris"),
            ("Gradient-based", "gradient"),
            ("Sobol-like", "sobol"),
            ("GP Lengthscale", "lengthscale"),
            ("Feature Importance", "feature_importance"),
        ]
        
        self.sensitivity_method_var = tk.StringVar(
            value=sensitivity_methods[0][0]
        )
        
        # Store mapping for method lookup
        self.sensitivity_method_mapping = {
            method[0]: method[1] for method in sensitivity_methods
        }
        
        self.sensitivity_samples_var = tk.StringVar(value="500")
        
        # Initialize info label variable
        self.sensitivity_info_label = None

        # Create plot with compact controls using helper method
        self._create_plot_with_compact_controls(
            parent=parent,
            plot_type="sensitivity_analysis",
            fig_attr="sensitivity_fig",
            canvas_attr="sensitivity_canvas",
            params_config=params_config,
            responses_config=responses_config,
            figsize=(8, 8),  # Square aspect ratio
        )

    def _update_sensitivity_info(self, event=None):
        """Update sensitivity method information."""
        method_name = self.sensitivity_method_var.get()

        info_text = {
            "Variance-based": "Measures how much each parameter contributes to output variance. Higher values indicate more influential parameters.",
            "Morris Elementary Effects": "Calculates elementary effects using Morris screening method. Shows local sensitivity with statistical confidence.",
            "Gradient-based": "Estimates local gradients at multiple points. Good for smooth response surfaces with uncertainty quantification.",
            "Sobol-like": "Simplified Sobol indices showing global sensitivity. Robust across different response surface types.",
            "GP Lengthscale": "Uses GP model lengthscales directly. Short lengthscales indicate high sensitivity (model intrinsic).",
            "Feature Importance": "Permutation-based importance using variance differences. Model-agnostic sensitivity measure.",
        }

        self.sensitivity_info_label.config(
            text=info_text.get(method_name, "Select a sensitivity analysis method")
        )

    def _refresh_suggestion(self):
        """CORRECTED - Refresh suggestion manually"""
        if self.controller:
            try:
                # Generate new suggestion
                suggestions = self.controller.optimizer.suggest_next_experiment(
                    n_suggestions=1
                )
                if suggestions:
                    self.current_suggestion = suggestions[0]

                    # Update display
                    for name, label in self.suggestion_labels.items():
                        value = self.current_suggestion.get(name)
                        if value is not None:
                            if isinstance(value, float):
                                formatted_value = f"{value:.3f}"
                            else:
                                formatted_value = str(value)
                            label.config(
                                text=formatted_value, bg="#e8f5e8", fg="#2d5a3d"
                            )
                        else:
                            label.config(
                                text="Not available", bg="#ffeaa7", fg="#636e72"
                            )

                    self.set_status("New suggestion generated")
                else:
                    self.set_status("Could not generate suggestion")

            except Exception as e:
                logger.error(f"Error refreshing suggestion: {e}")
                self.set_status(f"Error: {e}")

    def _submit_results(self):
        """Submit experimental results"""
        if self.controller:
            try:
                result_values = {}
                for name, entry in self.results_entries.items():
                    value_str = entry.get().strip()
                    if not value_str:
                        raise ValueError(f"Please enter a value for {name}")

                    try:
                        result_values[name] = float(value_str)
                    except ValueError:
                        raise ValueError(
                            f"Invalid numeric format for {name}: {value_str}"
                        )

                # Submit results
                self.controller.submit_single_result(
                    self.current_suggestion, result_values
                )

                # Clear entries
                for entry in self.results_entries.values():
                    entry.delete(0, tk.END)

                # Update plots and suggestions after submission
                self.update_all_plots()
                self._refresh_suggestion()

            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
            except Exception as e:
                messagebox.showerror("Submission Error", str(e))

    def _generate_batch_suggestions(self):
        """Generate a batch of suggestions and display them."""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            num_suggestions = int(self.num_suggestions_entry.get())
            if num_suggestions <= 0:
                raise ValueError("Number of suggestions must be a positive integer.")

            self.set_status(f"Generating {num_suggestions} batch suggestions...")
            suggestions = self.controller.generate_batch_suggestions(num_suggestions)
            self.generated_batch_suggestions = suggestions

            self.batch_suggestions_text.config(state=tk.NORMAL)
            self.batch_suggestions_text.delete(1.0, tk.END)
            if suggestions:
                for i, s in enumerate(suggestions):
                    self.batch_suggestions_text.insert(tk.END, f"Suggestion {i + 1}:\n")

                    for param, value in s.items():
                        if isinstance(value, float):
                            self.batch_suggestions_text.insert(
                                tk.END, f"  {param}: {value:.3f}"
                            )
                        else:
                            self.batch_suggestions_text.insert(
                                tk.END, f"  {param}: {value}"
                            )
                    self.batch_suggestions_text.insert(tk.END, "---")
                self.set_status(f"Generated {len(suggestions)} batch suggestions.")
            else:
                self.batch_suggestions_text.insert(
                    tk.END, "No batch suggestions could be generated."
                )
                self.set_status("No batch suggestions generated.")
            self.batch_suggestions_text.config(state=tk.DISABLED)

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except Exception as e:
            logger.error(
                f"Error generating batch suggestions in GUI: {e}", exc_info=True
            )
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _download_batch_suggestions_csv(self):
        """Download generated batch suggestions as a CSV file."""
        if not self.generated_batch_suggestions:
            messagebox.showwarning(
                "No Data", "No batch suggestions have been generated yet."
            )
            return

        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.* ")],
                title="Save Batch Suggestions CSV",
            )
            if filepath:
                self.set_status("Saving batch suggestions to CSV...")
                success = self.controller.save_suggestions_to_csv(
                    self.generated_batch_suggestions, filepath
                )
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"Batch suggestions saved to {
                            Path(filepath).name}",
                    )
                    self.set_status("Batch suggestions CSV saved.")
                else:
                    messagebox.showerror(
                        "Error", "Failed to save batch suggestions to CSV."
                    )
                    self.set_status("Failed to save batch suggestions CSV.")
        except Exception as e:
            logger.error(f"Error downloading batch suggestions CSV: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _upload_batch_suggestions_csv(self):
        """Upload experimental data from a CSV file."""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            filepath = filedialog.askopenfilename(
                filetypes=[("CSV files", "*.csv"), ("All files", "*.* ")],
                title="Upload Experimental Data CSV",
            )
            if filepath:
                self.set_status("Uploading experimental data from CSV...")
                success = self.controller.add_batch_data_from_csv(filepath)
                if success:
                    messagebox.showinfo(
                        "Success",
                        f"Experimental data uploaded from {
                            Path(filepath).name}",
                    )
                    self.set_status("Experimental data CSV uploaded.")
                    # After successful upload, update all displays to reflect
                    # new data
                    self.controller.update_view()
                else:
                    messagebox.showerror(
                        "Error", "Failed to upload experimental data from CSV."
                    )
                    self.set_status("Failed to upload experimental data CSV.")
        except Exception as e:
            logger.error(f"Error uploading batch suggestions CSV: {e}", exc_info=True)
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.set_busy_state(False)

    def _load_existing_study(self):
        """Load existing optimization study"""
        filepath = filedialog.askopenfilename(
            title="Load Optimization Study",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.* ")],
        )
        if filepath and self.controller:
            if self.controller.load_optimization_from_file(filepath):
                messagebox.showinfo(
                    "Load Complete", f"Study loaded: {Path(filepath).name}"
                )
            else:
                messagebox.showerror("Load Error", "Failed to load study")

    def _import_experimental_data(self):
        """Import experimental data"""
        self._upload_batch_suggestions_csv()

    def _create_status_bar(self):
        """Create modern status bar with improved styling"""
        # Separator line
        separator = tk.Frame(self, bg=ModernTheme.DIVIDER, height=1)
        separator.pack(side=tk.BOTTOM, fill=tk.X)

        # Status bar frame
        self.status_bar = tk.Frame(self, bg=ModernTheme.SURFACE, height=32)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)

        # Status bar content
        status_content = tk.Frame(self.status_bar, bg=ModernTheme.SURFACE)
        status_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=0)

        # Status label with icon
        self.status_icon = tk.Label(
            status_content,
            text="●",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
            font=ModernTheme.get_font(10, "bold"),
        )
        self.status_icon.pack(side=tk.LEFT, pady=8)

        status_label = tk.Label(
            status_content,
            textvariable=self.status_var,
            anchor=tk.W,
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0), pady=8)

        # Data count with modern styling
        data_label = tk.Label(
            status_content,
            textvariable=self.data_count_var,
            anchor=tk.E,
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(10, "normal"),
        )
        data_label.pack(side=tk.RIGHT, padx=0, pady=8)

        self.status_var.set("Application ready")
        self.data_count_var.set("Experiments: 0")

    def update_status(self, message, status_type="info"):
        """Update status bar with message and appropriate color"""
        self.status_var.set(message)

        # Update header status as well
        if hasattr(self, "status_text"):
            try:
                if self.status_text.winfo_exists():
                    self.status_text.config(
                        text=message.split(" - ")[0] if " - " in message else message
                    )
            except tk.TclError:
                # Widget was destroyed, ignore the update
                pass

        # Update status icon color based on type
        try:
            if status_type == "success":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.SUCCESS)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.SUCCESS)
            elif status_type == "warning":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.WARNING)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.WARNING)
            elif status_type == "error":
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.ERROR)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.ERROR)
            else:  # info
                if hasattr(self, "status_icon") and self.status_icon.winfo_exists():
                    self.status_icon.config(fg=ModernTheme.PRIMARY)
                if (
                    hasattr(self, "status_indicator")
                    and self.status_indicator.winfo_exists()
                ):
                    self.status_indicator.config(fg=ModernTheme.PRIMARY)
        except tk.TclError:
            # Widget was destroyed, ignore the update
            pass

    def set_controller(self, controller):
        """Set the controller reference"""
        self.controller = controller

    def set_busy_state(self, busy: bool):
        """Set busy state"""
        cursor = "wait" if busy else ""
        self.configure(cursor=cursor)

    def set_status(
        self, text: str, clear_after_ms: Optional[int] = None, status_type: str = "info"
    ):
        """Set status text with modern styling"""
        self.update_status(text, status_type)
        self.update_idletasks()

        if clear_after_ms:
            self.after(clear_after_ms, lambda: self.update_status("Ready", "info"))

    def create_tooltip(self, widget, text):
        self.tooltip_window = None
        self.text = text

        def enter(event):
            self.show_tooltip(event)

        def leave(event):
            self.hide_tooltip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def show_tooltip(self, event):
        x = y = 0
        x, y, cx, cy = event.widget.bbox("insert")
        x += event.widget.winfo_rootx() + 25
        y += event.widget.winfo_rooty() + 20

        # creates a toplevel window
        self.tooltip_window = tk.Toplevel(event.widget)
        # Leaves only the label and removes the app window
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+%d+%d" % (x, y))
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="yellow",
            relief="solid",
            borderwidth=1,
            font=("tahoma", "8", "normal"),
        )
        label.pack(ipadx=1)

    def hide_tooltip(self):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None

    def show_error(self, title: str, message: str):
        """Show error dialog"""
        messagebox.showerror(title, message, parent=self)

    def show_info(self, title: str, message: str):
        """Show info dialog"""
        messagebox.showinfo(title, message, parent=self)

    def update_displays(self, view_data: Dict):
        """CORRECTED - Update displays with new data"""
        logger.debug(
            f"Entering update_displays with view_data keys: {
                view_data.keys()}"
        )
        # Update suggestions
        suggestion = view_data.get("suggestion", {})
        # Handle both single suggestion dict and list of suggestions
        if isinstance(suggestion, list) and len(suggestion) > 0:
            # Take the first suggestion if it's a list
            current_suggestion = suggestion[0]
        elif isinstance(suggestion, dict):
            # Use the suggestion directly if it's already a dict
            current_suggestion = suggestion
        else:
            # Fallback for empty or invalid suggestions
            current_suggestion = {}

        self.current_suggestion = current_suggestion
        logger.debug(f"Updating suggestion labels with: {current_suggestion}")

        for name, label in self.suggestion_labels.items():
            value = current_suggestion.get(name)
            if value is not None:
                if isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)
                label.config(text=formatted_value, bg="#e8f5e8", fg="#2d5a3d")
            else:
                label.config(text="Calculating...", bg="#ffeaa7", fg="#636e72")

        # Update best solution
        best_compromise = view_data.get("best_compromise", {})
        best_params = best_compromise.get("params", {})
        logger.debug(f"Updating best solution parameters with: {best_params}")
        for name, label in self.best_solution_labels["params"].items():
            value = best_params.get(name)
            if value is not None:
                if isinstance(value, float):
                    formatted_value = f"{value:.3f}"
                else:
                    formatted_value = str(value)
                label.config(text=formatted_value)
            else:
                label.config(text="Not available")

        best_responses = best_compromise.get("responses", {})
        logger.debug(f"Updating best solution responses with: {best_responses}")
        for name, labels in self.best_solution_labels["responses"].items():
            response_data = best_responses.get(name)
            if response_data and isinstance(response_data, dict):
                mean_value = response_data.get("mean")
                lower_ci = response_data.get("lower_ci")
                upper_ci = response_data.get("upper_ci")

                if mean_value is not None:
                    labels["mean"].config(text=f"{mean_value:.3f}")
                else:
                    labels["mean"].config(text="N/A")

                if lower_ci is not None and upper_ci is not None:
                    labels["ci"].config(
                        text=f"(95% CI: {lower_ci:.3f} - {upper_ci:.3f})"
                    )
                else:
                    labels["ci"].config(text="")
            else:
                labels["mean"].config(text="Not available")
                labels["ci"].config(text="")

        # Update data count
        data_count = view_data.get("data_count", 0)
        logger.debug(f"Updating data count to: {data_count}")
        self.data_count_var.set(f"Experiments: {data_count}")

        # Update plots
        self.update_all_plots()

    def _save_current_study(self):
        """Save current optimization study"""
        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".pkl",
            filetypes=[("Pickle files", "*.pkl"), ("All files", "*.* ")],
            title="Save Optimization Study",
        )
        if filepath:
            if self.controller.save_optimization_to_file(filepath):
                messagebox.showinfo(
                    "Save Complete", f"Study saved to {Path(filepath).name}"
                )
            else:
                messagebox.showerror("Save Error", "Failed to save study")

    def _on_generate_report(self):
        """Handle report generation button click."""
        self._show_report_options_dialog()

    def _show_report_options_dialog(self):
        """Show a dialog for report generation options."""
        dialog = tk.Toplevel(self)
        dialog.title("Report Options")
        dialog.transient(self)  # Make dialog appear on top of main window
        dialog.grab_set()  # Make dialog modal
        dialog.focus_set()

        # Output Format Selection
        format_frame = ttk.LabelFrame(dialog, text="Output Format")
        format_frame.pack(padx=10, pady=5, fill=tk.X)

        self.report_format_var = tk.StringVar(value="pdf")  # Default to PDF
        formats = [
            ("PDF", "pdf"),
            ("HTML", "html"),
            ("Markdown", "markdown"),
            ("JSON (Data Only)", "json"),
            ("Pickle (Raw Data)", "pkl"),
        ]
        for text, mode in formats:
            ttk.Radiobutton(
                format_frame, text=text, variable=self.report_format_var, value=mode
            ).pack(anchor=tk.W)

        # Plot Selection
        plot_selection_frame = ttk.LabelFrame(dialog, text="Include Plots")
        plot_selection_frame.pack(padx=10, pady=5, fill=tk.X)

        self.include_pareto_plot = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Pareto Front Plot",
            variable=self.include_pareto_plot,
        ).pack(anchor=tk.W)

        self.include_progress_plot = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Optimization Progress Plot",
            variable=self.include_progress_plot,
        ).pack(anchor=tk.W)

        self.include_parallel_coordinates_plot = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Parallel Coordinates Plot",
            variable=self.include_parallel_coordinates_plot,
        ).pack(anchor=tk.W)

        self.include_gp_uncertainty_map = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="GP Uncertainty Map",
            variable=self.include_gp_uncertainty_map,
        ).pack(anchor=tk.W)

        self.include_model_diagnostics = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Model Diagnostics Plots",
            variable=self.include_model_diagnostics,
        ).pack(anchor=tk.W)

        self.include_sensitivity_analysis = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Sensitivity Analysis Plot",
            variable=self.include_sensitivity_analysis,
        ).pack(anchor=tk.W)

        # Dynamic GP Slice Plot Options
        self.gp_slice_plot_configs = []
        self.gp_slice_plots_frame = ttk.LabelFrame(
            plot_selection_frame, text="GP Slice Plots"
        )
        self.gp_slice_plots_frame.pack(fill=tk.X, pady=5)

        self.add_gp_slice_button = ttk.Button(
            self.gp_slice_plots_frame,
            text="Add GP Slice Plot",
            command=self._add_gp_slice_plot_config,
        )
        self.add_gp_slice_button.pack(pady=5)

        # Dynamic 3D Surface Plot Options
        self.surface_3d_plot_configs = []
        self.surface_3d_plots_frame = ttk.LabelFrame(
            plot_selection_frame, text="3D Surface Plots"
        )
        self.surface_3d_plots_frame.pack(fill=tk.X, pady=5)

        self.add_3d_surface_button = ttk.Button(
            self.surface_3d_plots_frame,
            text="Add 3D Surface Plot",
            command=self._add_3d_surface_plot_config,
        )
        self.add_3d_surface_button.pack(pady=5)

        # Initialize with one of each dynamic plot type
        self._add_gp_slice_plot_config()
        self._add_3d_surface_plot_config()

        # Model Diagnostics and Sensitivity Analysis don't need dynamic
        # configs, just a checkbox
        self.include_model_diagnostics = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Model Diagnostics Plots",
            variable=self.include_model_diagnostics,
        ).pack(anchor=tk.W)

        self.include_sensitivity_analysis = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            plot_selection_frame,
            text="Sensitivity Analysis Plot",
            variable=self.include_sensitivity_analysis,
        ).pack(anchor=tk.W)

        # Model Diagnostics and Sensitivity Analysis don't need dynamic
        # configs, just a checkbox

        # Action Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        generate_btn = ttk.Button(
            button_frame,
            text="Generate Report",
            command=lambda: self._generate_report_from_dialog(dialog),
        )
        generate_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = ttk.Button(button_frame, text="Cancel", command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+%d+%d" % (x, y))

    def _add_gp_slice_plot_config(self):
        """Adds a new GP Slice plot configuration section to the dialog."""
        responses = []
        parameters = []
        if self.controller and self.controller.optimizer:
            responses = list(self.controller.optimizer.responses_config.keys())
            parameters = list(self.controller.optimizer.params_config.keys())

        frame = ttk.Frame(self.gp_slice_plots_frame, borderwidth=1, relief="solid")
        frame.pack(fill=tk.X, padx=5, pady=2)

        config = {
            "frame": frame,
            "include": tk.BooleanVar(value=True),
            "response": tk.StringVar(value=responses[0] if responses else ""),
            "param1": tk.StringVar(value=parameters[0] if parameters else ""),
            "param2": tk.StringVar(
                value=(
                    parameters[1]
                    if len(parameters) > 1
                    else parameters[0] if parameters else ""
                )
            ),
        }
        self.gp_slice_plot_configs.append(config)

        ttk.Checkbutton(frame, text="Include", variable=config["include"]).pack(
            side=tk.LEFT
        )

        tk.Label(frame, text="Response:").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["response"],
            values=responses,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Param 1 (X): ").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["param1"],
            values=parameters,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Param 2 (Fixed): ").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["param2"],
            values=parameters,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        remove_btn = ttk.Button(
            frame,
            text="Remove",
            command=lambda: self._remove_plot_config(
                frame, self.gp_slice_plot_configs, config
            ),
        )
        remove_btn.pack(side=tk.RIGHT, padx=2)

    def _add_3d_surface_plot_config(self):
        """Adds a new 3D Surface plot configuration section to the dialog."""
        responses = []
        parameters = []
        if self.controller and self.controller.optimizer:
            responses = list(self.controller.optimizer.responses_config.keys())
            parameters = list(self.controller.optimizer.params_config.keys())

        frame = ttk.Frame(self.surface_3d_plots_frame, borderwidth=1, relief="solid")
        frame.pack(fill=tk.X, padx=5, pady=2)

        config = {
            "frame": frame,
            "include": tk.BooleanVar(value=True),
            "response": tk.StringVar(value=responses[0] if responses else ""),
            "param1": tk.StringVar(value=parameters[0] if parameters else ""),
            "param2": tk.StringVar(
                value=(
                    parameters[1]
                    if len(parameters) > 1
                    else parameters[0] if parameters else ""
                )
            ),
        }
        self.surface_3d_plot_configs.append(config)

        ttk.Checkbutton(frame, text="Include", variable=config["include"]).pack(
            side=tk.LEFT
        )

        tk.Label(frame, text="Response:").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["response"],
            values=responses,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Param 1 (X): ").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["param1"],
            values=parameters,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="Param 2 (Y): ").pack(side=tk.LEFT, padx=2)
        ttk.Combobox(
            frame,
            textvariable=config["param2"],
            values=parameters,
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=2)

        remove_btn = ttk.Button(
            frame,
            text="Remove",
            command=lambda: self._remove_plot_config(
                frame, self.surface_3d_plot_configs, config
            ),
        )
        remove_btn.pack(side=tk.RIGHT, padx=2)

    def _remove_plot_config(self, frame, config_list, config_item):
        """Removes a plot configuration section from the dialog."""
        frame.destroy()
        config_list.remove(config_item)

    def _generate_report_from_dialog(self, dialog):
        """Initiate report generation based on dialog selections."""
        dialog.destroy()
        output_format = self.report_format_var.get()

        plot_configs = {
            "pareto_plot": self.include_pareto_plot.get(),
            "progress_plot": self.include_progress_plot.get(),
            "parallel_coordinates_plot": self.include_parallel_coordinates_plot.get(),
            "gp_uncertainty_map": self.include_gp_uncertainty_map.get(),
            "gp_slice_plots": [],
            "3d_surface_plots": [],
        }

        for config in self.gp_slice_plot_configs:
            if config["include"].get():
                plot_configs["gp_slice_plots"].append(
                    {
                        "response": config["response"].get(),
                        "param1": config["param1"].get(),
                        "param2": config["param2"].get(),
                    }
                )

        for config in self.surface_3d_plot_configs:
            if config["include"].get():
                plot_configs["3d_surface_plots"].append(
                    {
                        "response": config["response"].get(),
                        "param1": config["param1"].get(),
                        "param2": config["param2"].get(),
                    }
                )

        if not self.controller:
            messagebox.showerror("Error", "Controller not initialized.")
            return

        try:
            filepath = filedialog.asksaveasfilename(
                defaultextension=f".{output_format}",
                filetypes=[
                    ("PDF files", "*.pdf") if output_format == "pdf" else ("", ""),
                    ("HTML files", "*.html") if output_format == "html" else ("", ""),
                    (
                        ("Markdown files", "*.md")
                        if output_format == "markdown"
                        else ("", "")
                    ),
                    ("JSON files", "*.json") if output_format == "json" else ("", ""),
                    ("Pickle files", "*.pkl") if output_format == "pkl" else ("", ""),
                    ("All files", "*.* "),
                ],
                title="Save Comprehensive Report As",
            )
            if filepath:
                # Ensure matplotlib is not trying to open a window if running
                # headless
                import matplotlib

                # Set backend to Agg for non-interactive plotting
                matplotlib.use("Agg")

                self.set_busy_state(True)
                success = self.controller.export_comprehensive_report(
                    filepath, output_format, plot_configs
                )
                self.set_busy_state(False)

                if success:
                    messagebox.showinfo(
                        "Report Generated", f"Report successfully saved to {filepath}"
                    )
                else:
                    messagebox.showerror("Report Error", "Failed to generate report.")
        except Exception as e:
            logger.error(
                f"An error occurred during report generation: {e}", exc_info=True
            )
            messagebox.showerror(
                "Error", f"An error occurred during report generation: {e}"
            )
        finally:
            self.set_busy_state(False)

    def _create_plot_with_compact_controls(
        self,
        parent: tk.Frame,
        plot_type: str,
        fig_attr: str,
        canvas_attr: str,
        params_config: Dict[str, Any] = None,
        responses_config: Dict[str, Any] = None,
        figsize: Tuple[int, int] = (8, 8),
    ) -> tk.Frame:
        """Helper method to create plot with windowed controls (separate Windows)"""

        # Frame to hold the Matplotlib plot only (no overlay controls)
        plot_container = tk.Frame(parent, bg="white")
        plot_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Main plot frame (full size since no overlay controls)
        plot_frame = tk.Frame(plot_container, bg="white")
        plot_frame.pack(fill=tk.BOTH, expand=True)

        # Create Matplotlib figure and embed it in the Tkinter canvas (square aspect ratio)
        fig = Figure(figsize=figsize, facecolor="white")
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Store figure and canvas as instance attributes
        setattr(self, fig_attr, fig)
        setattr(self, canvas_attr, canvas)

        # Store configuration for lazy window creation (don't create windows during init!)
        if not hasattr(self, "window_configs"):
            self.window_configs = {}

        self.window_configs[plot_type] = {
            "params_config": params_config or {},
            "responses_config": responses_config or {},
            "plot_container": plot_container,
        }

        # Don't create any controls during initialization - they will be created on-demand
        logger.info(
            f"Stored configuration for {plot_type} - window will be created when user clicks button"
        )

        # Store plot type mapping for tab detection (no individual buttons)
        # The single button will detect active tab and open appropriate controls

        return plot_container

    def _open_active_tab_controls(self):
        """Open control panel for the currently active tab"""
        try:
            # Get the currently selected tab index
            current_tab_index = self.plot_notebook.index(self.plot_notebook.select())
            
            # Get the plot type for this tab
            plot_type = self.tab_to_plot_type.get(current_tab_index)
            
            if not plot_type:
                logger.warning(f"No plot type found for tab index {current_tab_index}")
                return
                
            # Check if window already exists for this plot type
            if plot_type in self.enhanced_controls:
                # Window exists, just show it
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "show"):
                    window_control.show()
                    logger.info(f"Showed existing {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(f"Created movable {plot_type} controls")
                        return
                except Exception as e2:
                    logger.warning(f"Could not create movable {plot_type} controls: {e2}")

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(f"Created compact {plot_type} controls")
                        return
                except Exception as e3:
                    logger.warning(f"All control fallbacks failed for {plot_type}: {e3}")

            logger.error(f"Failed to create any controls for {plot_type}")
            
        except Exception as e:
            logger.error(f"Error opening controls for active tab: {e}")

    def _add_header_control_button(self, plot_type: str):
        """Add control button to the visualization header"""
        if not hasattr(self, 'control_buttons_frame'):
            return  # Header frame not created yet
            
        def toggle_window_controls():
            """Create and show window controls on-demand"""
            # Check if window already exists
            if plot_type in self.enhanced_controls:
                # Window exists, just show it
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "show"):
                    window_control.show()
                    logger.info(f"Showed existing {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(f"Created movable {plot_type} controls")
                        return
                except Exception as e2:
                    logger.warning(
                        f"Could not create movable {plot_type} controls: {e2}"
                    )

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(x=10, y=y_offset, anchor="sw", relx=0, rely=1)
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(f"Created compact {plot_type} controls")
                        return
                except Exception as e3:
                    logger.warning(
                        f"All control fallbacks failed for {plot_type}: {e3}"
                    )

            logger.error(f"Failed to create any controls for {plot_type}")

        # Create compact button for header
        control_btn = tk.Button(
            self.control_buttons_frame,
            text=f"⚙ {plot_type.replace('_', ' ').title()}",
            font=("Segoe UI", 8, "bold"),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=toggle_window_controls,
        )
        control_btn.pack(side=tk.LEFT, padx=2)

        # Add hover effect
        def on_enter(e):
            control_btn.config(bg="#1565C0")

        def on_leave(e):
            control_btn.config(bg="#1976D2")

        control_btn.bind("<Enter>", on_enter)
        control_btn.bind("<Leave>", on_leave)

    def _add_window_control_button(self, plot_container: tk.Frame, plot_type: str):
        """Add button to show/hide window controls"""
        button_frame = tk.Frame(plot_container, bg="white")
        button_frame.place(x=10, y=10, anchor="nw")

        def toggle_window_controls():
            """Create and show window controls on-demand"""
            # Check if window already exists
            if plot_type in self.enhanced_controls:
                # Window exists, just show it
                window_control = self.enhanced_controls[plot_type]
                if hasattr(window_control, "show"):
                    window_control.show()
                    logger.info(f"Showed existing {plot_type} window controls")
                return

            # Create window on first use
            config = self.window_configs.get(plot_type, {})

            # Try windowed controls first
            if WINDOW_CONTROLS_AVAILABLE:
                try:
                    window_control = create_window_plot_control_panel(
                        parent=self,
                        plot_type=plot_type,
                        params_config=config.get("params_config", {}),
                        responses_config=config.get("responses_config", {}),
                        update_callback=self.update_all_plots,
                    )
                    self.enhanced_controls[plot_type] = window_control
                    window_control.show()
                    logger.info(f"Created and opened {plot_type} window controls")
                    return
                except Exception as e:
                    logger.warning(f"Could not create window {plot_type} controls: {e}")

            # Fallback to movable controls if window fails
            if MOVABLE_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        movable_control = create_movable_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        movable_control.place(
                            x=10, y=y_offset, anchor="sw", relx=0, rely=1
                        )
                        self.enhanced_controls[plot_type] = movable_control
                        logger.info(
                            f"Created movable controls as fallback for {plot_type}"
                        )
                        return
                except Exception as e2:
                    logger.warning(
                        f"Fallback to movable controls failed for {plot_type}: {e2}"
                    )

            # Ultimate fallback to compact controls
            if COMPACT_CONTROLS_AVAILABLE:
                try:
                    plot_container = config.get("plot_container")
                    if plot_container:
                        compact_control = create_compact_plot_control_panel(
                            parent=plot_container,
                            plot_type=plot_type,
                            params_config=config.get("params_config", {}),
                            responses_config=config.get("responses_config", {}),
                            update_callback=self.update_all_plots,
                        )
                        y_offset = (
                            -160
                            if plot_type in ["pareto", "gp_slice", "gp_uncertainty"]
                            else -120
                        )
                        compact_control.place(
                            x=10, y=y_offset, anchor="sw", relx=0, rely=1
                        )
                        self.enhanced_controls[plot_type] = compact_control
                        logger.info(
                            f"Created compact controls as ultimate fallback for {plot_type}"
                        )
                        return
                except Exception as e3:
                    logger.warning(
                        f"All control fallbacks failed for {plot_type}: {e3}"
                    )

            logger.error(f"Failed to create any controls for {plot_type}")

        control_btn = tk.Button(
            button_frame,
            text=f"⚙ Open {plot_type.replace('_', ' ').title()} Controls",
            font=("Segoe UI", 9, "bold"),
            bg="#1976D2",
            fg="white",
            relief=tk.FLAT,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=toggle_window_controls,
        )
        control_btn.pack()

        # Hover effect
        control_btn.bind("<Enter>", lambda e: control_btn.config(bg="#1565C0"))
        control_btn.bind("<Leave>", lambda e: control_btn.config(bg="#1976D2"))

    def _get_axis_ranges(self, plot_type: str) -> dict:
        """Get axis ranges from enhanced controls if available"""
        axis_ranges = {"x_range": None, "y_range": None, "z_range": None}

        logger.info(f"Getting axis ranges for plot_type: {plot_type}")
        logger.info(f"ENHANCED_CONTROLS_AVAILABLE: {ENHANCED_CONTROLS_AVAILABLE}")
        logger.info(f"Has enhanced_controls attr: {hasattr(self, 'enhanced_controls')}")
        
        if ENHANCED_CONTROLS_AVAILABLE and hasattr(self, "enhanced_controls"):
            logger.info(f"Available control panels: {list(self.enhanced_controls.keys())}")
            control_panel = self.enhanced_controls.get(plot_type)
            logger.info(f"Found control panel for {plot_type}: {control_panel is not None}")
            
            if control_panel:
                ranges = control_panel.get_axis_ranges()
                logger.info(f"Raw ranges from control panel: {ranges}")
                
                for axis_name, (min_val, max_val, is_auto) in ranges.items():
                    logger.info(f"Processing axis {axis_name}: min={min_val}, max={max_val}, auto={is_auto}")
                    if not is_auto and min_val is not None and max_val is not None:
                        if axis_name == "x_axis":
                            axis_ranges["x_range"] = (min_val, max_val)
                            logger.info(f"Set x_range to: {axis_ranges['x_range']}")
                        elif axis_name == "y_axis":
                            axis_ranges["y_range"] = (min_val, max_val)
                            logger.info(f"Set y_range to: {axis_ranges['y_range']}")
                        elif axis_name == "z_axis":
                            axis_ranges["z_range"] = (min_val, max_val)
                            logger.info(f"Set z_range to: {axis_ranges['z_range']}")

        logger.info(f"Final axis ranges for {plot_type}: {axis_ranges}")
        return axis_ranges

    def _validate_and_setup_plotting(self):
        """Validate plotting components and return plot manager and current tab.
        
        Returns:
            tuple: (plot_manager, current_tab) if valid, (None, None) if invalid
        """
        if (
            not hasattr(self, "controller")
            or not self.controller
            or not self.controller.plot_manager
        ):
            logger.warning(
                "Plotting not available: controller or plot_manager missing."
            )
            return None, None
            
        plot_manager = self.controller.plot_manager
        current_tab = self.plot_notebook.tab(self.plot_notebook.select(), "text")
        logger.debug(f"Current plot notebook tab: {current_tab}")
        return plot_manager, current_tab

    def _update_pareto_front_plot(self, plot_manager):
        """Update the Pareto Front plot."""
        if not hasattr(self, "pareto_fig"):
            return
            
        logger.debug("Updating Pareto plot.")
        pareto_X_df, pareto_obj_df, _ = (
            self.controller.optimizer.get_pareto_front()
        )

        # Get axis ranges
        ranges = self._get_axis_ranges("pareto")

        if not pareto_X_df.empty and not pareto_obj_df.empty:
            plot_manager.create_pareto_plot(
                self.pareto_fig,
                self.pareto_canvas,
                self.pareto_x_var.get(),
                self.pareto_y_var.get(),
                pareto_X_df,
                pareto_obj_df,
                x_range=ranges.get("x_range"),
                y_range=ranges.get("y_range"),
            )
        else:
            plot_manager.create_pareto_plot(
                self.pareto_fig,
                self.pareto_canvas,
                self.pareto_x_var.get(),
                self.pareto_y_var.get(),
                pareto_X_df,
                pareto_obj_df,
                x_range=ranges.get("x_range"),
                y_range=ranges.get("y_range"),
            )
        self.pareto_canvas.draw()
        self.pareto_canvas.get_tk_widget().update()

    def _update_progress_plot(self, plot_manager):
        """Update the Progress plot."""
        if not hasattr(self, "progress_fig"):
            return
            
        logger.debug("Updating progress plot.")
        
        # Get axis ranges for progress plot
        ranges = self._get_axis_ranges("progress")
        
        plot_manager.create_progress_plot(
            self.progress_fig, 
            self.progress_canvas,
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range")
        )
        self.progress_canvas.draw()
        self.progress_canvas.get_tk_widget().update()

    def _update_gp_slice_plot(self, plot_manager):
        """Update the GP Slice plot."""
        if not hasattr(self, "gp_slice_fig"):
            return
            
        logger.debug("Updating GP Slice plot.")
        ranges = self._get_axis_ranges("gp_slice")
        plot_manager.create_gp_slice_plot(
            self.gp_slice_fig,
            self.gp_slice_canvas,
            self.gp_response_var.get(),
            self.gp_param1_var.get(),
            self.gp_param2_var.get(),
            float(self.gp_fixed_value_var.get()),
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
        )
        self.gp_slice_canvas.draw()
        self.gp_slice_canvas.get_tk_widget().update()

    def _update_3d_surface_plot(self, plot_manager):
        """Update the 3D Surface plot."""
        if not hasattr(self, "surface_3d_fig"):
            return
            
        logger.debug("Updating 3D Surface plot.")
        ranges = self._get_axis_ranges("3d_surface")
        
        # Get surface settings from control panel if available
        resolution = 60
        plot_style = "surface"
        show_uncertainty = False
        show_contours = True
        
        # Try to get settings from 3D surface control panel
        control_panel = self.enhanced_controls.get("3d_surface")
        if control_panel and hasattr(control_panel, 'get_surface_settings'):
            try:
                settings = control_panel.get_surface_settings()
                logger.debug(f"Retrieved surface settings: {settings}")
                
                # Map control panel settings to plot manager parameters
                if settings:
                    resolution = max(10, min(200, settings.get('x_resolution', 60)))
                    show_contours = settings.get('show_contours', True)
                    show_uncertainty = False  # Could be mapped to a setting if available
                    
                    # Determine plot style based on wireframe and surface_fill settings
                    wireframe = settings.get('wireframe', False)
                    surface_fill = settings.get('surface_fill', True)
                    
                    if wireframe and surface_fill:
                        plot_style = "both"
                    elif wireframe and not surface_fill:
                        plot_style = "wireframe"
                    else:
                        plot_style = "surface"
                
                logger.info(f"Using 3D surface settings - resolution: {resolution}, style: {plot_style}, contours: {show_contours}")
                
            except Exception as e:
                logger.warning(f"Error getting surface settings: {e}, using defaults")
        
        plot_manager.create_3d_surface_plot(
            self.surface_3d_fig,
            self.surface_3d_canvas,
            self.surface_response_var.get(),
            self.surface_param1_var.get(),
            self.surface_param2_var.get(),
            x_range=ranges.get("x_range"),
            y_range=ranges.get("y_range"),
            z_range=ranges.get("z_range"),
            resolution=resolution,
            plot_style=plot_style,
            show_uncertainty=show_uncertainty,
            show_contours=show_contours,
        )
        self.surface_3d_canvas.draw()
        self.surface_3d_canvas.get_tk_widget().update()

    def _update_parallel_coordinates_plot(self, plot_manager):
        """Update the Parallel Coordinates plot."""
        if not hasattr(self, "parallel_coords_fig"):
            return
            
        logger.debug("Updating Parallel Coordinates plot.")
        selected_vars = [
            name
            for name, var in self.parallel_coords_vars.items()
            if var.get()
        ]
        plot_manager.create_parallel_coordinates_plot(
            self.parallel_coords_fig,
            self.parallel_coords_canvas,
            selected_vars,
        )
        self.parallel_coords_canvas.draw()
        self.parallel_coords_canvas.get_tk_widget().update()

    def _update_gp_uncertainty_map_plot(self, plot_manager):
        """Update the GP Uncertainty Map plot."""
        if not hasattr(self, "gp_uncertainty_map_fig"):
            return
            
        logger.debug("Updating Enhanced GP Uncertainty Map plot.")

        # Get all the enhanced control values
        plot_style = getattr(
            self,
            "gp_uncertainty_plot_style_var",
            tk.StringVar(value="heatmap"),
        ).get()
        uncertainty_metric = getattr(
            self,
            "gp_uncertainty_metric_var",
            tk.StringVar(value="data_density"),
        ).get()
        colormap = getattr(
            self, "gp_uncertainty_colormap_var", tk.StringVar(value="Reds")
        ).get()
        resolution = int(
            getattr(
                self,
                "gp_uncertainty_resolution_var",
                tk.StringVar(value="70"),
            ).get()
        )
        show_data = getattr(
            self, "gp_uncertainty_show_data_var", tk.BooleanVar(value=True)
        ).get()

        plot_manager.create_gp_uncertainty_map(
            self.gp_uncertainty_map_fig,
            self.gp_uncertainty_map_canvas,
            self.gp_uncertainty_response_var.get(),
            self.gp_uncertainty_param1_var.get(),
            self.gp_uncertainty_param2_var.get(),
            plot_style=plot_style,
            uncertainty_metric=uncertainty_metric,
            colormap=colormap,
            resolution=resolution,
            show_experimental_data=show_data,
        )
        self.gp_uncertainty_map_canvas.draw()
        self.gp_uncertainty_map_canvas.get_tk_widget().update()

    def _update_model_diagnostics_plots(self, plot_manager):
        """Update the Model Diagnostics plots based on selected sub-tab."""
        # Determine which sub-tab is active within Model Diagnostics
        if not hasattr(self, "diagnostics_notebook") or not self.diagnostics_notebook:
            logger.warning("Diagnostics notebook not found or not available")
            return
            
        logger.debug("Found diagnostics notebook, checking sub-tab")
        selected_diagnostics_tab_id = self.diagnostics_notebook.select()
        selected_diagnostics_tab_text = self.diagnostics_notebook.tab(
            selected_diagnostics_tab_id, "text"
        )
        logger.debug(
            f"Selected diagnostics sub-tab: {selected_diagnostics_tab_text}"
        )

        if selected_diagnostics_tab_text == "Parity Plot":
            if hasattr(self, "parity_fig"):
                logger.debug("Updating Parity Plot.")
                response_name = self.parity_response_var.get()
                plot_manager.create_parity_plot(
                    self.parity_fig, self.parity_canvas, response_name
                )
                self.parity_canvas.draw()
                self.parity_canvas.get_tk_widget().update()
        elif selected_diagnostics_tab_text == "Residuals Plot":
            if hasattr(self, "residuals_fig"):
                logger.debug("Updating Residuals Plot.")
                response_name = self.residuals_response_var.get()
                plot_manager.create_residuals_plot(
                    self.residuals_fig, self.residuals_canvas, response_name
                )
                self.residuals_canvas.draw()
                self.residuals_canvas.get_tk_widget().update()

    def _update_sensitivity_analysis_plot(self, plot_manager):
        """Update the Sensitivity Analysis plot."""
        if not hasattr(self, "sensitivity_fig"):
            return
            
        logger.debug("Updating Sensitivity Analysis plot.")
        response_name = self.sensitivity_response_var.get()

        # Get selected method and parameters
        method_display = self.sensitivity_method_var.get()
        method_code = self.sensitivity_method_mapping.get(
            method_display, "variance"
        )
        n_samples = int(self.sensitivity_samples_var.get())

        logger.debug(
            f"Using sensitivity method: {method_code} with {n_samples} samples"
        )

        plot_manager.create_sensitivity_analysis_plot(
            self.sensitivity_fig,
            self.sensitivity_canvas,
            response_name,
            method=method_code,
            n_samples=n_samples,
        )
        self.sensitivity_canvas.draw()
        self.sensitivity_canvas.get_tk_widget().update()

    def update_all_plots(self):
        """Update all plots based on the currently selected tab.
        
        This method serves as the main orchestrator for plot updates, delegating
        to specific plot update methods based on the active tab.
        """
        logger.debug("Entering update_all_plots")
        plot_manager, current_tab = self._validate_and_setup_plotting()
        if not plot_manager:
            return
            
        try:
            # Map tab names to their corresponding update methods
            plot_updaters = {
                "Pareto Front": lambda: self._update_pareto_front_plot(plot_manager),
                "Progress": lambda: self._update_progress_plot(plot_manager),
                "GP Slice": lambda: self._update_gp_slice_plot(plot_manager),
                "3D Surface": lambda: self._update_3d_surface_plot(plot_manager),
                "Parallel Coordinates": lambda: self._update_parallel_coordinates_plot(plot_manager),
                "GP Uncertainty Map": lambda: self._update_gp_uncertainty_map_plot(plot_manager),
                "Model Diagnostics": lambda: self._update_model_diagnostics_plots(plot_manager),
                "Sensitivity Analysis": lambda: self._update_sensitivity_analysis_plot(plot_manager),
            }
            
            # Update the plot for the current tab
            updater = plot_updaters.get(current_tab)
            if updater:
                updater()
            else:
                logger.warning(f"No updater found for tab: {current_tab}")
                
        except Exception as e:
            logger.error(f"Error updating plots: {e}", exc_info=True)
        finally:
            self.update_idletasks()
            self.update()

    # SGLBO Screening Methods
    def _start_screening_wizard(self) -> None:
        """
        Initiates the SGLBO screening wizard, clearing the main frame
        and preparing the interface for parameter and response definition for screening.
        """
        # Clear the main frame to remove the welcome screen.
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Reset lists that hold references to parameter and response input rows.
        self.param_rows = []
        self.response_rows = []

        # Build the screening setup interface
        self._create_screening_interface()

    def _create_screening_interface(self) -> None:
        """
        Creates the graphical interface for setting up a new SGLBO screening study.
        This includes tabs for defining parameters and responses, and controls
        for screening-specific settings.
        """
        # Create main screening frame with modern styling
        screening_frame = tk.Frame(self.main_frame, bg=ModernTheme.BACKGROUND)
        screening_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header for the screening section
        header_frame = tk.Frame(screening_frame, bg=ModernTheme.BACKGROUND)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title
        header_label = tk.Label(
            header_frame,
            text="SGLBO Screening Setup",
            font=ModernTheme.get_font(20, "bold"),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
        )
        header_label.pack(side=tk.LEFT)

        # Info about screening
        info_label = tk.Label(
            header_frame,
            text="Fast parameter space exploration using Stochastic Gradient Line Bayesian Optimization",
            font=ModernTheme.get_font(11, "normal"),
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_SECONDARY,
        )
        info_label.pack(side=tk.LEFT, padx=(20, 0))

        # Back button
        back_btn = self.create_modern_button(
            header_frame,
            text="← Back to Welcome",
            command=self._show_welcome_screen,
            style="secondary",
        )
        back_btn.pack(side=tk.RIGHT)

        # Main content area
        content_frame = self.create_modern_card(screening_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook widget to organize tabs
        notebook = ttk.Notebook(content_frame, style="Modern.TNotebook")
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Parameters tab
        params_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(params_tab, text="Parameters")

        # Responses tab
        responses_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(responses_tab, text="Responses")

        # Screening Settings tab
        settings_tab = tk.Frame(notebook, bg=ModernTheme.SURFACE)
        notebook.add(settings_tab, text="Screening Settings")

        # Build tab contents
        self._build_screening_parameters_tab(params_tab)
        self._build_screening_responses_tab(responses_tab)
        self._build_screening_settings_tab(settings_tab)

        # Control buttons at bottom
        controls_frame = tk.Frame(screening_frame, bg=ModernTheme.BACKGROUND)
        controls_frame.pack(fill=tk.X, pady=(20, 0))

        # Start Screening button
        start_btn = self.create_modern_button(
            controls_frame,
            text="🎯 Start SGLBO Screening",
            command=self._start_screening_optimization,
            style="primary",
        )
        # Apply custom styling
        start_btn.config(
            bg=ModernTheme.SUCCESS,
            activebackground=ModernTheme.SUCCESS,
            fg="white"
        )
        start_btn.pack(side=tk.RIGHT, padx=(10, 0))

        # Validate Configuration button
        validate_btn = self.create_modern_button(
            controls_frame,
            text="✓ Validate Configuration",
            command=self._validate_screening_config,
            style="secondary",
        )
        validate_btn.pack(side=tk.RIGHT)

    def _build_screening_parameters_tab(self, parent: tk.Frame) -> None:
        """Build the parameters tab for screening setup (similar to main setup but simplified)."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Parameters header
        header_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Define Parameters for Screening",
            font=ModernTheme.get_font(14, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        add_param_btn = self.create_modern_button(
            header_frame,
            text="+ Add Parameter",
            command=self._add_screening_parameter_row,
            style="secondary",
        )
        add_param_btn.pack(side=tk.RIGHT)

        # Parameters container (use name expected by _add_parameter_row)
        self.params_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        self.params_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add initial parameter row
        self._add_screening_parameter_row()

    def _build_screening_responses_tab(self, parent: tk.Frame) -> None:
        """Build the responses tab for screening setup."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Responses header
        header_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))

        tk.Label(
            header_frame,
            text="Define Responses for Screening",
            font=ModernTheme.get_font(14, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        add_response_btn = self.create_modern_button(
            header_frame,
            text="+ Add Response",
            command=self._add_screening_response_row,
            style="secondary",
        )
        add_response_btn.pack(side=tk.RIGHT)

        # Responses container (use name expected by _add_response_row)
        self.responses_frame = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        self.responses_frame.pack(fill=tk.X, padx=20, pady=10)

        # Add initial response row
        self._add_screening_response_row()

    def _build_screening_settings_tab(self, parent: tk.Frame) -> None:
        """Build the screening settings tab with SGLBO-specific parameters."""
        # Create scrollable frame
        canvas = tk.Canvas(parent, bg=ModernTheme.SURFACE)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=ModernTheme.SURFACE)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Settings content
        settings_content = tk.Frame(scrollable_frame, bg=ModernTheme.SURFACE)
        settings_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # SGLBO Algorithm Settings
        algo_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        algo_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            algo_frame,
            text="SGLBO Algorithm Settings",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        # Create settings variables
        self.screening_settings = {}

        # Helper function to create setting row with explanation
        def create_setting_row(parent, label, var_name, default_val, explanation, recommended_range):
            # Main frame for this setting
            setting_frame = tk.Frame(parent, bg=ModernTheme.SURFACE)
            setting_frame.pack(fill=tk.X, pady=8)
            
            # Top row with label and input
            top_row = tk.Frame(setting_frame, bg=ModernTheme.SURFACE)
            top_row.pack(fill=tk.X)
            
            tk.Label(top_row, text=f"{label}:", 
                    bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_PRIMARY,
                    font=ModernTheme.get_font(10, "bold")).pack(side=tk.LEFT)
            
            self.screening_settings[var_name] = tk.StringVar(value=default_val)
            entry = tk.Entry(top_row, textvariable=self.screening_settings[var_name], width=8)
            entry.pack(side=tk.RIGHT)
            
            # Recommended range label
            range_label = tk.Label(top_row, text=f"({recommended_range})", 
                                 bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                                 font=ModernTheme.get_font(9, "italic"))
            range_label.pack(side=tk.RIGHT, padx=(0, 10))
            
            # Explanation text
            explanation_label = tk.Label(setting_frame, text=explanation,
                                       bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_SECONDARY,
                                       font=ModernTheme.get_font(8, "normal"),
                                       wraplength=450, justify=tk.LEFT)
            explanation_label.pack(anchor="w", padx=(0, 0), pady=(2, 0))
            
            return entry

        # Initial samples
        create_setting_row(
            algo_frame,
            "Initial Samples",
            "n_initial_samples",
            "8",
            "Number of initial experiments using Latin Hypercube Sampling to seed the optimization. " +
            "More samples give better initial coverage but require more experiments. " +
            "Recommended: 2×(number of parameters) to 3×(number of parameters).",
            "5-15"
        )

        # Gradient step size
        create_setting_row(
            algo_frame,
            "Gradient Step Size",
            "gradient_step_size", 
            "0.15",
            "Step size for gradient-based moves in normalized parameter space [0,1]. " +
            "Larger values = more aggressive exploration, smaller values = more conservative moves. " +
            "Too large may overshoot optima, too small may converge slowly.",
            "0.05-0.3"
        )

        # Exploration factor
        create_setting_row(
            algo_frame,
            "Exploration Factor",
            "exploration_factor",
            "0.2", 
            "Balance between exploitation (using best known regions) and exploration (trying new areas). " +
            "Higher values encourage more exploration of uncertain regions. " +
            "Use higher values for complex response surfaces, lower for smooth surfaces.",
            "0.1-0.5"
        )

        # Max iterations
        create_setting_row(
            algo_frame,
            "Max Iterations",
            "max_iterations",
            "25",
            "Maximum number of SGLBO iterations after initial sampling. " +
            "Each iteration suggests one new experiment. Total experiments = Initial Samples + Max Iterations. " +
            "More iterations allow better convergence but take longer.",
            "15-40"
        )

        # Convergence threshold
        create_setting_row(
            algo_frame,
            "Convergence Threshold", 
            "convergence_threshold",
            "0.015",
            "Relative improvement threshold below which screening is considered converged. " +
            "Smaller values = stricter convergence (more iterations), larger values = earlier stopping. " +
            "0.01 = 1% improvement needed to continue, 0.05 = 5% improvement needed.",
            "0.01-0.05"
        )

        # Design Space Settings
        design_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        design_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            design_frame,
            text="Design Space Generation Settings",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor="w", pady=(0, 10))

        # Add explanation for design space
        design_info = tk.Label(
            design_frame,
            text="After screening finds the optimal region, a design space is generated around the best point " +
                 "for detailed Bayesian optimization. These settings control that design space.",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(9, "italic"),
            wraplength=450,
            justify=tk.LEFT
        )
        design_info.pack(anchor="w", pady=(0, 15))

        # Design radius
        create_setting_row(
            design_frame,
            "Design Radius",
            "design_radius",
            "0.18",
            "Radius of the design space around the optimal point (as fraction of parameter range). " +
            "Larger radius = broader exploration around optimum, smaller radius = focused search. " +
            "Too large may include poor regions, too small may miss the true optimum.",
            "0.1-0.3"
        )

        # Design type with custom layout for combobox
        design_type_frame = tk.Frame(design_frame, bg=ModernTheme.SURFACE)
        design_type_frame.pack(fill=tk.X, pady=8)
        
        # Top row with label and combobox
        type_top_row = tk.Frame(design_type_frame, bg=ModernTheme.SURFACE)
        type_top_row.pack(fill=tk.X)
        
        tk.Label(type_top_row, text="Design Type:", 
                bg=ModernTheme.SURFACE, fg=ModernTheme.TEXT_PRIMARY,
                font=ModernTheme.get_font(10, "bold")).pack(side=tk.LEFT)
        
        self.screening_settings['design_type'] = tk.StringVar(value="ccd")
        design_combo = ttk.Combobox(type_top_row, 
                                  textvariable=self.screening_settings['design_type'],
                                  values=["ccd", "factorial", "box_behnken", "adaptive"],
                                  state="readonly", width=12)
        design_combo.pack(side=tk.RIGHT)
        
        # Explanation for design types
        design_type_explanation = tk.Label(
            design_type_frame,
            text="• CCD (Recommended): Central Composite Design - efficient, good for response surfaces\n" +
                 "• Factorial: Full factorial design - systematic but more experiments\n" +
                 "• Box-Behnken: Efficient for 3+ parameters, fewer corner points\n" +
                 "• Adaptive: Custom design based on parameter importance",
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            font=ModernTheme.get_font(8, "normal"),
            wraplength=450,
            justify=tk.LEFT
        )
        design_type_explanation.pack(anchor="w", pady=(2, 0))

        # Add a recommendations section
        recommendations_frame = self.create_modern_card(settings_content, padx=15, pady=15)
        recommendations_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            recommendations_frame,
            text="Quick Setup Recommendations",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.SUCCESS,
        ).pack(anchor="w", pady=(0, 10))

        # Recommendation buttons
        rec_buttons_frame = tk.Frame(recommendations_frame, bg=ModernTheme.SURFACE)
        rec_buttons_frame.pack(fill=tk.X)

        # Fast screening preset
        fast_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Fast Screening (15-20 experiments)",
            command=lambda: self._apply_screening_preset("fast"),
            style="secondary"
        )
        fast_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Thorough screening preset  
        thorough_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Thorough Screening (25-35 experiments)",
            command=lambda: self._apply_screening_preset("thorough"),
            style="secondary"
        )
        thorough_btn.pack(side=tk.LEFT, padx=(0, 10))

        # Conservative screening preset
        conservative_btn = self.create_modern_button(
            rec_buttons_frame,
            text="Many Parameters (30-45 experiments)",
            command=lambda: self._apply_screening_preset("conservative"),
            style="secondary"
        )
        conservative_btn.pack(side=tk.LEFT)

    def _apply_screening_preset(self, preset_type: str) -> None:
        """Apply preset configurations for different screening scenarios."""
        try:
            if preset_type == "fast":
                # Fast screening - minimal experiments
                self.screening_settings['n_initial_samples'].set("6")
                self.screening_settings['gradient_step_size'].set("0.2")
                self.screening_settings['exploration_factor'].set("0.25")
                self.screening_settings['max_iterations'].set("15")
                self.screening_settings['convergence_threshold'].set("0.03")
                self.screening_settings['design_radius'].set("0.2")
                self.screening_settings['design_type'].set("ccd")
                
                messagebox.showinfo("Preset Applied", 
                                  "Fast Screening preset applied!\n" +
                                  "• 6 initial samples + up to 15 iterations\n" +
                                  "• Aggressive exploration for quick results\n" +
                                  "• Total: ~15-20 experiments")
                                  
            elif preset_type == "thorough":
                # Thorough screening - balanced approach
                self.screening_settings['n_initial_samples'].set("10")
                self.screening_settings['gradient_step_size'].set("0.15")
                self.screening_settings['exploration_factor'].set("0.2")
                self.screening_settings['max_iterations'].set("25")
                self.screening_settings['convergence_threshold'].set("0.015")
                self.screening_settings['design_radius'].set("0.18")
                self.screening_settings['design_type'].set("ccd")
                
                messagebox.showinfo("Preset Applied",
                                  "Thorough Screening preset applied!\n" +
                                  "• 10 initial samples + up to 25 iterations\n" +
                                  "• Balanced exploration/exploitation\n" +
                                  "• Total: ~25-35 experiments")
                                  
            elif preset_type == "conservative":
                # Conservative screening - many parameters or complex system
                self.screening_settings['n_initial_samples'].set("12")
                self.screening_settings['gradient_step_size'].set("0.1")
                self.screening_settings['exploration_factor'].set("0.15")
                self.screening_settings['max_iterations'].set("30")
                self.screening_settings['convergence_threshold'].set("0.01")
                self.screening_settings['design_radius'].set("0.15")
                self.screening_settings['design_type'].set("box_behnken")
                
                messagebox.showinfo("Preset Applied",
                                  "Many Parameters preset applied!\n" +
                                  "• 12 initial samples + up to 30 iterations\n" +
                                  "• Conservative, thorough exploration\n" +
                                  "• Total: ~30-45 experiments")
                                  
        except Exception as e:
            messagebox.showerror("Preset Error", f"Failed to apply preset: {str(e)}")

    def _add_screening_parameter_row(self) -> None:
        """Add a new parameter row for screening setup (reuse existing method)."""
        self._add_parameter_row()

    def _add_screening_response_row(self) -> None:
        """Add a new response row for screening setup (reuse existing method)."""
        self._add_response_row()

    def _validate_screening_config(self) -> None:
        """Validate the screening configuration before starting."""
        try:
            # Collect parameter data
            params_config = {}
            valid_params = 0
            
            for i, row_widgets in enumerate(self.param_rows):
                try:
                    # Try to get basic info, skip if problematic
                    if "name" not in row_widgets or "type" not in row_widgets:
                        continue
                        
                    name = row_widgets["name"].get().strip()
                    param_type = row_widgets["type"].get()
                    
                    # Skip completely empty rows
                    if not name:
                        continue
                    
                    # Process valid parameter rows
                    if param_type == "continuous":
                        # The parameter rows use a "bounds" field with format like "[0.0, 100.0]"
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to continuous but bounds field is missing.")
                        
                        bounds_str = row_widgets["bounds"].get().strip()
                        
                        # Handle "None" and empty values
                        if not bounds_str or bounds_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Bounds are required (don't use 'None'). Use format [min, max] like [0, 100]")
                        
                        # Parse bounds format [min, max]
                        try:
                            # Remove brackets and split by comma
                            bounds_str = bounds_str.strip("[]")
                            bounds_parts = [part.strip() for part in bounds_str.split(",")]
                            
                            if len(bounds_parts) != 2:
                                raise ValueError(f"Bounds must be in format [min, max]")
                            
                            min_val = float(bounds_parts[0])
                            max_val = float(bounds_parts[1])
                            
                        except (ValueError, IndexError) as e:
                            raise ValueError(f"Parameter '{name}': Invalid bounds format '{bounds_str}'. Use [min, max] like [0, 100]")
                        
                        if min_val >= max_val:
                            raise ValueError(f"Parameter '{name}': Max ({max_val}) must be greater than Min ({min_val})")
                        
                        # Handle precision - not used in this interface but keep for compatibility
                        precision_val = None
                        
                        params_config[name] = {
                            "type": "continuous",
                            "bounds": [min_val, max_val],
                            "precision": precision_val
                        }
                        valid_params += 1
                        
                    elif param_type == "categorical":
                        # Categorical parameters also use the "bounds" field but with comma-separated values
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to categorical but bounds field is missing.")
                        
                        values_str = row_widgets["bounds"].get().strip()
                        if not values_str or values_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Values are required for categorical parameters. Use comma-separated format like 'A,B,C'")
                        
                        values = [v.strip() for v in values_str.split(",") if v.strip()]
                        if len(values) < 2:
                            raise ValueError(f"Parameter '{name}': At least 2 categorical values required. Use format like 'A,B,C'")
                        
                        params_config[name] = {
                            "type": "categorical",
                            "bounds": values
                        }
                        valid_params += 1
                        
                    elif param_type == "discrete":
                        # Discrete parameters use bounds field with format like "[0, 10]"
                        if "bounds" not in row_widgets:
                            raise ValueError(f"Parameter '{name}' is set to discrete but bounds field is missing.")
                        
                        bounds_str = row_widgets["bounds"].get().strip()
                        
                        # Handle "None" and empty values
                        if not bounds_str or bounds_str.lower() == "none":
                            raise ValueError(f"Parameter '{name}': Bounds are required (don't use 'None'). Use format [min, max] like [0, 10]")
                        
                        # Parse bounds format [min, max]
                        try:
                            # Remove brackets and split by comma
                            bounds_str = bounds_str.strip("[]")
                            bounds_parts = [part.strip() for part in bounds_str.split(",")]
                            
                            if len(bounds_parts) != 2:
                                raise ValueError(f"Bounds must be in format [min, max]")
                            
                            min_val = int(float(bounds_parts[0]))  # Convert to int for discrete
                            max_val = int(float(bounds_parts[1]))  # Convert to int for discrete
                            
                        except (ValueError, IndexError) as e:
                            raise ValueError(f"Parameter '{name}': Invalid bounds format '{bounds_str}'. Use [min, max] like [0, 10]")
                        
                        if min_val >= max_val:
                            raise ValueError(f"Parameter '{name}': Max ({max_val}) must be greater than Min ({min_val})")
                        
                        params_config[name] = {
                            "type": "discrete",
                            "bounds": [min_val, max_val]
                        }
                        valid_params += 1
                        
                except Exception as row_error:
                    # Skip this row and continue, but show which row failed
                    raise ValueError(f"Parameter row {i+1} error: {str(row_error)}")

            # Collect response data
            responses_config = {}
            valid_responses = 0
            
            for row_widgets in self.response_rows:
                name = row_widgets["name"].get().strip()
                goal = row_widgets["goal"].get()
                
                if name and goal:  # Both name and goal are required
                    responses_config[name] = {"goal": goal}
                    
                    if goal == "Target":
                        try:
                            target_widget = row_widgets.get("target")
                            if target_widget and hasattr(target_widget, 'get'):
                                target_val = target_widget.get().strip()
                                if target_val:
                                    responses_config[name]["target"] = float(target_val)
                                else:
                                    raise ValueError("Target value is required when goal is 'Target'")
                        except (ValueError, AttributeError) as e:
                            raise ValueError(f"Invalid target value for response '{name}': {str(e)}")
                    
                    valid_responses += 1

            # Validation
            if valid_params < 1:
                messagebox.showerror("Validation Error", "At least one parameter must be defined.")
                return
                
            if valid_responses < 1:
                messagebox.showerror("Validation Error", "At least one response must be defined.")
                return

            # Validate settings
            try:
                n_initial = int(self.screening_settings['n_initial_samples'].get())
                gradient_step = float(self.screening_settings['gradient_step_size'].get())
                exploration = float(self.screening_settings['exploration_factor'].get())
                max_iter = int(self.screening_settings['max_iterations'].get())
                conv_thresh = float(self.screening_settings['convergence_threshold'].get())
                design_radius = float(self.screening_settings['design_radius'].get())
                
                if n_initial < 3:
                    raise ValueError("Initial samples must be at least 3")
                if not (0.01 <= gradient_step <= 1.0):
                    raise ValueError("Gradient step size must be between 0.01 and 1.0")
                if not (0.01 <= exploration <= 1.0):
                    raise ValueError("Exploration factor must be between 0.01 and 1.0")
                if max_iter < 5:
                    raise ValueError("Max iterations must be at least 5")
                if not (0.001 <= conv_thresh <= 0.5):
                    raise ValueError("Convergence threshold must be between 0.001 and 0.5")
                if not (0.05 <= design_radius <= 0.5):
                    raise ValueError("Design radius must be between 0.05 and 0.5")
                    
            except ValueError as e:
                messagebox.showerror("Settings Error", f"Invalid setting: {str(e)}")
                return

            messagebox.showinfo("Validation Success", 
                              f"Configuration is valid!\n"
                              f"Parameters: {valid_params}\n"
                              f"Responses: {valid_responses}\n"
                              f"Ready to start screening.")

        except Exception as e:
            error_msg = f"Configuration validation failed: {str(e)}\n\n"
            error_msg += "PARAMETER SETUP GUIDE:\n"
            error_msg += "• Name: Temperature, Pressure, etc.\n"
            error_msg += "• Type: continuous, categorical, discrete\n"
            error_msg += "• Bounds: [min, max] for continuous (e.g., [0, 100])\n"
            error_msg += "• Bounds: A,B,C for categorical (e.g., Catalyst1,Catalyst2,Catalyst3)\n"
            error_msg += "• Goal: Usually 'None' for parameters\n\n"
            error_msg += "RESPONSE SETUP GUIDE:\n"
            error_msg += "• Name: Yield, Purity, etc.\n"
            error_msg += "• Goal: Maximize, Minimize, or Target\n"
            error_msg += "• Target: only when Goal = 'Target'\n\n"
            error_msg += "COMMON FIXES:\n"
            error_msg += "• For continuous parameters: use [50, 200] format\n"
            error_msg += "• For categorical parameters: use A,B,C format\n"
            error_msg += "• Don't use 'None' in bounds fields\n"
            error_msg += "• Remove empty rows before validation"
            
            messagebox.showerror("Validation Error", error_msg)

    def _start_screening_optimization(self) -> None:
        """Start the SGLBO screening optimization process."""
        try:
            # First validate configuration
            self._validate_screening_config()
            
            # If validation passes, start screening
            if hasattr(self, 'controller') and self.controller and hasattr(self.controller, 'start_sglbo_screening'):
                # Use controller if available and has SGLBO method
                config = self._get_screening_config()
                print(f"DEBUG: Sending config to controller: {config}")
                print(f"DEBUG: Parameters: {config.get('parameters', {})}")
                print(f"DEBUG: Responses: {config.get('responses', {})}")
                self.controller.start_sglbo_screening(config)
            else:
                # Standalone SGLBO execution (default for now)
                self._run_sglbo_screening_standalone()
            
        except Exception as e:
            messagebox.showerror("Start Error", f"Failed to start screening: {str(e)}")
    
    def _get_screening_config(self) -> dict:
        """Get the complete screening configuration from GUI."""
        # Collect parameter data (same logic as validation)
        params_config = {}
        for i, row_widgets in enumerate(self.param_rows):
            try:
                if "name" not in row_widgets or "type" not in row_widgets:
                    continue
                    
                name = row_widgets["name"].get().strip()
                param_type = row_widgets["type"].get()
                
                if not name:
                    continue
                
                if param_type == "continuous":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        bounds_str = bounds_str.strip("[]")
                        parts = [part.strip() for part in bounds_str.split(",")]
                        if len(parts) == 2:
                            min_val, max_val = float(parts[0]), float(parts[1])
                            params_config[name] = {
                                "type": "continuous",
                                "bounds": [min_val, max_val],
                                "precision": None
                            }
                            
                elif param_type == "categorical":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        values = [v.strip() for v in bounds_str.split(",") if v.strip()]
                        if len(values) >= 2:
                            params_config[name] = {
                                "type": "categorical",
                                "bounds": values
                            }
                            
                elif param_type == "discrete":
                    bounds_str = row_widgets["bounds"].get().strip()
                    if bounds_str and bounds_str.lower() != "none":
                        bounds_str = bounds_str.strip("[]")
                        parts = [part.strip() for part in bounds_str.split(",")]
                        if len(parts) == 2:
                            min_val, max_val = int(float(parts[0])), int(float(parts[1]))
                            params_config[name] = {
                                "type": "discrete",
                                "bounds": [min_val, max_val]
                            }
            except:
                continue
        
        # Collect response data
        responses_config = {}
        for row_widgets in self.response_rows:
            try:
                name = row_widgets["name"].get().strip()
                goal = row_widgets["goal"].get()
                
                if name and goal:
                    responses_config[name] = {"goal": goal}
                    
                    if goal == "Target":
                        target_widget = row_widgets.get("target")
                        if target_widget and hasattr(target_widget, 'get'):
                            target_val = target_widget.get().strip()
                            if target_val:
                                responses_config[name]["target"] = float(target_val)
            except:
                continue
        
        # Get SGLBO settings
        sglbo_settings = {}
        if hasattr(self, 'screening_settings'):
            try:
                sglbo_settings = {
                    "n_initial_samples": int(self.screening_settings['n_initial_samples'].get()),
                    "gradient_step_size": float(self.screening_settings['gradient_step_size'].get()),
                    "exploration_factor": float(self.screening_settings['exploration_factor'].get()),
                    "max_iterations": int(self.screening_settings['max_iterations'].get()),
                    "convergence_threshold": float(self.screening_settings['convergence_threshold'].get()),
                    "design_radius": float(self.screening_settings['design_radius'].get()),
                    "design_type": self.screening_settings['design_type'].get()
                }
            except:
                # Use defaults if settings can't be read
                sglbo_settings = {
                    "n_initial_samples": 8,
                    "gradient_step_size": 0.15,
                    "exploration_factor": 0.2,
                    "max_iterations": 25,
                    "convergence_threshold": 0.015,
                    "design_radius": 0.18,
                    "design_type": "CCD"
                }
        
        return {
            "parameters": params_config,
            "responses": responses_config,
            "sglbo_settings": sglbo_settings
        }
    
    def _run_sglbo_screening_standalone(self) -> None:
        """Run SGLBO screening in standalone mode (without controller)."""
        import sys
        import os
        
        # Add screening module to path
        screening_path = os.path.join(os.path.dirname(__file__), 'screening')
        if screening_path not in sys.path:
            sys.path.append(screening_path)
        
        try:
            from ..screening.screening_optimizer import ScreeningOptimizer
            import pandas as pd
            
            # Get configuration
            config = self._get_screening_config()
            params_config = config["parameters"]
            responses_config = config["responses"]
            settings = config["sglbo_settings"]
            
            if not params_config or not responses_config:
                messagebox.showerror("Configuration Error", "Please set up at least one parameter and one response.")
                return
            
            # Show screening execution window
            self._show_screening_execution_window(params_config, responses_config, settings)
            
        except ImportError as e:
            messagebox.showerror("Module Error", f"Could not import screening modules: {e}")
        except Exception as e:
            messagebox.showerror("Execution Error", f"Failed to run screening: {e}")
    
    def _show_screening_execution_window(self, params_config, responses_config, settings):
        """Show a window for SGLBO screening execution."""
        # Create new window for screening execution
        screening_window = tk.Toplevel(self)
        screening_window.title("SGLBO Screening Execution")
        screening_window.geometry("800x600")
        screening_window.configure(bg=ModernTheme.BACKGROUND)
        
        # Header
        header_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(
            header_frame,
            text="🎯 SGLBO Screening in Progress",
            font=ModernTheme.get_font(16, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack()
        
        # Configuration summary
        config_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        config_text = f"Parameters: {list(params_config.keys())}\n"
        config_text += f"Responses: {list(responses_config.keys())}\n"
        config_text += f"Initial Samples: {settings['n_initial_samples']}\n"
        config_text += f"Max Iterations: {settings['max_iterations']}"
        
        tk.Label(
            config_frame,
            text=config_text,
            font=ModernTheme.get_font(10),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_SECONDARY,
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Progress text area
        progress_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            progress_frame,
            text="Screening Progress:",
            font=ModernTheme.get_font(12, "bold"),
            bg=ModernTheme.SURFACE,
            fg=ModernTheme.TEXT_PRIMARY,
        ).pack(anchor=tk.W)
        
        progress_text = scrolledtext.ScrolledText(
            progress_frame,
            height=20,
            bg=ModernTheme.BACKGROUND,
            fg=ModernTheme.TEXT_PRIMARY,
            font=ModernTheme.get_font(9, family="monospace")
        )
        progress_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Buttons
        button_frame = tk.Frame(screening_window, bg=ModernTheme.SURFACE)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        start_btn = self.create_modern_button(
            button_frame,
            text="▶ Start Screening",
            command=lambda: self._execute_sglbo_screening(
                params_config, responses_config, settings, 
                progress_text, start_btn, screening_window
            ),
            style="primary"
        )
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        close_btn = self.create_modern_button(
            button_frame,
            text="Close",
            command=screening_window.destroy,
            style="secondary"
        )
        close_btn.pack(side=tk.RIGHT)
        
        progress_text.insert(tk.END, "SGLBO Screening configured and ready to start.\n")
        progress_text.insert(tk.END, "Click 'Start Screening' to begin optimization.\n\n")
    
    def _execute_sglbo_screening(self, params_config, responses_config, settings, progress_text, start_btn, window):
        """Execute the actual SGLBO screening algorithm."""
        try:
            # Disable start button
            start_btn.config(state="disabled", text="Running...")
            window.update()
            
            from ..screening.screening_optimizer import ScreeningOptimizer
            import pandas as pd
            import numpy as np
            
            progress_text.insert(tk.END, "Initializing SGLBO optimizer...\n")
            window.update()
            
            # Create optimizer (only pass valid optimizer parameters)
            optimizer = ScreeningOptimizer(
                params_config=params_config,
                responses_config=responses_config,
                gradient_step_size=settings["gradient_step_size"],
                exploration_factor=settings["exploration_factor"],
                max_iterations=settings["max_iterations"],
                convergence_threshold=settings["convergence_threshold"],
                n_initial_samples=settings["n_initial_samples"],
                random_seed=42
            )
            
            progress_text.insert(tk.END, f"Optimizer created with extrapolation: {optimizer.param_handler.allow_extrapolation}\n\n")
            window.update()
            
            # Generate initial experiments
            progress_text.insert(tk.END, "Generating initial experiments...\n")
            window.update()
            
            initial_experiments = optimizer.suggest_initial_experiments()
            
            progress_text.insert(tk.END, f"Generated {len(initial_experiments)} initial experiments:\n")
            for i, exp in enumerate(initial_experiments):
                progress_text.insert(tk.END, f"  Exp {i+1}: {exp}\n")
            progress_text.insert(tk.END, "\n")
            window.update()
            
            # Show message about manual experimentation
            progress_text.insert(tk.END, "=" * 50 + "\n")
            progress_text.insert(tk.END, "NEXT STEPS:\n")
            progress_text.insert(tk.END, "=" * 50 + "\n")
            progress_text.insert(tk.END, "1. Perform the experiments shown above\n")
            progress_text.insert(tk.END, "2. Record the response values\n")
            progress_text.insert(tk.END, "3. Input results to continue SGLBO iterations\n\n")
            progress_text.insert(tk.END, "This demo shows initial experiment suggestions.\n")
            progress_text.insert(tk.END, "Full implementation would continue with iterative screening\n")
            progress_text.insert(tk.END, "based on experimental results.\n\n")
            progress_text.insert(tk.END, f"SGLBO Configuration:\n")
            progress_text.insert(tk.END, f"- Extrapolation enabled: Can explore beyond initial bounds\n")
            progress_text.insert(tk.END, f"- Gradient step size: {settings['gradient_step_size']}\n")
            progress_text.insert(tk.END, f"- Max iterations: {settings['max_iterations']}\n")
            progress_text.insert(tk.END, f"- Initial samples: {settings['n_initial_samples']}\n")
            
            # Re-enable button
            start_btn.config(state="normal", text="✓ Screening Complete")
            
        except Exception as e:
            progress_text.insert(tk.END, f"\nERROR: {str(e)}\n")
            start_btn.config(state="normal", text="Error - Try Again")
    
    def _show_advanced_screening_execution_window(self, screening_optimizer, results_manager, design_generator, config):
        """Show the advanced screening execution window with manual experimental input."""
        try:
            if INTERACTIVE_SCREENING_AVAILABLE:
                # Use the interactive execution window (preferred)
                show_interactive_screening_window(
                    parent=self,
                    screening_optimizer=screening_optimizer,
                    results_manager=results_manager,
                    design_generator=design_generator,
                    config=config
                )
            elif SCREENING_WINDOW_AVAILABLE:
                # Fallback to automatic execution window
                show_screening_execution_window(
                    parent=self,
                    screening_optimizer=screening_optimizer,
                    results_manager=results_manager,
                    design_generator=design_generator,
                    config=config
                )
            else:
                # Fallback to basic window
                params_config = config.get("parameters", {})
                responses_config = config.get("responses", {})
                settings = config.get("sglbo_settings", {})
                self._show_screening_execution_window(params_config, responses_config, settings)
                
        except Exception as e:
            logger.error(f"Error showing advanced screening execution window: {e}")
            messagebox.showerror("Execution Window Error", 
                               f"Failed to show screening execution window: {e}")
