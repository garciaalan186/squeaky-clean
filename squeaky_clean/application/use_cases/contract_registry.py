"""ContractRegistry: filesystem-backed registry of cross-service Contracts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast

from squeaky_clean.application.dtos.contract import Contract
from squeaky_clean.application.dtos.contract_field import ContractField

_REPO_ROOT: Path = Path(__file__).resolve().parents[3]
_DEFAULT_ROOT: Path = _REPO_ROOT / "eval" / "contracts"


class ContractRegistry:
    """Loads + writes cross-service Contracts as JSON under eval/contracts/."""

    def __init__(self, root: Path | None = None) -> None:
        self._root: Path = root if root is not None else _DEFAULT_ROOT

    @property
    def root(self) -> Path:
        return self._root

    def lookup(self, name: str) -> Contract | None:
        """Return the Contract named ``name`` or None if unregistered."""
        path = self._path_for(name)
        if not path.is_file():
            return None
        return self._parse(json.loads(path.read_text()))

    def register(self, contract: Contract) -> Path:
        """Write ``contract`` to disk and return the resulting JSON path."""
        self._root.mkdir(parents=True, exist_ok=True)
        path = self._path_for(contract.name)
        path.write_text(json.dumps(self._dump(contract), indent=2))
        return path

    def all_contracts(self) -> tuple[Contract, ...]:
        """Return all registered contracts in deterministic name order."""
        if not self._root.is_dir():
            return ()
        files = sorted(self._root.glob("*.json"))
        return tuple(self._parse(json.loads(p.read_text())) for p in files)

    def _path_for(self, name: str) -> Path:
        return self._root / f"{name}.json"

    @staticmethod
    def _parse(raw: object) -> Contract:
        d = cast(dict[str, object], raw)
        fields_raw = cast(list[dict[str, object]], d.get("fields") or [])
        fields = tuple(
            ContractField(name=str(f.get("name") or ""),
                          type=str(f.get("type") or ""),
                          required=bool(f.get("required", True)))
            for f in fields_raw)
        producer = d.get("producer_problem_id")
        return Contract(
            name=str(d.get("name") or ""),
            transport=str(d.get("transport") or ""),
            fields=fields,
            producer_problem_id=str(producer) if producer is not None else None,
        )

    @staticmethod
    def _dump(c: Contract) -> dict[str, object]:
        return {"name": c.name, "transport": c.transport,
                "fields": [{"name": f.name, "type": f.type,
                            "required": f.required} for f in c.fields],
                "producer_problem_id": c.producer_problem_id}
