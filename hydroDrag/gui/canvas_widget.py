"""Canvas widget for visualization using matplotlib."""

import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from visualization.flow_visualizer import FlowVisualizer


class CanvasWidget(ttk.Frame):
    """Matplotlib canvas widget for wind tunnel visualization."""
    
    def __init__(self, parent, wind_tunnel, drag_calculator):
        """
        Initialize canvas widget.
        
        Args:
            parent: Parent widget
            wind_tunnel: WindTunnel instance
            drag_calculator: DragCalculator instance
        """
        super().__init__(parent)
        self.wind_tunnel = wind_tunnel
        self.drag_calculator = drag_calculator
        
        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM)
        
        # Visualization options
        self.show_streamlines = True
        self.show_pressure = True
        self.show_drag_vectors = True
        
        # Initial display
        self.update_display()
    
    def update_display(self):
        """Update the visualization display."""
        self.ax.clear()
        
        # Set up axes
        self.ax.set_xlim(0, self.wind_tunnel.width)
        self.ax.set_ylim(0, self.wind_tunnel.height)
        self.ax.set_aspect('equal')
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title('Wind Tunnel Simulation')
        
        # Draw tunnel walls
        self.ax.axhline(y=0, color='gray', linewidth=2, linestyle='--')
        self.ax.axhline(y=self.wind_tunnel.height, color='gray', linewidth=2, linestyle='--')
        
        # Plot flow field
        FlowVisualizer.plot_flow_field(
            self.ax,
            self.wind_tunnel,
            show_streamlines=self.show_streamlines,
            show_pressure=self.show_pressure
        )
        
        # Plot objects
        FlowVisualizer.plot_objects(self.ax, self.wind_tunnel)
        
        # Calculate and plot drag forces
        if self.wind_tunnel.objects and self.show_drag_vectors:
            drag_results = self.drag_calculator.calculate_all_drag_forces()
            FlowVisualizer.plot_drag_vectors(self.ax, self.wind_tunnel, drag_results)
        
        # Update control panel force display
        if hasattr(self, '_control_panel'):
            if self.wind_tunnel.objects:
                drag_results = self.drag_calculator.calculate_all_drag_forces()
                self._control_panel.update_force_display(drag_results)
            else:
                self._control_panel.update_force_display({})
        
        # Redraw
        self.canvas.draw()
    
    def set_control_panel(self, control_panel):
        """Set reference to control panel for force display updates."""
        self._control_panel = control_panel

