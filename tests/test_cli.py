from amt2abc.cli import main
from click.testing import CliRunner


def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "amt2abc" in result.output


def test_list():
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "AMT2ABC" in result.output
    assert "AMTs:" in result.output


def test_info_existing():
    runner = CliRunner()
    result = runner.invoke(main, ["info", "AMT_DC_THERMO_002"])
    assert result.exit_code == 0
    assert "AMT_DC_THERMO_002" in result.output
    assert "Triplets" in result.output


def test_info_json():
    runner = CliRunner()
    result = runner.invoke(
        main, ["info", "AMT_DC_THERMO_002", "--format", "json"]
    )
    assert result.exit_code == 0
    assert '"id": "AMT_DC_THERMO_002"' in result.output


def test_info_missing():
    runner = CliRunner()
    result = runner.invoke(main, ["info", "DOES_NOT_EXIST"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_graph_path():
    runner = CliRunner()
    result = runner.invoke(main, ["graph", "mold_temperature", "porosity_rate"])
    assert result.exit_code == 0
    assert "Path:" in result.output


def test_graph_no_path():
    runner = CliRunner()
    result = runner.invoke(main, ["graph", "xyz_unknown", "porosity_rate"])
    assert result.exit_code == 0
    assert "No path" in result.output


def test_compile():
    runner = CliRunner()
    result = runner.invoke(main, ["compile", "reduce porosity"])
    assert result.exit_code == 0
    assert "Goal:" in result.output
    assert "Matched AMTs" in result.output


def test_build():
    runner = CliRunner()
    result = runner.invoke(main, ["build"])
    assert result.exit_code == 0
    assert "AMTs:" in result.output
    assert "Status: OK" in result.output


def test_build_export(tmp_path):
    out = tmp_path / "graph.json"
    runner = CliRunner()
    result = runner.invoke(main, ["build", "--export", str(out)])
    assert result.exit_code == 0
    assert out.exists()


def test_goal_parse():
    runner = CliRunner()
    result = runner.invoke(main, ["goal", "reduce porosity rate"])
    assert result.exit_code == 0
    assert "Target variable: porosity" in result.output
    assert "Desired direction: decrease" in result.output


def test_abl_inspect():
    runner = CliRunner()
    result = runner.invoke(
        main, ["abl", "data/abl/reduce-porosity-loop.yaml"]
    )
    assert result.exit_code == 0
    assert "ABL: ABL_DC_POROSITY_REDUCTION" in result.output
    assert "Steps: 4" in result.output


def test_abl_json():
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["abl", "data/abl/reduce-porosity-loop.yaml", "--format", "json"],
    )
    assert result.exit_code == 0
    assert '"id": "ABL_DC_POROSITY_REDUCTION"' in result.output


def test_abl_missing_file():
    runner = CliRunner()
    result = runner.invoke(main, ["abl", "data/abl/nope.yaml"])
    assert result.exit_code != 0
    assert "Cannot read" in result.output


def test_compile_from_abl():
    runner = CliRunner()
    result = runner.invoke(
        main, ["compile", "--abl", "data/abl/reduce-porosity-loop.yaml"]
    )
    assert result.exit_code == 0
    assert "Recommended ABCs: 3" in result.output


def test_compile_requires_input():
    runner = CliRunner()
    result = runner.invoke(main, ["compile"])
    assert result.exit_code != 0
    assert "Provide GOAL text or --abl" in result.output
