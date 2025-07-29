from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Iterable, Optional, Union, Any

import yaml
import importlib.resources as _pkg

from pyqcircuit.primitives import Color

_BUILTIN_THEMES: Dict[str, CircuitTheme] = {}


# ---------------------------------------------------------------------
# Per‑gate style
# ---------------------------------------------------------------------
@dataclass
class GateStyle:
    facecolor: Optional[Color] = None
    edgecolor: Optional[Color] = None
    textcolor: Optional[Color] = None
    linewidth: Optional[float] = None
    fontsize: Optional[int] = None
    fontfamily: Optional[str] = None

    def merged(self, other: GateStyle) -> GateStyle:
        data = asdict(self)
        for k, v in asdict(other).items():
            if v is not None:
                data[k] = v
        return GateStyle(**data)


# ---------------------------------------------------------------------
# Global diagram style  (wires, background, etc.)
# ---------------------------------------------------------------------
@dataclass
class DiagramStyle:
    wirecolor: Optional[Color] = None
    wirewidth: Optional[float] = None
    background: Optional[Color] = None

    def merged(self, other: DiagramStyle) -> DiagramStyle:
        data = asdict(self)
        for k, v in asdict(other).items():
            if v is not None:
                data[k] = v
        return DiagramStyle(**data)


# ---------------------------------------------------------------------
# Library‑wide defaults
# ---------------------------------------------------------------------
_DEFAULT_GATE = GateStyle(
    facecolor="#e0e0e0",
    edgecolor="black",
    textcolor="black",
    linewidth=1.0,
    fontsize=8,
    fontfamily="sans-serif",
)

_DEFAULT_DIAGRAM = DiagramStyle(
    wirecolor="black",
    wirewidth=1.0,
    background="white",
)

_PER_GATE_DEFAULT: Dict[str, GateStyle] = {
    "MEASURE": GateStyle(facecolor="#ffffff"),
    "PULSE": GateStyle(facecolor="#ffffff"),
}


# ---------------------------------------------------------------------
# Resolved dataclasses (no None left)
# ---------------------------------------------------------------------
@dataclass
class ResolvedGateStyle:
    facecolor: Color
    edgecolor: Color
    textcolor: Color
    linewidth: float
    fontsize: int
    fontfamily: str


@dataclass
class ResolvedDiagramStyle:
    wirecolor: Color
    wirewidth: float
    background: Color


# ---------------------------------------------------------------------
# Theme object – can be loaded from YAML and layered
# ---------------------------------------------------------------------
@dataclass
class CircuitTheme:
    """A collection of style overrides that can be layered."""

    diagram: DiagramStyle = field(default_factory=DiagramStyle)
    global_gate: GateStyle = field(default_factory=GateStyle)
    per_gate: Dict[str, GateStyle] = field(default_factory=dict)

    # ---- merging two themes -----------------------------------------
    def merged(self, other: "CircuitTheme") -> "CircuitTheme":
        dg = self.diagram.merged(other.diagram)
        gg = self.global_gate.merged(other.global_gate)
        pg = {**self.per_gate}  # shallow copy then deep‑merge per‑gate
        for name, gs in other.per_gate.items():
            pg[name.upper()] = pg.get(name.upper(), GateStyle()).merged(gs)
        return CircuitTheme(dg, gg, pg)

    # ---- YAML loader -------------------------------------------------
    @classmethod
    def from_yaml(cls, path_or_str: Union[str, Path, Any]) -> "CircuitTheme":
        if isinstance(path_or_str, (str, Path)):
            with open(path_or_str, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:  # already-parsed dict
            data = path_or_str

        dg = DiagramStyle(**data.get("diagram", {}))
        gg = GateStyle(**data.get("global_style", {}))
        pgd = {k.upper(): GateStyle(**v) for k, v in data.get("per_gate", {}).items()}
        return CircuitTheme(diagram=dg, global_gate=gg, per_gate=pgd)


# ---------------------------------------------------------------------
# Resolvers – used by renderers & draw()
# ---------------------------------------------------------------------
def resolve_gate_style(
    gate_name: str, *layers: Iterable[Union[GateStyle, CircuitTheme]]
) -> ResolvedGateStyle:
    """Return a fully‑specified Gate style for a particular gate."""
    st = _DEFAULT_GATE.merged(_PER_GATE_DEFAULT.get(gate_name.upper(), GateStyle()))
    for layer in layers:
        if isinstance(layer, CircuitTheme):
            st = st.merged(layer.global_gate)
            st = st.merged(layer.per_gate.get(gate_name.upper(), GateStyle()))
        else:  # plain GateStyle
            st = st.merged(layer)
    return ResolvedGateStyle(**asdict(st))


def resolve_diagram_style(
    *layers: Iterable[Union[DiagramStyle, CircuitTheme]]
) -> ResolvedDiagramStyle:
    """Return fully‑specified diagram‑wide style (wires, background)."""
    st = _DEFAULT_DIAGRAM
    for layer in layers:
        if isinstance(layer, CircuitTheme):
            st = st.merged(layer.diagram)
        else:
            st = st.merged(layer)
    return ResolvedDiagramStyle(**asdict(st))


# ---------------------------------------------------------------------
# Lazy‑load built‑in themes
# ---------------------------------------------------------------------


def _load_builtin(name: str) -> CircuitTheme:
    """Lazy‑load a theme shipped inside the package."""
    name = name.lower()
    if name in _BUILTIN_THEMES:
        return _BUILTIN_THEMES[name]

    try:
        path = _pkg.files("pyqcircuit.themes").joinpath(f"{name}_theme.yaml")
        theme = CircuitTheme.from_yaml(path)
    except FileNotFoundError as exc:
        raise KeyError(f"No built‑in theme named '{name}'") from exc

    _BUILTIN_THEMES[name] = theme
    return theme


def get_theme(obj: str | CircuitTheme | None) -> CircuitTheme:
    """
    Helper used by QuantumCircuit.draw():
      * None: empty (default) theme
      * str: load built‑in theme of that name
      * CircuitTheme: pass through
    """
    if obj is None:
        return CircuitTheme()
    if isinstance(obj, CircuitTheme):
        return obj
    if isinstance(obj, str):
        return _load_builtin(obj)
    raise TypeError("theme must be str, CircuitTheme, or None")
