from app.domain.evidence import Evidence
from app.domain.expertise_estimate import ExpertiseEstimate

from .latent_state_estimator import LatentStateEstimator
from .policies.evidence_scoring_policy import EvidenceScoringPolicy
from .estimation_context import EstimationContext


class ExpertiseEstimator(
    LatentStateEstimator[ExpertiseEstimate]
):

    def __init__(
        self,
        scoring_policy: EvidenceScoringPolicy,
    ):
        self._policy = scoring_policy

    def estimate(
        self,
        current: ExpertiseEstimate,
        evidence: Evidence,
        context: EstimationContext,
    ) -> ExpertiseEstimate:

        raise NotImplementedError