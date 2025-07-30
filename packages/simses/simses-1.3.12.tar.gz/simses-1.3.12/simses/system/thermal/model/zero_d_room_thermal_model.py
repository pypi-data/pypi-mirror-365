import statistics
from scipy.integrate import solve_ivp
from simses.commons.config.simulation.general import GeneralSimulationConfig
from simses.commons.state.system import SystemState
from simses.system.auxiliary.auxiliary import Auxiliary
from simses.system.power_electronics.acdc_converter.abstract_acdc_converter import AcDcConverter
from simses.system.power_electronics.dcdc_converter.abstract_dcdc_converter import DcDcConverter
from simses.system.storage_system_dc import StorageSystemDC
from simses.system.thermal.ambient.ambient_thermal_model import AmbientThermalModel
from simses.system.thermal.model.system_thermal_model import SystemThermalModel
from simses.technology.storage import StorageTechnology


class ZeroDRoomThermalModel(SystemThermalModel):

    def __init__(self, ambient_thermal_model: AmbientThermalModel, general_config: GeneralSimulationConfig,
                 dc_systems: [StorageSystemDC], acdc_converter: AcDcConverter):

        super().__init__()

        # Components
        self.__acdc_converter = acdc_converter
        self.__dc_systems: [StorageSystemDC] = dc_systems
        self.__storage_technologies: [StorageTechnology] = list()
        self.__dc_dc_converters: [DcDcConverter] = list()
        for dc_system in self.__dc_systems:  # Unpack storage technologies and DC/DC converters from StorageSystemDC
            self.__storage_technologies.append(dc_system.get_storage_technology())
            self.__dc_dc_converters.append(dc_system.get_dc_dc_converter())

        # Simulation time parameters
        self.__sample_time: float = general_config.timestep
        self.__ts_adapted = 0

        # Models
        self.__ambient_thermal_model: AmbientThermalModel = ambient_thermal_model

        # Auto-adjust thermal model calculation timestep
        if general_config.end - general_config.start >= 86400:  # Choose a larger calculation_time_step for faster performance
            self.__calculation_time_step = 300
        else:
            self.__calculation_time_step = 60
        if self.__calculation_time_step >= self.__sample_time:
            self.__calculation_time_step = int(self.__sample_time)

        if self.__sample_time % self.__calculation_time_step != 0:
            raise Exception(self.__name__ +
                            ': For simulations longer than a day, please set a simulation timestep '
                            'in multiples of 5 minutes, for shorter simulations, use a timestep in multiples of 1 minute.')

        # -- Evaluation Time --
        # self.__t_eval_step is the time step after which the equation gets evaluated, it has impact on the I-controller
        # and the plotting (it results in the graphs getting more detailed).
        # Set t_eval-step to self.__calculation_time_step if plots are not needed because the impact on the I-Controller
        # is negligible.
        self.__t_eval_step: int = self.__calculation_time_step

        # Initialze temperatures of BESS components with the HVAC set-point temperature
        self.__internal_air_temperature: float = self.__ambient_thermal_model.get_initial_temperature()  # in K
        self.__storage_technology_temperatures = len(self.__storage_technologies) \
                                                 * [self.__ambient_thermal_model.get_initial_temperature()]  # K
        self.__converter_temperature_ac_dc = self.__ambient_thermal_model.get_initial_temperature()  # in K

        # Initialize internal air parameters
        # Model with p & V constant, i.e. if T rises, mass must decrease.
        # Quantities with reference to ideal gas equation
        self.__individual_gas_constant = self.universal_gas_constant / self.molecular_weight_air  # J/kgK
        self.__air_density = self.air_pressure / (self.__individual_gas_constant * 298.15)  # kg/m3

        # StorageTechnology thermal paramaters
        self.__surface_area_storage_technology = list()
        self.__mass_storage_technology = list()
        self.__specific_heat_capacity_storage_technology = list()
        self.__convection_coefficient_storage_technology_air = list()
        for storage_technology in self.__storage_technologies:
            self.__surface_area_storage_technology.append(storage_technology.surface_area)  # in m2
            self.__mass_storage_technology.append(storage_technology.mass)  # in kg
            self.__specific_heat_capacity_storage_technology.append(storage_technology.specific_heat)  # in J/kgK
            self.__convection_coefficient_storage_technology_air.append(storage_technology.convection_coefficient)  # in W/m2K

        # DC/DC Converter thermal parameters
        # Note: in this model the DC-DC Converter is treated as an part of the battery. That means battery and DC-DC
        # converter are seen as one thermal component with the same specific heat capacity and convection coefficient.
        # For the simulation/calculation the mass, surface area and thermal losses of the DC-DC converter are
        # added to the respective battery values.
        self.__surface_area_converter_dc_dc = list()
        self.__mass_converter_dc_dc = list()
        for dc_dc_converter in self.__dc_dc_converters:
            self.__surface_area_converter_dc_dc.append(dc_dc_converter.surface_area)  # in m2
            self.__mass_converter_dc_dc.append(dc_dc_converter.mass)  # in kg

        # AC/DC Converter thermal parameters
        self.__surface_area_converter_ac_dc = self.__acdc_converter.surface_area  # in m2
        self.__mass_converter_ac_dc = self.__acdc_converter.mass  # in kg
        self.__specific_heat_capacity_converter_ac_dc = statistics.mean(self.__specific_heat_capacity_storage_technology)  # in J/kgK
        self.__convection_coefficient_converter_ac_dc = statistics.mean(self.__convection_coefficient_storage_technology_air)  # in W/m2K

        self.__calculate_thermal_resistances()
        self.__calculate_thermal_capacities()

        self.__ambient_air_temperature = self.__ambient_thermal_model.get_initial_temperature()
        self.__solar_irradiation_thermal_load = 0
        self.__hvac_thermal_power = 0

    def __calculate_thermal_resistances(self) -> None:
        """
        calculates and sets the values of all thermal resistances in the model (in K/W)
        :return: None
        """
        # all units in K/W
        # calculates thermal convection resistance between the surrounding air (sa) and  the margin of Layer 3 (l3)

        # calculates thermal convection resistance  between the storage technologies and the internal air
        self.__storage_technology_ia_thermal_resistance = list()
        for storage_technology in self.__storage_technologies:
            index = self.__storage_technologies.index(storage_technology)
            self.__storage_technology_ia_thermal_resistance.append(
                1 / (self.__convection_coefficient_storage_technology_air[index] *
                     (self.__surface_area_storage_technology[index] + self.__surface_area_converter_dc_dc[index])))

        # calculates thermal convection resistance  between the converter and the inner air (ia)
        self.__converter_ia_thermal_resistance = 1 / (self.__convection_coefficient_converter_ac_dc *
                                                      self.__surface_area_converter_ac_dc)

    def __calculate_thermal_capacities(self) -> None:
        """
        calculates and sets the values of all thermal capacities in the model (in J/K)
        :return: None
        """
        # all units in J/K
        self.__storage_technology_thermal_capacity = list()
        for storage_technology in self.__storage_technologies:
            index = self.__storage_technologies.index(storage_technology)
            self.__storage_technology_thermal_capacity.append(
                (self.__mass_storage_technology[index] + self.__mass_converter_dc_dc[index]) * \
                self.__specific_heat_capacity_storage_technology[index])

        self.__converter_thermal_capacity = self.__mass_converter_ac_dc * self.__specific_heat_capacity_converter_ac_dc

    def update_air_parameters(self) -> None:
        """
        updates values of mass and air density stored within the HVAC object
        :return: None
        """
        pass

    def calculate_temperature(self, time, state: SystemState, storage_system_dc_states: [SystemState]) -> None:
        """
        primary method of the room thermal model which calculates and sets temperatures of all components
        :param time: timestamp of current timestep as float
        :param state: state of the StorageSystemAC as SystemState
        :param storage_system_dc_states: states of the StorageSystemDC objects within StorageSystemAC as [SystemState]
        :return: None
        """
        ambient_air_temperature = self.__ambient_thermal_model.get_temperature(time - self.__ts_adapted)
        self.__ambient_air_temperature = ambient_air_temperature
        self.__internal_air_temperature = ambient_air_temperature  # Housing is not present
        self.__air_density = self.air_pressure / (self.__individual_gas_constant * state.temperature)

        calculated_time = 0
        radiation_power = 0
        self.__solar_irradiation_thermal_load = radiation_power
        hvac_electric_consumption = []
        thermal_power_hvac = []

        while calculated_time < self.__sample_time:
            calculated_time += self.__calculation_time_step
            thermal_power = 0.0
            thermal_power_hvac.append(thermal_power)

            def equation_rhs(t, variable_array):
                """
                specifies the set of simultaneous differential equations to be solved
                """
                # variable_array = [inner_air_temperature,
                # storage_technology_temperatures(list, len = # storage technologies), converter_temperature]
                # Temperature variables: inner_air_temperature, storage_technology_temperatures, converter_temperature
                # independent variable: time

                number_storage_technologies = len(self.__storage_technologies)
                d_by_dt_storage_technology_temperature = list()
                heat_flow_storage_technology_ia = list()
                for storage_technology in self.__storage_technologies:
                    index = self.__storage_technologies.index(storage_technology)
                    storage_system_dc_state = storage_system_dc_states[index]
                    heat_flow_storage_technology_ia.append((variable_array[index + 1] - variable_array[0]) /
                                                           self.__storage_technology_ia_thermal_resistance[index])
                    # Differential equation for change in storage technology temperature
                    d_by_dt_storage_technology_temperature.append(
                        ((storage_system_dc_state.storage_power_loss + storage_system_dc_state.dc_power_loss) -
                         (variable_array[index + 1] - variable_array[0]) /
                         self.__storage_technology_ia_thermal_resistance[index]) / \
                        self.__storage_technology_thermal_capacity[index])

                # Differential equation for change in inner air temperature
                d_by_dt_inner_air_temperature = 0.0

                # Differential equation for change in converter temperature
                d_by_dt_converter_temperature_ac_dc = (state.pe_losses - (
                        (variable_array[number_storage_technologies + 1] - variable_array[0])
                        / self.__converter_ia_thermal_resistance)) / self.__converter_thermal_capacity

                equation_rhs_array = [d_by_dt_inner_air_temperature] + d_by_dt_storage_technology_temperature + \
                                     [d_by_dt_converter_temperature_ac_dc]
                return equation_rhs_array

            # time_interval is an array of times at which the equation get evaluated
            time_interval = [i for i in range(self.__t_eval_step, self.__calculation_time_step + self.__t_eval_step,
                                              self.__t_eval_step)]
            storage_technology_temperatures = self.__storage_technology_temperatures
            temperature_variable_array = [self.__internal_air_temperature] + storage_technology_temperatures + \
                                         [self.__converter_temperature_ac_dc]

            sol = solve_ivp(equation_rhs, (0, self.__calculation_time_step),
                            temperature_variable_array,
                            method='BDF', t_eval=time_interval)

            temperature_series = sol.y

            # setting temperatures for the next iteration of the while loop
            self.__internal_air_temperature = temperature_series[0, -1]
            number_storage_technologies = len(self.__storage_technologies)
            i = 0
            while i < len(self.__storage_technologies):
                self.__storage_technology_temperatures[i] = temperature_series[i + 1, -1]
                i += 1
            self.__converter_temperature_ac_dc = temperature_series[number_storage_technologies + 1, -1]

            hvac_electric_consumption.append(0.0)

        # setting storage technology temperature for SIMSES simulation and plotting
        for storage_technology in self.__storage_technologies:
            index = self.__storage_technologies.index(storage_technology)
            storage_technology.state.temperature = self.__storage_technology_temperatures[index]

        # Set HVAC electric consumption over sample time
        self.__hvac_thermal_power = 0.0

    def get_auxiliaries(self) -> [Auxiliary]:
        """
        :returns instances of the Auxiliary class (HVAC system in this case)
        :return: __heating_cooling as [Auxiliary]
        """
        return list()

    def get_temperature(self) -> float:
        """
        returns internal air temperature in the container in K
        :return: __internal_air_temperature as float
        """
        return self.__internal_air_temperature

    def get_ambient_temperature(self) -> float:
        """
        returns the ambient temperature at the location in K
        :return: __ambient_air_temperature as float
        """
        return self.__ambient_air_temperature

    def get_solar_irradiation_thermal_load(self) -> float:
        """
        returns the thermal load due to solar irradiation in W
        :return: __solar_irradiation_thermal_load as float
        """
        return self.__solar_irradiation_thermal_load

    def get_hvac_thermal_power(self) -> float:
        """
        returns the HVAC thermal power in W
        :return: __hvac_thermal_power as float
        """
        return self.__hvac_thermal_power

    def reset_profiles(self, ts_adapted: float) -> None:
        """
        Enables looping of the simulation beyond the original length of the time series for the AmbientThermalModel and
        SolarIrradiationModel
        """
        self.__ts_adapted = ts_adapted
        self.__ambient_thermal_model: AmbientThermalModel = self.__ambient_thermal_model.create_instance()

    def close(self) -> None:
        """
        closes specified open resources
        """
        self.__ambient_thermal_model.close()

    def get_ol_temperature(self) -> float:
        """
        Not applicable to this class
        """
        pass

    def get_il_temperature(self) -> float:
        """
        Not applicable to this class
        """
        pass
