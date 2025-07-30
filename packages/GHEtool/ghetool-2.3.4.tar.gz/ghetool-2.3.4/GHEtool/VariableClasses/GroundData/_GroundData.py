import abc
import warnings

import numpy as np
from abc import ABC
from GHEtool.VariableClasses.BaseClass import BaseClass
from typing import Union, List


class GroundLayer(BaseClass):
    """
    Contains the information about a certain ground layer.
    """

    __slots__ = "k_s", "volumetric_heat_capacity", "thickness"

    def __init__(self, k_s: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6,
                 thickness: float = None):
        """

        Parameters
        ----------
        k_s : float
            Layer thermal conductivity [W/(m·K)]
        volumetric_heat_capacity : float
            Layer volumetric heat capacity [J/(m³·K)]
        thickness : float
            Layer thickness [m]. None is assumed infinite depth
        """
        self.k_s: float = self.non_negative(k_s)
        self.volumetric_heat_capacity: float = self.non_negative(volumetric_heat_capacity)
        self.thickness: float = self.non_negative(thickness)

    def non_negative(self, value: float) -> float:
        """
        This function returns the value if the value > 0.
        Otherwise, an error is raised.

        Parameters
        ----------
        value : float
            Value to be checked

        Returns
        -------
        float
            Value

        Raises
        ------
        ValueError
            When the value equals 0 or is smaller
        """
        if value is None or value > 0:
            return value
        raise ValueError(f'The value {value} is smaller or equal to 0.')

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True

    def __export__(self):
        return {'Thickness [m]': self.thickness,
                'Conductivity [W/(m·K)]': self.k_s,
                'Volumetric heat capacity [MJ/(m³·K)]': self.volumetric_heat_capacity / 10 ** 6
                }


