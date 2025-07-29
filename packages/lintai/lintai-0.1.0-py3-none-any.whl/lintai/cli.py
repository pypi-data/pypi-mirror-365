# lintai/cli.py
from __future__ import annotations

import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Any

import typer
from typer import Argument, Context, Option

from lintai.cli_support import init_common
from lintai.detectors import run_all
from lintai.core import report
import lintai.engine as _engine
import uvicorn

from lintai.engine.inventory_builder import build_inventory
from lintai.engine.inventory_builder import (
    classify_sink,
    detect_frameworks,
    extract_ast_components,
)
from lintai.engine.analysis import ProjectAnalyzer
from lintai.models.inventory import FileInventory


app = typer.Typer(
    help="Lintai – shift-left GenAI security scanner",
    add_completion=False,  # ← hides show/install-completion flags
)


# ──────────────────────────────────────────────────────────────────────────────
# SHARED BOOTSTRAP (runs once per CLI call) ───────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
def _bootstrap(
    ctx: Context,
    *,
    paths: List[Path],
    env_file: Path | None,
    log_level: str,
    ai_call_depth: int,
    ruleset: Path | None,
) -> None:
    """Parse Python files + initialise AI-analysis engine (once)."""
    if ctx.obj is None:
        ctx.obj = {}
    if "units" in ctx.obj:  # another sub-command already did this
        return

    init_common(
        ctx,
        paths=paths,
        env_file=env_file,
        log_level=log_level,
        ai_call_depth=ai_call_depth,
        ruleset=ruleset,
    )


# ──────────────────────────────────────────────────────────────────────────────
# TOP-LEVEL OPTIONS – only --version here -------------------------------------
# ──────────────────────────────────────────────────────────────────────────────
@app.callback(invoke_without_command=True)
def top_callback(
    ctx: Context,
    version: bool = Option(False, "--version", help="Show version and exit"),
):
    if version:
        from lintai import __version__

        typer.echo(f"Lintai {__version__}")
        raise typer.Exit()


# ──────────────────────────────────────────────────────────────────────────────
# find-issues  ---------------------------------------------------------------
# ──────────────────────────────────────────────────────────────────────────────
@app.command("find-issues", help="Run all detectors and emit findings JSON.")
def find_issues_cmd(
    ctx: Context,
    paths: List[Path] = Argument(..., help="Files or directories to analyse"),
    ruleset: Path | None = Option(
        None, "--ruleset", "-r", help="Custom rule file/folder"
    ),
    env_file: Path | None = Option(None, "--env-file", "-e", help="Optional .env"),
    log_level: str = Option("INFO", "--log-level", "-l", help="Logging level"),
    ai_call_depth: int = Option(
        2,
        "--ai-call-depth",
        "-d",
        help="How many caller layers to mark as AI-related (default 2)",
    ),
    output: Path = Option(
        None, "--output", "-o", help="Write JSON output to file (default: stdout)"
    ),
):
    _bootstrap(
        ctx,
        paths=paths,
        env_file=env_file,
        log_level=log_level,
        ai_call_depth=ai_call_depth,
        ruleset=ruleset,
    )

    units = ctx.obj["units"]
    findings = []
    for u in units:
        findings.extend(run_all(u))

    # Save full report with LLM usage - use first path for report name
    path_for_report = str(paths[0]) if paths else "unknown"
    report_data = report.make_findings_report(findings, path_for_report)
    report.write_report_obj(report_data, output)

    if output:
        typer.echo(f"\n✅ Report written to {output}")

    # Exit codes for lintai find-issues command:
    # - 0: scan completed successfully with no blocking findings
    # - 1: scan completed successfully but found blocking/critical findings
    # Note: The UI server treats both 0 and 1 as successful scan completion
    if any(f.severity in ("blocker", "critical") for f in findings):
        raise typer.Exit(1)


