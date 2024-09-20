import pytest

import pyzx as zx
from fractions import Fraction
from cmath import isclose, exp, pi
from quizx import Decomposer, VecGraph


@pytest.fixture
def t_graph():
    # |T> = 1/√2(|0> + exp(iπ/4)|1>)
    g = VecGraph()

    v_out = g.add_vertex(zx.VertexType.BOUNDARY, qubit=0, row=1)
    g.set_outputs((v_out,))

    t = g.add_vertex(zx.VertexType.Z, phase=Fraction(1, 4), qubit=0, row=0)

    g.add_edge((t, v_out), zx.EdgeType.SIMPLE)

    s = zx.Scalar()
    s.add_power(-1)
    g.scalar = s

    return g


@pytest.fixture
def t_state_decomposer(t_graph):
    d = Decomposer(t_graph)
    d.save(True)
    d.apply_optimizations(True)
    return d


def test_apply_optimizations(t_state_decomposer):
    t_state_decomposer.decomp_all()
    for g in t_state_decomposer.done():
        assert len(list(g.vertices())) == 2

    d = Decomposer()
    d.apply_optimizations(False)
    d.save(True)
    d.decomp_all()
    for g in d.done():
        assert len(list(g.vertices())) == 3


def test_max_terms(t_state_decomposer):
    assert t_state_decomposer.max_terms() == 2


def test_decomp_top(t_state_decomposer):
    assert len(t_state_decomposer.graphs()) == 1
    assert len(t_state_decomposer.done()) == 0
    t_state_decomposer.decomp_top()
    assert len(t_state_decomposer.graphs()) == 2
    assert len(t_state_decomposer.done()) == 0
    t_state_decomposer.decomp_top()
    assert len(t_state_decomposer.graphs()) == 1
    assert len(t_state_decomposer.done()) == 1
    t_state_decomposer.decomp_top()
    assert len(t_state_decomposer.graphs()) == 0
    assert len(t_state_decomposer.done()) == 2


@pytest.mark.xfail(reason="quizx issue #63")
def test_decomp_all(t_state_decomposer, t_graph):
    t_state_decomposer.decomp_all()
    g1, g0 = t_state_decomposer.done()

    g0_vertices = list(g0.vertices())
    assert len(g0_vertices) == 2
    g0_phases = set(g0.phases().values())
    assert g0_phases == {Fraction(0, 1)}
    g0_vtypes = set(g0.type(v) for v in g0_vertices)
    assert g0_vtypes == {zx.VertexType.Z, zx.VertexType.BOUNDARY}
    g0_edges = list(g0.edges())
    assert len(g0_edges) == 1
    assert g0.edge_type(g0_edges[0]) == zx.EdgeType.HADAMARD
    assert isclose(g0.scalar.to_number(), 0.5)

    g1_vertices = list(g1.vertices())
    assert len(g1_vertices) == 2
    g1_phases = set(g1.phases().values())
    assert g1_phases == {Fraction(0, 1), Fraction(1, 1)}
    g1_vtypes = set(g1.type(v) for v in g1_vertices)
    assert g1_vtypes == {zx.VertexType.Z, zx.VertexType.BOUNDARY}
    g1_edges = list(g1.edges())
    assert len(g1_edges) == 1
    assert g0.edge_type(g1_edges[0]) == zx.EdgeType.HADAMARD
    assert isclose(g1.scalar.to_number(), 0.5 * exp(1j * pi / 4))


def test_decomp_until_depth(t_state_decomposer):
    assert len(t_state_decomposer.graphs()) == 1
    assert len(t_state_decomposer.done()) == 0
    t_state_decomposer.decomp_until_depth(1)
    assert len(t_state_decomposer.graphs()) == 2
    assert len(t_state_decomposer.done()) == 0
    t_state_decomposer.decomp_until_depth(2)
    assert len(t_state_decomposer.graphs()) == 0
    assert len(t_state_decomposer.done()) == 2


def test_get_nterms(t_state_decomposer):
    assert t_state_decomposer.get_nterms() == 0
    t_state_decomposer.decomp_all()
    print(t_state_decomposer.scalar)
    assert t_state_decomposer.get_nterms() == 2


def test_scalar(t_state_decomposer):
    assert t_state_decomposer.scalar.to_number() == 0.0
    new_scalar = zx.Scalar()
    new_scalar.add_float(2.0)
    t_state_decomposer.scalar = new_scalar
    assert t_state_decomposer.scalar.to_number() == 2.0


def test_is_ground(t_state_decomposer):
    assert not t_state_decomposer.is_ground(0)


@pytest.mark.xfail(reason="quizx issue #64")
def test_cat6():
    n = 6

    cat = VecGraph()

    z = cat.add_vertex(zx.VertexType.Z, row=-1)
    ts = tuple(
        cat.add_vertex(zx.VertexType.Z, phase=Fraction(1, 4), qubit=q, row=0)
        for q in range(n)
    )
    outputs = tuple(
        cat.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=1) for q in range(n)
    )
    cat.set_outputs(outputs)

    for i in range(n):
        cat.add_edge((z, ts[i]), zx.EdgeType.HADAMARD)
        cat.add_edge((ts[i], outputs[i]), zx.EdgeType.SIMPLE)

    d = Decomposer(cat)
    d.apply_optimizations(True)
    d.save(True)
    d.use_cats(True)

    d.decomp_all()
    assert len(d.done()) == 3
