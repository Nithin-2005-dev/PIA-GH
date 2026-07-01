from __future__ import annotations

from dataclasses import dataclass

from app.executive.intervention_cost import InterventionCost
from app.executive.portfolio_item import PortfolioItem


@dataclass(frozen=True)
class DecisionOptimizationRequest:
    impacts: tuple[object, ...]
    costs: tuple[InterventionCost, ...]
    budget: float
    max_items: int | None = None


@dataclass(frozen=True)
class DecisionOptimizationPlan:
    selected_items: tuple[PortfolioItem, ...]
    total_expected_gain: float
    total_cost: float
    total_roi: float
    rejected_count: int


class DecisionOptimizationEngine:
    def optimize(
        self,
        request: DecisionOptimizationRequest,
    ) -> DecisionOptimizationPlan:
        candidates = self._candidates(
            request.impacts,
            request.costs,
        )
        best: tuple[PortfolioItem, ...] = ()
        best_gain = -1.0
        best_cost = 0.0

        def visit(
            index: int,
            selected: tuple[PortfolioItem, ...],
            total_gain: float,
            total_cost: float,
        ) -> None:
            nonlocal best, best_gain, best_cost
            if total_cost > request.budget:
                return
            if (
                request.max_items is not None
                and len(selected) > request.max_items
            ):
                return
            if index == len(candidates):
                if (
                    total_gain > best_gain
                    or (
                        total_gain == best_gain
                        and total_cost < best_cost
                    )
                ):
                    best = selected
                    best_gain = total_gain
                    best_cost = total_cost
                return

            candidate = candidates[index]
            visit(
                index + 1,
                selected,
                total_gain,
                total_cost,
            )
            visit(
                index + 1,
                (*selected, candidate),
                total_gain + candidate.expected_health_gain,
                total_cost + candidate.estimated_cost,
            )

        visit(
            0,
            (),
            0.0,
            0.0,
        )

        ranked = tuple(
            PortfolioItem(
                module_ref=item.module_ref,
                action=item.action,
                expected_health_gain=item.expected_health_gain,
                estimated_cost=item.estimated_cost,
                roi=item.roi,
                rank=index + 1,
            )
            for index, item in enumerate(
                sorted(
                    best,
                    key=lambda item: (
                        item.roi,
                        item.expected_health_gain,
                    ),
                    reverse=True,
                )
            )
        )
        total_gain = sum(
            item.expected_health_gain
            for item in ranked
        )
        total_cost = sum(
            item.estimated_cost
            for item in ranked
        )
        return DecisionOptimizationPlan(
            selected_items=ranked,
            total_expected_gain=total_gain,
            total_cost=total_cost,
            total_roi=(
                total_gain / total_cost
                if total_cost
                else 0.0
            ),
            rejected_count=len(candidates) - len(ranked),
        )

    def _candidates(
        self,
        impacts,
        costs,
    ) -> tuple[PortfolioItem, ...]:
        candidates = []
        for impact in impacts:
            cost = next(
                (
                    item
                    for item in costs
                    if (
                        item.action == impact.action
                        and item.module_ref.id == impact.module_ref.id
                    )
                ),
                None,
            )
            if cost is None or cost.estimated_cost <= 0:
                continue
            candidates.append(
                PortfolioItem(
                    module_ref=impact.module_ref,
                    action=impact.action,
                    expected_health_gain=impact.expected_health_gain,
                    estimated_cost=cost.estimated_cost,
                    roi=(
                        impact.expected_health_gain
                        / cost.estimated_cost
                    ),
                    rank=0,
                )
            )
        return tuple(candidates)

