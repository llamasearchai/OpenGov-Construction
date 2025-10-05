from __future__ import annotations

import pytest

from open_gov_construction.states import get_state, list_states, StateCode

def test_list_states() -> None:
    states = list_states()
    assert len(states) == 3
    codes = [s.code for s in states]
    assert codes == ["CA", "IN", "OH"]

def test_get_state_california() -> None:
    ca = get_state("CA")
    assert ca.code == "CA"
    assert ca.name == "California"
    assert "Caltrans" in ca.agencies
    assert ca.reporting.emphasize_cost_compliance is True

def test_get_state_indiana() -> None:
    indiana = get_state("IN")
    assert indiana.code == "IN"
    assert indiana.name == "Indiana"
    assert "INDOT" in indiana.agencies
    assert indiana.reporting.emphasize_schedule_risk is True

def test_get_state_ohio() -> None:
    ohio = get_state("OH")
    assert ohio.code == "OH"
    assert ohio.name == "Ohio"
    assert "Ohio DOT" in ohio.agencies
    assert ohio.reporting.emphasize_document_control is True

def test_get_state_invalid() -> None:
    with pytest.raises(KeyError, match="Unsupported state"):
        get_state("TX")  # type: ignore


