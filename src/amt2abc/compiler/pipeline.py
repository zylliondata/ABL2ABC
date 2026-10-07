from typing import Any, Dict, List, Tuple

from amt2abc.compiler.graph import AMTGraph
from amt2abc.compiler.matcher import GraphMatcher
from amt2abc.models.abc import ABC
from amt2abc.models.amt import AMT
from amt2abc.parser.abc_parser import ABCParser
from amt2abc.parser.amt_parser import AMTParser
from amt2abc.parser.gs_parser import GSParser


class CompilerPipeline:
    def __init__(
        self,
        amt_dir: str = "data/amt",
        abc_dir: str = "data/abc",
    ) -> None:
        self.amts = AMTParser(amt_dir).load_all()
        self.graph = AMTGraph()
        self.graph.build(self.amts)
        self.matcher = GraphMatcher(self.amts, self.graph)
        self.abcs: List[ABC] = ABCParser(abc_dir).load_all()
        self._abc_index = self._index_abcs(self.abcs)

    def _index_abcs(self, abcs: List[ABC]) -> Dict[str, List[ABC]]:
        index: Dict[str, List[ABC]] = {}
        for abc in abcs:
            for amt_id in abc.source_amts:
                index.setdefault(amt_id, []).append(abc)
        return index

    def _recommend_abcs(
        self, matched: List[Tuple[AMT, float]]
    ) -> List[Dict[str, Any]]:
        amt_score = {amt.id: score for amt, score in matched}
        agg: Dict[str, Dict[str, Any]] = {}
        for amt_id, score in amt_score.items():
            for abc in self._abc_index.get(amt_id, []):
                entry = agg.setdefault(
                    abc.id,
                    {
                        "id": abc.id,
                        "name": abc.name,
                        "category": abc.category,
                        "industry": abc.industry,
                        "source_amts": [],
                        "score": 0.0,
                        "matched_amts": 0,
                    },
                )
                entry["source_amts"].append(amt_id)
                entry["score"] += score
                entry["matched_amts"] += 1
        recommended = sorted(
            agg.values(), key=lambda x: (-x["score"], x["id"])
        )
        for entry in recommended:
            entry["source_amts"].sort()
            entry["score"] = round(entry["score"], 3)
            entry["avg_amt_score"] = round(
                entry["score"] / max(entry["matched_amts"], 1), 3
            )
        return recommended

    def compile(self, goal_text: str) -> Dict[str, Any]:
        goal = GSParser().parse_text(goal_text)
        matches = self.matcher.match(goal)
        subgraph = self.matcher.influencing_subgraph(goal)
        recommended = self._recommend_abcs(matches)
        return {
            "goal": goal_text,
            "target_variable": goal.target_variable,
            "desired_direction": goal.desired_direction,
            "matched_amts": [
                {"id": amt.id, "name": amt.name, "score": round(s, 3)}
                for amt, s in matches
            ],
            "influencing_subgraph": subgraph,
            "recommended_abcs": recommended,
        }
