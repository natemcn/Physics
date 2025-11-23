"""Flow visualization utilities."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Ellipse


class FlowVisualizer:
    """Visualize flow patterns and pressure fields."""
    
    @staticmethod
    def plot_flow_field(ax, wind_tunnel, show_streamlines=True, show_pressure=True):
        """
        Plot flow field visualization.
        
        Args:
            ax: Matplotlib axes
            wind_tunnel: WindTunnel instance
            show_streamlines: Whether to show streamlines
            show_pressure: Whether to show pressure field
        """
        # Get grid coordinates
        x = np.linspace(0, wind_tunnel.width, wind_tunnel.grid_resolution[0])
        y = np.linspace(0, wind_tunnel.height, wind_tunnel.grid_resolution[1])
        # Use 'xy' indexing for matplotlib compatibility
        X, Y = np.meshgrid(x, y, indexing='xy')
        
        # Get velocity field
        velocity = wind_tunnel.get_velocity_field()
        # Velocity is in 'ij' indexing, transpose for 'xy' indexing
        u = velocity[0].T
        v = velocity[1].T
        
        # Plot pressure field as background
        if show_pressure:
            pressure = wind_tunnel.get_pressure_field()
            # Pressure is in 'ij' indexing, transpose for 'xy' indexing
            pressure_xy = pressure.T
            im = ax.contourf(X, Y, pressure_xy, levels=20, cmap='coolwarm', alpha=0.6)
            plt.colorbar(im, ax=ax, label='Pressure (Pa)')
        
        # Plot streamlines
        if show_streamlines:
            # Subsample for cleaner visualization
            skip = max(1, min(u.shape) // 20)
            
            # Subsample velocity arrays
            u_sub = u[::skip, ::skip]
            v_sub = v[::skip, ::skip]
            
            # Get the actual shape after subsampling
            n_y_sub, n_x_sub = u_sub.shape  # Note: 'xy' indexing means shape is (ny, nx)
            
            # Create coordinate arrays that match the subsampled velocity shape
            x_sub = np.linspace(0, wind_tunnel.width, n_x_sub)
            y_sub = np.linspace(0, wind_tunnel.height, n_y_sub)
            
            # Create meshgrid with 'xy' indexing which streamplot expects
            # This ensures X has constant rows and Y has constant columns
            X_sub, Y_sub = np.meshgrid(x_sub, y_sub, indexing='xy')
            
            # Verify shapes match
            if X_sub.shape == Y_sub.shape == u_sub.shape == v_sub.shape:
                ax.streamplot(
                    X_sub,
                    Y_sub,
                    u_sub,
                    v_sub,
                    density=1.5,
                    color='black',
                    linewidth=0.5,
                    arrowsize=0.5
                )
            else:
                # Fallback: use original arrays without subsampling
                ax.streamplot(
                    X,
                    Y,
                    u,
                    v,
                    density=1.5,
                    color='black',
                    linewidth=0.5,
                    arrowsize=0.5
                )
        
        # Plot velocity magnitude as quiver (optional, can be slow)
        # Uncomment for vector field visualization
        # skip = max(1, min(u.shape) // 15)
        # ax.quiver(
        #     X[::skip, ::skip],
        #     Y[::skip, ::skip],
        #     u[::skip, ::skip],
        #     v[::skip, ::skip],
        #     scale=50,
        #     width=0.002
        # )
    
    @staticmethod
    def plot_objects(ax, wind_tunnel):
        """
        Plot objects in the wind tunnel.
        
        Args:
            ax: Matplotlib axes
            wind_tunnel: WindTunnel instance
        """
        for obj in wind_tunnel.objects:
            pos = obj.get_position()
            x, y = pos[0], pos[1]
            
            if hasattr(obj, 'radius'):
                # Sphere or Cylinder (shown as circle in 2D)
                circle = Circle((x, y), obj.radius, fill=True, color='red', alpha=0.7, edgecolor='black')
                ax.add_patch(circle)
            elif hasattr(obj, 'dimensions'):
                # Box
                w, h = obj.dimensions[0], obj.dimensions[1]
                rect = Rectangle(
                    (x - w/2, y - h/2),
                    w, h,
                    fill=True, color='blue', alpha=0.7, edgecolor='black'
                )
                ax.add_patch(rect)
    
    @staticmethod
    def plot_drag_vectors(ax, wind_tunnel, drag_results):
        """
        Plot drag force vectors on objects.
        
        Args:
            ax: Matplotlib axes
            wind_tunnel: WindTunnel instance
            drag_results: Dictionary of drag calculation results
        """
        scale = 0.1  # Scale factor for force vectors
        
        for obj, results in drag_results.items():
            pos = obj.get_position()
            drag_force = results['drag_force']
            
            # Draw force vector
            x, y = pos[0], pos[1]
            dx, dy = drag_force[0] * scale, drag_force[1] * scale
            
            ax.arrow(x, y, dx, dy, head_width=0.1, head_length=0.1,
                    fc='green', ec='green', linewidth=2, alpha=0.8)

