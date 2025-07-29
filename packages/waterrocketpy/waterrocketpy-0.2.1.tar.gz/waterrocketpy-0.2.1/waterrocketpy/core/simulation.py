# waterrocketpy/core/simulation.py
"""
Main simulation engine for water rocket flight.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d
from typing import Dict, Any, Tuple, NamedTuple
from dataclasses import dataclass

from .physics_engine import PhysicsEngine
from .validation import ParameterValidator
from .constants import (
    WATER_DENSITY,
    DEFAULT_TIME_STEP,
    DEFAULT_MAX_TIME,
    DEFAULT_SOLVER,
    INITIAL_TEMPERATURE,
    ATMOSPHERIC_PRESSURE,
    ADIABATIC_INDEX_AIR,
)
import warnings
# warnings.filterwarnings('error')  # Convert all warnings to exceptions debugging



@dataclass
class FlightData:
    """Container for flight simulation results."""

    time: np.ndarray
    altitude: np.ndarray
    velocity: np.ndarray
    acceleration: np.ndarray
    water_mass: np.ndarray
    liquid_gas_mass: np.ndarray
    air_mass: np.ndarray
    pressure: np.ndarray
    air_temperature: np.ndarray
    thrust: np.ndarray
    drag: np.ndarray

    water_exhaust_speed: np.ndarray
    air_exhaust_speed: np.ndarray
    water_mass_flow_rate: np.ndarray
    air_mass_flow_rate: np.ndarray
    air_exit_pressure: np.ndarray
    air_exit_temperature: np.ndarray

    max_altitude: float
    max_velocity: float
    flight_time: float
    water_depletion_time: float
    air_depletion_time: float


class WaterRocketSimulator:
    """Main simulation class for water rocket flight."""

    def __init__(self, physics_engine: PhysicsEngine = None, verbose: bool = True):
        self.physics_engine = physics_engine or PhysicsEngine()
        self.validator = ParameterValidator()
        self.verbose = verbose  # Enable verbose output for debugging

        # Storage for derived quantities during integration
        self.derived_data = {
            "time": [],
            "pressure": [],
            "temperature": [],
            "thrust": [],
            "drag": [],
            "water_exhaust_speed": [],
            "air_exhaust_speed": [],
            "water_mass_flow_rate": [],
            "air_mass_flow_rate": [],
            "air_exit_pressure": [],
            "air_exit_temperature": [],
        }

    def _store_derived_quantities(
        self,
        t,
        pressure,
        temperature,
        thrust,
        drag,
        water_exhaust_speed=None,
        air_exhaust_speed=None,
        water_mass_flow_rate=None,
        air_mass_flow_rate=None,
        air_exit_pressure=None,
        air_exit_temperature=None,
    ):
        self.derived_data["time"].append(t)
        self.derived_data["pressure"].append(pressure)
        self.derived_data["temperature"].append(temperature)
        self.derived_data["thrust"].append(thrust)
        self.derived_data["drag"].append(drag)
        self.derived_data["water_exhaust_speed"].append(water_exhaust_speed)
        self.derived_data["air_exhaust_speed"].append(air_exhaust_speed)
        self.derived_data["water_mass_flow_rate"].append(water_mass_flow_rate)
        self.derived_data["air_mass_flow_rate"].append(air_mass_flow_rate)
        self.derived_data["air_exit_pressure"].append(air_exit_pressure)
        self.derived_data["air_exit_temperature"].append(air_exit_temperature)

    def _rocket_ode_water_phase(
        self, t: float, state: np.ndarray, params: Dict[str, Any]
    ) -> np.ndarray:
        """
        ODE system for rocket dynamics during water expulsion phase.

        Args:
            t: Current time
            state: [altitude, velocity, water_mass, liquid_gas_mass]
            params: Rocket parameters

        Returns:
            Derivatives [velocity, acceleration, dm_water/dt, dm_gas/dt]
        """
        altitude, velocity, water_mass, liquid_gas_mass = state

        # Calculate current air volume
        air_volume = self.physics_engine.calculate_air_volume(
            params["V_bottle"], water_mass
        )

        # Calculate pressure and temperature
        if water_mass > 0 and liquid_gas_mass > 0:
            # Pressure from vaporizing liquid gas (constant while liquid
            # remains)
            pressure = 10e5  # 10 bar in Pa
            air_temperature = INITIAL_TEMPERATURE
            dm_dt_liquid_gas = (
                0  # Simplified: no vaporization rate calculation
            )
        else:
            dm_dt_liquid_gas = 0
            if water_mass > 0 or True:
                # Adiabatic expansion
                initial_air_volume = params["V_bottle"] * (
                    1 - params["water_fraction"]
                )
                pressure = self.physics_engine.calculate_pressure_adiabatic(
                    params["P0"], initial_air_volume, air_volume
                )
                air_temperature = (
                    self.physics_engine.calculate_temperature_adiabatic(
                        INITIAL_TEMPERATURE, params["P0"], pressure
                    )
                )
            else:  # NO, bad. should not happen
                pressure = ATMOSPHERIC_PRESSURE
                air_temperature = INITIAL_TEMPERATURE

        # Calculate thrust and mass flow rate
        if water_mass > 0:
            thrust, exit_water_velocity, mass_flow_rate = (
                self.physics_engine.calculate_water_thrust(
                    pressure, params["A_nozzle"], params["C_d"]
                )
            )
            dm_dt_water = -mass_flow_rate
        else:
            thrust = 0
            dm_dt_water = 0
            exit_water_velocity = None
            mass_flow_rate = None

        # Calculate drag
        drag = self.physics_engine.calculate_drag(
            velocity, params["C_drag"], params["A_rocket"]
        )

        # Store derived quantities
        self._store_derived_quantities(
            t,
            pressure,
            air_temperature,
            thrust,
            drag,
            water_exhaust_speed=exit_water_velocity,
            water_mass_flow_rate=mass_flow_rate,
        )

        # Calculate acceleration
        total_mass = params["m_empty"] + water_mass
        _, acceleration = self.physics_engine.calculate_net_force(
            thrust, drag, total_mass
        )

        return np.array(
            [velocity, acceleration, dm_dt_water, dm_dt_liquid_gas]
        )

    def _rocket_ode_air_phase(
        self, t: float, state: np.ndarray, params: Dict[str, Any]
    ) -> np.ndarray:
        """
        ODE system for rocket dynamics during air expulsion phase.

        Args:
            t: Current time
            state: [altitude, velocity, air_mass, temperature]
            params: Rocket parameters

        Returns:
            Derivatives [velocity, acceleration, dm_air/dt, dT/dt]
        """
        altitude, velocity, air_mass, air_temperature = state

        if air_mass <= 0:
            # Store zero values for derived quantities
            self._store_derived_quantities(
                t, ATMOSPHERIC_PRESSURE, air_temperature, 0, 0
            )
            return np.array([velocity, -self.physics_engine.gravity, 0, 0])

        # Calculate current air volume and pressure
        air_volume = params["V_bottle"]  # All bottle volume is now air

        # Calculate pressure from ideal gas law: P = mRT/V
        pressure = (
            air_mass
            * self.physics_engine.air_gas_constant
            * air_temperature
            / air_volume
        )

        # Ensure pressure doesn't go below atmospheric
        pressure = max(pressure, ATMOSPHERIC_PRESSURE)

        # Calculate air thrust and mass flow rate
        if pressure > ATMOSPHERIC_PRESSURE:
            (
                thrust,
                exit_air_velocity,
                mass_flow_rate,
                air_exit_pressure,
                air_exit_temperature,
            ) = self.physics_engine.calculate_air_thrust(
                pressure, air_temperature, params["A_nozzle"], params["C_d"]
            )
            dm_dt_air = -mass_flow_rate

            # Recommended (correct):
            if air_mass > 0:
                dT_dt = air_temperature * (ADIABATIC_INDEX_AIR - 1) / air_mass * dm_dt_air
            else:
                dT_dt = 0
                
        else:
            thrust = 0
            dm_dt_air = 0
            dT_dt = 0
            exit_air_velocity = None
            mass_flow_rate = None
            air_exit_pressure = None
            air_exit_temperature = None

        # Calculate drag
        drag = self.physics_engine.calculate_drag(
            velocity, params["C_drag"], params["A_rocket"]
        )

        # Store derived quantities
        self._store_derived_quantities(
            t,
            pressure,
            air_temperature,
            thrust,
            drag,
            air_exhaust_speed=exit_air_velocity,
            air_mass_flow_rate=mass_flow_rate,
            air_exit_pressure=air_exit_pressure,
            air_exit_temperature=air_exit_temperature,
        )

        # Calculate acceleration
        total_mass = params["m_empty"] + air_mass
        _, acceleration = self.physics_engine.calculate_net_force(
            thrust, drag, total_mass
        )

        return np.array([velocity, acceleration, dm_dt_air, dT_dt])

    def _rocket_ode_coasting_phase(
        self,
        t: float,
        state: np.ndarray,
        params: Dict[str, Any],
        final_air_pressure,
        final_air_temperature,
    ) -> np.ndarray:
        """
        ODE system for rocket dynamics during coasting phase.

        Args:
            t: Current time
            state: [altitude, velocity]
            params: Rocket parameters

        Returns:
            Derivatives [velocity, acceleration]
        """
        altitude, velocity = state

        # Only drag and gravity forces
        drag = self.physics_engine.calculate_drag(
            velocity, params["C_drag"], params["A_rocket"]
        )

        # Store derived quantities
        self._store_derived_quantities(
            t,
            final_air_pressure,
            final_air_temperature,
            0,
            drag,
            water_exhaust_speed=None,
            air_exhaust_speed=None,
            water_mass_flow_rate=0,
            air_mass_flow_rate=0,
            air_exit_pressure=None,
            air_exit_temperature=None,
        )

        # Calculate acceleration
        total_mass = params["m_empty"]
        _, acceleration = self.physics_engine.calculate_net_force(
            0, drag, total_mass
        )

        return np.array([velocity, acceleration])

    def _water_depletion_event(
        self, t: float, state: np.ndarray, params: Dict[str, Any]
    ) -> float:
        """Event function to detect water depletion."""
        return state[2]  # water_mass

    def _air_depletion_event(
        self, t: float, state: np.ndarray, params: Dict[str, Any]
    ) -> float:
        """Event function to detect air depletion (pressure = atmospheric)."""
        if len(state) < 4:
            return 1.0  # Not in air phase

        altitude, velocity, air_mass, air_temperature = state
        if air_mass <= 0:
            return 0.0

        # Calculate pressure
        air_volume = params["V_bottle"]
        pressure = (
            air_mass
            * self.physics_engine.air_gas_constant
            * air_temperature
            / air_volume
        )
        #print(f"Pressure at t={t:.3f}s: {pressure:.2f} Pa")
        return pressure - ATMOSPHERIC_PRESSURE

    def _hit_ground_event(
        self, t: float, state: np.ndarray, params: Dict[str, Any]
    ) -> float:
        """Event function to detect _hit_ground_event (altetude < 0 )."""
        # if len(state) < 4:
        #    return 1.0  # Not in air phase

        altitude, velocity = state
        if altitude <= 0:
            return 0.0
        return altitude

    def _setup_water_events(self, params: Dict[str, Any]):
        """Setup event functions for water phase simulation."""

        def water_depletion(t, state, *args):
            return self._water_depletion_event(t, state, params)

        water_depletion.terminal = True
        water_depletion.direction = -1

        return [water_depletion]

    def _setup_air_events(self, params: Dict[str, Any]):
        """Setup event functions for air phase simulation."""

        def air_depletion(t, state, *args):
            return self._air_depletion_event(t, state, params)

        air_depletion.terminal = True
        air_depletion.direction = -1

        return [air_depletion]

    def _setup_coasting_events(self, params: Dict[str, Any]):
        """Setup event functions for coasting phase simulation."""

        def hit_ground(t, state, *args):
            return self._hit_ground_event(t, state, params)

        hit_ground.terminal = True
        hit_ground.direction = -1

        return [hit_ground]

    def simulate(
        self, rocket_params: Dict[str, Any], sim_params: Dict[str, Any] = None
    ) -> FlightData:
        """
        Run complete water rocket simulation with three phases.

        Args:
            rocket_params: Rocket configuration parameters
            sim_params: Simulation parameters (optional)

        Returns:
            FlightData object with simulation results
        """
        # Validate parameters
        warnings = self.validator.validate_rocket_parameters(rocket_params)
        if warnings:
            print("Warnings:", warnings)

        # Set default simulation parameters
        if sim_params is None:
            sim_params = {}

        max_time = sim_params.get("max_time", DEFAULT_MAX_TIME)
        time_step = sim_params.get("time_step", DEFAULT_TIME_STEP)
        solver = sim_params.get("solver", DEFAULT_SOLVER)

        # Initialize storage for derived quantities
        self.derived_data = {
            "time": [],
            "pressure": [],
            "temperature": [],
            "thrust": [],
            "drag": [],
            "water_exhaust_speed": [],
            "air_exhaust_speed": [],
            "water_mass_flow_rate": [],
            "air_mass_flow_rate": [],
            "air_exit_pressure": [],
            "air_exit_temperature": [],
        }

        # Initialize storage for all phases
        all_times = []
        all_altitudes = []
        all_velocities = []
        all_water_masses = []
        all_liquid_gas_masses = []
        all_air_masses = []

        water_depletion_time = 0.0
        air_depletion_time = 0.0

        # Phase 1: Water expulsion phase
        if self.verbose:
            print("Starting water expulsion phase...")
        water_volume_initial = (
            rocket_params["V_bottle"] * rocket_params["water_fraction"]
        )
        water_mass_initial = WATER_DENSITY * water_volume_initial
        liquid_gas_mass_initial = rocket_params.get("liquid_gas_mass", 0.0)

        initial_state_water = np.array(
            [0.0, 0.0, water_mass_initial, liquid_gas_mass_initial]
        )
        time_span = (0, max_time)

        # Setup events for water phase
        water_events = self._setup_water_events(rocket_params)

        # Solve water phase
        solution_water = solve_ivp(
            self._rocket_ode_water_phase,
            time_span,
            initial_state_water,
            args=(rocket_params,),
            events=water_events,
            max_step=time_step,
            method=solver,
            rtol=1e-8,
            atol=1e-10,
        )

        # Store water phase results
        all_times.append(solution_water.t)
        all_altitudes.append(solution_water.y[0, :])
        all_velocities.append(solution_water.y[1, :])
        all_water_masses.append(solution_water.y[2, :])
        all_liquid_gas_masses.append(solution_water.y[3, :])

        # Calculate air mass during water phase
        initial_air_volume = rocket_params["V_bottle"] * (
            1 - rocket_params["water_fraction"]
        )
        initial_air_mass = (
            self.physics_engine.calculate_air_mass_from_conditions(
                rocket_params["P0"], INITIAL_TEMPERATURE, initial_air_volume
            )
        )
        air_masses_water_phase = np.full_like(
            solution_water.t, initial_air_mass
        )
        all_air_masses.append(air_masses_water_phase)

        # Phase 2: Air expulsion phase (if water depleted)
        if solution_water.t_events[0].size > 0:
            water_depletion_time = solution_water.t_events[0][0]
            if self.verbose:
                print(
                    f"Water depleted at t={water_depletion_time:.3f}s, starting air expulsion phase..."
                )

            # Get final state from water phase
            final_state_water = solution_water.y[:, -1]

            # Calculate initial conditions for air phase
            final_altitude = final_state_water[0]
            final_velocity = final_state_water[1]

            # Calculate air mass and temperature at start of air phase
            air_volume_at_transition = rocket_params["V_bottle"]
            initial_air_volume = rocket_params["V_bottle"] * (
                1 - rocket_params["water_fraction"]
            )

            # Pressure at end of water phase
            pressure_at_transition = (
                self.physics_engine.calculate_pressure_adiabatic(
                    rocket_params["P0"],
                    initial_air_volume,
                    air_volume_at_transition,
                )
            )

            # Temperature at end of water phase
            temperature_at_transition = (
                self.physics_engine.calculate_temperature_adiabatic(
                    INITIAL_TEMPERATURE,
                    rocket_params["P0"],
                    pressure_at_transition,
                )
            )

            # Air mass at transition
            air_mass_at_transition = (
                self.physics_engine.calculate_air_mass_from_conditions(
                    pressure_at_transition,
                    temperature_at_transition,
                    air_volume_at_transition,
                )
            )

            initial_state_air = np.array(
                [
                    final_altitude,
                    final_velocity,
                    air_mass_at_transition,
                    temperature_at_transition,
                ]
            )

            # Setup events for air phase
            air_events = self._setup_air_events(rocket_params)

            # Solve air phase
            solution_air = solve_ivp(
                self._rocket_ode_air_phase,
                (water_depletion_time, max_time),
                initial_state_air,
                args=(rocket_params,),
                events=air_events,
                max_step=time_step,
                method=solver,
                rtol=1e-8,
                atol=1e-10,
            )
            final_air_mass = solution_air.y[2, -1]
            final_air_temperature = solution_air.y[3, -1]
            final_air_pressure = (
                final_air_mass
                * self.physics_engine.air_gas_constant
                * final_air_temperature
                / rocket_params["V_bottle"]
            )

            # Store air phase results
            all_times.append(solution_air.t)
            all_altitudes.append(solution_air.y[0, :])
            all_velocities.append(solution_air.y[1, :])
            all_water_masses.append(np.zeros_like(solution_air.t))
            all_liquid_gas_masses.append(np.zeros_like(solution_air.t))
            all_air_masses.append(solution_air.y[2, :])

            # Phase 3: Coasting phase (if air depleted)
            if solution_air.t_events[0].size > 0:
                air_depletion_time = solution_air.t_events[0][0]
                if self.verbose:
                    print(
                        f"Air depleted at t={air_depletion_time:.3f}s, starting coasting phase..."
                    )

                # Get final state from air phase
                final_state_air = solution_air.y[:, -1]
                final_altitude = final_state_air[0]
                final_velocity = final_state_air[1]

                initial_state_coasting = np.array(
                    [final_altitude, final_velocity]
                )
                # Setup events for coasting phase
                coasting_events = self._setup_coasting_events(rocket_params)
                # Solve coasting phase
                solution_coasting = solve_ivp(
                    lambda t, y: self._rocket_ode_coasting_phase(
                        t,
                        y,
                        rocket_params,
                        final_air_pressure,
                        final_air_temperature,
                    ),
                    (air_depletion_time, max_time),
                    initial_state_coasting,
                    # args=(rocket_params,),
                    events=coasting_events,
                    max_step=time_step,
                    method=solver,
                    rtol=1e-8,
                    atol=1e-10,
                )

                # Store coasting phase results
                all_times.append(solution_coasting.t)
                all_altitudes.append(solution_coasting.y[0, :])
                all_velocities.append(solution_coasting.y[1, :])
                all_water_masses.append(np.zeros_like(solution_coasting.t))
                all_liquid_gas_masses.append(
                    np.zeros_like(solution_coasting.t)
                )
                all_air_masses.append(
                    np.ones_like(solution_coasting.t) * final_air_mass
                )
                # i just want to have the same air mass temperature and
                # pressure as after the end of the air run.

        # Combine all phases
        time = np.concatenate(all_times)
        altitude = np.concatenate(all_altitudes)
        velocity = np.concatenate(all_velocities)
        water_mass = np.concatenate(all_water_masses)
        liquid_gas_mass = np.concatenate(all_liquid_gas_masses)
        air_mass = np.concatenate(all_air_masses)
        
        # Remove duplicates from the original time series arrays
        time, altitude, velocity, water_mass, liquid_gas_mass, air_mass = filter_unique_time_series(
            time, altitude, velocity, water_mass, liquid_gas_mass, air_mass
        )

        # Convert to NumPy for interpolation
        derived_time = np.array(self.derived_data["time"])
        # Interpolate each quantity
        pressure = interp1d(
            derived_time,
            self.derived_data["pressure"],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )(time)
        air_temperature = interp1d(
            derived_time,
            self.derived_data["temperature"],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )(time)
        thrust = interp1d(
            derived_time,
            self.derived_data["thrust"],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )(time)
        drag = interp1d(
            derived_time,
            self.derived_data["drag"],
            kind="linear",
            bounds_error=False,
            fill_value="extrapolate",
        )(time)

        # Interpolate additional derived quantities
        water_exhaust_speed = interp1d(
            derived_time,
            self.derived_data["water_exhaust_speed"],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )(time)
        air_exhaust_speed = interp1d(
            derived_time,
            self.derived_data["air_exhaust_speed"],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )(time)
        water_mass_flow_rate = interp1d(
            derived_time,
            self.derived_data["water_mass_flow_rate"],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )(time)
        air_mass_flow_rate = interp1d(
            derived_time,
            self.derived_data["air_mass_flow_rate"],
            kind="linear",
            bounds_error=False,
            fill_value=0.0,
        )(time)
        air_exit_pressure = interp1d(
            derived_time,
            self.derived_data["air_exit_pressure"],
            kind="linear",
            bounds_error=False,
            fill_value=ATMOSPHERIC_PRESSURE,
        )(time)
        air_exit_temperature = interp1d(
            derived_time,
            self.derived_data["air_exit_temperature"],
            kind="linear",
            bounds_error=False,
            fill_value=INITIAL_TEMPERATURE,
        )(time)

        # Calculate accelerations
        acceleration = np.gradient(velocity, time)

        # Create flight data object
        flight_data = FlightData(
            time=time,
            altitude=altitude,
            velocity=velocity,
            acceleration=acceleration,
            water_mass=water_mass,
            liquid_gas_mass=liquid_gas_mass,
            air_mass=air_mass,
            pressure=pressure,
            air_temperature=air_temperature,
            thrust=thrust,
            drag=drag,
            water_exhaust_speed=water_exhaust_speed,
            air_exhaust_speed=air_exhaust_speed,
            water_mass_flow_rate=water_mass_flow_rate,
            air_mass_flow_rate=air_mass_flow_rate,
            air_exit_pressure=air_exit_pressure,
            air_exit_temperature=air_exit_temperature,
            max_altitude=np.max(altitude),
            max_velocity=np.max(velocity),
            flight_time=time[-1],
            water_depletion_time=water_depletion_time,
            air_depletion_time=air_depletion_time,
        )

        return flight_data
    
def filter_unique_time_series(time, *arrays):
    _, idx = np.unique(time, return_index=True)
    idx = np.sort(idx)
    filtered = [time[idx]]
    for arr in arrays:
        filtered.append(arr[idx])
    return filtered
