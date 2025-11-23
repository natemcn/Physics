"""Control panel for wind tunnel simulator."""

import tkinter as tk
from tkinter import ttk
from objects.sphere import Sphere
from objects.cylinder import Cylinder
from objects.box import Box


class ControlPanel(ttk.Frame):
    """Control panel widget."""
    
    def __init__(self, parent, wind_tunnel, drag_calculator, canvas_widget):
        """
        Initialize control panel.
        
        Args:
            parent: Parent widget
            wind_tunnel: WindTunnel instance
            drag_calculator: DragCalculator instance
            canvas_widget: CanvasWidget instance for updates
        """
        super().__init__(parent)
        self.wind_tunnel = wind_tunnel
        self.drag_calculator = drag_calculator
        self.canvas_widget = canvas_widget
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create control widgets."""
        # Wind properties
        wind_frame = ttk.LabelFrame(self, text="Wind Properties", padding=10)
        wind_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(wind_frame, text="Wind Speed (m/s):").pack(anchor=tk.W)
        self.wind_speed_var = tk.DoubleVar(value=self.wind_tunnel.wind_speed)
        wind_speed_scale = ttk.Scale(
            wind_frame,
            from_=0.0,
            to=50.0,
            variable=self.wind_speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_wind_speed_change
        )
        wind_speed_scale.pack(fill=tk.X, pady=2)
        
        self.wind_speed_label = ttk.Label(wind_frame, text=f"{self.wind_tunnel.wind_speed:.1f} m/s")
        self.wind_speed_label.pack(anchor=tk.W)
        
        ttk.Label(wind_frame, text="Density (kg/m³):").pack(anchor=tk.W, pady=(10, 0))
        self.density_var = tk.DoubleVar(value=self.wind_tunnel.density)
        density_scale = ttk.Scale(
            wind_frame,
            from_=0.5,
            to=2.0,
            variable=self.density_var,
            orient=tk.HORIZONTAL,
            command=self._on_density_change
        )
        density_scale.pack(fill=tk.X, pady=2)
        
        self.density_label = ttk.Label(wind_frame, text=f"{self.wind_tunnel.density:.3f} kg/m³")
        self.density_label.pack(anchor=tk.W)
        
        # Object controls
        object_frame = ttk.LabelFrame(self, text="Add Objects", padding=10)
        object_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(
            object_frame,
            text="Add Sphere",
            command=lambda: self._add_object('sphere')
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            object_frame,
            text="Add Cylinder",
            command=lambda: self._add_object('cylinder')
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            object_frame,
            text="Add Box",
            command=lambda: self._add_object('box')
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            object_frame,
            text="Clear All Objects",
            command=self._clear_objects
        ).pack(fill=tk.X, pady=2)
        
        # Object list
        list_frame = ttk.LabelFrame(self, text="Objects", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Listbox with scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.object_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.object_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.object_listbox.yview)
        
        self.object_listbox.bind('<Double-Button-1>', self._on_object_select)
        
        ttk.Button(
            list_frame,
            text="Remove Selected",
            command=self._remove_selected_object
        ).pack(fill=tk.X, pady=(5, 0))
        
        # Drag force display
        force_frame = ttk.LabelFrame(self, text="Drag Forces", padding=10)
        force_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.force_text = tk.Text(force_frame, height=8, wrap=tk.WORD)
        self.force_text.pack(fill=tk.BOTH, expand=True)
        self.force_text.config(state=tk.DISABLED)
    
    def _on_wind_speed_change(self, value):
        """Handle wind speed change."""
        speed = float(value)
        self.wind_tunnel.set_wind_speed(speed)
        self.wind_speed_label.config(text=f"{speed:.1f} m/s")
        self.canvas_widget.update_display()
    
    def _on_density_change(self, value):
        """Handle density change."""
        density = float(value)
        self.wind_tunnel.set_density(density)
        self.density_label.config(text=f"{density:.3f} kg/m³")
        self.canvas_widget.update_display()
    
    def _add_object(self, obj_type):
        """Add an object to the wind tunnel."""
        # Default position (center of tunnel)
        x = self.wind_tunnel.width / 2
        y = self.wind_tunnel.height / 2
        
        if obj_type == 'sphere':
            obj = Sphere([x, y, 0], radius=0.3)
        elif obj_type == 'cylinder':
            obj = Cylinder([x, y, 0], radius=0.2, height=0.4)
        elif obj_type == 'box':
            obj = Box([x, y, 0], dimensions=[0.4, 0.3, 0.2])
        else:
            return
        
        self.wind_tunnel.add_object(obj)
        self._update_object_list()
        self.canvas_widget.update_display()
        # Update force display
        if self.wind_tunnel.objects:
            drag_results = self.drag_calculator.calculate_all_drag_forces()
            self.update_force_display(drag_results)
    
    def _clear_objects(self):
        """Clear all objects."""
        self.wind_tunnel.clear_objects()
        self._update_object_list()
        self.canvas_widget.update_display()
        self.update_force_display({})
    
    def _update_object_list(self):
        """Update the object listbox."""
        self.object_listbox.delete(0, tk.END)
        for i, obj in enumerate(self.wind_tunnel.objects):
            obj_type = type(obj).__name__
            pos = obj.get_position()
            self.object_listbox.insert(tk.END, f"{i+1}. {obj_type} at ({pos[0]:.2f}, {pos[1]:.2f})")
    
    def _on_object_select(self, event):
        """Handle object selection (double-click)."""
        selection = self.object_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.wind_tunnel.objects):
                obj = self.wind_tunnel.objects[index]
                self._show_object_properties(obj)
    
    def _remove_selected_object(self):
        """Remove the selected object."""
        selection = self.object_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.wind_tunnel.objects):
                obj = self.wind_tunnel.objects[index]
                self.wind_tunnel.remove_object(obj)
                self._update_object_list()
                self.canvas_widget.update_display()
    
    def _show_object_properties(self, obj):
        """Show object properties dialog."""
        from .object_properties import ObjectPropertiesDialog
        dialog = ObjectPropertiesDialog(self, obj, self.wind_tunnel, self.canvas_widget)
        dialog.show()
    
    def update_force_display(self, drag_results):
        """Update the drag force display."""
        self.force_text.config(state=tk.NORMAL)
        self.force_text.delete(1.0, tk.END)
        
        if not drag_results:
            self.force_text.insert(tk.END, "No objects in tunnel")
        else:
            for obj, results in drag_results.items():
                obj_type = type(obj).__name__
                force = results['drag_magnitude']
                Re = results['reynolds_number']
                Cd = results['drag_coefficient']
                
                self.force_text.insert(tk.END, f"{obj_type}:\n")
                self.force_text.insert(tk.END, f"  Drag Force: {force:.4f} N\n")
                self.force_text.insert(tk.END, f"  Reynolds #: {Re:.2e}\n")
                self.force_text.insert(tk.END, f"  Drag Coeff: {Cd:.3f}\n\n")
        
        self.force_text.config(state=tk.DISABLED)

