"""Module for vehicle classes."""
from __future__ import annotations
from typing import TYPE_CHECKING

from carconnectivity.vehicle import GenericVehicle, ElectricVehicle, CombustionVehicle, HybridVehicle
from carconnectivity.attributes import BooleanAttribute

from carconnectivity_connectors.volkswagen.capability import Capabilities
from carconnectivity_connectors.volkswagen.climatization import VolkswagenClimatization
from carconnectivity_connectors.volkswagen.charging import VolkswagenCharging

SUPPORT_IMAGES = False
try:
    from PIL import Image
    SUPPORT_IMAGES = True
except ImportError:
    pass

if TYPE_CHECKING:
    from typing import Optional, Dict
    from carconnectivity.garage import Garage
    from carconnectivity_connectors.base.connector import BaseConnector


class VolkswagenVehicle(GenericVehicle):  # pylint: disable=too-many-instance-attributes
    """
    A class to represent a generic volkswagen vehicle.

    Attributes:
    -----------
    vin : StringAttribute
        The vehicle identification number (VIN) of the vehicle.
    license_plate : StringAttribute
        The license plate of the vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[VolkswagenVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
            self.capabilities: Capabilities = origin.capabilities
            self.capabilities.parent = self
            self.is_active: BooleanAttribute = origin.is_active
            self.is_active.parent = self
            if SUPPORT_IMAGES:
                self._car_images = origin._car_images
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
            self.capabilities: Capabilities = Capabilities(vehicle=self)
            self.climatization = VolkswagenClimatization(vehicle=self, origin=self.climatization)
            self.is_active = BooleanAttribute(name='is_active', parent=self, tags={'connector_custom'})
            if SUPPORT_IMAGES:
                self._car_images: Dict[str, Image.Image] = {}
        self.manufacturer._set_value(value='Volkswagen')  # pylint: disable=protected-access


class VolkswagenElectricVehicle(ElectricVehicle, VolkswagenVehicle):
    """
    Represents a Volkswagen electric vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[VolkswagenVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
            if isinstance(origin, ElectricVehicle):
                self.charging = VolkswagenCharging(vehicle=self, origin=origin.charging)
            else:
                self.charging = VolkswagenCharging(vehicle=self, origin=self.charging)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
            self.charging = VolkswagenCharging(vehicle=self, origin=self.charging)


class VolkswagenCombustionVehicle(CombustionVehicle, VolkswagenVehicle):
    """
    Represents a Volkswagen combustion vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[VolkswagenVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)


class VolkswagenHybridVehicle(HybridVehicle, VolkswagenElectricVehicle, VolkswagenCombustionVehicle):
    """
    Represents a Volkswagen hybrid vehicle.
    """
    def __init__(self, vin: Optional[str] = None, garage: Optional[Garage] = None, managing_connector: Optional[BaseConnector] = None,
                 origin: Optional[VolkswagenVehicle] = None) -> None:
        if origin is not None:
            super().__init__(garage=garage, origin=origin)
        else:
            super().__init__(vin=vin, garage=garage, managing_connector=managing_connector)
