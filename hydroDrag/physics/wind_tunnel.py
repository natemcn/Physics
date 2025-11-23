"""Wind tunnel environment with boundary conditions and flow management."""

import numpy as np
from .fluid_simulator import FluidSimulator


class WindTunnel:
    """Wind tunnel environment that manages fluid simulation and objects."""
    
    def __init__(self, width=10.0, height=5.0, grid_resolution=(100, 50),
                 wind_speed=10.0, density=1.225, viscosity=1.5e-5):
        """
        Initialize wind tunnel.
        
        Args:
            width: Tunnel width in meters (x-direction)
            height: Tunnel height in meters (y-direction)
            grid_resolution: (nx, ny) grid resolution
            wind_speed: Inflow wind speed in m/s
            density: Air density in kg/m³ (default: 1.225 at sea level)
            viscosity: Kinematic viscosity in m²/s (default: 1.5e-5 for air)
        """
        self.width = width
        self.height = height
        self.grid_resolution = grid_resolution
        self.wind_speed = wind_speed
        self.density = density
        self.viscosity = viscosity
        
        # Initialize fluid simulator
        self.simulator = FluidSimulator(
            grid_size=grid_resolution,
            domain_size=(width, height),
            viscosity=viscosity,
            density=density
        )
        
        # Set inflow velocity
        self.simulator.set_inflow_velocity([wind_speed, 0.0])
        
        # List of objects in the tunnel
        self.objects = []
        
        # Simulation state
        self.is_running = False
        self.time = 0.0
    
    def add_object(self, obj):
        """Add an object to the wind tunnel."""
        self.objects.append(obj)
        self._update_obstacle_mask()
    
    def remove_object(self, obj):
        """Remove an object from the wind tunnel."""
        if obj in self.objects:
            self.objects.remove(obj)
            self._update_obstacle_mask()
    
    def clear_objects(self):
        """Remove all objects from the wind tunnel."""
        self.objects = []
        self.simulator.clear_obstacles()
    
    def _update_obstacle_mask(self):
        """Update the obstacle mask in the simulator based on objects."""
        self.simulator.clear_obstacles()
        
        for obj in self.objects:
            mask = self._create_obstacle_mask(obj)
            self.simulator.add_obstacle(mask)
    
    def _create_obstacle_mask(self, obj):
        """Create a grid mask for an object."""
        mask = np.zeros(self.grid_resolution, dtype=bool)
        
        # Create coordinate grids
        x = np.linspace(0, self.width, self.grid_resolution[0])
        y = np.linspace(0, self.height, self.grid_resolution[1])
        X, Y = np.meshgrid(x, y, indexing='ij')
        
        # Check each grid point
        for i in range(self.grid_resolution[0]):
            for j in range(self.grid_resolution[1]):
                point = np.array([X[i, j], Y[i, j]])
                if obj.contains_point(point):
                    mask[i, j] = True
        
        return mask
    
    def set_wind_speed(self, speed):
        """Set the wind speed at the inlet."""
        self.wind_speed = speed
        self.simulator.set_inflow_velocity([speed, 0.0])
    
    def set_density(self, density):
        """Set the fluid density."""
        self.density = density
        self.simulator.density = density
    
    def set_viscosity(self, viscosity):
        """Set the kinematic viscosity."""
        self.viscosity = viscosity
        self.simulator.viscosity = viscosity
    
    def step(self, dt=None):
        """
        Advance simulation by one time step.
        
        Args:
            dt: Time step (uses simulator's default if None)
        """
        if dt is not None:
            self.simulator.dt = dt
        
        # Update obstacle mask if objects changed
        self._update_obstacle_mask()
        
        # Step fluid simulation
        self.simulator.step()
        
        # Update time
        self.time += self.simulator.dt
    
    def get_flow_velocity(self, position):
        """
        Get flow velocity at a position.
        
        Args:
            position: (x, y) coordinates in world space
        """
        return self.simulator.get_velocity_at(position)
    
    def get_pressure(self, position):
        """
        Get pressure at a position.
        
        Args:
            position: (x, y) coordinates in world space
        """
        return self.simulator.get_pressure_at(position)
    
    def get_velocity_field(self):
        """Get the entire velocity field."""
        return self.simulator.velocity
    
    def get_pressure_field(self):
        """Get the entire pressure field."""
        return self.simulator.pressure
    
    def get_obstacle_mask(self):
        """Get the obstacle mask."""
        return self.simulator.obstacle_mask
    
    def reset(self):
        """Reset the simulation to initial state."""
        self.simulator = FluidSimulator(
            grid_size=self.grid_resolution,
            domain_size=(self.width, self.height),
            viscosity=self.viscosity,
            density=self.density
        )
        self.simulator.set_inflow_velocity([self.wind_speed, 0.0])
        self._update_obstacle_mask()
        self.time = 0.0

