#!/usr/bin/env python3
"""
Minimal test script to verify the water rocket simulation works.
"""

import sys
import os

# Add the package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from waterrocketpy.core.simulation import WaterRocketSimulator
    from waterrocketpy.rocket.builder import RocketBuilder,create_standard_rocket
    from waterrocketpy.core.constants import ATMOSPHERIC_PRESSURE
    from waterrocketpy.visualization.flight_animation import animate_flight

    print("✓ All imports successful")

    # Create a simple rocket
    print("\n1. Creating standard rocket...")
    rocket = create_standard_rocket()
    
    print(f"   Rocket created: {rocket.name}")
    print(f"   Total mass: {rocket.total_mass:.3f} kg")

    # Convert to simulation parameters
    print("\n2. Converting to simulation parameters...")
    builder = RocketBuilder.from_dict(rocket.__dict__)
    sim_params = builder.to_simulation_params()
    print(f"   Parameters ready: {len(sim_params)} parameters")

    # Run simulation
    print("\n3. Running simulation...")
    simulator = WaterRocketSimulator()

    # Short simulation for testing
    sim_settings = {"max_time": 100.0, "time_step": 0.01, "solver": "RK45"}

    flight_data = simulator.simulate(sim_params, sim_settings)
    

    print(f"   ✓ Simulation completed successfully!")
    print(f"   Maximum altitude: {flight_data.max_altitude:.2f} m")
    print(f"   Maximum velocity: {flight_data.max_velocity:.2f} m/s")
    print(f"   Flight time: {flight_data.flight_time:.2f} s")
    print(f"   Data points: {len(flight_data.time)}")

    animate_flight(flight_data)
    print("\n✓ All tests passed! Your simulation is working correctly.")

except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you're running this from the correct directory.")
except Exception as e:
    print(f"✗ Error: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback

    traceback.print_exc()
