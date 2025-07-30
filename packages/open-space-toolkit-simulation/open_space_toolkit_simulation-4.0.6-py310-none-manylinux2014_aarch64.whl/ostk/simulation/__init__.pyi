from __future__ import annotations
from ostk import astrodynamics as OpenSpaceToolkitAstrodynamicsPy
from ostk.astrodynamics import Access
from ostk.astrodynamics import Dynamics
from ostk.astrodynamics import EventCondition
from ostk.astrodynamics import GuidanceLaw
from ostk.astrodynamics import RootSolver
from ostk.astrodynamics import Trajectory
from ostk.astrodynamics import access
from ostk.astrodynamics import conjunction
from ostk.astrodynamics import converters
from ostk.astrodynamics import data
from ostk.astrodynamics import dynamics
from ostk.astrodynamics import eclipse
from ostk.astrodynamics import estimator
from ostk.astrodynamics import event_condition
import ostk.astrodynamics.flight
from ostk.astrodynamics import flight
from ostk.astrodynamics import guidance_law
from ostk.astrodynamics import pytrajectory
from ostk.astrodynamics import solver
from ostk.astrodynamics import trajectory
from ostk.astrodynamics.trajectory import State as PyState
from ostk import core as OpenSpaceToolkitCorePy
from ostk.core import container
from ostk.core import filesystem
from ostk.core import type
import ostk.core.type
from ostk import io as OpenSpaceToolkitIOPy
from ostk.io import URL
from ostk.io import ip
from ostk import mathematics as OpenSpaceToolkitMathematicsPy
from ostk.mathematics import curve_fitting
from ostk.mathematics import geometry
import ostk.mathematics.geometry.d3.transformation.rotation
from ostk.mathematics import object
import ostk.physics
from ostk import physics as OpenSpaceToolkitPhysicsPy
from ostk.physics import Environment
from ostk.physics import Manager
from ostk.physics import Unit
from ostk.physics import coordinate
import ostk.physics.coordinate
from ostk.physics import environment
from ostk.physics import time
import ostk.physics.time
from ostk.physics import unit
from ostk import simulation as OpenSpaceToolkitSimulationPy
import typing
from . import component
__all__ = ['Access', 'Component', 'ComponentConfiguration', 'ComponentHolder', 'Dynamics', 'Entity', 'Environment', 'EventCondition', 'GuidanceLaw', 'Manager', 'OpenSpaceToolkitAstrodynamicsPy', 'OpenSpaceToolkitCorePy', 'OpenSpaceToolkitIOPy', 'OpenSpaceToolkitMathematicsPy', 'OpenSpaceToolkitPhysicsPy', 'OpenSpaceToolkitSimulationPy', 'PyState', 'RootSolver', 'Satellite', 'SatelliteConfiguration', 'Simulator', 'SimulatorConfiguration', 'Trajectory', 'URL', 'Unit', 'access', 'component', 'conjunction', 'container', 'converters', 'coordinate', 'curve_fitting', 'data', 'dynamics', 'eclipse', 'environment', 'estimator', 'event_condition', 'filesystem', 'flight', 'geometry', 'guidance_law', 'ip', 'object', 'pytrajectory', 'solver', 'time', 'trajectory', 'type', 'unit']
class Component(Entity, ComponentHolder):
    class Type:
        """
        Members:
        
          Undefined
        
          Assembly
        
          Controller
        
          Sensor
        
          Actuator
        
          Other
        """
        Actuator: typing.ClassVar[Component.Type]  # value = <Type.Actuator: 4>
        Assembly: typing.ClassVar[Component.Type]  # value = <Type.Assembly: 1>
        Controller: typing.ClassVar[Component.Type]  # value = <Type.Controller: 2>
        Other: typing.ClassVar[Component.Type]  # value = <Type.Other: 5>
        Sensor: typing.ClassVar[Component.Type]  # value = <Type.Sensor: 3>
        Undefined: typing.ClassVar[Component.Type]  # value = <Type.Undefined: 0>
        __members__: typing.ClassVar[dict[str, Component.Type]]  # value = {'Undefined': <Type.Undefined: 0>, 'Assembly': <Type.Assembly: 1>, 'Controller': <Type.Controller: 2>, 'Sensor': <Type.Sensor: 3>, 'Actuator': <Type.Actuator: 4>, 'Other': <Type.Other: 5>}
        def __eq__(self, other: typing.Any) -> bool:
            ...
        def __getstate__(self) -> int:
            ...
        def __hash__(self) -> int:
            ...
        def __index__(self) -> int:
            ...
        def __init__(self, value: int) -> None:
            ...
        def __int__(self) -> int:
            ...
        def __ne__(self, other: typing.Any) -> bool:
            ...
        def __repr__(self) -> str:
            ...
        def __setstate__(self, state: int) -> None:
            ...
        def __str__(self) -> str:
            ...
        @property
        def name(self) -> str:
            ...
        @property
        def value(self) -> int:
            ...
    @staticmethod
    def configure(configuration: typing.Any, parent_component: Component) -> Component:
        ...
    @staticmethod
    def string_from_type(type: typing.Any) -> ostk.core.type.String:
        ...
    @staticmethod
    def undefined() -> Component:
        ...
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, type: typing.Any, tags: list[ostk.core.type.String], geometries: list[...], components: list[Component], parent: ComponentHolder, frame: ostk.physics.coordinate.Frame, simulator: Simulator) -> None:
        ...
    def __repr__(self) -> str:
        ...
    def __str__(self) -> str:
        ...
    def access_frame(self) -> ostk.physics.coordinate.Frame:
        ...
    def access_geometry_with_name(self, name: ostk.core.type.String) -> ...:
        ...
    def access_simulator(self) -> Simulator:
        ...
    def add_component(self, component: Component) -> None:
        ...
    def add_geometry(self, geometry: typing.Any) -> None:
        ...
    def get_geometries(self) -> list[...]:
        ...
    def get_tags(self) -> list[ostk.core.type.String]:
        ...
    def get_type(self) -> ...:
        ...
    def is_defined(self) -> bool:
        ...
    def set_parent(self, component: Component) -> None:
        ...
