import pytest
from amt2abc.models.abl import ABL, KPI, ABLStep
from amt2abc.models.gs import GoalStatement
from amt2abc.parser.abl_parser import ABLParseError, ABLParser


def test_load_bundled_abl():
    loop = ABLParser().load("data/abl/reduce-porosity-loop.yaml")
    assert loop.id == "ABL_DC_POROSITY_REDUCTION"
    assert loop.domain == "die_casting"
    assert loop.goal.text.startswith("Reduce porosity rate")
    assert loop.goal.target_variable == "porosity_rate"
    assert len(loop.steps) == 4
    assert len(loop.actors) == 3
    assert {k.name for k in loop.kpis} == {"porosity_rate", "scrap_rate"}


def test_load_all_from_data_dir():
    loops = ABLParser(data_dir="data/abl").load_all()
    assert len(loops) >= 1
    assert loops[0].id == "ABL_DC_POROSITY_REDUCTION"


def test_load_all_missing_dir(tmp_path):
    assert ABLParser(data_dir=str(tmp_path / "missing")).load_all() == []


def test_load_text_with_steps_and_kpis():
    text = """
id: ABL_TEST_001
name: Test Loop
domain: test
goal:
  text: reduce defects
  target_variable: defects
  desired_direction: decrease
trigger: defect spike
steps:
  - name: Detect
    actor: operator
    secp_stage: E
kpis:
  - name: defect_rate
    unit: "%"
    direction: decrease
"""
    loop = ABLParser().load_text(text)
    assert isinstance(loop.goal, GoalStatement)
    assert loop.steps[0].secp_stage == "E"
    assert loop.kpis[0].direction == "decrease"


def test_load_invalid_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("id: [unclosed", encoding="utf-8")
    with pytest.raises(ABLParseError):
        ABLParser().load(str(path))


def test_load_missing_file():
    with pytest.raises(ABLParseError):
        ABLParser().load("data/abl/does-not-exist.yaml")


def test_load_not_mapping():
    with pytest.raises(ABLParseError):
        ABLParser().load_text("- just\n- a\n- list")


def test_abl_requires_goal():
    with pytest.raises(ABLParseError):
        ABLParser().load_text("id: ABL_X\nname: X")


def test_abl_models_direct():
    loop = ABL(
        id="ABL_X",
        name="Loop X",
        goal=GoalStatement(text="improve quality"),
        steps=[ABLStep(name="Step 1", secp_stage="S")],
        kpis=[KPI(name="quality", unit="%", target=99.0)],
    )
    assert loop.steps[0].name == "Step 1"
    assert loop.kpis[0].target == 99.0
