import pytest
import pyzx as zx
import quizx._quizx as _quizx
from fractions import Fraction
from cmath import isclose
from quizx import VecGraph
from quizx.simplify import clifford_simp
from helpers import assert_clifford_operators_equal


def test_get_raw_graph():
    g = VecGraph()
    assert isinstance(g.get_raw_graph(), _quizx.VecGraph)


def test_from_raw_graph():
    _g = _quizx.VecGraph()
    g = VecGraph.from_raw_graph(_g)
    assert_clifford_operators_equal(g, VecGraph())


def test_vindex(h_0_graph):
    # this graph has four vertices, labelled 0, 1, 2, 3, so the next one should be 4
    assert h_0_graph.vindex() == 4


def test_depth(epr_graph):
    # this graph is laid out with inputs in row -1, spiders in row 0, and outputs in row 1
    assert epr_graph.depth() == 1


def test_qubit_count(cnot_01_graph):
    assert cnot_01_graph.qubit_count() == 2


def test_add_vertices(h_0_graph):
    assert h_0_graph.num_vertices() == 4
    assert h_0_graph.num_edges() == 2
    h_0_graph.add_vertices(3)
    assert h_0_graph.num_vertices() == 7
    assert h_0_graph.num_edges() == 2
    for v in range(4, 7):
        assert h_0_graph.type(v) == zx.VertexType.BOUNDARY


def test_add_edges(cnot_01_graph):
    cnot_01_graph.add_edges([(0, 5), (1, 4)])
    cnot_01_graph.add_edges([(3, 4), (2, 5)], edgetype=zx.EdgeType.HADAMARD)

    expected_edges = {
        (0, 4),  # input 0 to CNOT control
        (1, 5),  # input 1 to CNOT target
        (4, 5),  # CNOT control to CNOT target
        (2, 4),  # CNOT control to output 0
        (3, 5),  # CNOT target to output 1
        # new simple edges
        (0, 5),
        (1, 4),
        # new Hadamard edges
        (3, 4),
        (2, 5),
    }
    assert cnot_01_graph.edge_set() == expected_edges

    assert cnot_01_graph.edge_type((0, 5)) == zx.EdgeType.SIMPLE
    assert cnot_01_graph.edge_type((1, 4)) == zx.EdgeType.SIMPLE
    assert cnot_01_graph.edge_type((3, 4)) == zx.EdgeType.HADAMARD
    assert cnot_01_graph.edge_type((2, 5)) == zx.EdgeType.HADAMARD


def test_remove_vertices(cnot_01_graph):
    cnot_01_graph.remove_vertices((0, 4))
    assert list(cnot_01_graph.vertices()) == [1, 2, 3, 5]
    expected_edges = {
        (1, 5),  # input 1 to CNOT target
        (3, 5),  # CNOT target to output 1
    }
    assert cnot_01_graph.edge_set() == expected_edges


def test_remove_vertex(cnot_01_graph):
    cnot_01_graph.remove_vertex(0)
    assert list(cnot_01_graph.vertices()) == [1, 2, 3, 4, 5]
    expected_edges = {
        (1, 5),  # input 1 to CNOT target
        (4, 5),  # CNOT control to CNOT target
        (2, 4),  # CNOT control to output 0
        (3, 5),  # CNOT target to output 1
    }
    assert cnot_01_graph.edge_set() == expected_edges


def test_remove_edges(cnot_01_graph):
    cnot_01_graph.remove_edges([(2, 4), (4, 5)])

    expected_edges = {
        (0, 4),  # input 0 to CNOT control
        (1, 5),  # input 1 to CNOT target
        (3, 5),  # CNOT target to output 1
    }
    assert cnot_01_graph.edge_set() == expected_edges


def test_remove_edge(cnot_01_graph):
    cnot_01_graph.remove_edge((2, 4))

    expected_edges = {
        (0, 4),  # input 0 to CNOT control
        (1, 5),  # input 1 to CNOT target
        (4, 5),  # CNOT control to CNOT target
        (3, 5),  # CNOT target to output 1
    }
    assert cnot_01_graph.edge_set() == expected_edges


