import pytest
import pyzx as zx

from quizx import VecGraph, Circuit
from fractions import Fraction
from quizx.simplify import interior_clifford_simp, clifford_simp, full_simp


@pytest.fixture
def interior_clifford_simp_graph():
    qasm = """
                OPENQASM 2.0;
                include "qelib1.inc";
                qreg q[2];
                h q[0];
                h q[0];
                s q[1];
                z q[1];
                s q[1];
                cx q[0], q[1];
                cx q[0], q[1];
        """
    c = Circuit.from_qasm(qasm)
    return c.to_graph()


@pytest.fixture
def clifford_simp_graph():
    qasm = """
            OPENQASM 2.0;
            include "qelib1.inc";
            qreg q[2];
            t q[0];
            cx q[1], q[0];
            t q[0];
            cx q[1], q[0];
            t q[0];
            t q[1];
    """
    c = Circuit.from_qasm(qasm)
    return c.to_graph()


@pytest.fixture
def pi_in_the_middle_gadget():
    g = VecGraph()

    v_in = g.add_vertex(zx.VertexType.BOUNDARY, qubit=0, row=-1)
    v_out = g.add_vertex(zx.VertexType.BOUNDARY, qubit=0, row=1)
    bottom = g.add_vertex(zx.VertexType.Z, phase=Fraction(1, 8), qubit=0, row=0)
    middle = g.add_vertex(zx.VertexType.Z, phase=Fraction(1), row=0)
    top = g.add_vertex(zx.VertexType.Z, phase=Fraction(1, 8), row=0)

    g.set_inputs((v_in,))
    g.set_outputs((v_out,))

    g.add_edge((v_in, bottom), zx.EdgeType.HADAMARD)
    g.add_edge((bottom, v_out), zx.EdgeType.HADAMARD)
    g.add_edge((bottom, middle), zx.EdgeType.HADAMARD)
    g.add_edge((middle, top), zx.EdgeType.HADAMARD)

    return g


def test_interior_clifford_simp(interior_clifford_simp_graph):
    assert not interior_clifford_simp_graph.is_id()
    interior_clifford_simp(interior_clifford_simp_graph)
    assert interior_clifford_simp_graph.is_id()


def test_clifford_simp(clifford_simp_graph):
    # clifford_simp can reduce this further than can interior_clifford_simp, since it also includes a generalized
    # pivoting step; this reduces the number of non-Clifford spiders by two
    g = clifford_simp_graph

    interior_clifford_simp(g)
    num_non_clifford_spiders = sum(
        1 for v in g.vertices() if g.phase(v) == Fraction(1, 4)
    )
    assert num_non_clifford_spiders == 4

    clifford_simp(g)
    num_non_clifford_spiders = sum(
        1 for v in g.vertices() if g.phase(v) == Fraction(1, 4)
    )
    assert num_non_clifford_spiders == 2


def test_full_simp(pi_in_the_middle_gadget):
    # full_simp uses remove_gadget_pi where the others don't, so we can check that it successfully reduces this gadget
    # with a pi phase in the middle to the identity
    assert not pi_in_the_middle_gadget.is_id()
    interior_clifford_simp(pi_in_the_middle_gadget)
    assert not pi_in_the_middle_gadget.is_id()
    clifford_simp(pi_in_the_middle_gadget)
    assert not pi_in_the_middle_gadget.is_id()

    full_simp(pi_in_the_middle_gadget)
    assert pi_in_the_middle_gadget.is_id()
