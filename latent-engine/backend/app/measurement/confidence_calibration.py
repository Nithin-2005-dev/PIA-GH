from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceObservation:
    measurement_id: str
    predicted_confidence: float
    observed_success: bool


@dataclass(frozen=True)
class ConfidenceCalibrationReport:
    measurement_id: str
    predicted_confidence: float
    observed_reliability: float
    calibration_error: float
    sample_size: int


class ConfidenceCalibrationModel:

    def calibrate(
        self,
        measurement_id: str,
        predicted_confidence: float,
        observations: list[ConfidenceObservation],
    ) -> ConfidenceCalibrationReport:
        relevant = [
            observation
            for observation in observations
            if observation.measurement_id == measurement_id
        ]

        if not relevant:
            return ConfidenceCalibrationReport(
                measurement_id=measurement_id,
                predicted_confidence=predicted_confidence,
                observed_reliability=predicted_confidence,
                calibration_error=0.0,
                sample_size=0,
            )

        observed = sum(
            1
            for observation in relevant
            if observation.observed_success
        ) / len(
            relevant
        )

        return ConfidenceCalibrationReport(
            measurement_id=measurement_id,
            predicted_confidence=predicted_confidence,
            observed_reliability=observed,
            calibration_error=abs(
                predicted_confidence - observed
            ),
            sample_size=len(
                relevant
            ),
        )

    def adjusted_confidence(
        self,
        report: ConfidenceCalibrationReport,
    ) -> float:
        if report.sample_size == 0:
            return report.predicted_confidence

        return max(
            0.0,
            min(
                1.0,
                (
                    report.predicted_confidence
                    + report.observed_reliability
                )
                / 2.0,
            ),
        )
