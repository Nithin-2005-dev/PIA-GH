from abc import ABC
from abc import abstractmethod


class SimulationPolicy(
    ABC
):

    @abstractmethod
    def simulate(
        self,
        *args,
        **kwargs,
    ):
        pass