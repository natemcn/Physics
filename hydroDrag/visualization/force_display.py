"""Force display utilities."""

import numpy as np


class ForceDisplay:
    """Display drag forces and metrics."""
    
    @staticmethod
    def format_force(force_magnitude):
        """Format force value for display."""
        if force_magnitude < 1e-6:
            return "0.0 N"
        elif force_magnitude < 1e-3:
            return f"{force_magnitude * 1e6:.2f} μN"
        elif force_magnitude < 1:
            return f"{force_magnitude * 1e3:.2f} mN"
        else:
            return f"{force_magnitude:.4f} N"
    
    @staticmethod
    def format_reynolds(reynolds_number):
        """Format Reynolds number for display."""
        if reynolds_number < 1:
            return f"{reynolds_number:.4f}"
        elif reynolds_number < 1000:
            return f"{reynolds_number:.2f}"
        else:
            return f"{reynolds_number:.2e}"
    
    @staticmethod
    def get_summary(drag_results):
        """
        Get summary statistics from drag results.
        
        Args:
            drag_results: Dictionary of drag calculation results
            
        Returns:
            Dictionary with summary statistics
        """
        if not drag_results:
            return {
                'total_drag': 0.0,
                'num_objects': 0,
                'avg_drag': 0.0,
                'max_drag': 0.0
            }
        
        forces = [r['drag_magnitude'] for r in drag_results.values()]
        
        return {
            'total_drag': sum(forces),
            'num_objects': len(forces),
            'avg_drag': np.mean(forces),
            'max_drag': np.max(forces),
            'min_drag': np.min(forces)
        }

