from abc import ABC, abstractmethod

from app.domain.event import Event

from .domain import Measurement, MeasurementContext, ValidationResult


class MeasurementEvaluator(ABC):

    @abstractmethod
    def evaluate(
        self,
        event: Event,
        context: MeasurementContext,
    ) -> list[Measurement]:
        raise NotImplementedError


class MeasurementNormalizer(ABC):

    @abstractmethod
    def supports(
        self,
        measurement: Measurement,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def normalize(
        self,
        measurement: Measurement,
    ) -> Measurement:
        raise NotImplementedError


class MeasurementValidator(ABC):

    @abstractmethod
    def validate(
        self,
        measurement: Measurement,
    ) -> ValidationResult:
        raise NotImplementedError


class ConfidenceEstimator(ABC):

    @abstractmethod
    def estimate(
        self,
        measurement: Measurement,
        context: MeasurementContext,
    ) -> Measurement:
        raise NotImplementedError


class QualityScorer(ABC):

    @abstractmethod
    def score(
        self,
        measurement: Measurement,
        validation: ValidationResult,
        context: MeasurementContext,
    ) -> Measurement:
        raise NotImplementedError
