import pytest

from pyzx.graph.scalar import Scalar as PyzxScalar
from quizx._quizx import Scalar as QuizxScalar
from quizx.scalar import from_pyzx_scalar, to_pyzx_scalar
from fractions import Fraction
from cmath import isclose


@pytest.fixture()
def pyzx_scalar():
    p = PyzxScalar()
    p.add_phase(Fraction(1, 4))
    p.add_power(1)
    return p


@pytest.fixture()
def quizx_scalar():
    q = QuizxScalar.from_phase(1 / 4)
    q = q.mul_sqrt2_pow(1)
    return q


def test_from_pyzx_scalar(pyzx_scalar, quizx_scalar):
    converted_pyzx_scalar = from_pyzx_scalar(pyzx_scalar)
    assert isinstance(converted_pyzx_scalar, QuizxScalar)
    assert isclose(converted_pyzx_scalar.complex_value(), quizx_scalar.complex_value())


@pytest.mark.xfail(reason="quizx issue #63")
def test_to_pyzx_scalar(pyzx_scalar, quizx_scalar):
    converted_quizx_scalar = to_pyzx_scalar(quizx_scalar)
    print(quizx_scalar)
    assert isinstance(converted_quizx_scalar, PyzxScalar)
    assert isclose(converted_quizx_scalar.to_number(), pyzx_scalar.to_number())
