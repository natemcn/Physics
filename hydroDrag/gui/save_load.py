"""Save and load functionality for wind tunnel simulations."""

import json
from objects.sphere import Sphere
from objects.cylinder import Cylinder
from objects.box import Box
import numpy as np


class SimulationSerializer:
    """Serialize and deserialize wind tunnel simulations."""
    
    @staticmethod
    def save_simulation(wind_tunnel, filename):
        """
        Save simulation state to file.
        
        Args:
            wind_tunnel: WindTunnel instance
            filename: Output filename
        """
        data = {
            'width': wind_tunnel.width,
            'height': wind_tunnel.height,
            'grid_resolution': wind_tunnel.grid_resolution,
            'wind_speed': wind_tunnel.wind_speed,
            'density': wind_tunnel.density,
            'viscosity': wind_tunnel.viscosity,
            'objects': []
        }
        
        # Serialize objects
        for obj in wind_tunnel.objects:
            obj_data = {
                'type': type(obj).__name__,
                'position': obj.get_position().tolist(),
                'material_properties': obj.material_properties
            }
            
            if isinstance(obj, Sphere):
                obj_data['radius'] = obj.radius
            elif isinstance(obj, Cylinder):
                obj_data['radius'] = obj.radius
                obj_data['height'] = obj.height
                obj_data['axis'] = obj.axis
            elif isinstance(obj, Box):
                obj_data['dimensions'] = obj.dimensions.tolist()
            
            data['objects'].append(obj_data)
        
        # Save as JSON
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def load_simulation(wind_tunnel, filename):
        """
        Load simulation state from file.
        
        Args:
            wind_tunnel: WindTunnel instance to populate
            filename: Input filename
        """
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Update wind tunnel properties
        wind_tunnel.width = data['width']
        wind_tunnel.height = data['height']
        wind_tunnel.grid_resolution = tuple(data['grid_resolution'])
        wind_tunnel.wind_speed = data['wind_speed']
        wind_tunnel.density = data['density']
        wind_tunnel.viscosity = data['viscosity']
        
        # Recreate simulator with new properties
        from physics.fluid_simulator import FluidSimulator
        wind_tunnel.simulator = FluidSimulator(
            grid_size=wind_tunnel.grid_resolution,
            domain_size=(wind_tunnel.width, wind_tunnel.height),
            viscosity=wind_tunnel.viscosity,
            density=wind_tunnel.density
        )
        wind_tunnel.simulator.set_inflow_velocity([wind_tunnel.wind_speed, 0.0])
        
        # Clear existing objects
        wind_tunnel.clear_objects()
        
        # Recreate objects
        for obj_data in data['objects']:
            obj_type = obj_data['type']
            position = np.array(obj_data['position'])
            material_props = obj_data.get('material_properties', {})
            
            if obj_type == 'Sphere':
                obj = Sphere(position, obj_data['radius'], material_props)
            elif obj_type == 'Cylinder':
                obj = Cylinder(
                    position,
                    obj_data['radius'],
                    obj_data['height'],
                    obj_data.get('axis', 'z'),
                    material_props
                )
            elif obj_type == 'Box':
                obj = Box(position, obj_data['dimensions'], material_props)
            else:
                continue
            
            wind_tunnel.add_object(obj)
        
        # Reset simulation
        wind_tunnel.reset()

