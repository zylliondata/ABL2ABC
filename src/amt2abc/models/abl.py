from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from amt2abc.models.gs import GoalStatement


class ABLStep(BaseModel):
    """A single activity inside an Atomic Business Loop."""

    name: str = Field(description="Step name, e.g. 'Detect porosity spike'")
    actor: Optional[str] = Field(
        default=None,
        description="Role or system performing the step",
    )
    description: str = Field(default="")
    secp_stage: Optional[Literal["S", "E", "C", "P"]] = Field(
        default=None,
        description="Which SECP dimension this step belongs to",
    )


class KPI(BaseModel):
    """Key performance indicator tracked by a business loop."""

    name: str = Field(description="Metric name, e.g. 'porosity_rate'")
    unit: str = Field(default="")
    target: Optional[float] = Field(default=None)
    direction: Optional[Literal["increase", "decrease"]] = Field(default=None)


class ABL(BaseModel):
    """Atomic Business Loop: the business-level input to the compiler."""

    id: str = Field(description="Unique identifier, e.g. 'ABL_DC_POROSITY_REDUCTION'")
    name: str = Field(description="Human-readable loop name")
    domain: str = Field(default="", description="Industry domain, e.g. 'die_casting'")
    goal: GoalStatement = Field(description="Business goal driving the loop")
    trigger: str = Field(default="", description="Event that starts the loop")
    steps: List[ABLStep] = Field(default_factory=list)
    actors: List[str] = Field(default_factory=list)
    kpis: List[KPI] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)
    source: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)
