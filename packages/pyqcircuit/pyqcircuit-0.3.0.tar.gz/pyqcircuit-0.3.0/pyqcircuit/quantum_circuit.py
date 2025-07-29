"""
A tiny pure‑Python helper for drawing quantum‑circuit diagrams.


Quick demo
----------
```python
qc = QuantumCircuit(3)
qc.h(0)
qc.x(2, step=1)           # share column 1
qc.custom([0,2], "Foo")   # tall box spanning q0‑q2 in column 2
qc.cx(0, 1, step=3)

qc.draw()
```
"""

import matplotlib.pyplot as plt

__all__ = [
    "QuantumCircuit",
]

from typing import List, Sequence, Mapping, Any, Optional

from pyqcircuit.primitives import Line, Text
from pyqcircuit.graphics_target import GraphicsTarget
from pyqcircuit.style import GateStyle, resolve_diagram_style, CircuitTheme, get_theme
from pyqcircuit.renderers import gate_registry
from pyqcircuit.matplotlib_backend import MatplotlibTarget


class Gate:
    """Data plus the ability to render itself as primitives."""

    def __init__(
        self,
        name: str,
        qubits: Sequence[int],
        params: Sequence[float] | None = None,
        label: str | None = None,
        step: int = 1,
        style: Mapping[str, Any] | None = None,
    ):
        self.name = name.upper()
        self.qubits = tuple(qubits)  # Store as a tuple for immutability and hashability
        self.params = tuple(params) if params else ()
        self.label = label
        self.step = step
        self.style_overrides = GateStyle(**(style or {}))

    # ------------------------------------------------------------------
    def render(self, tgt: GraphicsTarget, global_style: GateStyle) -> None:
        fn = gate_registry.get(self.name)
        if fn is None:
            raise NotImplementedError(f"No renderer for gate {self.name}")
        fn(self, tgt, global_style)


