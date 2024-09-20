import pytest

from quizx import Circuit, extract_circuit, VecGraph
from helpers import assert_clifford_operators_equal


def validate_bell_state_circuit_stats(circuit: Circuit):
    stats = circuit.stats()
    assert stats.qubits() == 2
    assert stats.total() == 2
    assert stats.oneq() == 1
    assert stats.twoq() == 1
    assert stats.moreq() == 0
    assert stats.cliff() == 2
    assert stats.non_cliff() == 0


def test_load(test_assets_path, epr_qasm_string):
    c = Circuit.load(str(test_assets_path / "epr.qasm"))
    validate_bell_state_circuit_stats(c)
    assert c.to_qasm() == epr_qasm_string


def test_from_qasm(epr_qasm_string):
    c = Circuit.from_qasm(epr_qasm_string)
    validate_bell_state_circuit_stats(c)
    assert c.to_qasm() == epr_qasm_string


def test_to_qasm(test_assets_path, epr_qasm_string):
    for c in (
        Circuit.load(str(test_assets_path / "epr.qasm")),
        Circuit.from_qasm(epr_qasm_string),
    ):
        assert c.to_qasm() == epr_qasm_string


def test_to_graph(test_assets_path, epr_qasm_string, epr_graph):
    for c in (
        Circuit.load(str(test_assets_path / "epr.qasm")),
        Circuit.from_qasm(epr_qasm_string),
    ):
        g = c.to_graph()
        assert isinstance(g, VecGraph)
        assert_clifford_operators_equal(g, epr_graph)


def test_extract_circuit_working(h_0_graph, h_0_qasm_string):
    c = extract_circuit(h_0_graph)
    assert isinstance(c, Circuit)
    assert c.to_qasm() == h_0_qasm_string


@pytest.mark.xfail
def test_extract_circuit_buggy(cnot_01_graph, cnot_01_qasm_string):
    # Currently, circuit extraction is noted to be "working but buggy", so we mark this xfail to capture a buggy case
    c = extract_circuit(cnot_01_graph)
    assert isinstance(c, Circuit)
    assert c.to_qasm() == cnot_01_qasm_string
