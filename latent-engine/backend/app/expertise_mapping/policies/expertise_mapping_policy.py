from abc import ABC, abstractmethod

from app.expertise_mapping.expertise_profile import (
    ExpertiseProfile,
)


class ExpertiseMappingPolicy(
    ABC
):

    @abstractmethod
    def build_profiles(
        self,
        expertise_estimates,
    ) -> list[ExpertiseProfile]:
        pass