def create_graph_payload(
    inventories: List[FileInventory],
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Converts the inventories into a Cytoscape.js-compatible graph format.
    Includes all function/component nodes and their call relationships.
    Shows complete call chains: function → function → AI component.
    Optimized for performance using flat maps.
    Canonicalizes AI/LLM nodes so all edges point to a single node per AI/LLM component.
    """
    AI_TYPES = {
        "LLM",
        "Prompt",
        "Chain",
        "Tool",
        "Agent",
        "MultiAgent",
        "Memory",
        "VectorDB",
        "Retriever",
        "Parser",
        "GenericAI",
        "UI",
        "Lifecycle",
        "DocumentLoader",
    }
    nodes = []
    edges = []
    seen_nodes = set()
    component_id_map = {}
    ai_component_names = set()
    all_components = {}
    llm_canonical_id_map = {}

    # Build a flat map of all components for fast lookup
    for inventory in inventories:
        for comp in inventory.components:
            node_id = f"{comp.name}:{comp.location}:{comp.component_type}"
            component_id_map[comp.name] = node_id
            all_components[comp.name] = comp
            if comp.component_type in AI_TYPES:
                ai_component_names.add(comp.name)

    # Build canonical map for AI/LLM nodes (name+type only)
    for name in ai_component_names:
        comp = all_components[name]
        canonical_id = f"{comp.name}:{comp.component_type}"
        llm_canonical_id_map[name] = canonical_id
        if canonical_id not in seen_nodes:
            nodes.append(
                {
                    "data": {
                        "id": canonical_id,
                        "label": comp.name,
                        "type": comp.component_type,
                        "file": (
                            comp.location.split(":")[0]
                            if ":" in comp.location
                            else "unknown"
                        ),
                    }
                }
            )
            seen_nodes.add(canonical_id)

    # Add all callers of AI components as nodes
    for comp in all_components.values():
        node_id = component_id_map[comp.name]
        for rel in comp.relationships:
            if rel.type == "calls" and rel.target_name in ai_component_names:
                if node_id not in seen_nodes:
                    nodes.append(
                        {
                            "data": {
                                "id": node_id,
                                "label": comp.name,
                                "type": comp.component_type,
                                "file": (
                                    comp.location.split(":")[0]
                                    if ":" in comp.location
                                    else "unknown"
                                ),
                            }
                        }
                    )
                    seen_nodes.add(node_id)

    # Add all function components that have "calls" relationships as nodes
    for comp in all_components.values():
        node_id = component_id_map[comp.name]
        has_calls = any(rel.type == "calls" for rel in comp.relationships)
        if has_calls and node_id not in seen_nodes:
            nodes.append(
                {
                    "data": {
                        "id": node_id,
                        "label": comp.name,
                        "type": comp.component_type,
                        "file": (
                            comp.location.split(":")[0]
                            if ":" in comp.location
                            else "unknown"
                        ),
                    }
                }
            )
            seen_nodes.add(node_id)

    # Add target functions that are called by other functions as nodes
    for comp in all_components.values():
        for rel in comp.relationships:
            if rel.type == "calls" and rel.target_name in all_components:
                target_comp = all_components[rel.target_name]
                target_node_id = component_id_map[rel.target_name]
                if target_node_id not in seen_nodes:
                    nodes.append(
                        {
                            "data": {
                                "id": target_node_id,
                                "label": target_comp.name,
                                "type": target_comp.component_type,
                                "file": (
                                    target_comp.location.split(":")[0]
                                    if ":" in target_comp.location
                                    else "unknown"
                                ),
                            }
                        }
                    )
                    seen_nodes.add(target_node_id)

    # Add ALL 'calls' edges: function→function and function→AI component
    for comp in all_components.values():
        source_id = component_id_map[comp.name]
        for rel in comp.relationships:
            if rel.type == "calls":
                target_id = None
                # Check if target is an AI component (use canonical ID)
                if rel.target_name in ai_component_names:
                    target_id = llm_canonical_id_map.get(rel.target_name)
                # Check if target is a regular function component
                elif rel.target_name in all_components:
                    target_id = component_id_map[rel.target_name]

                if source_id and target_id:
                    edges.append(
                        {
                            "data": {
                                "source": source_id,
                                "target": target_id,
                                "label": rel.type,
                            }
                        }
                    )
    return {"nodes": nodes, "edges": edges}


# ──────────────────────────────────────────────────────────────────────────────
# catalog-ai  ----------------------------------------------------------------
# ──────────────────────────────────────────────────────────────────────────────
@app.command("catalog-ai", help="Emit a unified JSON inventory of all AI components.")
def catalog_ai_cmd(
    ctx: Context,
    paths: List[Path] = Argument(..., help="Files or directories to analyse"),
    ruleset: Path = Option(None, "--ruleset", "-r", help="Custom rule file/folder"),
    env_file: Path = Option(None, "--env-file", "-e", help="Optional .env"),
    log_level: str = Option("INFO", "--log-level", "-l", help="Logging level"),
    ai_call_depth: int = Option(
        2,
        "--ai-call-depth",
        "-d",
        help="How many caller layers to trace for relationships",
    ),
    output: Path = Option(
        None, "--output", "-o", help="Write JSON output to file (default: stdout)"
    ),
    graph: bool = Option(
        False,
        "--graph",
        "-g",
        help="Include full call-graph payload for visualization.",
    ),
):
    """
    Analyzes the codebase to produce a unified inventory of AI components,
    optionally including a full graph representation.
    """
    _bootstrap(
        ctx,
        paths=paths,
        env_file=env_file,
        log_level=log_level,
        ai_call_depth=ai_call_depth,
        ruleset=ruleset,
    )

    units = ctx.obj["units"]

    # Use the already-initialized global ai_analyzer
    from lintai.engine import ai_analyzer

    analyzer = ai_analyzer

    # Get the results from the .inventories attribute
    inventory_list = [inv.model_dump() for inv in analyzer.inventories.values()]

    # Prepare the final output object
    final_output = {"inventory_by_file": inventory_list}

    # Conditionally add the graph payload if the --graph flag is present
    if graph:
        graph_data = create_graph_payload(list(analyzer.inventories.values()))
        final_output["graph"] = graph_data

    # 5. Write the final JSON to the specified output or to the console
    if output:
        output.write_text(json.dumps(final_output, indent=2))
        typer.echo(f"\n✅ Inventory written to {output}")
    else:
        typer.echo(json.dumps(final_output, indent=2))


# ──────────────────────────────────────────────────────────────────────────────
# ui  ---------------------------------------------------------------------------
# ──────────────────────────────────────────────────────────────────────────────
@app.command("ui", help="Launch browser UI")
def ui_cmd(
    ctx: Context,
    port: int = Option(8501, "--port", "-p", help="Port to listen on"),
    reload: bool = Option(False, "--reload", help="Auto-reload on code changes"),
    log_level: str = Option("INFO", "--log-level", "-l", help="Logging level"),
):
    """
    Start FastAPI + React UI.
    """
    # Initialize logging with the specified level
    init_common(
        ctx,
        paths=[Path.cwd()],  # dummy path for UI
        env_file=None,
        log_level=log_level,
        ai_call_depth=1,  # dummy depth for UI
        ruleset=None,
    )

    # Set the server log level for CLI subprocesses
    from lintai.ui.server import set_server_log_level

    set_server_log_level(log_level)

    uvicorn.run(
        "lintai.ui.server:app",
        host="127.0.0.1",
        port=port,
        reload=reload,
        log_level=log_level.lower(),
    )


# ──────────────────────────────────────────────────────────────────────────────
def main() -> None:  # entry-point in setup.cfg / pyproject.toml
    app()


if __name__ == "__main__":
    main()