def test_vertices(cnot_01_graph):
    assert cnot_01_graph.num_vertices() == 6
    assert set(cnot_01_graph.vertices()) == {0, 1, 2, 3, 4, 5}


def test_vertices_in_range(cnot_01_graph):
    assert set(cnot_01_graph.vertices_in_range(-1, 6)) == {0, 1, 2, 3, 4, 5}
    assert set(cnot_01_graph.vertices_in_range(3, 6)) == set()
    assert set(cnot_01_graph.vertices_in_range(1, 5)) == {2}


def test_edges(cnot_01_graph):
    expected_edges = {
        (0, 4),  # input 0 to CNOT control
        (1, 5),  # input 1 to CNOT target
        (4, 5),  # CNOT control to CNOT target
        (2, 4),  # CNOT control to output 0
        (3, 5),  # CNOT target to output 1
    }

    assert cnot_01_graph.num_edges() == 5
    assert set(cnot_01_graph.edges()) == expected_edges
    assert cnot_01_graph.edge_set() == expected_edges
    assert cnot_01_graph.edge(4, 5) == (4, 5)
    assert cnot_01_graph.edge(5, 4) == (4, 5)


def test_edge_st(cnot_01_graph):
    assert cnot_01_graph.edge_st("test") == "test"


def test_vertex_degree(cnot_01_graph):
    assert cnot_01_graph.vertex_degree(0) == 1
    assert cnot_01_graph.vertex_degree(4) == 3


def test_neighbors(cnot_01_graph):
    assert set(cnot_01_graph.neighbors(1)) == {5}
    assert set(cnot_01_graph.neighbors(5)) == {1, 3, 4}


def test_incident_edges(cnot_01_graph):
    found_edges = set()
    for e in cnot_01_graph.incident_edges(5):
        found_edges.add(frozenset(e))

    expected_edges = {frozenset({1, 5}), frozenset({3, 5}), frozenset({4, 5})}
    assert found_edges == expected_edges


def test_connected(cnot_01_graph):
    assert not cnot_01_graph.connected(0, 5)
    assert cnot_01_graph.connected(1, 5)


def test_edge_type(epr_graph):
    assert epr_graph.edge_type((0, 4)) == zx.EdgeType.HADAMARD
    assert epr_graph.edge_type((4, 5)) == zx.EdgeType.SIMPLE

    epr_graph.set_edge_type((0, 4), zx.EdgeType.SIMPLE)
    epr_graph.set_edge_type((4, 5), zx.EdgeType.HADAMARD)

    assert epr_graph.edge_type((0, 4)) == zx.EdgeType.SIMPLE
    assert epr_graph.edge_type((4, 5)) == zx.EdgeType.HADAMARD


def test_types(cnot_01_graph):
    expected_types = {
        0: zx.VertexType.BOUNDARY,
        1: zx.VertexType.BOUNDARY,
        2: zx.VertexType.BOUNDARY,
        3: zx.VertexType.BOUNDARY,
        4: zx.VertexType.Z,
        5: zx.VertexType.X,
    }
    assert cnot_01_graph.types() == expected_types

    assert cnot_01_graph.type(0) == zx.VertexType.BOUNDARY
    assert cnot_01_graph.type(4) == zx.VertexType.Z
    assert cnot_01_graph.type(5) == zx.VertexType.X

    cnot_01_graph.set_type(0, zx.VertexType.Z)
    assert cnot_01_graph.type(0) == zx.VertexType.Z


def test_phases(s_graph):
    expected_phases = {0: 0, 1: 0, 2: Fraction(1, 2)}
    assert s_graph.phases() == expected_phases

    assert s_graph.phase(2) == Fraction(1, 2)
    s_graph.set_phase(2, Fraction(3, 4))
    assert s_graph.phase(2) == Fraction(3, 4)
    s_graph.add_to_phase(2, Fraction(-1, 4))
    assert s_graph.phase(2) == Fraction(1, 2)


