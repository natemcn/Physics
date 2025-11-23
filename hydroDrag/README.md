# Wind Tunnel Drag Simulator

A Python application for simulating drag and wind resistance in a wind tunnel environment. Add objects to the tunnel and visualize flow patterns and drag forces in real-time using advanced fluid dynamics calculations.

## Features

- **Interactive GUI**: User-friendly interface built with tkinter
- **Advanced Fluid Dynamics**: Grid-based Navier-Stokes solver for realistic flow simulation
- **Real-time Visualization**: 
  - Flow streamlines
  - Pressure field visualization
  - Drag force vectors
  - Object rendering
- **Drag Force Calculations**:
  - Pressure-based drag from CFD simulation
  - Viscous drag calculations
  - Reynolds number-dependent drag coefficients
  - Real-time force display
- **Object Support**: 
  - Spheres
  - Cylinders (with configurable orientation)
  - Boxes (rectangular prisms)
- **Simulation Controls**:
  - Adjustable wind speed (0-50 m/s)
  - Configurable fluid density
  - Start/stop/step simulation
  - Reset functionality
- **Save/Load**: Save and load simulation configurations

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python main.py
```

## Usage

### Basic Operations

1. **Add Objects**: Click "Add Sphere", "Add Cylinder", or "Add Box" to place objects in the wind tunnel
2. **Configure Objects**: Double-click an object in the list to edit its position and size
3. **Adjust Wind Properties**: Use the sliders to change wind speed and air density
4. **Run Simulation**: 
   - Use "Start" from the Simulation menu to run continuously
   - Use "Step" to advance one time step
   - Use "Stop" to pause the simulation
5. **View Results**: Drag forces, Reynolds numbers, and drag coefficients are displayed in the control panel

### Advanced Features

- **Save/Load**: Use File menu to save and load simulation configurations
- **Object Properties**: Edit object properties by double-clicking in the object list
- **Visualization**: The main canvas shows:
  - Pressure field (color-coded)
  - Flow streamlines (black lines)
  - Objects (colored shapes)
  - Drag force vectors (green arrows)

## Physics

The simulator uses:
- **Navier-Stokes equations** for fluid flow
- **Finite difference method** on a regular grid
- **Pressure-based drag** from pressure distribution around objects
- **Viscous drag** from velocity gradients
- **Reynolds number** calculations for flow regime determination
- **Empirical drag coefficients** based on Reynolds number and object shape

## Requirements

- Python 3.8+
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- scipy >= 1.10.0

## Project Structure

```
hydroDrag/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── physics/               # Physics simulation modules
│   ├── fluid_simulator.py # Navier-Stokes solver
│   ├── drag_calculator.py # Drag force calculations
│   └── wind_tunnel.py     # Wind tunnel environment
├── objects/               # Object classes
│   ├── base_object.py     # Base class for objects
│   ├── sphere.py          # Sphere implementation
│   ├── cylinder.py        # Cylinder implementation
│   └── box.py             # Box implementation
├── gui/                   # GUI components
│   ├── main_window.py     # Main application window
│   ├── canvas_widget.py   # Visualization canvas
│   ├── control_panel.py   # Control panel widget
│   ├── object_properties.py # Object properties dialog
│   └── save_load.py       # Save/load functionality
└── visualization/         # Visualization utilities
    ├── flow_visualizer.py # Flow field visualization
    └── force_display.py   # Force display utilities
```

