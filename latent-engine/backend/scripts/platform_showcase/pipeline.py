"""Canonical PIA showcase pipeline orchestrator."""

from __future__ import annotations

import time

from .config import load_config
from .context import PlatformContext
from .stages.stage01_initialize import InitializeStage
from .stages.stage02_collection import CollectionStage
from .stages.stage03_observation import ObservationStage
from .stages.stage04_measurement import MeasurementStage
from .stages.stage05_evidence import EvidenceStage
from .stages.stage06_repository import ExpertiseStage
from .stages.stage07_knowledge import KnowledgeStage
from .stages.stage07b_graph import KnowledgeGraphStage
from .stages.stage08_org_intelligence import OrganizationIntelligenceStage
from .stages.stage09_reasoning import ReasoningStage
from .stages.stage10_decision import DecisionStage
from .stages.stage11_executive import ExecutiveDashboardStage
from .stages.stage12_validation import PipelineValidationStage
from .stages.stage13_summary import SummaryStage
from .ui import banner, stage, summary


class PlatformPipeline:
    def __init__(self):
        self.config = load_config()
        self.context = PlatformContext(
            repository=self.config.repository,
            branch=self.config.branch,
            commit_limit=self.config.commit_limit,
            github_token=self.config.github_token,
            tenant_id=self.config.tenant_id,
            output_directory=self.config.output_directory,
        )
        self.stages = [
            InitializeStage(),           # 01
            CollectionStage(),           # 02
            ObservationStage(),          # 03
            MeasurementStage(),          # 04
            EvidenceStage(),             # 05
            ExpertiseStage(),            # 06  Evidence → Expertise
            KnowledgeStage(),            # 07  Expertise → Knowledge
            KnowledgeGraphStage(),       # 07b Knowledge → Graph
            OrganizationIntelligenceStage(),  # 08  Expertise + Knowledge → Org Intel
            ReasoningStage(),            # 09  Knowledge + Org Intel → Reasoning
            DecisionStage(),             # 10  Reasoning → Decision
            ExecutiveDashboardStage(),   # 11  Decision + Org Intel → Dashboard
            PipelineValidationStage(),   # 12  Layer health checks
            SummaryStage(),              # 13  Final executive report
        ]

    def run(self):
        overall_started = time.perf_counter()
        banner()

        total = len(self.stages)
        for index, pipeline_stage in enumerate(self.stages, start=1):
            stage(index, total, pipeline_stage.name)
            started = time.perf_counter()
            pipeline_stage.run(self.context)
            finished = time.perf_counter()

            timing = self.context.stage(pipeline_stage.name)
            timing.started_at = started
            timing.finished_at = finished
            timing.duration = finished - started

        overall = time.perf_counter() - overall_started
        org = self.context.org_intelligence
        summary(
            "CANONICAL PIPELINE COMPLETE",
            [
                ("Repository",          self.context.repository),
                ("Branch",              self.context.branch),
                ("Observations",        len(self.context.observations)),
                ("Measurements",        len(self.context.measurements)),
                (
                    "Evidence",
                    len(self.context.evidence_package.evidence)
                    if self.context.evidence_package
                    else 0,
                ),
                ("Expertise Models",    len(self.context.expertise_models)),
                ("Knowledge Models",    len(self.context.knowledge)),
                ("Org Intel — Ownership",    len(org.ownership) if org else "N/A"),
                ("Org Intel — Bus Factors",  len(org.bus_factors) if org else "N/A"),
                ("Org Intel — Knowledge Risks", len(org.knowledge_risks) if org else "N/A"),
                ("Org Intel — Health",   f"{org.health.average_health:.3f}" if org else "N/A"),
                ("Org Intel — Recommendations", len(org.recommendations) if org else "N/A"),
                ("Reasoning Results",   len(self.context.reasoning_results)),
                ("Decisions",           len(self.context.decisions)),
                ("Pipeline Time",       f"{overall:.3f}s"),
            ],
        )
