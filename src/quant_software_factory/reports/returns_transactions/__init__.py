"""Returns & Transactions report: CSV inputs to checked Markdown and JSON."""

from .cli import main
from .definitions import BLOCK_IDS, REPORT_DEFINITIONS, ReportDefinition
from .engine import EngineResult, run_engine
from .loader import load_inputs
from .report import build_report, render_markdown

__all__ = [
    "BLOCK_IDS",
    "REPORT_DEFINITIONS",
    "EngineResult",
    "ReportDefinition",
    "build_report",
    "load_inputs",
    "main",
    "render_markdown",
    "run_engine",
]
