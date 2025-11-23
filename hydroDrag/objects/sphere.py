"""Sphere object for wind tunnel simulation."""

import numpy as np
from .base_object import BaseObject


class Sphere(BaseObject):
    """Sphere object with drag calculations."""
    
    def __init__(self, position, radius, material_properties=None):
        """
        Initialize a sphere.
        
        Args:
            position: Tuple (x, y, z) or (x, y) for center position
            radius: Radius of the sphere
            material_properties: Dict with material properties
        """
        super().__init__(position, radius, material_properties)
        self.radius = radius
    
    def get_surface_area(self):
        """Calculate surface area of sphere: 4πr²"""
        return 4 * np.pi * self.radius ** 2
    
    def get_cross_sectional_area(self, flow_direction):
        """Cross-sectional area is always πr² for a sphere."""
        return np.pi * self.radius ** 2
    
    def get_volume(self):
        """Calculate volume of sphere: (4/3)πr³"""
        return (4.0 / 3.0) * np.pi * self.radius ** 3
    
    def contains_point(self, point):
        """Check if point is inside sphere."""
        point = np.array(point)
        distance = np.linalg.norm(point - self.position)
        return distance <= self.radius
    
    def get_characteristic_length(self):
        """Characteristic length is diameter for sphere."""
        return 2 * self.radius
    
    def get_drag_coefficient(self, reynolds_number):
        """
        Get drag coefficient for sphere based on Reynolds number.
        
        Uses empirical correlations:
        - Re < 0.1: Stokes flow (Cd = 24/Re)
        - 0.1 < Re < 1000: Transition region
        - Re > 1000: Constant Cd ≈ 0.47
        """
        if reynolds_number < 0.1:
            # Stokes flow
            return 24.0 / reynolds_number if reynolds_number > 0 else 240.0
        elif reynolds_number < 1000:
            # Transition region - smooth interpolation
            cd_stokes = 24.0 / reynolds_number
            cd_turbulent = 0.47
            # Smooth transition
            alpha = (reynolds_number - 0.1) / (1000 - 0.1)
            alpha = np.clip(alpha, 0, 1)
            return cd_stokes * (1 - alpha) + cd_turbulent * alpha
        else:
            # Turbulent flow
            return 0.47

