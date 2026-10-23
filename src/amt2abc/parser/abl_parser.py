from pathlib import Path
from typing import Any, Dict, List

import yaml  # type: ignore[import-untyped]

from amt2abc.models.abl import ABL


class ABLParseError(Exception):
    """Raised when an ABL YAML file cannot be parsed or validated."""


class ABLParser:
    def __init__(
        self,
        data_dir: str = "data/abl",
        strict: bool = True,
    ) -> None:
        self.data_dir = Path(data_dir)
        self.strict = strict

    def load_all(self) -> List[ABL]:
        abls: List[ABL] = []
        if not self.data_dir.exists():
            return abls
        for file in sorted(self.data_dir.glob("*.yaml")):
            abls.append(self.load(str(file)))
        return abls

    def load(self, path: str) -> ABL:
        p = Path(path)
        try:
            with p.open(encoding="utf-8") as f:
                raw = self._parse(f.read())
        except OSError as exc:
            raise ABLParseError(f"Cannot read {p}: {exc}") from exc
        try:
            return ABL(**raw)
        except Exception as exc:
            if self.strict:
                raise ABLParseError(
                    f"Invalid ABL in {p}: {exc}"
                ) from exc
            raise

    def load_text(self, text: str) -> ABL:
        raw = self._parse(text)
        try:
            return ABL(**raw)
        except Exception as exc:
            if self.strict:
                raise ABLParseError(f"Invalid ABL: {exc}") from exc
            raise

    def _parse(self, text: str) -> Dict[str, Any]:
        try:
            raw = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ABLParseError(f"Invalid YAML: {exc}") from exc
        if not isinstance(raw, dict):
            raise ABLParseError("ABL document must be a mapping")
        return raw
