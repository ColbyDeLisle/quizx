import pytest
import pyzx as zx
from pathlib import Path
from quizx import VecGraph
from fractions import Fraction


@pytest.fixture
def test_assets_path():
    return Path(__file__).resolve().parent / "assets"


@pytest.fixture
def h_0_graph():
    g = VecGraph()

    inputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=-1) for q in range(2)
    )
    outputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=0) for q in range(2)
    )
    g.set_inputs(inputs)
    g.set_outputs(outputs)

    g.add_edge((inputs[0], outputs[0]), zx.EdgeType.HADAMARD)
    g.add_edge((inputs[1], outputs[1]), zx.EdgeType.SIMPLE)

    return g


@pytest.fixture
def h_0_qasm_string():
    return 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\n'


@pytest.fixture
def cnot_01_graph():
    g = VecGraph()

    inputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=-1) for q in range(2)
    )
    outputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=1) for q in range(2)
    )
    g.set_inputs(inputs)
    g.set_outputs(outputs)

    cnot_control = g.add_vertex(zx.VertexType.Z, qubit=0, row=0)
    cnot_target = g.add_vertex(zx.VertexType.X, qubit=1, row=0)

    edges = [
        (inputs[0], cnot_control),
        (cnot_control, outputs[0]),
        (inputs[1], cnot_target),
        (cnot_target, outputs[1]),
        (cnot_control, cnot_target),
    ]
    for e in edges:
        g.add_edge(e, zx.EdgeType.SIMPLE)

    scalar = zx.Scalar()
    scalar.add_power(1)
    g.scalar = scalar

    return g


@pytest.fixture
def cnot_01_qasm_string():
    return 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\ncx q[0], q[1];\n'


@pytest.fixture
def epr_graph():
    g = VecGraph()

    inputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=-1) for q in range(2)
    )
    outputs = tuple(
        g.add_vertex(zx.VertexType.BOUNDARY, qubit=q, row=1) for q in range(2)
    )
    g.set_inputs(inputs)
    g.set_outputs(outputs)

    cnot_control = g.add_vertex(zx.VertexType.Z, qubit=0, row=0)
    cnot_target = g.add_vertex(zx.VertexType.X, qubit=1, row=0)

    g.add_edge((inputs[0], cnot_control), zx.EdgeType.HADAMARD)

    simple_edges = [
        (cnot_control, outputs[0]),
        (inputs[1], cnot_target),
        (cnot_target, outputs[1]),
        (cnot_control, cnot_target),
    ]
    for e in simple_edges:
        g.add_edge(e, zx.EdgeType.SIMPLE)

    scalar = zx.Scalar()
    scalar.add_power(1)
    g.scalar = scalar

    return g


@pytest.fixture
def epr_qasm_string():
    return 'OPENQASM 2.0;\ninclude "qelib1.inc";\nqreg q[2];\nh q[0];\ncx q[0], q[1];\n'


@pytest.fixture
def s_graph():
    g = VecGraph()

    v_in = g.add_vertex(zx.VertexType.BOUNDARY, qubit=0, row=-1)
    v_out = g.add_vertex(zx.VertexType.BOUNDARY, qubit=0, row=1)
    g.set_inputs((v_in,))
    g.set_outputs((v_out,))

    s = g.add_vertex(zx.VertexType.Z, phase=Fraction(1, 2), qubit=0, row=0)

    g.add_edge((v_in, s), zx.EdgeType.SIMPLE)
    g.add_edge((s, v_out), zx.EdgeType.SIMPLE)

    return g
