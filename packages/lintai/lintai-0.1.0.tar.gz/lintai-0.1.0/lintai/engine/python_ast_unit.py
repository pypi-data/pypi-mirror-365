"""
A thin wrapper around `ast` that satisfies lintai.detectors.base.SourceUnit.

It:
•  Parses a single *.py* file.
•  Exposes helper methods detectors need today.
•  Is intentionally simple – improve taint‑tracking heuristics over time.
"""

from __future__ import annotations
import ast
from pathlib import Path
from typing import Iterable, List

from lintai.detectors.base import SourceUnit


class PythonASTUnit(SourceUnit):
    __slots__ = (
        "tree",
        "source",
        "_current",
        "_call_nodes",
        "_fstring_nodes",
        "modname",
        "is_ai_module",
    )

    def __init__(self, path: Path, text: str, project_root: Path):
        super().__init__(path)
        self.source = text
        self.tree = ast.parse(text, filename=str(path))
        for parent in ast.walk(self.tree):
            for child in ast.iter_child_nodes(parent):
                setattr(child, "parent", parent)
                # let helpers (is_ai_call) reach the tracker for this module
                setattr(child, "_unit", self)

        # --- NEW LOGIC for cleaner module names ---
        try:
            relative_path = path.relative_to(project_root)
            self.modname = ".".join(relative_path.with_suffix("").parts)
        except ValueError:
            # Fallback for paths outside the project root (like the test temp file)
            self.modname = ".".join(path.with_suffix("").parts[-2:])

        self._current = None
        self._call_nodes = None  # lazy build
        self._fstring_nodes = []  # filled by visitor
        # e.g.  path src/app/foo.py →  src.app.foo
        self.modname: str = ".".join(path.with_suffix("").parts).lstrip(".")

        # will be set by ProjectAnalyzer._mark_ai_modules()
        self.is_ai_module: bool = False

    # ──────────────────────────────────────────────────────────────
    #  Public helper: get dotted qualname of a node
    # ──────────────────────────────────────────────────────────────
    def qualname(self, node: ast.AST) -> str:  # noqa: D401
        """
        Return *module-qualified* name for **node**.

        • Works for ``FunctionDef``, ``AsyncFunctionDef`` and ``Lambda``
        • If node is not one of those, climbs to the nearest enclosing
          function; returns just ``self.modname`` when nothing matches.
        """
        # climb up until we're outside every nested function
        fn = node
        while fn and not isinstance(
            fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            fn = getattr(fn, "parent", None)

        if not fn:  # top-level statement
            return self.modname

        parts: list[str] = []
        cur = fn
        while cur and isinstance(
            cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)
        ):
            parts.append(cur.name if hasattr(cur, "name") else "<lambda>")
            cur = getattr(cur, "parent", None)

        parts.reverse()
        return ".".join([self.modname, *parts])

    # ---- helpers detectors already use ----------------------------------
    def joined_fstrings(self) -> Iterable[ast.JoinedStr]:
        """
        Return a cached list of all JoinedStr (f‑string) nodes.
        We build it only once with ast.walk ‑‑ cheap and correct.
        """
        if not self._fstring_nodes:  # first call → populate
            self._fstring_nodes = [
                n for n in ast.walk(self.tree) if isinstance(n, ast.JoinedStr)
            ]
        return self._fstring_nodes

    def calls(self) -> Iterable[ast.Call]:
        if self._call_nodes is None:  # only build once if somebody needs it
            self._call_nodes = [
                n for n in ast.walk(self.tree) if isinstance(n, ast.Call)
            ]
        return self._call_nodes

    def has_call(self, name: str, node: ast.AST) -> bool:
        """Does *node* (or its children) contain a Call whose dotted name ends‑with *name*?"""
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                func = n.func
                if isinstance(func, ast.Attribute):
                    dotted = _attr_to_str(func)
                elif isinstance(func, ast.Name):
                    dotted = func.id
                else:
                    continue
                if dotted.endswith(name):
                    return True
        return False

    # ----------------------- naïve taint logic --------------------------- #
    _TAINT_SOURCES = {"input", "sys.stdin"}

    def is_user_tainted(self, node: ast.AST) -> bool:
        """
        Very simple heuristic:
        • any Name whose id == 'user_input'
        • any Call to built‑in input()
        • any attribute/Name matching _TAINT_SOURCES
        """
        for n in ast.walk(node):
            if isinstance(n, ast.Name) and n.id.lower().startswith("user_"):
                return True
            if isinstance(n, ast.Call):
                target = _attr_to_str(n.func)
                if target in self._TAINT_SOURCES:
                    return True
        return False

    # placeholder – required by LLM02 detector
    def is_model_response(self, arg: ast.AST) -> bool:  # noqa: D401
        """Return True if *arg* is obviously an LLM completion response (heuristic)."""
        if isinstance(arg, ast.Call):
            return _attr_to_str(arg.func).endswith("ChatCompletion.create")
        return False


# ------------------------------------------------------------------------- #
# helpers                                                                   #
# ------------------------------------------------------------------------- #
def _attr_to_str(node: ast.AST) -> str:
    """Convert `foo.bar.baz` Attribute node into dotted string."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))
