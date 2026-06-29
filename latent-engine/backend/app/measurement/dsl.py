from dataclasses import dataclass

from .domain import MeasurementDefinition
from .domain import MeasurementUnit


@dataclass(frozen=True)
class MeasurementDslDefinition:
    name: str
    sources: tuple[str, ...]
    formula: str
    confidence_model: str
    validator: str
    normalizer: str


class MeasurementDslParser:
    """
    Minimal deterministic DSL parser for customer-defined measurements.

    Supported form:

    measure Risk
    from Complexity
    from Ownership
    formula Complexity * Ownership
    confidence Bayesian
    validator Range
    normalizer Percentile
    """

    def parse(
        self,
        text: str,
    ) -> MeasurementDslDefinition:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        name = None
        sources = []
        formula = None
        confidence_model = "default_factor_model"
        validator = "default_validation_pipeline"
        normalizer = "default_normalization_pipeline"

        for line in lines:
            if line.startswith(
                "measure "
            ):
                name = line.removeprefix(
                    "measure "
                ).strip()

            elif line.startswith(
                "from "
            ):
                sources.append(
                    line.removeprefix(
                        "from "
                    ).strip()
                )

            elif line.startswith(
                "formula "
            ):
                formula = line.removeprefix(
                    "formula "
                ).strip()

            elif line.startswith(
                "confidence "
            ):
                confidence_model = line.removeprefix(
                    "confidence "
                ).strip()

            elif line.startswith(
                "validator "
            ):
                validator = line.removeprefix(
                    "validator "
                ).strip()

            elif line.startswith(
                "normalizer "
            ):
                normalizer = line.removeprefix(
                    "normalizer "
                ).strip()

        if name is None or formula is None:
            raise ValueError(
                "measurement DSL requires measure and formula"
            )

        return MeasurementDslDefinition(
            name=name,
            sources=tuple(sources),
            formula=formula,
            confidence_model=confidence_model,
            validator=validator,
            normalizer=normalizer,
        )

    def to_definition(
        self,
        parsed: MeasurementDslDefinition,
        unit: MeasurementUnit = MeasurementUnit.SCORE,
        version: str = "1.0",
    ) -> MeasurementDefinition:
        definition_id = (
            parsed.name
            .strip()
            .lower()
            .replace(" ", "_")
        )

        return MeasurementDefinition(
            id=definition_id,
            name=parsed.name,
            description=(
                f"Customer-defined measurement {parsed.name}."
            ),
            unit=unit,
            version=version,
            formula=parsed.formula,
            dependencies=parsed.sources,
            confidence_model=parsed.confidence_model,
            validator=parsed.validator,
            normalizer=parsed.normalizer,
            aggregation_strategy="formula",
            category="custom",
        )
