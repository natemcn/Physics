"""Dialog for configuring object properties."""

import tkinter as tk
from tkinter import ttk
import numpy as np


class ObjectPropertiesDialog:
    """Dialog for editing object properties."""
    
    def __init__(self, parent, obj, wind_tunnel, canvas_widget):
        """
        Initialize properties dialog.
        
        Args:
            parent: Parent widget
            obj: Object to configure
            wind_tunnel: WindTunnel instance
            canvas_widget: CanvasWidget for updates
        """
        self.parent = parent
        self.obj = obj
        self.wind_tunnel = wind_tunnel
        self.canvas_widget = canvas_widget
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Object Properties")
        self.dialog.geometry("300x400")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Position
        pos_frame = ttk.LabelFrame(self.dialog, text="Position", padding=10)
        pos_frame.pack(fill=tk.X, padx=10, pady=5)
        
        pos = self.obj.get_position()
        
        ttk.Label(pos_frame, text="X:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.x_var = tk.DoubleVar(value=pos[0])
        ttk.Entry(pos_frame, textvariable=self.x_var, width=10).grid(row=0, column=1, pady=2)
        
        ttk.Label(pos_frame, text="Y:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.y_var = tk.DoubleVar(value=pos[1])
        ttk.Entry(pos_frame, textvariable=self.y_var, width=10).grid(row=1, column=1, pady=2)
        
        # Size properties (shape-dependent)
        size_frame = ttk.LabelFrame(self.dialog, text="Size", padding=10)
        size_frame.pack(fill=tk.X, padx=10, pady=5)
        
        if hasattr(self.obj, 'radius'):
            # Sphere or Cylinder
            ttk.Label(size_frame, text="Radius:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.radius_var = tk.DoubleVar(value=self.obj.radius)
            ttk.Entry(size_frame, textvariable=self.radius_var, width=10).grid(row=0, column=1, pady=2)
            
            if hasattr(self.obj, 'height'):
                # Cylinder
                ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky=tk.W, pady=2)
                self.height_var = tk.DoubleVar(value=self.obj.height)
                ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, pady=2)
        elif hasattr(self.obj, 'dimensions'):
            # Box
            dims = self.obj.dimensions
            ttk.Label(size_frame, text="Width:").grid(row=0, column=0, sticky=tk.W, pady=2)
            self.width_var = tk.DoubleVar(value=dims[0])
            ttk.Entry(size_frame, textvariable=self.width_var, width=10).grid(row=0, column=1, pady=2)
            
            ttk.Label(size_frame, text="Height:").grid(row=1, column=0, sticky=tk.W, pady=2)
            self.height_var = tk.DoubleVar(value=dims[1])
            ttk.Entry(size_frame, textvariable=self.height_var, width=10).grid(row=1, column=1, pady=2)
            
            if len(dims) > 2:
                ttk.Label(size_frame, text="Depth:").grid(row=2, column=0, sticky=tk.W, pady=2)
                self.depth_var = tk.DoubleVar(value=dims[2])
                ttk.Entry(size_frame, textvariable=self.depth_var, width=10).grid(row=2, column=1, pady=2)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=self._apply).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _apply(self):
        """Apply changes to object."""
        # Update position
        new_pos = [self.x_var.get(), self.y_var.get(), 0]
        self.obj.set_position(new_pos)
        
        # Update size
        if hasattr(self.obj, 'radius'):
            self.obj.radius = self.radius_var.get()
            self.obj.size = self.obj.radius
            if hasattr(self.obj, 'height'):
                self.obj.height = self.height_var.get()
        elif hasattr(self.obj, 'dimensions'):
            if hasattr(self, 'depth_var'):
                new_dims = [self.width_var.get(), self.height_var.get(), self.depth_var.get()]
            else:
                new_dims = [self.width_var.get(), self.height_var.get()]
            self.obj.dimensions = np.array(new_dims)
            self.obj.size = new_dims
        
        # Update wind tunnel obstacle mask
        self.wind_tunnel._update_obstacle_mask()
        
        # Update display
        self.canvas_widget.update_display()
        self.parent._update_object_list()
        
        self.dialog.destroy()
    
    def show(self):
        """Show the dialog."""
        self.dialog.grab_set()
        self.dialog.wait_window()

