from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal

StateCode = Literal["CA", "IN", "OH"]

@dataclass(frozen=True)
class ReportingPrefs:
    emphasize_cost_compliance: bool
    emphasize_schedule_risk: bool
    emphasize_document_control: bool

@dataclass(frozen=True)
class StateProfile:
    code: StateCode
    name: str
    agencies: List[str]
    reporting: ReportingPrefs

def _ca() -> StateProfile:
    return StateProfile(
        code="CA",
        name="California",
        agencies=["Caltrans", "DGS", "OSHPD/HCAI", "Local Agencies"],
        reporting=ReportingPrefs(
            emphasize_cost_compliance=True,
            emphasize_schedule_risk=True,
            emphasize_document_control=True,
        ),
    )

def _in_() -> StateProfile:
    return StateProfile(
        code="IN",
        name="Indiana",
        agencies=["INDOT", "IDOA", "State/Local Agencies"],
        reporting=ReportingPrefs(
            emphasize_cost_compliance=True,
            emphasize_schedule_risk=True,
            emphasize_document_control=True,
        ),
    )

def _oh() -> StateProfile:
    return StateProfile(
        code="OH",
        name="Ohio",
        agencies=["Ohio DOT", "OPW/PW", "Local Agencies"],
        reporting=ReportingPrefs(
            emphasize_cost_compliance=True,
            emphasize_schedule_risk=True,
            emphasize_document_control=True,
        ),
    )

_REGISTRY: Dict[StateCode, StateProfile] = {"CA": _ca(), "IN": _in_(), "OH": _oh()}

def list_states() -> List[StateProfile]:
    return [p for _, p in sorted(_REGISTRY.items(), key=lambda kv: kv[0])]

def get_state(code: StateCode) -> StateProfile:
    if code not in _REGISTRY:
        raise KeyError(f"Unsupported state '{code}'. Supported: {', '.join(_REGISTRY.keys())}")
    return _REGISTRY[code]

