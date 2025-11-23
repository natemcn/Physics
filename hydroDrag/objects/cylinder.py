"""Cylinder object for wind tunnel simulation."""

import numpy as np
from .base_object import BaseObject


class Cylinder(BaseObject):
    """Cylinder object with drag calculations."""
    
    def __init__(self, position, radius, height, axis='z', material_properties=None):
        """
        Initialize a cylinder.
        
        Args:
            position: Tuple (x, y, z) or (x, y) for center position
            radius: Radius of the cylinder
            height: Height/length of the cylinder
            axis: Orientation axis ('x', 'y', or 'z')
            material_properties: Dict with material properties
        """
        super().__init__(position, (radius, height), material_properties)
        self.radius = radius
        self.height = height
        self.axis = axis.lower()
    
    def get_surface_area(self):
        """Calculate surface area: 2πr² + 2πrh"""
        return 2 * np.pi * self.radius ** 2 + 2 * np.pi * self.radius * self.height
    
    def get_cross_sectional_area(self, flow_direction):
        """
        Calculate cross-sectional area perpendicular to flow.
        Depends on flow direction relative to cylinder axis.
        """
        flow_direction = np.array(flow_direction)
        flow_direction = flow_direction / (np.linalg.norm(flow_direction) + 1e-10)
        
        # Determine which axis the cylinder is aligned with
        axis_vec = np.zeros(3)
        if self.axis == 'x':
            axis_vec[0] = 1
        elif self.axis == 'y':
            axis_vec[1] = 1
        else:  # 'z'
            axis_vec[2] = 1
        
        # Project flow direction onto plane perpendicular to cylinder axis
        flow_perp = flow_direction - np.dot(flow_direction, axis_vec) * axis_vec
        flow_perp_norm = np.linalg.norm(flow_perp)
        
        if flow_perp_norm < 1e-6:
            # Flow parallel to axis - cross-section is circle
            return np.pi * self.radius ** 2
        else:
            # Flow perpendicular to axis - cross-section is rectangle
            return 2 * self.radius * self.height
    
    def get_volume(self):
        """Calculate volume: πr²h"""
        return np.pi * self.radius ** 2 * self.height
    
    def contains_point(self, point):
        """Check if point is inside cylinder."""
        point = np.array(point)
        rel_pos = point - self.position
        
        # Project onto cylinder axis
        axis_vec = np.zeros(3)
        if self.axis == 'x':
            axis_vec[0] = 1
            axis_dist = abs(rel_pos[0])
            perp_dist = np.linalg.norm(rel_pos[1:])
        elif self.axis == 'y':
            axis_vec[1] = 1
            axis_dist = abs(rel_pos[1])
            perp_dist = np.sqrt(rel_pos[0]**2 + rel_pos[2]**2)
        else:  # 'z'
            axis_vec[2] = 1
            axis_dist = abs(rel_pos[2])
            perp_dist = np.linalg.norm(rel_pos[:2])
        
        return axis_dist <= self.height / 2 and perp_dist <= self.radius
    
    def get_characteristic_length(self):
        """Characteristic length is diameter for cylinder."""
        return 2 * self.radius
    
    def get_drag_coefficient(self, reynolds_number):
        """
        Get drag coefficient for cylinder based on Reynolds number.
        
        Uses empirical correlations for flow perpendicular to axis:
        - Re < 1: Stokes-like flow
        - 1 < Re < 100: Transition
        - Re > 100: Constant Cd ≈ 1.0-1.2
        """
        if reynolds_number < 1:
            return 10.0 / (reynolds_number + 0.1)
        elif reynolds_number < 100:
            # Transition region
            cd_low = 10.0 / reynolds_number
            cd_high = 1.1
            alpha = (reynolds_number - 1) / (100 - 1)
            alpha = np.clip(alpha, 0, 1)
            return cd_low * (1 - alpha) + cd_high * alpha
        else:
            # Turbulent flow
            return 1.1

