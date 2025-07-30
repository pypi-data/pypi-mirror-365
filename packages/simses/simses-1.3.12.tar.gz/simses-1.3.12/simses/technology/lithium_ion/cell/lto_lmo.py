import math

import pandas as pd
import scipy.interpolate

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.prismatic import PrismaticCell
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class LTOLMO(CellType):
    """An LTO_LMO is a special cell type and inherited by CellType"""

    # Source:
    # Thomas Nemeth, Philipp Schröer, Matthias Kuipers, Dirk Uwe Sauer:
    # Lithium titanate oxide battery cells for high-power automotive applications -
    # Electro-thermal  properties, aging behavior and cost considerations,
    # Journal of Energy Storage 31 (2020) 101656, https://doi.org/10.1016/j.est.2020.101656

    __SOC_HEADER: str = 'SOC'
    __SOC_IDX: int = 0
    __TEMP_IDX: int = 1
    __C_RATE_IDX: int = 0
    __ETA_IDX: int = 1

    __CELL_VOLTAGE: float = 2.4  # V
    __CELL_CAPACITY: float = 2.9  # Ah
    __MAX_VOLTAGE: float = 2.8  # V
    __MIN_VOLTAGE: float = 1.8  # V
    __CELL_RESISTANCE: float = 0.81 * 10 ** (-3)  # Ohm # from lmo_daimler
    __MIN_TEMPERATURE: float = 263.15  # K
    __MAX_TEMPERATURE: float = 318.15  # K
    __MAX_CHARGE_RATE: float = 10.0  # 1/h
    __MAX_DISCHARGE_RATE: float = 10.0  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per month in second step, e.g., 0.015 / (30.5 * 24 * 3600) for 1.5%
    __MASS: float = 0.151  # kg per cell
    # Source of specific heat:
    # Hamidreza Behi, Danial Karimi, Mohammadreza Behi, Joris Jaguemont, Morteza Ghanbarpour, Masud Behnia, Maitane Berecibar, Joeri Van Mierlo:
    # Thermal management analysis using heat pipe in the high current discharging of lithium-ion battery in electric vehicles,
    # Journal of Energy Storage 32 (2020) 101893, https://doi.org/10.1016/j.est.2020.101893
    __SPECIFIC_HEAT: float = 1150  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K convection coefficient of LFP Sony
    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    __LENGTH: float = 69  # mm
    __WIDE: float = 62  # mm
    __HEIGHT: float = 13  # mm

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE,
                                                                            __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = PrismaticCell(__HEIGHT, __WIDE, __LENGTH)

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

        # Physical parameters for lithium_ion thermal model
        # See SimSES Paper for Sources
        self.__volume = self.__LENGTH * self.__WIDE * self.__HEIGHT * 10 ** (-9) \
                        * self.get_serial_scale() * self.get_parallel_scale()  # m3
        self.__surface_area = 2 * (self.__LENGTH * self.__WIDE + self.__LENGTH * self.__HEIGHT + self.__HEIGHT * self.__WIDE) \
                              * 10 ** (-6) * self.get_serial_scale() * self.get_parallel_scale()  # m2



    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        '''Parameters build with ocv fitting'''
        a1 = -98.0995
        a2 = 0.6497
        a3 = -17.7261
        a4 = -3.1726
        b1 = 1.0308
        b2 = -3.3736
        k0 = 2.6329
        k1 = -1.4900
        k2 = -4.8486
        k3 = 1.5915
        k4 = -0.4285
        k5 = 0.0033

        soc = battery_state.soc

        ocv = k0 + \
              k1 / (1 + math.exp(a1 * (soc - b1))) + \
              k2 / (1 + math.exp(a2 * (soc - b2))) + \
              k3 / (1 + math.exp(a3 * (soc - 1))) +\
              k4 / (1 + math.exp(a4 * soc)) +\
              k5 * soc

        return ocv * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        return float(self.__CELL_RESISTANCE / self.get_parallel_scale() * self.get_serial_scale())

    def close(self):
        self.__log.close()