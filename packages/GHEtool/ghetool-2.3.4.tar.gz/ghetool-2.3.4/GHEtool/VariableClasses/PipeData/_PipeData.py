import abc
import pygfunction as gt
from abc import ABC
from GHEtool.VariableClasses.BaseClass import BaseClass
from GHEtool.VariableClasses.FluidData import _FluidData
from GHEtool.VariableClasses.FlowData import _FlowData


class _PipeData(BaseClass, ABC):
    """
    Contains information regarding the pipe data of the borefield.
    """

    __slots__ = 'k_g', 'k_p', 'epsilon'

    def __init__(self, k_g: float = None,
                 k_p: float = None,
                 epsilon: float = 1e-6):
        """

        Parameters
        ----------
        k_g : float
            Grout thermal conductivity [W/mK]
        k_p : float
            Pipe thermal conductivity [W/mK]
        epsilon : float
            Pipe roughness [m]
        """

        self.k_g = k_g  # grout thermal conductivity W/mK
        self.k_p = k_p  # pipe thermal conductivity W/mK
        self.epsilon = epsilon  # pipe roughness m

    @abc.abstractmethod
    def calculate_resistances(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                              **kwargs) -> None:
        """
        This function calculates the conductive and convective resistances, which are constant.

        Parameters
        ----------
        fluid_data : FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        None
        """

    @abc.abstractmethod
    def pipe_model(self, k_s: float, borehole: gt.boreholes.Borehole) -> gt.pipes._BasePipe:
        """
        This function returns the BasePipe model.

        Parameters
        ----------
        k_s : float
            Ground thermal conductivity
        borehole : Borehole
            Borehole object

        Returns
        -------
        BasePipe
        """

    @abc.abstractmethod
    def Re(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float, **kwargs) -> float:
        """
        Reynolds number.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]

        Returns
        -------
        Reynolds number : float
        """

    @abc.abstractmethod
    def pressure_drop(self, fluid_data: _FluidData, flow_rate_data: _FlowData, borehole_length: float,
                      include_bend: bool = True, **kwargs) -> float:
        """
        Calculates the pressure drop across the entire borehole.
        It assumed that the U-tubes are all connected in parallel.

        Parameters
        ----------
        fluid_data: FluidData
            Fluid data
        flow_rate_data : FlowData
            Flow rate data
        borehole_length : float
            Borehole length [m]
        include_bend : bool
            True if the losses in the bend should be included

        Returns
        -------
        Pressure drop : float
            Pressure drop [kPa]
        """

    @abc.abstractmethod
    def draw_borehole_internal(self, r_b: float) -> None:
        """
        This function draws the internal structure of a borehole.
        This means, it draws the pipes inside the borehole.

        Parameters
        ----------
        r_b : float
            Borehole radius [m]

        Returns
        -------
        None
        """

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        for i in self.__slots__:
            if getattr(self, i) != getattr(other, i):
                return False
        return True
