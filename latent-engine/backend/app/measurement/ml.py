from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import replace

from .domain import Measurement


@dataclass(frozen=True)
class CalibrationResult:
    calibrated_value: float
    confidence_adjustment: float
    model_name: str
    model_version: str


class MeasurementCalibrationModel(ABC):
    """
    Boundary for optional ML-assisted calibration.

    Implementations may improve noise filtering or confidence estimates,
    but deterministic measurements remain the source of record.
    """

    @abstractmethod
    def calibrate(
        self,
        measurement: Measurement,
    ) -> CalibrationResult:
        raise NotImplementedError


class MlCalibrationService:
    """
    Applies optional ML calibration after deterministic measurement.

    The original measurement remains the dependency/source of record.
    Calibration is recorded as an auditable transformation that may adjust
    bias and confidence, but does not become an independent measurement fact.
    """

    def __init__(
        self,
        model: MeasurementCalibrationModel,
    ):
        self._model = model

    def calibrate(
        self,
        measurement: Measurement,
    ) -> Measurement:
        result = self._model.calibrate(
            measurement
        )

        confidence = max(
            0.0,
            min(
                1.0,
                measurement.confidence
                + result.confidence_adjustment,
            ),
        )

        return replace(
            measurement,
            value=result.calibrated_value,
            confidence=confidence,
            provenance=replace(
                measurement.provenance,
                transformations=(
                    *measurement.provenance.transformations,
                    "ml_calibration",
                    "bias_correction",
                    "confidence_adjustment",
                ),
            ),
            dependencies=(
                *measurement.dependencies,
                measurement.id,
            ),
            metadata={
                **measurement.metadata,
                "ml_calibration": {
                    "model_name": result.model_name,
                    "model_version": result.model_version,
                    "source_measurement_id": measurement.id,
                },
            },
        )
