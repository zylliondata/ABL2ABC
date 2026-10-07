from amt2abc.compiler.graph import AMTGraph
from amt2abc.compiler.matcher import GoalMatcher, GraphMatcher
from amt2abc.compiler.pipeline import CompilerPipeline
from amt2abc.models.abc import ABC
from amt2abc.models.amt import AMT, Triplet
from amt2abc.models.gs import GoalStatement


def _amt(amt_id, triplets, name="test", domain="test"):
    return AMT(
        id=amt_id,
        name=name,
        domain=domain,
        triplets=[
            Triplet(
                cause=c,
                effect=e,
                relation=r,
                mechanism="m",
            )
            for c, e, r in triplets
        ],
    )


def test_graph_build():
    amt = _amt("g001", [("temp", "porosity", "increases")])
    graph = AMTGraph()
    graph.build([amt])
    assert graph.graph.has_edge("temp", "porosity")
    assert graph.amt_graph.has_node("g001")


def test_graph_find_path():
    amt = _amt(
        "g001",
        [
            ("a", "b", "increases"),
            ("b", "c", "increases"),
        ],
    )
    graph = AMTGraph()
    graph.build([amt])
    assert graph.find_path("a", "c") == ["a", "b", "c"]
    assert graph.find_path("c", "a") == []
    assert graph.find_path("missing", "a") == []


def test_graph_amt_linking():
    up = _amt("up", [("a", "shared", "increases")])
    down = _amt("down", [("shared", "b", "increases")])
    graph = AMTGraph()
    graph.build([up, down])
    assert graph.amt_graph.has_edge("up", "down")
    assert graph.amt_edge_details() == [("up", "down", "shared")]
    assert graph.find_amt_path("up", "down") == ["up", "down"]


def test_graph_upstream_downstream():
    amt = _amt(
        "g001",
        [
            ("a", "b", "increases"),
            ("b", "c", "increases"),
        ],
    )
    graph = AMTGraph()
    graph.build([amt])
    assert graph.upstream("c") == ["a", "b"]
    assert graph.downstream("a") == ["b", "c"]
    assert graph.upstream("unknown") == []


def test_graph_amts_causing():
    amt = _amt("m1", [("temp", "porosity", "increases")])
    graph = AMTGraph()
    graph.build([amt])
    assert graph.amts_causing("porosity") == ["m1"]
    assert graph.amts_caused_by("temp") == ["m1"]


def test_graph_connected_components():
    a = _amt("a", [("x1", "x2", "increases")])
    b = _amt("b", [("y1", "y2", "increases")])
    graph = AMTGraph()
    graph.build([a, b])
    components = graph.connected_components()
    assert len(components) == 2


def test_graph_subgraph():
    amt = _amt(
        "g001",
        [
            ("a", "b", "increases"),
            ("c", "d", "increases"),
        ],
    )
    graph = AMTGraph()
    graph.build([amt])
    sub = graph.subgraph(["a", "b"])
    assert set(sub.graph.nodes) == {"a", "b"}
    assert "c" not in sub.graph.nodes


def test_graph_stats_and_dict():
    amt = _amt("g001", [("a", "b", "increases")])
    graph = AMTGraph()
    graph.build([amt])
    stats = graph.stats()
    assert stats["variables"] == 2
    assert stats["variable_edges"] == 1
    assert stats["amts"] == 1
    data = graph.to_dict()
    assert "a" in data["variables"]
    assert data["amt_nodes"] == ["g001"]


def test_matcher_score():
    amt = AMT(
        id="m001",
        name="temperature control",
        domain="test",
        triplets=[
            Triplet(
                cause="temp",
                effect="porosity",
                relation="increases",
                mechanism="thermal",
            ),
        ],
        tags=["porosity", "mold"],
    )
    goal = GoalStatement(text="reduce porosity", keywords=["porosity"])
    matcher = GoalMatcher([amt])
    matches = matcher.match(goal)
    assert len(matches) == 1
    assert matches[0][0].id == "m001"


def test_pipeline_no_data(tmp_path):
    pipeline = CompilerPipeline(amt_dir=str(tmp_path))
    result = pipeline.compile("reduce porosity")
    assert result["goal"] == "reduce porosity"
    assert result["matched_amts"] == []


