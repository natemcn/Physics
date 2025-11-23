"""Main entry point for Wind Tunnel Drag Simulator."""

import tkinter as tk
from physics.wind_tunnel import WindTunnel
from physics.drag_calculator import DragCalculator
from gui.main_window import MainWindow


def main():
    """Main function to start the application."""
    # Create wind tunnel
    wind_tunnel = WindTunnel(
        width=10.0,
        height=5.0,
        grid_resolution=(100, 50),
        wind_speed=10.0,
        density=1.225,  # Air density at sea level
        viscosity=1.5e-5  # Kinematic viscosity of air
    )
    
    # Create drag calculator
    drag_calculator = DragCalculator(wind_tunnel)
    
    # Create GUI
    root = tk.Tk()
    app = MainWindow(root, wind_tunnel, drag_calculator)
    
    # Start application
    app.run()


if __name__ == "__main__":
    main()