class ComponentConfiguration:
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, type: Component.Type = ..., tags: list[ostk.core.type.String] = [], orientation: ostk.mathematics.geometry.d3.transformation.rotation.Quaternion = [0.0, 0.0, 0.0, 1.0], geometries: list[...] = [], components: list[ComponentConfiguration] = []) -> None:
        ...
class ComponentHolder:
    def access_component_at(self, arg0: ostk.core.type.String) -> ...:
        ...
    def access_component_with_id(self, arg0: ostk.core.type.String) -> ...:
        ...
    def access_component_with_name(self, arg0: ostk.core.type.String) -> ...:
        ...
    def access_components(self) -> list[...]:
        ...
    def access_components_with_tag(self, arg0: ostk.core.type.String) -> list[...]:
        ...
    def add_component(self, arg0: typing.Any) -> None:
        ...
    def has_component_at(self, arg0: ostk.core.type.String) -> bool:
        ...
    def has_component_with_id(self, arg0: ostk.core.type.String) -> bool:
        ...
    def has_component_with_name(self, arg0: ostk.core.type.String) -> bool:
        ...
class Entity:
    @staticmethod
    def undefined() -> Entity:
        ...
    def get_id(self) -> ostk.core.type.String:
        ...
    def get_name(self) -> ostk.core.type.String:
        ...
    def is_defined(self) -> bool:
        ...
class Satellite(Component):
    @staticmethod
    def configure(configuration: typing.Any, simulator: Simulator = None) -> Satellite:
        ...
    @staticmethod
    def undefined() -> Satellite:
        ...
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, tags: list[ostk.core.type.String], geometries: list[component.Geometry], components: list[Component], frame: ostk.physics.coordinate.Frame, profile: ostk.astrodynamics.flight.Profile, simulator: Simulator) -> None:
        ...
    def access_profile(self) -> ostk.astrodynamics.flight.Profile:
        ...
    def is_defined(self) -> bool:
        ...
class SatelliteConfiguration:
    def __init__(self, id: ostk.core.type.String, name: ostk.core.type.String, profile: ostk.astrodynamics.flight.Profile, components: list[ComponentConfiguration] = [], tags: list[ostk.core.type.String] = [], geometries: list[component.GeometryConfiguration] = []) -> None:
        ...
class Simulator:
    @staticmethod
    def configure(configuration: typing.Any) -> Simulator:
        ...
    @staticmethod
    def undefined() -> Simulator:
        ...
    def __init__(self, environment: ostk.physics.Environment, satellites: list[...]) -> None:
        ...
    def access_environment(self) -> ostk.physics.Environment:
        ...
    def access_satellite_map(self) -> dict[ostk.core.type.String, ...]:
        ...
    def access_satellite_with_name(self, name: ostk.core.type.String) -> ...:
        ...
    def add_satellite(self, satellite: typing.Any) -> None:
        ...
    def get_instant(self) -> ostk.physics.time.Instant:
        ...
    def has_satellite_with_name(self, name: ostk.core.type.String) -> bool:
        ...
    def is_defined(self) -> bool:
        ...
    def set_instant(self, instant: ostk.physics.time.Instant) -> None:
        ...
    def step_forward(self, duration: ostk.physics.time.Duration) -> None:
        ...
class SimulatorConfiguration:
    def __init__(self, environment: ostk.physics.Environment, satellites: list[...] = []) -> None:
        ...
