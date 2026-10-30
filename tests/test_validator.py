from amt2abc.compiler.validator import ABLValidator
from amt2abc.models.abl import ABL, KPI, ABLStep
from amt2abc.models.gs import GoalStatement
from amt2abc.parser.abl_parser import ABLParser


def _valid_abl() -> ABL:
    return ABL(
        id="ABL_TEST_001",
        name="Test Loop",
        domain="die_casting",
        goal=GoalStatement(
            text="reduce porosity",
            domain="die_casting",
            target_variable="porosity_rate",
            desired_direction="decrease",
            keywords=["porosity"],
        ),
        trigger="defect spike",
        actors=["operator", "engineer"],
        steps=[
            ABLStep(name="Detect", actor="operator", secp_stage="E"),
            ABLStep(name="Diagnose", actor="engineer", secp_stage="S"),
            ABLStep(name="Act", actor="operator", secp_stage="P"),
            ABLStep(name="Verify", actor="engineer", secp_stage="C"),
        ],
        kpis=[KPI(name="porosity_rate", unit="%", target=1.0)],
    )


def test_valid_abl_has_no_errors():
    report = ABLValidator().validate(_valid_abl())
    assert report.is_valid
    assert report.errors == []


def test_missing_target_is_error():
    abl = _valid_abl()
    abl.goal.target_variable = None
    report = ABLValidator().validate(abl)
    assert not report.is_valid
    assert "ABL_GOAL_MISSING_TARGET" in [f.code for f in report.errors]


def test_missing_steps_is_error():
    abl = _valid_abl()
    abl.steps = []
    report = ABLValidator().validate(abl)
    assert not report.is_valid
    assert "ABL_NO_STEPS" in [f.code for f in report.errors]


def test_missing_direction_is_warning():
    abl = _valid_abl()
    abl.goal.desired_direction = None
    report = ABLValidator().validate(abl)
    assert report.is_valid
    assert "ABL_GOAL_MISSING_DIRECTION" in [
        f.code for f in report.warnings
    ]


def test_no_trigger_and_no_kpi_warnings():
    abl = _valid_abl()
    abl.trigger = ""
    abl.kpis = []
    report = ABLValidator().validate(abl)
    codes = [f.code for f in report.warnings]
    assert "ABL_NO_TRIGGER" in codes
    assert "ABL_NO_KPI" in codes


def test_step_actor_checks():
    abl = _valid_abl()
    abl.steps.append(ABLStep(name="NoActor", secp_stage="S"))
    abl.steps.append(ABLStep(name="Stranger", actor="ghost"))
    report = ABLValidator().validate(abl)
    codes = [f.code for f in report.warnings]
    assert "ABL_STEP_NO_ACTOR" in codes
    assert "ABL_STEP_UNKNOWN_ACTOR" in codes


def test_duplicate_step_warning():
    abl = _valid_abl()
    abl.steps.append(ABLStep(name="Detect", actor="operator", secp_stage="E"))
    report = ABLValidator().validate(abl)
    assert "ABL_DUPLICATE_STEP" in [f.code for f in report.warnings]


def test_secp_incomplete_warning():
    abl = _valid_abl()
    abl.steps = [ABLStep(name="Only", actor="operator", secp_stage="E")]
    report = ABLValidator().validate(abl)
    assert "ABL_SECP_INCOMPLETE" in [f.code for f in report.warnings]


def test_domain_mismatch_warning():
    abl = _valid_abl()
    abl.goal.domain = "other_domain"
    report = ABLValidator().validate(abl)
    assert "ABL_GOAL_DOMAIN_MISMATCH" in [
        f.code for f in report.warnings
    ]


def test_kpi_not_linked_and_no_target_info():
    abl = _valid_abl()
    abl.kpis = [KPI(name="scrap_rate")]
    report = ABLValidator().validate(abl)
    codes = [f.code for f in report.findings]
    assert "ABL_KPI_NOT_LINKED_TO_GOAL" in codes
    assert "ABL_KPI_NO_TARGET" in codes


def test_report_to_dict():
    report = ABLValidator().validate(_valid_abl())
    payload = report.to_dict()
    assert payload["abl_id"] == "ABL_TEST_001"
    assert payload["valid"] is True
    assert payload["findings"] == []


def test_bundled_abl_is_valid():
    loop = ABLParser().load("data/abl/reduce-porosity-loop.yaml")
    report = ABLValidator().validate(loop)
    assert report.is_valid
    assert report.errors == []