def test_qubits(cnot_01_graph):
    expected_qubits = {0: 0, 1: 1, 2: 0, 3: 1, 4: 0, 5: 1}
    assert cnot_01_graph.qubits() == expected_qubits

    assert cnot_01_graph.qubit(0) == 0
    cnot_01_graph.set_qubit(0, 77)
    assert cnot_01_graph.qubit(0) == 77


def test_row(cnot_01_graph):
    assert cnot_01_graph.row(0) == -1
    assert cnot_01_graph.row(5) == 0
    assert cnot_01_graph.row(2) == 1


def test_rows(cnot_01_graph):
    expected_rows = {0: -1, 1: -1, 2: 1, 3: 1, 4: 0, 5: 0}
    assert cnot_01_graph.rows() == expected_rows


def test_set_row(cnot_01_graph):
    assert cnot_01_graph.row(0) == -1
    cnot_01_graph.set_row(0, 77)
    assert cnot_01_graph.row(0) == 77


def test_vdata(cnot_01_graph):
    assert list(cnot_01_graph.vdata_keys(0)) == []
    assert cnot_01_graph.vdata(0, "some_key") == 0

    cnot_01_graph.set_vdata(0, "some_key", 10)
    assert list(cnot_01_graph.vdata_keys(0)) == ["some_key"]
    assert cnot_01_graph.vdata(0, "some_key") == 10

    cnot_01_graph.set_vdata(0, "some_key", 100)
    assert cnot_01_graph.vdata(0, "some_key") == 100


def test_inputs_and_outputs(cnot_01_graph):
    assert cnot_01_graph.num_inputs() == 2
    assert cnot_01_graph.num_outputs() == 2
    assert cnot_01_graph.inputs() == (0, 1)
    assert cnot_01_graph.outputs() == (2, 3)

    cnot_01_graph.set_inputs((0, 1, 2))
    cnot_01_graph.set_outputs((3,))

    assert cnot_01_graph.num_inputs() == 3
    assert cnot_01_graph.num_outputs() == 1
    assert cnot_01_graph.inputs() == (0, 1, 2)
    assert cnot_01_graph.outputs() == (3,)


@pytest.mark.xfail(reason="quizx issue #63")
def test_scalar(cnot_01_graph):
    sqrt_two = zx.Scalar()
    sqrt_two.add_power(1)

    assert isclose(cnot_01_graph.scalar.to_number(), sqrt_two.to_number())


def test_is_ground(cnot_01_graph):
    assert not cnot_01_graph.is_ground(0)


def test_adjoint(s_graph):
    # add a phase to the graph to make sure it gets conjugated
    scalar = zx.Scalar()
    scalar.add_phase(Fraction(1, 4))
    s_graph.scalar = scalar

    assert s_graph.phase(2) == Fraction(1, 2)
    assert isclose(s_graph.scalar.to_number(), scalar.to_number())

    s_graph.adjoint()
    adjoint_scalar = zx.Scalar()
    adjoint_scalar.add_phase(Fraction(-1, 4))

    assert s_graph.phase(2) == Fraction(-1, 2)
    assert isclose(s_graph.scalar.to_number(), adjoint_scalar.to_number())


def test_plug(h_0_graph, cnot_01_graph, epr_graph):
    reconstructed_epr = h_0_graph.clone()
    reconstructed_epr.plug(cnot_01_graph)
    assert_clifford_operators_equal(reconstructed_epr, epr_graph)

    eye = h_0_graph.clone()
    eye.plug(eye)
    clifford_simp(eye)
    assert eye.is_id()


def test_clone(cnot_01_graph):
    cnot_01_graph_ = cnot_01_graph.clone()
    assert_clifford_operators_equal(cnot_01_graph_, cnot_01_graph)