def test_pipeline_recommends_abcs():
    pipeline = CompilerPipeline()  # uses data/amt + data/abc defaults
    result = pipeline.compile("reduce porosity rate")
    assert len(result["matched_amts"]) == 3
    assert len(result["recommended_abcs"]) == 3
    abcs = {a["id"]: a for a in result["recommended_abcs"]}
    assert "mold-temperature-control" in abcs
    assert abcs["mold-temperature-control"]["source_amts"] == [
        "AMT_DC_THERMO_002"
    ]
    assert abcs["mold-temperature-control"]["matched_amts"] == 1
    assert abcs["mold-temperature-control"]["category"] == "control"


def test_pipeline_recommend_sums_scores():
    amt_a = AMT(
        id="m1",
        name="temp control",
        domain="test",
        triplets=[Triplet(cause="temp", effect="defect", relation="increases", mechanism="m")],
    )
    amt_b = AMT(
        id="m2",
        name="vacuum control",
        domain="test",
        triplets=[Triplet(cause="vacuum", effect="defect", relation="decreases", mechanism="m")],
    )
    abc = ABC(
        id="abc1",
        name="Defect Control ABC",
        category="control",
        industry="test",
        source_amts=["m1", "m2"],
    )
    pipeline = CompilerPipeline(amt_dir="data/amt")
    pipeline._amts = [amt_a, amt_b]
    pipeline._abc_index = pipeline._index_abcs([abc])
    recommended = pipeline._recommend_abcs([(amt_a, 0.8), (amt_b, 0.3)])
    assert recommended == [
        {
            "id": "abc1",
            "name": "Defect Control ABC",
            "category": "control",
            "industry": "test",
            "source_amts": ["m1", "m2"],
            "score": 1.1,
            "matched_amts": 2,
            "avg_amt_score": 0.55,
        }
    ]


def test_graph_matcher_target_resolution():
    amt = _amt(
        "m1",
        [("mold_temperature", "porosity_rate", "increases")],
    )
    graph = AMTGraph()
    graph.build([amt])
    matcher = GraphMatcher([amt], graph)
    assert matcher.resolve_target("porosity_rate") == "porosity_rate"
    assert matcher.resolve_target("porosity") == "porosity_rate"
    assert matcher.resolve_target("mold") == "mold_temperature"
    assert matcher.resolve_target("unknown") is None


def test_graph_matcher_direct_ranks_higher():
    direct = _amt("direct", [("temp", "porosity_rate", "increases")])
    unrelated = _amt("unrelated", [("a", "b", "increases")])
    graph = AMTGraph()
    graph.build([direct, unrelated])
    matcher = GraphMatcher([direct, unrelated], graph)
    goal = GoalStatement(
        text="reduce porosity",
        target_variable="porosity",
        desired_direction="decrease",
        keywords=["porosity", "improve"],
    )
    matches = matcher.match(goal)
    assert len(matches) == 1
    assert matches[0][0].id == "direct"


def test_graph_matcher_handles_unmatched_target():
    amt = _amt("m1", [("temp", "porosity", "increases")], name="porosity fix")
    matcher = GraphMatcher([amt])
    goal = GoalStatement(
        text="reduce porosity",
        target_variable="nonexistent_var",
        desired_direction="decrease",
        keywords=["porosity"],
    )
    matches = matcher.match(goal)
    assert matches[0][0].id == "m1"


def test_graph_matcher_fallback_without_target():
    amt = _amt("m1", [("temp", "porosity", "increases")], name="porosity fix")
    matcher = GraphMatcher([amt])
    goal = GoalStatement(text="fix porosity", keywords=["porosity"])
    matches = matcher.match(goal)
    assert matches[0][0].id == "m1"


def test_graph_matcher_influencing_subgraph():
    probe = _amt(
        "probe",
        [("probe_var", "shared", "increases")],
    )
    target = _amt(
        "target",
        [("shared", "final_var", "increases")],
    )
    graph = AMTGraph()
    graph.build([probe, target])
    matcher = GraphMatcher([probe, target], graph)
    sub = matcher.influencing_subgraph(
        GoalStatement(
            text="improve final_var",
            target_variable="final_var",
            keywords=["final_var"],
        )
    )
    assert sub["target"] == "final_var"
    assert set(sub["amts"]) == {"probe", "target"}
    assert sub["edges"] == [
        {"from": "probe", "to": "target", "via": "shared"}
    ]


def test_graph_matcher_subgraph_with_no_target():
    matcher = GraphMatcher([])
    sub = matcher.influencing_subgraph(
        GoalStatement(text="hello", keywords=[])
    )
    assert sub["target"] is None
    assert sub["amts"] == []