class _GroundData(BaseClass, ABC):
    """
    Contains information regarding the ground data of the borefield.
    """

    __slots__ = 'layers', 'layer_depths', 'variable_Tg', 'Tg', 'last_layer_infinite'

    def __init__(self, k_s: float = None,
                 volumetric_heat_capacity: float = 2.4 * 10 ** 6):
        """

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity [W/mK]
        volumetric_heat_capacity : float
            The volumetric heat capacity of the ground [J/m3K]
        """

        self.layers: List[GroundLayer] = []
        self.layer_depths: list = []
        self.variable_Tg: bool = False
        self.Tg: float = 10
        self.last_layer_infinite: bool = True  # assumes that the last ground layer is infinite

        if k_s is not None:
            self.add_layer_on_bottom(GroundLayer(k_s, volumetric_heat_capacity, thickness=None))

    def add_layer_on_top(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        """
        This function adds a ground layer on the top of the array. This hence becomes the highest
        ground layer.

        Parameters
        ----------
        layer : GroundLayer or list of ground layers
            GroundLayer object with thermal properties of this layer

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When you add a ground layer with no specified depth and there are already ground layers in the array
        """
        if not isinstance(layer, GroundLayer):
            for i in layer:
                self.add_layer_on_top(i)
            return
        # check if previous layer has a thickness different from None
        if np.any(self.layers):
            if layer.thickness is None:
                raise ValueError('You cannot add a layer on top of another layer if you have an undetermined depth.')

        self.layers.insert(0, layer)
        self.layer_depths = [0]
        for idx, layer in enumerate(self.layers):
            if layer.thickness is None:
                continue
            self.layer_depths.append(self.layer_depths[idx] + layer.thickness)

    def add_layer_on_bottom(self, layer: Union[GroundLayer, List[GroundLayer]]) -> None:
        """
        This function adds a ground layer on the bottom of the array. This hence becomes the deepest
        ground layer.

        Parameters
        ----------
        layer : GroundLayer or list of ground layers
            GroundLayer object with thermal properties of this layer

        Returns
        -------
        None

        Raises
        ------
        ValueError
            When you add a ground layer on the bottom of a layer which has no predefined depth
        """
        if not isinstance(layer, GroundLayer):
            for i in layer:
                self.add_layer_on_bottom(i)
            return
        # check if previous layer has a thickness different from None
        if np.any(self.layers):
            if self.layers[-1].thickness is None:
                raise ValueError('You cannot add a layer on bottom of a layer which has un undetermined depth.')

        self.layers.append(layer)
        self.layer_depths.append(0 if len(self.layers) == 1 else self.layers[-2].thickness + self.layer_depths[-1])

    def check_depth(self, depth: float) -> bool:
        """
        Checks if the depth is correct.
        A depth is False when it is lower than 0 or it exceeds the deepest ground layer and
        last_layer_infinite is set to False.

        Parameters
        ----------
        depth : float
            Borehole depth [m]

        Returns
        -------
        bool
            True if the depth is valid

        Raises
        ------
        ValueError
            When a depth is requested that is either smaller than zero or larger than the maximum depth.
        """
        if not np.any(self.layers):
            raise ValueError('There is no ground data available.')

        if self.layers[-1].thickness is None:
            # last layer is unbounded
            return True

        highest_depth = self.layer_depths[-1] + self.layers[-1].thickness
        if depth <= highest_depth:
            return True

        if not self.last_layer_infinite:
            raise ValueError(f'The depth of {depth}m exceeds the maximum depth that is provided: {highest_depth}m. '
                             f'One can set the last_layer_infinite assumption to True in the ground class.')

        warnings.warn(f'The depth of {depth}m exceeds the maximum depth that is provided: {highest_depth}m. '
                      f'In order to continue, it is assumed the deepest layer is infinite.')
        return True

    def calculate_value(self, thickness_list: list, cumulative_thickness_list: list, y_range: list,
                        depth: float, start_depth: float) -> float:
        """
        This function calculates the average value of a certain y_range of values for a certain depth,
        given the thickness of the ground layers.

        Parameters
        ----------
        thickness_list : list
            List of all the layer thicknesses
        cumulative_thickness_list : list
            Cumulative sum of all the layer thicknesses
        y_range : list
            Range with the values for each layer
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        float
            Calculated value for either k_s or volumetric heat capacity
        """
        if depth <= 0:
            # For negative values, the first conductivity is returned
            return y_range[0]

        # raise error when the start_depth is larger or equal to the end_depth
        if depth - start_depth <= 0:
            raise ValueError('The length of the borehole is 0.')

        result_buried = 0
        result_depth = 0

        if start_depth == 0:
            result_buried = 0
        else:
            idx_of_layer_in_which_H_falls = [i for i, v in enumerate(cumulative_thickness_list) if v <= start_depth][-1]
            for idx, val in enumerate(y_range[:idx_of_layer_in_which_H_falls]):
                result_buried += val * thickness_list[idx + 1] / start_depth

            result_buried += y_range[idx_of_layer_in_which_H_falls] * (
                    start_depth - cumulative_thickness_list[idx_of_layer_in_which_H_falls]) / start_depth

        idx_of_layer_in_which_H_falls = [i for i, v in enumerate(cumulative_thickness_list) if v <= depth][-1]
        for idx, val in enumerate(y_range[:idx_of_layer_in_which_H_falls]):
            result_depth += val * thickness_list[idx + 1] / depth

        result_depth += y_range[idx_of_layer_in_which_H_falls] * (
                depth - cumulative_thickness_list[idx_of_layer_in_which_H_falls]) / depth

        return (result_depth * depth - result_buried * start_depth) / (depth - start_depth)

    def k_s(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        Returns the ground thermal conductivity in W/mK for a given depth.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        float
            Ground thermal conductivity in W/mK for a given depth.
        """
        self.check_depth(depth)
        if len(self.layers) == 1 and (self.layers[0].thickness is None or self.last_layer_infinite):
            return self.layers[0].k_s
        return self.calculate_value([0] + [layer.thickness for layer in self.layers], self.layer_depths,
                                    [layer.k_s for layer in self.layers], depth, start_depth)

    def volumetric_heat_capacity(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        Returns the ground volumetric heat capacity in J/m³K for a given depth.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        float
            Ground volumetric heat capacity in J/m³K for a given depth.
        """
        self.check_depth(depth)
        if len(self.layers) == 1 and (self.layers[0].thickness is None or self.last_layer_infinite):
            return self.layers[0].volumetric_heat_capacity
        return self.calculate_value([0] + [layer.thickness for layer in self.layers], self.layer_depths,
                                    [layer.volumetric_heat_capacity for layer in self.layers], depth, start_depth)

    def alpha(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        Returns the ground thermal diffusivity in m²/s for a given depth.
        If no volumetric heat capacity or conductivity is given, None is returned.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        float
            Ground thermal diffusivity in m²/s for a given depth.
        """

        if not np.any(self.layers):
            return None
        else:
            return self.k_s(depth, start_depth) / self.volumetric_heat_capacity(depth, start_depth)  # m2/s

    @abc.abstractmethod
    def calculate_Tg(self, depth: float = 100, start_depth: float = 0) -> float:
        """
        This function gives back the average ground temperature for the borehole.

        Parameters
        ----------
        depth : float
            Depth of the borehole [m]
        start_depth : float
            Depth at which the borehole starts [m]

        Returns
        -------
        Tg : float
            Ground temperature [deg C]
        """

    @abc.abstractmethod
    def calculate_delta_H(self, temperature_diff: float) -> float:
        """
        This function calculates the difference in depth for a given difference in temperature.

        Parameters
        ----------
        temperature_diff : float
            Difference in temperature [deg C]

        Returns
        -------
        Difference in depth [m] : float
        """

    def max_depth(self, max_temp: float) -> float:
        """
        This function returns the maximum borehole depth, based on the maximum temperature.
        The maximum is the depth where the ground temperature equals the maximum temperature limit.

        Parameters
        ----------
        max_temp : float
            Maximum temperature [deg C]

        Returns
        -------
        Depth : float
            Maximum depth [m]
        """
        return self.calculate_delta_H(max_temp - self.Tg)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True

    def __export__(self):
        if len(self.layers) == 1:
            return {
                'Conductivity [W/(m·K)]': self.layers[0].k_s,
                'Volumetric heat capacity [MJ/(m³·K)]': self.layers[0].volumetric_heat_capacity / 10 ** 6
            }
        else:
            result = {'layers': dict()}
            for idx, layer in enumerate(self.layers):
                result['layers'][idx + 1] = layer.__export__()
            return result
