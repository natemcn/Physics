"""Base class for all objects in the wind tunnel simulation."""

from abc import ABC, abstractmethod
import numpy as np


class BaseObject(ABC):
    """Abstract base class for all objects in the wind tunnel."""
    
    def __init__(self, position, size, material_properties=None):
        """
        Initialize a base object.
        
        Args:
            position: Tuple (x, y, z) or (x, y) for 2D position
            size: Size parameters (shape-dependent)
            material_properties: Dict with properties like density, roughness, etc.
        """
        self.position = np.array(position, dtype=float)
        self.size = size
        self.material_properties = material_properties or {}
        self.drag_force = np.array([0.0, 0.0, 0.0])
        self.drag_coefficient = 0.0
        
    @abstractmethod
    def get_surface_area(self):
        """Calculate the surface area of the object."""
        pass
    
    @abstractmethod
    def get_cross_sectional_area(self, flow_direction):
        """
        Calculate the cross-sectional area perpendicular to flow direction.
        
        Args:
            flow_direction: Normalized flow direction vector
        """
        pass
    
    @abstractmethod
    def get_volume(self):
        """Calculate the volume of the object."""
        pass
    
    @abstractmethod
    def contains_point(self, point):
        """
        Check if a point is inside the object.
        
        Args:
            point: Point coordinates (x, y, z) or (x, y)
        """
        pass
    
    @abstractmethod
    def get_drag_coefficient(self, reynolds_number):
        """
        Get drag coefficient based on Reynolds number.
        
        Args:
            reynolds_number: Reynolds number for the flow
        """
        pass
    
    def get_characteristic_length(self):
        """Get characteristic length for Reynolds number calculation."""
        # Default: use largest dimension
        if isinstance(self.size, (int, float)):
            return self.size
        elif isinstance(self.size, (list, tuple, np.ndarray)):
            return max(self.size)
        return 1.0
    
    def update_drag_force(self, drag_force):
        """Update the drag force acting on the object."""
        self.drag_force = np.array(drag_force)
    
    def get_position(self):
        """Get the position of the object."""
        return self.position.copy()
    
    def set_position(self, position):
        """Set the position of the object."""
        self.position = np.array(position, dtype=float)

