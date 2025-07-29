# tests/test_draw.py
import pytest
from pyqcircuit import QuantumCircuit  # your new primitive‑based package
from .conftest import assert_fig_equal


@pytest.mark.parametrize("face", ["#ffe680", "#dddddd"])
def test_three_qubit_demo(face):
    qc = QuantumCircuit(3)
    gstyle = {"facecolor": face}

    qc.h(0, style=gstyle)  # step 1  (auto)
    qc.x(2, step=1, style=gstyle)  # share column 1
    qc.custom([0, 2], "Foo", style=gstyle)  # auto column 2
    qc.cx(0, 1, step=3, style=gstyle)  # explicit column 3
    qc.toffoli(0, 1, 2, step=4, style=gstyle)  # explicit column 4

    fig, _ = qc.draw()  # no extra kwargs now
    assert_fig_equal(fig, f"demo_{face.strip('#')}")


@pytest.mark.parametrize("theme", ["dark", "groovy", "one"])
def test_draw_theme(theme):
    """
    Draw a circuit with a built‑in theme.
    """
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.custom([0, 1], "Custom\nGate")
    qc.custom([0], "Single\nQubit")
    qc.swap(0, 1)
    qc.pulse(0, "mod_gauss")
    qc.pulse(1, "mod_square")
    qc.pulse(0, "ramp_in")
    qc.pulse(1, "ramp_out")
    qc.measure(0)

    fig, _ = qc.draw(theme=theme)
    # allow 1pixel tolerance for anti‑aliasing
    assert_fig_equal(fig, f"theme_{theme}", tol=1.0)


def test_measure_symbol():
    """
    Single‑qubit circuit with a measurement symbol – signature unchanged.
    """
    qc = QuantumCircuit(1)
    qc.h(0)
    qc.measure(0)
    fig, _ = qc.draw()
    # allow 1pixel tolerance for anti‑aliasing
    assert_fig_equal(fig, "measure_symbol", tol=1.0)


def test_pulse_gates():
    """
    Single‑qubit circuit with a measurement symbol – signature unchanged.
    """
    qc = QuantumCircuit(1)
    qc.pulse(0, "mod_gauss")
    qc.pulse(0, "mod_square")
    qc.pulse(0, "ramp_in")
    qc.pulse(0, "square")
    qc.pulse(0, "ramp_out")
    qc.pulse(0, "trapezoid")
    qc.pulse(0, "fallback")

    qc.measure(0)
    fig, _ = qc.draw()
    # allow 1pixel tolerance for anti‑aliasing
    assert_fig_equal(fig, "pulse_gates", tol=1.0)
