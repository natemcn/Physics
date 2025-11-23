"""Main application window for wind tunnel simulator."""

import tkinter as tk
from tkinter import ttk, filedialog
from .canvas_widget import CanvasWidget
from .control_panel import ControlPanel
from .save_load import SimulationSerializer


class MainWindow:
    """Main application window."""
    
    def __init__(self, root, wind_tunnel, drag_calculator):
        """
        Initialize main window.
        
        Args:
            root: Tkinter root window
            wind_tunnel: WindTunnel instance
            drag_calculator: DragCalculator instance
        """
        self.root = root
        self.wind_tunnel = wind_tunnel
        self.drag_calculator = drag_calculator
        
        self.root.title("Wind Tunnel Drag Simulator")
        self.root.geometry("1200x800")
        
        # Create main layout
        self._create_layout()
        
        # Simulation state
        self.is_running = False
        self.update_interval = 50  # milliseconds
        
    def _create_layout(self):
        """Create the main window layout."""
        # Create paned window for resizable panels
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel: Canvas for visualization
        canvas_frame = ttk.Frame(paned)
        paned.add(canvas_frame, weight=3)
        
        self.canvas_widget = CanvasWidget(
            canvas_frame,
            self.wind_tunnel,
            self.drag_calculator
        )
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        
        # Right panel: Controls
        control_frame = ttk.Frame(paned, width=300)
        paned.add(control_frame, weight=1)
        
        self.control_panel = ControlPanel(
            control_frame,
            self.wind_tunnel,
            self.drag_calculator,
            self.canvas_widget
        )
        self.control_panel.pack(fill=tk.BOTH, expand=True)
        
        # Connect canvas to control panel for force display updates
        self.canvas_widget.set_control_panel(self.control_panel)
        
        # Menu bar
        self._create_menu()
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Simulation...", command=self._save_simulation)
        file_menu.add_command(label="Load Simulation...", command=self._load_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Reset Simulation", command=self._reset_simulation)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Simulation menu
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulation", menu=sim_menu)
        sim_menu.add_command(label="Start", command=self._start_simulation)
        sim_menu.add_command(label="Stop", command=self._stop_simulation)
        sim_menu.add_command(label="Step", command=self._step_simulation)
    
    def _start_simulation(self):
        """Start the simulation."""
        self.is_running = True
        self._update_simulation()
    
    def _stop_simulation(self):
        """Stop the simulation."""
        self.is_running = False
    
    def _step_simulation(self):
        """Perform a single simulation step."""
        self.wind_tunnel.step()
        self.drag_calculator.calculate_all_drag_forces()
        self.canvas_widget.update_display()
    
    def _reset_simulation(self):
        """Reset the simulation."""
        self._stop_simulation()
        self.wind_tunnel.reset()
        self.canvas_widget.update_display()
        self.control_panel._update_object_list()
    
    def _save_simulation(self):
        """Save simulation to file."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            SimulationSerializer.save_simulation(self.wind_tunnel, filename)
    
    def _load_simulation(self):
        """Load simulation from file."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self._stop_simulation()
            SimulationSerializer.load_simulation(self.wind_tunnel, filename)
            self.canvas_widget.update_display()
            self.control_panel._update_object_list()
            # Update control panel values
            self.control_panel.wind_speed_var.set(self.wind_tunnel.wind_speed)
            self.control_panel.wind_speed_label.config(text=f"{self.wind_tunnel.wind_speed:.1f} m/s")
            self.control_panel.density_var.set(self.wind_tunnel.density)
            self.control_panel.density_label.config(text=f"{self.wind_tunnel.density:.3f} kg/m³")
    
    def _update_simulation(self):
        """Update simulation loop."""
        if self.is_running:
            self._step_simulation()
            self.root.after(self.update_interval, self._update_simulation)
    
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()

