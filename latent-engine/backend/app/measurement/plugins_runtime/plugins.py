from app.measurement.core.interfaces import MeasurementEvaluator
from app.measurement.core.interfaces import MeasurementNormalizer
from app.measurement.core.interfaces import MeasurementValidator


class MeasurementPluginRegistry:

    def __init__(
        self,
    ):
        self._evaluators = {}
        self._normalizers = {}
        self._validators = {}

    def register_evaluator(
        self,
        name: str,
        evaluator: MeasurementEvaluator,
    ):
        self._evaluators[name] = evaluator

    def register_normalizer(
        self,
        name: str,
        normalizer: MeasurementNormalizer,
    ):
        self._normalizers[name] = normalizer

    def register_validator(
        self,
        name: str,
        validator: MeasurementValidator,
    ):
        self._validators[name] = validator

    def evaluators(
        self,
    ) -> list[MeasurementEvaluator]:
        return list(
            self._evaluators.values()
        )

    def normalizers(
        self,
    ) -> list[MeasurementNormalizer]:
        return list(
            self._normalizers.values()
        )

    def validators(
        self,
    ) -> list[MeasurementValidator]:
        return list(
            self._validators.values()
        )


