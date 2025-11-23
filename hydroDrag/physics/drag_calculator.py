"""Advanced drag force calculations with Reynolds number and pressure distribution."""

import numpy as np


class DragCalculator:
    """Calculate drag forces on objects in a wind tunnel."""
    
    def __init__(self, wind_tunnel):
        """
        Initialize drag calculator.
        
        Args:
            wind_tunnel: WindTunnel instance
        """
        self.wind_tunnel = wind_tunnel
    
    def calculate_reynolds_number(self, obj, flow_velocity):
        """
        Calculate Reynolds number for an object.
        
        Re = ρ * v * L / μ
        
        Args:
            obj: Object instance
            flow_velocity: Flow velocity vector at object position
        """
        v = np.linalg.norm(flow_velocity)
        if v < 1e-6:
            return 0.0
        
        L = obj.get_characteristic_length()
        rho = self.wind_tunnel.density
        mu = self.wind_tunnel.viscosity * rho  # Dynamic viscosity
        
        Re = (rho * v * L) / (mu + 1e-10)
        return Re
    
    def calculate_pressure_drag(self, obj):
        """
        Calculate pressure drag based on pressure distribution around object.
        
        Args:
            obj: Object instance
        """
        # Sample pressure at multiple points around the object
        position = obj.get_position()
        
        # For 2D simulation, sample points around the object
        # Create a circle/ellipse of sample points
        n_samples = 32
        angles = np.linspace(0, 2 * np.pi, n_samples)
        
        # Get object size for sampling radius
        if hasattr(obj, 'radius'):
            sample_radius = obj.radius * 1.1  # Slightly outside object
        elif hasattr(obj, 'dimensions'):
            sample_radius = np.max(obj.dimensions[:2]) * 0.6
        else:
            sample_radius = obj.get_characteristic_length() * 0.5
        
        # Sample points around object
        pressures = []
        normals = []
        
        for angle in angles:
            # Point on surface
            offset = sample_radius * np.array([np.cos(angle), np.sin(angle)])
            sample_point = position[:2] + offset
            
            # Get pressure at this point
            pressure = self.wind_tunnel.get_pressure(sample_point)
            pressures.append(pressure)
            
            # Normal vector (pointing outward)
            normal = offset / (np.linalg.norm(offset) + 1e-10)
            normals.append(normal)
        
        pressures = np.array(pressures)
        normals = np.array(normals)
        
        # Calculate pressure force
        # Force = pressure * area * normal
        # For 2D, we use perimeter element
        perimeter_element = 2 * np.pi * sample_radius / n_samples
        
        # Pressure force components
        force_x = np.sum(pressures * normals[:, 0] * perimeter_element)
        force_y = np.sum(pressures * normals[:, 1] * perimeter_element)
        
        # Project onto flow direction (drag is opposite to flow)
        flow_direction = np.array([1.0, 0.0])  # Wind flows in +x direction
        force_vector = np.array([force_x, force_y])
        
        # Drag is the component opposite to flow
        drag_force = -np.dot(force_vector, flow_direction)
        
        return drag_force
    
    def calculate_viscous_drag(self, obj, flow_velocity):
        """
        Calculate viscous drag based on surface area and velocity gradient.
        
        Args:
            obj: Object instance
            flow_velocity: Flow velocity at object position
        """
        v = np.linalg.norm(flow_velocity)
        if v < 1e-6:
            return 0.0
        
        # Viscous drag: F = μ * A * (du/dn)
        # Simplified: use characteristic velocity gradient
        mu = self.wind_tunnel.viscosity * self.wind_tunnel.density
        surface_area = obj.get_surface_area()
        
        # Estimate velocity gradient (simplified)
        # Assume velocity changes from v to 0 over characteristic length
        L = obj.get_characteristic_length()
        du_dn = v / (L + 1e-10)
        
        # For 2D, use perimeter instead of surface area
        if hasattr(obj, 'radius'):
            perimeter = 2 * np.pi * obj.radius
        elif hasattr(obj, 'dimensions'):
            # Approximate perimeter for box
            w, h = obj.dimensions[:2]
            perimeter = 2 * (w + h)
        else:
            perimeter = obj.get_characteristic_length() * np.pi
        
        viscous_force = mu * perimeter * du_dn
        
        return viscous_force
    
    def calculate_drag_force(self, obj):
        """
        Calculate total drag force on an object.
        Combines pressure drag and viscous drag.
        
        Args:
            obj: Object instance
        """
        # Get flow velocity at object position
        position = obj.get_position()
        flow_velocity = self.wind_tunnel.get_flow_velocity(position[:2])
        
        # Calculate Reynolds number
        Re = self.calculate_reynolds_number(obj, flow_velocity)
        
        # Calculate pressure drag
        pressure_drag = self.calculate_pressure_drag(obj)
        
        # Calculate viscous drag
        viscous_drag = self.calculate_viscous_drag(obj, flow_velocity)
        
        # Total drag
        total_drag = pressure_drag + viscous_drag
        
        # Also calculate using drag coefficient method as validation
        v = np.linalg.norm(flow_velocity)
        if v > 1e-6:
            Cd = obj.get_drag_coefficient(Re)
            A = obj.get_cross_sectional_area([1.0, 0.0, 0.0])
            rho = self.wind_tunnel.density
            
            # Drag force: F = 0.5 * ρ * v² * Cd * A
            drag_coefficient_force = 0.5 * rho * v ** 2 * Cd * A
            
            # Use weighted combination (pressure-based is more accurate for CFD)
            # But coefficient method is good for validation
            total_drag = 0.7 * total_drag + 0.3 * drag_coefficient_force
        else:
            total_drag = 0.0
        
        # Store drag coefficient for display
        if v > 1e-6:
            obj.drag_coefficient = obj.get_drag_coefficient(Re)
        else:
            obj.drag_coefficient = 0.0
        
        # Return drag force vector (opposite to flow direction)
        if v > 1e-6:
            flow_direction = flow_velocity / v
            drag_force_vector = -total_drag * flow_direction
        else:
            drag_force_vector = np.array([0.0, 0.0, 0.0])
        
        # Update object's drag force
        obj.update_drag_force(drag_force_vector)
        
        return drag_force_vector, Re
    
    def calculate_all_drag_forces(self):
        """Calculate drag forces for all objects in the tunnel."""
        results = {}
        for obj in self.wind_tunnel.objects:
            drag_force, Re = self.calculate_drag_force(obj)
            results[obj] = {
                'drag_force': drag_force,
                'drag_magnitude': np.linalg.norm(drag_force),
                'reynolds_number': Re,
                'drag_coefficient': obj.drag_coefficient
            }
        return results

