from __future__ import annotations

from typing import Protocol


class MeasurementRuntimeApi(Protocol):
    def measure_observations(
        self,
        observations,
        context=None,
    ):
        ...


class EstimationRuntimeApi(Protocol):
    def estimate(
        self,
        evidence,
        context=None,
    ):
        ...


class GraphRuntimeApi(Protocol):
    def build_graph(
        self,
        context=None,
    ):
        ...


class SimulationRuntimeApi(Protocol):
    def simulate(
        self,
        scenario,
        context=None,
    ):
        ...


class ForecastingRuntimeApi(Protocol):
    def forecast(
        self,
        history,
        context=None,
    ):
        ...


class AgentRuntimeApi(Protocol):
    def answer(
        self,
        question: str,
        context=None,
    ):
        ...


class ExecutiveRuntimeApi(Protocol):
    def summarize(
        self,
        context=None,
    ):
        ...


class StorageRuntimeApi(Protocol):
    def append(
        self,
        record,
    ) -> None:
        ...

