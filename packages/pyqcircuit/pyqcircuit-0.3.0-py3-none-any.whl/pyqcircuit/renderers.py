"""
Renderers for each gate type –Matplotlib‑agnostic layer.
Uses resolve_style() so no literal colour/size fall‑backs are needed, except
where the design intentionally differs from the library defaults (e.g. MEASURE
and PULSE boxes use white fill if the user did not override).
"""

from __future__ import annotations

import math
from math import pi
from typing import Dict, Callable, Sequence, Union, Iterable, List, Tuple

from pyqcircuit.graphics_target import GraphicsTarget
from pyqcircuit.primitives import (
    Line,
    Box,
    Circle,
    Arc,
    Text,
    Polyline,
)
from pyqcircuit.style import (
    GateStyle,
    resolve_gate_style,
)

# ----------------------------------------------------------------------
# Gate‑renderer registry + decorator
# ----------------------------------------------------------------------

gate_registry: Dict[str, Callable] = {}
NameArg = Union[str, Sequence[str]]


def gate_renderer(names: NameArg):
    """Decorator: register *fn* for one or several gate names."""
    if isinstance(names, str):
        name_list = [names.upper()]
    elif isinstance(names, Iterable):
        name_list = [n.upper() for n in names]
    else:
        raise TypeError("names must be a string or iterable of strings")

    def decorator(fn: Callable):
        for n in name_list:
            gate_registry[n] = fn
        return fn

    return decorator


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def _pretty(gate):
    """Return a math‑text label with parameters for rotation gates."""
    pretty = {"RX": r"$R_x$", "RY": r"$R_y$", "RZ": r"$R_z$", "RXY": r"$R_{xy}$"}

    def _fmt(val: float) -> str:
        close = lambda a, b: abs(a - b) < 1e-4
        if close(val, pi):
            return r"π"
        if close(val, -pi):
            return "-π"
        if close(val, pi / 2):
            return "π/2"
        if close(val, -pi / 2):
            return "-π/2"
        return f"{val:.2f}"

    base = gate.label if gate.label is not None else pretty.get(gate.name, gate.name)
    if gate.params:
        parms = ", ".join(_fmt(p) for p in gate.params)
        return f"{base}({parms})"
    return base


Point = Tuple[float, float]


def _pulse_shape(kind: str) -> List[Point]:
    """Return local coordinates for symbolic pulse icons."""
    kind = kind.lower().replace(" ", "_")
    amp = 0.20
    left, right = -0.20, 0.20

    def lin(a: float, b: float, n: int) -> List[float]:
        step = (b - a) / n
        return [a + i * step for i in range(n + 1)]

    if kind in {"mod_gauss", "mod_gaussian", "modulated_gaussian"}:
        lp, rp = left + 0.05, right - 0.05
        xs = lin(lp, rp, 60)
        num_period = 5
        pts = [
            (
                x,
                amp
                * math.sin(2 * num_period * math.pi * (x - lp) / (rp - lp))
                * math.exp(-((x / 0.18) ** 2) * 2.0),
            )
            for x in xs
        ]
        return [(left, 0.0), *pts, (right, 0.0)]

    if kind in {"mod_square", "modulated_square", "mw_pulse"}:
        lp, rp = left + 0.06, right - 0.06
        xs = lin(lp, rp, 120)
        num_period = 5
        pts = [(x, amp * math.sin(2 * num_period * math.pi * (x - lp) / (rp - lp))) for x in xs]
        return [(left, 0.0), *pts, (right, 0.0)]

    if kind in {"square", "rectangular"}:
        return [
            (left, -amp / 2),
            (-0.10, -amp / 2),
            (-0.10, amp / 2),
            (0.10, amp / 2),
            (0.10, -amp / 2),
            (right, -amp / 2),
        ]

    if kind == "ramp_in":
        return [
            (left, -amp / 2),
            (-0.05, -amp / 2),
            (0.05, amp / 2),
            (right, amp / 2),
        ]

    if kind == "ramp_out":
        return [
            (left, amp / 2),
            (-0.05, amp / 2),
            (0.05, -amp / 2),
            (right, -amp / 2),
        ]

    if kind in {"trapezoid", "ramp_in_hold_ramp_out"}:
        return [
            (left, -amp / 2),
            (-0.15, -amp / 2),
            (-0.08, amp / 2),
            (0.08, amp / 2),
            (0.15, -amp / 2),
            (right, -amp / 2),
        ]

    xs = lin(left, right, 12)
    return [
        (x, amp * (0.3 + 0.7 * math.sin(3 * math.pi * (x - left) / (right - left)))) for x in xs
    ]


# ----------------------------------------------------------------------
# Renderers
# ----------------------------------------------------------------------