class QuantumCircuit:
    def __init__(self, n_qubits: int):
        if n_qubits < 1:
            raise ValueError("Circuit must contain at least one qubit.")
        self.n_qubits = n_qubits
        self._gates: List[Gate] = []
        self._current_step = 0

    # ---------- helpers ------------------------------------------------
    def _validate_qubits(self, qubits):
        bad = [q for q in qubits if q < 0 or q >= self.n_qubits]
        if bad:
            raise IndexError(f"Qubit index out of range: {bad}")

    def add_gate(
        self,
        name: str,
        qubits: Sequence[int] | int,
        *,
        step: Optional[int] = None,
        label: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
        style: Optional[Mapping[str, Any]] = None,
    ):
        """
        Add a gate to the circuit.

        This method is for adding gates that do not have a specific convenience
        method.

        Parameters
        ----------
        name: str
            Name of the gate (e.g., "H", "X", "CNOT"). Should have a corresponding
            renderer in the `gate_registry`.
        qubits: Sequence[int] | int
            Qubit index or indices the gate acts on. If a single integer is given,
            it is converted to a list containing that index.
        step: int, optional
            Step number for the gate. If not provided, it defaults to the next step
            in sequence.
        label: str, optional
            Label for the gate, which can be used for custom gates or annotations.
        params: Sequence[Any] | None, optional
            Parameters for the gate, if applicable. Defaults to None.
        style: Mapping[str, Any] | None, optional
            Style overrides for the gate, such as colors or line widths. Defaults to None.

        Returns
        -------
        None
        """
        if isinstance(qubits, int):
            qubits = [qubits]
        self._validate_qubits(qubits)
        if step is None:
            self._current_step += 1
            step = self._current_step
        else:
            self._current_step = max(self._current_step, step)

        self._gates.append(Gate(name, qubits, params, label, step, style=style))

    # --------------------------------------------------------------
    # Convenience wrappers -----------------------------------------
    def h(self, q: int, **kwargs):
        self.add_gate("H", q, **kwargs)

    def x(self, q: int, **kwargs):
        self.add_gate("X", q, **kwargs)

    def y(self, q: int, **kwargs):
        self.add_gate("Y", q, **kwargs)

    def z(self, q: int, **kwargs):
        self.add_gate("Z", q, **kwargs)

    def x90(self, q: int, **kwargs):
        self.add_gate("X90", q, **kwargs)

    def y90(self, q: int, **kwargs):
        self.add_gate("Y90", q, **kwargs)

    def z90(self, q: int, **kwargs):
        self.add_gate("Z90", q, **kwargs)

    def s(self, q: int, **kwargs):
        self.add_gate("S", q, **kwargs)

    def t(self, q: int, **kwargs):
        self.add_gate("T", q, **kwargs)

    def i(self, q: int, **kwargs):
        self.add_gate("I", q, **kwargs)

    def rx(self, q: int, theta: float, **kwargs):
        self.add_gate("RX", q, params=[theta], **kwargs)

    def cx(self, control: int, target: int, **kwargs):
        self.add_gate("CNOT", [control, target], **kwargs)

    def cz(self, control: int, target: int, **kwargs):
        self.add_gate("CZ", [control, target], **kwargs)

    def swap(self, q1: int, q2: int, **kwargs):
        self.add_gate("SWAP", [q1, q2], **kwargs)

    def toffoli(self, control1: int, control2: int, target: int, **kwargs):
        """Add a Toffoli gate (CCNOT) with two controls and one target."""
        self.add_gate("TOFFOLI", [control1, control2, target], **kwargs)

    def measure(self, qs, **kwargs):
        self.add_gate("MEASURE", qs, **kwargs)

    def custom(self, qubits: Sequence[int] | int, label: str, **kwargs):
        """Insert a *labelled* one‑ or multi‑qubit gate."""
        self.add_gate("CUSTOM", qubits, label=label, **kwargs)

    def pulse(
        self,
        q: int,
        kind: str = "gaussian",
        *,
        step=None,
        amp: float | None = None,
        duration: float | None = None,
        style=None,
    ):
        """
        Draw a pulse symbol (gaussian, square, square_mod, etc.)
        Parameters are purely informational for now.
        """
        params = [amp or 0.0, duration or 0.0, kind]
        self.add_gate("PULSE", q, params=params, step=step, style=style)

    # ---------- drawing entry point -----------------------------------
    def draw(self, backend: str = "mpl", *, theme: CircuitTheme | str | None = None, **backend_kw):
        """
        Render the circuit.

        Parameters
        ----------
        backend : {'mpl'}
            Drawing backend to use (matplotlib only for now).
        theme : CircuitTheme | str, optional
            Theme containing global and per‑gate style overrides. If a string is provided,
            it is interpreted as a theme name to load from the default themes.
        backend_kw :
            Extra keyword args forwarded to the backend constructor.
        """
        theme = get_theme(theme)

        if backend == "mpl":
            tgt = MatplotlibTarget(self._current_step, self.n_qubits, **backend_kw)
        else:
            raise ValueError(f"Backend {backend!r} not recognised")

        # --- diagram‑wide style ---------------------------------------
        dstyle = resolve_diagram_style(theme)
        tgt.set_background(dstyle.background)

        # --- wires ----------------------------------------------------
        for q in range(self.n_qubits):
            y = -q
            tgt.add(
                Line(
                    0,
                    y,
                    self._current_step + 1,
                    y,
                    width=dstyle.wirewidth,
                    color=dstyle.wirecolor,
                    layer=0,
                )
            )
            tgt.add(
                Text(
                    -0.2,
                    y,
                    f"q{q} |0>",
                    size=9,  # fixed label font
                    family="sans-serif",
                    color=dstyle.wirecolor,
                    ha="right",
                    va="center",
                    layer=1,
                )
            )

        # --- gates ----------------------------------------------------
        for g in self._gates:
            g.render(tgt, theme)

        return tgt.finalize()


if __name__ == "__main__":
    c = QuantumCircuit(6)
    c.custom(range(6), "SetV\n(_111)", step=1)
    c.h(0, step=2)
    c.i(3, step=2)
    c.rx(4, 3.1415, step=2)
    c.cz(1, 3, step=3)
    c.cx(4, 5, step=3)
    c.cx(5, 4, step=4)

    # c.z(2, step=3)

    c.z90(0, step=4)
    c.pulse(1, kind="mod_square", step=5)
    c.pulse(2, kind="mod_gauss", step=5)
    c.x(2, step=4)
    c.swap(4, 5, step=5)
    c.custom(0, "Custom\nGate", step=5)
    c.measure([0, 1, 2], step=6)
    c.custom([3, 4, 5], "Custom\nGate", step=6)
    c.draw(theme="groovy")
    # plt.tight_layout()
    plt.show()
