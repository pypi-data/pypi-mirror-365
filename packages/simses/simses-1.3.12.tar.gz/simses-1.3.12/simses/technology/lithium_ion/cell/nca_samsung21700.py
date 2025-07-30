import math

import pandas as pd
import scipy.interpolate
from numpy import asarray

from simses.commons.config.data.battery import BatteryDataConfig
from simses.commons.config.simulation.battery import BatteryConfig
from simses.commons.log import Logger
from simses.commons.state.technology.lithium_ion import LithiumIonState
from simses.technology.lithium_ion.cell.electric.properties import ElectricalCellProperties
from simses.technology.lithium_ion.cell.format.abstract import CellFormat
from simses.technology.lithium_ion.cell.format.round_18650 import RoundCell18650
from simses.technology.lithium_ion.cell.format.round_21700 import RoundCell21700
from simses.technology.lithium_ion.cell.thermal.properties import ThermalCellProperties
from simses.technology.lithium_ion.cell.type import CellType


class SamsungNCA21700(CellType):
    """This is a special cell type and inherited by CellType"""
    """Source: 
    Chair internal cell characterization tests 
    """

    __SOC_HEADER = 'SOC'
    __SOC_IDX = 0
    __OCV_IDX = 1
    __TEMP_IDX = 1
    __C_RATE_IDX = 0
    __ETA_IDX = 1

    __CELL_VOLTAGE = 3.64  # V (17.47 Wh / 4.8 Ah)
    __CELL_CAPACITY = 4.8  # Ah
    __MAX_VOLTAGE: float = 4.2  # V
    __MIN_VOLTAGE: float = 2.5  # V
    __MIN_TEMPERATURE: float = 273.15  # K
    __MAX_TEMPERATURE: float = 318.15  # K
    __MAX_CHARGE_RATE: float = 1.5  # 1/h
    __MAX_DISCHARGE_RATE: float = 1.5  # 1/h
    __SELF_DISCHARGE_RATE: float = 0.0  # X.X%-soc per day, e.g., 0.015 for 1.5% SOC loss per day
    __MASS: float = 0.068  # kg per cell

    __SPECIFIC_HEAT: float = 1048  # J/kgK
    __CONVECTION_COEFFICIENT: float = 15  # W/m2K
    __COULOMB_EFFICIENCY: float = 1.0  # p.u.

    __ELECTRICAL_PROPS: ElectricalCellProperties = ElectricalCellProperties(__CELL_VOLTAGE, __CELL_CAPACITY,
                                                                            __MIN_VOLTAGE, __MAX_VOLTAGE,
                                                                            __MAX_CHARGE_RATE, __MAX_DISCHARGE_RATE,
                                                                            __SELF_DISCHARGE_RATE, __COULOMB_EFFICIENCY)
    __THERMAL_PROPS: ThermalCellProperties = ThermalCellProperties(__MIN_TEMPERATURE, __MAX_TEMPERATURE, __MASS,
                                                                   __SPECIFIC_HEAT, __CONVECTION_COEFFICIENT)
    __CELL_FORMAT: CellFormat = RoundCell21700()

    def __init__(self, voltage: float, capacity: float, soh: float, battery_config: BatteryConfig,
                 battery_data_config: BatteryDataConfig):
        super().__init__(voltage, capacity, soh, self.__ELECTRICAL_PROPS, self.__THERMAL_PROPS, self.__CELL_FORMAT,
                         battery_config)
        self.__log: Logger = Logger(type(self).__name__)

        # ocv
        ocv_file: str = battery_data_config.nca_samsung21700_ocv_file
        ocv_df = pd.read_csv(ocv_file)  # V
        soc = ocv_df.loc[:, "SOC"]
        ocv = ocv_df.loc[:, "OCV"]
        self.__ocv_interp1d = scipy.interpolate.interp1d(soc, ocv, kind='linear')

        # internal resistance
        rint_file: str = battery_data_config.nca_samsung21700_rint_file
        internal_resistance_df = pd.read_csv(rint_file)  # Ohm
        soc =  internal_resistance_df.loc[:, "SOC"]
        r_ch =  internal_resistance_df.loc[:, "R_Ch"]
        r_dch =  internal_resistance_df.loc[:, "R_Dch"]
        self.__rint_interp1d_ch = scipy.interpolate.interp1d(soc, r_ch, kind='linear')
        self.__rint_interp1d_dch = scipy.interpolate.interp1d(soc, r_dch, kind='linear')

        # hysteresis voltage
        hystv_file: str = battery_data_config.nca_samsung21700_hystv_file
        hystv_df = pd.read_csv(hystv_file)  # V
        soc = hystv_df.loc[:, "SOC"]
        hystv = hystv_df.loc[:, "HystV"]
        self.__hystv_interp1d = scipy.interpolate.interp1d(soc, hystv, kind ='linear')

    def get_open_circuit_voltage(self, battery_state: LithiumIonState) -> float:
        cell_ocv = float(self.__ocv_interp1d(battery_state.soc))
        return cell_ocv  * self.get_serial_scale()

    def get_internal_resistance(self, battery_state: LithiumIonState) -> float:
        soc: float = self.check_soc_range(battery_state.soc)
        if battery_state.is_charge:
            # internal resistance for charge
            res_cell = self.__rint_interp1d_ch(soc)
            return float(res_cell / self.get_parallel_scale() * self.get_serial_scale())
        else:
            # internal resistance for discharge
            res_cell = self.__rint_interp1d_dch(soc)
            return float(res_cell / self.get_parallel_scale() * self.get_serial_scale())

    def get_hysteresis_voltage(self, battery_state: LithiumIonState) -> float:
        soc: float = self.check_soc_range(battery_state.soc)
        hystv_cell = self.__hystv_interp1d(soc)
        return float(hystv_cell * self.get_serial_scale())

    def close(self):
        self.__log.close()