# --- Single‑qubit fixed boxes -----------------------------------------
@gate_renderer(["Z", "H", "X", "Y", "S", "T", "S†", "T†", "I", "X90", "Y90", "Z90"])
def render_single_box(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x, y = gate.step, -gate.qubits[0]
    tgt.add(
        Box(
            x - 0.4,
            y - 0.4,
            0.8,
            0.8,
            face=st.facecolor,
            edge=st.edgecolor,
            lw=st.linewidth,
            layer=1,
        )
    )
    tgt.add(
        Text(
            x,
            y,
            gate.label or gate.name,
            size=st.fontsize,
            family=st.fontfamily,
            color=st.textcolor,
            layer=3,
        )
    )


# --- Rotation gates ----------------------------------------------------
@gate_renderer(["RX", "RY", "RZ", "RXY"])
def render_rotation(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x, y = gate.step, -gate.qubits[0]
    tgt.add(
        Box(
            x - 0.4,
            y - 0.4,
            0.8,
            0.8,
            face=st.facecolor,
            edge=st.edgecolor,
            lw=st.linewidth,
            layer=1,
        )
    )
    tgt.add(
        Text(
            x, y, _pretty(gate), size=st.fontsize, family=st.fontfamily, color=st.textcolor, layer=2
        )
    )


# --- Pulse gate --------------------------------------------------------
@gate_renderer("PULSE")
def render_pulse(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x, y = gate.step, -gate.qubits[0]

    tgt.add(
        Box(
            x - 0.4,
            y - 0.4,
            0.8,
            0.8,
            face=st.facecolor,
            edge=st.edgecolor,
            lw=st.linewidth,
            layer=1,
        )
    )

    kind = gate.params[2] if len(gate.params) >= 3 else "gaussian"
    pts = [(x + px, y + py) for px, py in _pulse_shape(kind)]
    tgt.add(Polyline(pts, width=st.linewidth, color=st.edgecolor, layer=2))


# --- Two‑qubit: CX -----------------------------------------------------
@gate_renderer(["CX", "CNOT"])
def render_cnot(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    c, t = gate.qubits
    cy, ty = -c, -t
    r, lw, col = 0.1, st.linewidth, st.edgecolor
    tgt.add(Circle(x, cy, r, True, col, lw, layer=1))
    tgt.add(Line(x, cy, x, ty, lw, col, layer=1))
    tgt.add(Circle(x, ty, 1.8 * r, False, col, lw, layer=1))
    tgt.add(Line(x, ty - 1.8 * r, x, ty + 1.8 * r, lw, col, layer=1))
    tgt.add(Line(x - 1.8 * r, ty, x + 1.8 * r, ty, lw, col, layer=1))


# --- Two‑qubit: CZ -----------------------------------------------------
@gate_renderer("CZ")
def render_cz(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    c, t = gate.qubits
    cy, ty = -c, -t
    tgt.add(Circle(x, cy, 0.1, True, st.edgecolor, st.linewidth, layer=1))
    tgt.add(Line(x, cy, x, ty, st.linewidth, st.edgecolor, layer=1))
    tgt.add(Circle(x, ty, 0.1, True, st.edgecolor, st.linewidth, layer=1))


# --- Two‑qubit: SWAP ---------------------------------------------------
@gate_renderer("SWAP")
def render_swap(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    q1, q2 = gate.qubits
    y1, y2 = -q1, -q2
    col, lw = st.edgecolor, st.linewidth
    # vertical line
    tgt.add(Line(x, y1, x, y2, lw, col, layer=1))
    # crosses
    for y in (y1, y2):
        tgt.add(Line(x - 0.18, y - 0.18, x + 0.18, y + 0.18, lw, col, layer=1))
        tgt.add(Line(x + 0.18, y - 0.18, x - 0.18, y + 0.18, lw, col, layer=1))


# --- Three‑qubit: TOFFOLI ----------------------------------------------
@gate_renderer("TOFFOLI")
def render_toffoli(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    c1, c2, t = gate.qubits
    c1y, c2y, ty = -c1, -c2, -t

    ytop = max(c1y, c2y, ty)
    ybot = min(c1y, c2y, ty)
    r, lw, col = 0.1, st.linewidth, st.edgecolor
    # connecting line
    tgt.add(Line(x, ytop, x, ybot, lw, col, layer=1))
    # circles for control qubits
    tgt.add(Circle(x, c1y, r, True, col, lw, layer=1))
    tgt.add(Circle(x, c2y, r, True, col, lw, layer=1))
    # circle for target qubit with cross
    tgt.add(Circle(x, ty, 1.8 * r, False, col, lw, layer=1))
    tgt.add(Line(x, ty - 1.8 * r, x, ty + 1.8 * r, lw, col, layer=1))
    tgt.add(Line(x - 1.8 * r, ty, x + 1.8 * r, ty, lw, col, layer=1))


# --- Measure -----------------------------------------------------------
@gate_renderer("MEASURE")
def render_measure(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    for q in gate.qubits:
        y = -q
        tgt.add(Box(x - 0.4, y - 0.4, 0.8, 0.8, st.facecolor, st.edgecolor, st.linewidth, layer=1))

        # Draw the measure meter symbol
        r = 0.2
        tgt.add(Arc(x, y - r / 2, 2 * r, 2 * r, 0, 180, st.linewidth, st.edgecolor, layer=3))
        tgt.add(Line(x, y - r / 2, x + r, y + r - r / 2, st.linewidth, st.edgecolor, layer=3))


# --- Custom box (multi‑qubit) -----------------------------------------
@gate_renderer("CUSTOM")
def render_custom(gate, tgt: GraphicsTarget, global_style: GateStyle):
    st = resolve_gate_style(gate.name, global_style, gate.style_overrides)
    x = gate.step
    ybot, ytop = -max(gate.qubits), -min(gate.qubits)
    tgt.add(
        Box(
            x - 0.4,
            ybot - 0.4,
            0.8,
            0.8 + ytop - ybot,
            face=st.facecolor,
            edge=st.edgecolor,
            lw=st.linewidth,
            layer=1,
        )
    )
    tgt.add(
        Text(
            x,
            (ytop + ybot) / 2,
            gate.label or gate.name,
            size=st.fontsize,
            family=st.fontfamily,
            color=st.textcolor,
            layer=3,
        )
    )
