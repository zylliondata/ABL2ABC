from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

from amt2abc.models.abl import ABL

ERROR = "error"
WARNING = "warning"
INFO = "info"

REQUIRED_SECP_STAGES: Set[str] = {"S", "E", "C", "P"}


@dataclass
class Finding:
    level: str
    code: str
    message: str


@dataclass
class ABLValidationReport:
    abl_id: str
    findings: List[Finding] = field(default_factory=list)

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self.findings if f.level == ERROR]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.level == WARNING]

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "abl_id": self.abl_id,
            "valid": self.is_valid,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "findings": [
                {"level": f.level, "code": f.code, "message": f.message}
                for f in self.findings
            ],
        }


class ABLValidator:
    """Checks that an ABL is complete enough to drive the compiler."""

    def validate(self, abl: ABL) -> ABLValidationReport:
        report = ABLValidationReport(abl_id=abl.id)
        self._check_goal(abl, report)
        self._check_steps(abl, report)
        self._check_secp_coverage(abl, report)
        self._check_kpis(abl, report)
        return report

    def _check_goal(
        self, abl: ABL, report: ABLValidationReport
    ) -> None:
        goal = abl.goal
        if not goal.target_variable:
            report.findings.append(
                Finding(
                    ERROR,
                    "ABL_GOAL_MISSING_TARGET",
                    "Goal has no target_variable; graph matching will "
                    "fall back to keywords only",
                )
            )
        if not goal.desired_direction:
            report.findings.append(
                Finding(
                    WARNING,
                    "ABL_GOAL_MISSING_DIRECTION",
                    "Goal has no desired_direction (increase/decrease)",
                )
            )
        if not goal.keywords:
            report.findings.append(
                Finding(
                    INFO,
                    "ABL_GOAL_MISSING_KEYWORDS",
                    "Goal has no keywords; matching precision may drop",
                )
            )
        if (
            goal.domain
            and abl.domain
            and goal.domain != abl.domain
        ):
            report.findings.append(
                Finding(
                    WARNING,
                    "ABL_GOAL_DOMAIN_MISMATCH",
                    f"Goal domain '{goal.domain}' differs from ABL "
                    f"domain '{abl.domain}'",
                )
            )

    def _check_steps(
        self, abl: ABL, report: ABLValidationReport
    ) -> None:
        if not abl.steps:
            report.findings.append(
                Finding(
                    ERROR,
                    "ABL_NO_STEPS",
                    "ABL has no business steps",
                )
            )
        if not abl.trigger:
            report.findings.append(
                Finding(
                    WARNING,
                    "ABL_NO_TRIGGER",
                    "ABL has no trigger event",
                )
            )

        known_actors = set(abl.actors)
        seen: Set[str] = set()
        for step in abl.steps:
            if step.name in seen:
                report.findings.append(
                    Finding(
                        WARNING,
                        "ABL_DUPLICATE_STEP",
                        f"Duplicate step name '{step.name}'",
                    )
                )
            seen.add(step.name)
            if not step.actor:
                report.findings.append(
                    Finding(
                        WARNING,
                        "ABL_STEP_NO_ACTOR",
                        f"Step '{step.name}' has no actor",
                    )
                )
            elif known_actors and step.actor not in known_actors:
                report.findings.append(
                    Finding(
                        WARNING,
                        "ABL_STEP_UNKNOWN_ACTOR",
                        f"Step '{step.name}' uses actor '{step.actor}' "
                        "not listed in actors",
                    )
                )
            if not step.secp_stage:
                report.findings.append(
                    Finding(
                        INFO,
                        "ABL_STEP_NO_SECP_STAGE",
                        f"Step '{step.name}' has no SECP stage",
                    )
                )

    def _check_secp_coverage(
        self, abl: ABL, report: ABLValidationReport
    ) -> None:
        stages = {
            step.secp_stage for step in abl.steps if step.secp_stage
        }
        missing = REQUIRED_SECP_STAGES - stages
        if abl.steps and missing:
            report.findings.append(
                Finding(
                    WARNING,
                    "ABL_SECP_INCOMPLETE",
                    "Business loop does not cover SECP stages: "
                    + ", ".join(sorted(missing)),
                )
            )

    def _check_kpis(
        self, abl: ABL, report: ABLValidationReport
    ) -> None:
        if not abl.kpis:
            report.findings.append(
                Finding(
                    WARNING,
                    "ABL_NO_KPI",
                    "ABL defines no KPIs; loop closure cannot be measured",
                )
            )
            return
        target = abl.goal.target_variable
        if target:
            names = {k.name for k in abl.kpis}
            related = any(
                target in name or name in target for name in names
            )
            if not related:
                report.findings.append(
                    Finding(
                        INFO,
                        "ABL_KPI_NOT_LINKED_TO_GOAL",
                        f"No KPI name relates to goal target "
                        f"'{target}'",
                    )
                )
        for kpi in abl.kpis:
            if kpi.target is None:
                report.findings.append(
                    Finding(
                        INFO,
                        "ABL_KPI_NO_TARGET",
                        f"KPI '{kpi.name}' has no numeric target",
                    )
                )
