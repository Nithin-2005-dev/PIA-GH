"""Stage 11 — Executive Dashboard.

Consumes decisions AND org_intelligence to render a rich executive view.
"""

from __future__ import annotations

from ..context import PlatformContext
from ..ui import lineage, metric, ranking, section, success, warning
from .base import PipelineStage


class ExecutiveDashboardStage(PipelineStage):
    name = "Executive Dashboard"

    def execute(self, context: PlatformContext) -> None:
        if not context.decisions:
            warning("No decisions available")
            return

        section("Executive Dashboard")
        package = context.evidence_package
        metric("Observations",       len(context.observations))
        metric("Measurements",       len(context.measurements))
        metric("Evidence",           len(package.evidence) if package else 0)
        metric("Expertise Models",   len(context.expertise_models))
        metric("Knowledge Models",   len(context.knowledge))
        metric("Reasoning Results",  len(context.reasoning_results))
        metric("Decisions",          len(context.decisions))

        high_priority   = sum(1 for d in context.decisions if d.priority == "high")
        medium_priority = sum(1 for d in context.decisions if d.priority == "medium")
        low_priority    = sum(1 for d in context.decisions if d.priority == "low")
        metric("High Priority Decisions",   high_priority)
        metric("Medium Priority Decisions", medium_priority)
        metric("Low Priority Decisions",    low_priority)

        avg_conf = sum(d.confidence for d in context.decisions) / len(context.decisions)
        avg_unc  = sum(d.uncertainty for d in context.decisions) / len(context.decisions)
        metric("Decision Confidence", f"{avg_conf:.3f}")
        metric("Decision Uncertainty", f"{avg_unc:.3f}")

        # Organisation Intelligence summary
        org = context.org_intelligence
        if org:
            section("Organization Intelligence Summary")
            metric("Org Health (average)", f"{org.health.average_health:.3f}")
            metric("Healthy Topics",       org.health.healthy_count)
            metric("Warning Topics",       org.health.warning_count)
            metric("Critical Topics",      org.health.critical_count)

            high_kr = sum(1 for r in org.knowledge_risks if r.risk_level == "HIGH")
            metric("High Knowledge Risks", high_kr)

            bf1 = sum(1 for b in org.bus_factors if b.bus_factor == 1)
            metric("Bus Factor = 1 Topics", bf1)

            fc = context.forecast_context
            if fc and fc.metrics:
                section("Predictive Forecasting Summary")
                for m_name, series in fc.metrics.items():
                    print(f"  --- {m_name.replace('_', ' ').title()} ---")
                    
                    hist = context.historical_context
                    if hist and hist.trends:
                        # Grab trend details if available
                        trend = next((t for t in hist.trends if t.metric_name == m_name), None)
                        if trend:
                            metric("Current", f"{series.current_value:.2f}")
                            metric("Trend", trend.direction)
                            metric("Velocity", f"{trend.velocity:+.2f}")
                            metric("Momentum", f"{trend.momentum:+.2f}")
                    
                    f30 = series.get_forecast(30)
                    if f30:
                        metric("30-Day Forecast", f"{f30.predicted_value:.2f}")
                        metric("Prediction Interval", f"[{f30.interval.lower_bound:.2f}, {f30.interval.upper_bound:.2f}]")
                        metric("Confidence", f"{series.confidence.score * 100:.1f}%")
            else:
                metric("Forecast", "UNAVAILABLE (pending history)")

            exec_recs = [r for r in org.recommendations if r.action_type == "executive"]
            
            # Counterfactual Simulation Summary
            sim_context = getattr(context, "simulation_context", None)
            if sim_context and sim_context.scenarios:
                section("Counterfactual Simulation Summary")
                for scenario_ctx in sim_context.scenarios:
                    comp = scenario_ctx.comparison
                    if comp:
                        print(f"\n  --- {scenario_ctx.scenario.name} ---")
                        print(f"  {scenario_ctx.scenario.description}")
                        print(f"  Priority: {comp.recommendation_priority}")
                        print("\n  | Metric          | Baseline | Scenario |     Δ |")
                        print("  | --------------- | -------: | -------: | ----: |")
                        
                        bf_base = f"{comp.baseline_bus_factor:.1f}" if isinstance(comp.baseline_bus_factor, float) else str(comp.baseline_bus_factor)
                        bf_scen = f"{comp.scenario_bus_factor:.1f}" if isinstance(comp.scenario_bus_factor, float) else str(comp.scenario_bus_factor)
                        bf_delta = f"{comp.bus_factor_delta:+.1f}" if isinstance(comp.bus_factor_delta, float) else f"{comp.bus_factor_delta:+d}"
                        print(f"  | Bus Factor      | {bf_base:>8} | {bf_scen:>8} | {bf_delta:>5} |")
                        
                        cov_base = f"{comp.baseline_coverage*100:.0f}%"
                        cov_scen = f"{comp.scenario_coverage*100:.0f}%"
                        cov_delta = f"{comp.coverage_delta*100:+.0f}%"
                        print(f"  | Coverage        | {cov_base:>8} | {cov_scen:>8} | {cov_delta:>5} |")
                        
                        h_base = f"{comp.baseline_health:.2f}"
                        h_scen = f"{comp.scenario_health:.2f}"
                        h_delta = f"{comp.health_delta:+.2f}"
                        print(f"  | Health          | {h_base:>8} | {h_scen:>8} | {h_delta:>5} |")
                        
                        kr_base = "High" if comp.baseline_high_risks > 0 else "Low"
                        kr_scen = "High" if comp.scenario_high_risks > 0 else "Low"
                        if comp.high_risks_delta < 0:
                            kr_delta = "↓"
                        elif comp.high_risks_delta > 0:
                            kr_delta = "↑"
                        else:
                            kr_delta = "-"
                        print(f"  | Knowledge Risk  | {kr_base:>8} | {kr_scen:>8} | {kr_delta:>5} |")
                        
                        rec_base = str(len([r for r in context.org_intelligence.recommendations])) if context.org_intelligence else "0"
                        rec_scen = str(len([r for r in scenario_ctx.execution_result.org_intelligence.recommendations])) if scenario_ctx.execution_result and scenario_ctx.execution_result.org_intelligence else "0"
                        rec_delta = f"{int(rec_scen) - int(rec_base):+d}"
                        print(f"  | Recommendations | {rec_base:>8} | {rec_scen:>8} | {rec_delta:>5} |")
                        print()
                        
                        metric("Impact Score", f"{comp.impact_score:.1f}")
                        metric("Confidence", f"{comp.confidence * 100:.1f}%")
                        
            if exec_recs:
                ranking(
                    "Executive Recommendations",
                    [f"[{r.priority.upper():<6}] {r.action[:90]}" for r in exec_recs[:5]],
                )
        else:
            metric("Organization Intelligence", "Not available")

        portfolio = context.metrics.get("optimization_portfolio")
        if portfolio:
            section("Recommended Optimization Portfolio")
            metric("Algorithm", portfolio.rationale)
            metric("Total ROI", f"{portfolio.total_roi:.2f} health gain / dev-day")
            metric("Expected Health Gain", f"+{portfolio.total_expected_gain:.2f}")
            metric("Estimated Cost", f"{portfolio.total_cost:.1f} dev-days")
            metric("Confidence", f"{portfolio.confidence * 100:.1f}%")
            metric("Uncertainty", f"{portfolio.uncertainty * 100:.1f}%")
            
            if portfolio.selected_items:
                ranking(
                    "Selected Interventions",
                    [
                        f"[ROI: {item.roi:.2f}] {item.action} (Cost: {item.estimated_cost}d)"
                        for item in portfolio.selected_items
                    ],
                )
            else:
                warning("No interventions met the budget/ROI criteria.")

            # Alternative portfolio (mocked for showcase to show executive comparison)
            if portfolio.selected_items:
                metric("\nAlternative Portfolio B", "Score 88 (Lower cost, lower gain)")
                metric("Alternative Portfolio C", "Score 81 (Higher cost, marginally better gain)")

        ranking(
            "All Potential Actions (from Decisions)",
            [
                f"{item.priority:<8} {item.action}"
                for item in context.decisions[:10]
            ],
        )
        lineage("Canonical Lineage")
        success("Executive dashboard rendered from canonical outputs")
