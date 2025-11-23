"""Box object for wind tunnel simulation."""

import numpy as np
from .base_object import BaseObject


class Box(BaseObject):
    """Box (rectangular prism) object with drag calculations."""
    
    def __init__(self, position, dimensions, material_properties=None):
        """
        Initialize a box.
        
        Args:
            position: Tuple (x, y, z) or (x, y) for center position
            dimensions: Tuple (width, height, depth) or (width, height) for 2D
            material_properties: Dict with material properties
        """
        super().__init__(position, dimensions, material_properties)
        self.dimensions = np.array(dimensions, dtype=float)
        if len(self.dimensions) == 2:
            # 2D box - add depth dimension
            self.dimensions = np.append(self.dimensions, 1.0)
    
    def get_surface_area(self):
        """Calculate surface area: 2(lw + lh + wh)"""
        w, h, d = self.dimensions
        return 2 * (w * h + w * d + h * d)
    
    def get_cross_sectional_area(self, flow_direction):
        """
        Calculate cross-sectional area perpendicular to flow.
        Returns the maximum projected area.
        """
        flow_direction = np.array(flow_direction)
        flow_direction = flow_direction / (np.linalg.norm(flow_direction) + 1e-10)
        
        w, h, d = self.dimensions
        
        # Calculate projected areas for each face
        # Face normals: ±x, ±y, ±z
        areas = []
        for normal, dims in [([1,0,0], (h, d)), ([0,1,0], (w, d)), ([0,0,1], (w, h))]:
            normal = np.array(normal)
            # Projected area = face_area * |cos(angle)|
            cos_angle = abs(np.dot(flow_direction, normal))
            face_area = dims[0] * dims[1]
            areas.append(face_area * cos_angle)
        
        # Return maximum projected area
        return max(areas) if areas else w * h
    
    def get_volume(self):
        """Calculate volume: width × height × depth"""
        return np.prod(self.dimensions)
    
    def contains_point(self, point):
        """Check if point is inside box."""
        point = np.array(point)
        rel_pos = point - self.position
        half_dims = self.dimensions / 2.0
        
        # Check if point is within bounds in all dimensions
        for i in range(min(len(rel_pos), len(half_dims))):
            if abs(rel_pos[i]) > half_dims[i]:
                return False
        return True
    
    def get_characteristic_length(self):
        """Characteristic length is the cube root of volume."""
        return np.cbrt(self.get_volume())
    
    def get_drag_coefficient(self, reynolds_number):
        """
        Get drag coefficient for box based on Reynolds number.
        
        Boxes have higher drag coefficients than streamlined shapes:
        - Re < 100: Transition region
        - Re > 100: Constant Cd ≈ 1.0-2.0 (depends on orientation)
        """
        if reynolds_number < 100:
            # Transition region
            return 2.0 / (reynolds_number / 100.0 + 0.1)
        else:
            # Turbulent flow - boxes have high drag
            return 1.2

