from quizx import VecGraph
from quizx.simplify import clifford_simp

from cmath import isclose


def assert_clifford_operators_equal(graph: VecGraph, graph_: VecGraph) -> None:
    """
    Assert that two VecGraph instances representing unitary Clifford operators are the same.
    """
    # clone first, since we'll be mutating to check equality
    g = graph.clone()

    g.adjoint()

    g.plug(graph_)
    clifford_simp(g)

    assert g.is_id()
    assert isclose(g.scalar.to_number(), 1)
