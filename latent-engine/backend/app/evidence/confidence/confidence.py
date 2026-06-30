from dataclasses import dataclass

from app.evidence.domain import EvidenceMeasurementRef
from app.evidence.knowledge.definitions import EvidenceDefinition


@dataclass(frozen=True)
class EvidenceConfidenceScore:
    value: float
    uncertainty: float
    quality: float
    strength: float
    factors: dict[str, float]
    explanation: str


class EvidenceConfidenceEngine:

    def aggregate(
        self,
        definition: EvidenceDefinition,
        supporting_measurements: tuple[EvidenceMeasurementRef, ...],
        validation_factor: float = 1.0,
    ) -> EvidenceConfidenceScore:
        if not supporting_measurements:
            return EvidenceConfidenceScore(
                value=0.0,
                uncertainty=1.0,
                quality=0.0,
                strength=0.0,
                factors={},
                explanation="No supporting measurements were available.",
            )

        measurement_confidence = sum(
            measurement.confidence
            for measurement in supporting_measurements
        ) / len(
            supporting_measurements
        )

        relative_uncertainties = []
        for measurement in supporting_measurements:
            relative_uncertainties.append(
                (
                    max(
                        0.0,
                        measurement.uncertainty_variance,
                    )
                    ** 0.5
                )
                / (
                    abs(
                        measurement.value
                    )
                    + 1.0
                )
            )

        average_uncertainty = sum(
            relative_uncertainties
        ) / len(
            relative_uncertainties
        )

        uncertainty_factor = max(
            0.0,
            min(
                1.0,
                1.0 - average_uncertainty,
            ),
        )

        quality = sum(
            measurement.quality_score
            for measurement in supporting_measurements
        ) / len(
            supporting_measurements
        )

        source_count = len(
            {
                measurement.source_system
                for measurement in supporting_measurements
            }
        )
        source_diversity = min(
            1.0,
            0.5 + (source_count * 0.25),
        )

        entity_count = len(
            {
                entity_id
                for measurement in supporting_measurements
                for entity_id in measurement.entity_ids
            }
        )
        cross_source_agreement = min(
            1.0,
            0.7 + (entity_count * 0.05),
        )

        benchmark_quality = float(
            definition.metadata.get(
                "benchmark_quality",
                1.0,
            )
        )
        historical_consistency = float(
            definition.metadata.get(
                "historical_consistency",
                1.0,
            )
        )

        factors = {
            "measurement_confidence": measurement_confidence,
            "measurement_uncertainty": uncertainty_factor,
            "source_diversity": source_diversity,
            "evidence_rule_reliability": definition.rule_reliability,
            "benchmark_quality": benchmark_quality,
            "historical_consistency": historical_consistency,
            "cross_source_agreement": cross_source_agreement,
            "validation_results": validation_factor,
        }

        value = 1.0
        for factor in factors.values():
            value *= max(
                0.0,
                min(
                    1.0,
                    factor,
                ),
            )

        value = max(
            0.0,
            min(
                1.0,
                value,
            ),
        )
        strength = value * quality * (
            1.0 + definition.severity.rank()
        ) / 5.0

        return EvidenceConfidenceScore(
            value=value,
            uncertainty=1.0 - uncertainty_factor,
            quality=quality,
            strength=strength,
            factors=factors,
            explanation=(
                "confidence = product(measurement confidence, "
                "uncertainty factor, source diversity, rule reliability, "
                "benchmark quality, historical consistency, agreement, "
                "validation factor)"
            ),
        )
