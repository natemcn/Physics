"""Grid-based fluid dynamics simulator using simplified Navier-Stokes equations."""

import numpy as np
from scipy import ndimage


class FluidSimulator:
    """2D/3D fluid dynamics simulator using finite difference method."""
    
    def __init__(self, grid_size, domain_size, viscosity=0.01, density=1.0):
        """
        Initialize fluid simulator.
        
        Args:
            grid_size: Tuple (nx, ny) or (nx, ny, nz) for grid resolution
            domain_size: Tuple (lx, ly) or (lx, ly, lz) for domain size
            viscosity: Kinematic viscosity (default: 0.01)
            density: Fluid density (default: 1.0 kg/m³)
        """
        self.grid_size = np.array(grid_size, dtype=int)
        self.domain_size = np.array(domain_size, dtype=float)
        self.viscosity = viscosity
        self.density = density
        self.dim = len(grid_size)
        
        # Grid spacing
        self.dx = self.domain_size / self.grid_size
        
        # Velocity field (u, v) for 2D or (u, v, w) for 3D
        if self.dim == 2:
            self.u = np.zeros(grid_size)
            self.v = np.zeros(grid_size)
            self.velocity = np.zeros((2, *grid_size))
        else:
            self.u = np.zeros(grid_size)
            self.v = np.zeros(grid_size)
            self.w = np.zeros(grid_size)
            self.velocity = np.zeros((3, *grid_size))
        
        # Pressure field
        self.pressure = np.zeros(grid_size)
        
        # Obstacle mask (True where objects are)
        self.obstacle_mask = np.zeros(grid_size, dtype=bool)
        
        # Time step (adaptive based on CFL condition)
        self.dt = 0.01
    
    def add_obstacle(self, obstacle_mask):
        """Add obstacle to the simulation domain."""
        self.obstacle_mask = np.logical_or(self.obstacle_mask, obstacle_mask)
    
    def clear_obstacles(self):
        """Clear all obstacles."""
        self.obstacle_mask = np.zeros(self.grid_size, dtype=bool)
    
    def set_inflow_velocity(self, velocity):
        """
        Set inflow velocity at boundaries.
        
        Args:
            velocity: Velocity vector (u, v) or (u, v, w)
        """
        velocity = np.array(velocity)
        if self.dim == 2:
            # Set velocity at left boundary (inflow)
            self.u[0, :] = velocity[0]
            self.v[0, :] = velocity[1]
        else:
            self.u[0, :, :] = velocity[0]
            self.v[0, :, :] = velocity[1]
            self.w[0, :, :] = velocity[2]
    
    def world_to_grid(self, world_pos):
        """Convert world coordinates to grid indices."""
        grid_pos = (world_pos / self.dx).astype(int)
        # Clamp to grid bounds
        for i in range(self.dim):
            grid_pos[i] = np.clip(grid_pos[i], 0, self.grid_size[i] - 1)
        return grid_pos
    
    def grid_to_world(self, grid_pos):
        """Convert grid indices to world coordinates."""
        return grid_pos * self.dx
    
    def compute_pressure(self, max_iter=50, tolerance=1e-6):
        """
        Solve pressure Poisson equation using Jacobi iteration.
        ∇²p = -ρ∇·(u·∇u)
        """
        # Compute divergence of velocity
        if self.dim == 2:
            du_dx = np.gradient(self.u, self.dx[0], axis=0)
            dv_dy = np.gradient(self.v, self.dx[1], axis=1)
            divergence = du_dx + dv_dy
        else:
            du_dx = np.gradient(self.u, self.dx[0], axis=0)
            dv_dy = np.gradient(self.v, self.dx[1], axis=1)
            dw_dz = np.gradient(self.w, self.dx[2], axis=2)
            divergence = du_dx + dv_dy + dw_dz
        
        # Source term
        rhs = -self.density * divergence / self.dt
        
        # Apply boundary conditions: zero pressure gradient at boundaries
        p_new = self.pressure.copy()
        
        for _ in range(max_iter):
            p_old = p_new.copy()
            
            # Jacobi iteration for Poisson equation
            if self.dim == 2:
                # 5-point stencil
                p_new[1:-1, 1:-1] = 0.25 * (
                    p_old[2:, 1:-1] + p_old[:-2, 1:-1] +
                    p_old[1:-1, 2:] + p_old[1:-1, :-2] -
                    self.dx[0] * self.dx[1] * rhs[1:-1, 1:-1]
                )
            else:
                # 7-point stencil
                p_new[1:-1, 1:-1, 1:-1] = (1.0/6.0) * (
                    p_old[2:, 1:-1, 1:-1] + p_old[:-2, 1:-1, 1:-1] +
                    p_old[1:-1, 2:, 1:-1] + p_old[1:-1, :-2, 1:-1] +
                    p_old[1:-1, 1:-1, 2:] + p_old[1:-1, 1:-1, :-2] -
                    self.dx[0] * self.dx[1] * self.dx[2] * rhs[1:-1, 1:-1, 1:-1]
                )
            
            # Apply obstacle boundary conditions (zero velocity inside obstacles)
            p_new[self.obstacle_mask] = 0
            
            # Check convergence
            if np.max(np.abs(p_new - p_old)) < tolerance:
                break
        
        self.pressure = p_new
    
    def advect(self, field, velocity_field):
        """
        Advect a field using the velocity field.
        Uses simple upwind differencing for stability.
        """
        if self.dim == 2:
            u, v = velocity_field
            advected = field.copy()
            
            # Upwind differencing for advection
            # For u > 0, use backward difference; for u < 0, use forward difference
            u_forward = np.roll(field, -1, axis=0)
            u_backward = np.roll(field, 1, axis=0)
            v_forward = np.roll(field, -1, axis=1)
            v_backward = np.roll(field, 1, axis=1)
            
            # Advection term: -u·∇field
            du_dx = np.where(u > 0, 
                            (field - u_backward) / self.dx[0],
                            (u_forward - field) / self.dx[0])
            dv_dy = np.where(v > 0,
                            (field - v_backward) / self.dx[1],
                            (v_forward - field) / self.dx[1])
            
            advected -= self.dt * (u * du_dx + v * dv_dy)
            
            # Handle boundaries
            advected[0, :] = field[0, :]  # Inflow boundary
            advected[-1, :] = field[-1, :]  # Outflow boundary
            advected[:, 0] = field[:, 0]  # Top boundary
            advected[:, -1] = field[:, -1]  # Bottom boundary
            
            return advected
        else:
            # 3D advection (simplified)
            return field  # Placeholder for 3D
    
    def apply_viscosity(self):
        """Apply viscous diffusion term."""
        if self.dim == 2:
            # Laplacian of velocity
            laplacian_u = ndimage.laplace(self.u) / (self.dx[0] ** 2)
            laplacian_v = ndimage.laplace(self.v) / (self.dx[1] ** 2)
            
            self.u += self.viscosity * self.dt * laplacian_u
            self.v += self.viscosity * self.dt * laplacian_v
        else:
            laplacian_u = ndimage.laplace(self.u) / (self.dx[0] ** 2)
            laplacian_v = ndimage.laplace(self.v) / (self.dx[1] ** 2)
            laplacian_w = ndimage.laplace(self.w) / (self.dx[2] ** 2)
            
            self.u += self.viscosity * self.dt * laplacian_u
            self.v += self.viscosity * self.dt * laplacian_v
            self.w += self.viscosity * self.dt * laplacian_w
    
    def apply_pressure_gradient(self):
        """Apply pressure gradient to velocity field."""
        if self.dim == 2:
            grad_p_x = np.gradient(self.pressure, self.dx[0], axis=0)
            grad_p_y = np.gradient(self.pressure, self.dx[1], axis=1)
            
            self.u -= (self.dt / self.density) * grad_p_x
            self.v -= (self.dt / self.density) * grad_p_y
        else:
            grad_p_x = np.gradient(self.pressure, self.dx[0], axis=0)
            grad_p_y = np.gradient(self.pressure, self.dx[1], axis=1)
            grad_p_z = np.gradient(self.pressure, self.dx[2], axis=2)
            
            self.u -= (self.dt / self.density) * grad_p_x
            self.v -= (self.dt / self.density) * grad_p_y
            self.w -= (self.dt / self.density) * grad_p_z
    
    def enforce_boundary_conditions(self):
        """Enforce boundary conditions on velocity field."""
        # No-slip at obstacles
        if self.dim == 2:
            self.u[self.obstacle_mask] = 0
            self.v[self.obstacle_mask] = 0
        else:
            self.u[self.obstacle_mask] = 0
            self.v[self.obstacle_mask] = 0
            self.w[self.obstacle_mask] = 0
        
        # Inflow at left boundary
        if self.dim == 2:
            # Keep inflow velocity (set in set_inflow_velocity)
            pass
        else:
            pass
    
    def step(self):
        """Perform one time step of the simulation."""
        # 1. Advect velocity
        if self.dim == 2:
            self.u = self.advect(self.u, (self.u, self.v))
            self.v = self.advect(self.v, (self.u, self.v))
        else:
            # Simplified for 3D
            pass
        
        # 2. Apply viscosity
        self.apply_viscosity()
        
        # 3. Compute pressure
        self.compute_pressure()
        
        # 4. Apply pressure gradient
        self.apply_pressure_gradient()
        
        # 5. Enforce boundary conditions
        self.enforce_boundary_conditions()
        
        # Update velocity field array
        if self.dim == 2:
            self.velocity[0] = self.u
            self.velocity[1] = self.v
        else:
            self.velocity[0] = self.u
            self.velocity[1] = self.v
            self.velocity[2] = self.w
    
    def get_velocity_at(self, position):
        """
        Get velocity at a specific world position using interpolation.
        
        Args:
            position: World coordinates (x, y) or (x, y, z)
        """
        grid_pos = self.world_to_grid(position)
        if self.dim == 2:
            # Simple nearest neighbor for now
            i, j = grid_pos
            i = np.clip(i, 0, self.grid_size[0] - 1)
            j = np.clip(j, 0, self.grid_size[1] - 1)
            return np.array([self.u[i, j], self.v[i, j]])
        else:
            i, j, k = grid_pos
            i = np.clip(i, 0, self.grid_size[0] - 1)
            j = np.clip(j, 0, self.grid_size[1] - 1)
            k = np.clip(k, 0, self.grid_size[2] - 1)
            return np.array([self.u[i, j, k], self.v[i, j, k], self.w[i, j, k]])
    
    def get_pressure_at(self, position):
        """Get pressure at a specific world position."""
        grid_pos = self.world_to_grid(position)
        if self.dim == 2:
            i, j = grid_pos
            i = np.clip(i, 0, self.grid_size[0] - 1)
            j = np.clip(j, 0, self.grid_size[1] - 1)
            return self.pressure[i, j]
        else:
            i, j, k = grid_pos
            i = np.clip(i, 0, self.grid_size[0] - 1)
            j = np.clip(j, 0, self.grid_size[1] - 1)
            k = np.clip(k, 0, self.grid_size[2] - 1)
            return self.pressure[i, j, k]

