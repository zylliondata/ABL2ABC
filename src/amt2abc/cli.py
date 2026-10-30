import json
from typing import Any, Dict, Optional

import click

from amt2abc import __version__


@click.group()
@click.version_option(version=__version__, prog_name="amt2abc")
def main() -> None:
    """AMT2ABC: Atomic Mechanism Triplets to Atomic Business Capabilities."""


@main.command()
def list() -> None:  # noqa: A001
    """List available AMTs and ABCs."""
    from amt2abc.parser.abc_parser import ABCParser
    from amt2abc.parser.amt_parser import AMTParser

    amts = AMTParser().load_all()
    abcs = ABCParser().load_all()
    click.echo(f"AMT2ABC Compiler v{__version__}")
    click.echo(f"AMTs: {len(amts)} available")
    for amt in amts:
        click.echo(f"  - {amt.id}: {amt.name}")
    click.echo(f"ABCs: {len(abcs)} available")
    for abc in abcs:
        click.echo(f"  - {abc.id}: {abc.name}")


@main.command()
@click.argument("amt_id")
@click.option("--format", "-f", "output_format", default="text")
def info(amt_id: str, output_format: str) -> None:
    """Show details of an AMT by ID."""
    from amt2abc.parser.amt_parser import AMTParser

    amt = next(
        (a for a in AMTParser().load_all() if a.id == amt_id),
        None,
    )
    if amt is None:
        raise click.ClickException(f"AMT not found: {amt_id}")

    data: Dict[str, Any] = {
        "id": amt.id,
        "name": amt.name,
        "domain": amt.domain,
        "triplets": [
            {
                "cause": t.cause,
                "effect": t.effect,
                "relation": t.relation,
                "mechanism": t.mechanism,
                "weight": t.weight,
                "confidence": t.confidence,
            }
            for t in amt.triplets
        ],
        "layer": amt.layer,
        "evidence_source": amt.evidence_source,
        "mcl_engine": amt.mcl_engine,
    }

    if output_format == "json":
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
        return

    click.echo(f"AMT: {amt.id}  ({amt.name})")
    click.echo(f"Domain: {amt.domain}")
    click.echo(f"Layer: {amt.layer or '-'}  Evidence: {amt.evidence_source or '-'}")
    click.echo(f"Triplets: {len(amt.triplets)}")
    for t in amt.triplets:
        click.echo(
            f"  {t.cause} --{t.relation}--> {t.effect} "
            f"(w={t.weight}, c={t.confidence})"
        )
    if amt.secp is not None:
        click.echo(f"SECP subject: {amt.secp.S.subject}")
        click.echo(f"SECP process: {', '.join(amt.secp.P)}")


@main.command()
@click.argument("source")
@click.argument("target")
def graph(source: str, target: str) -> None:
    """Find a causal path between two variables in the AMT graph."""
    from amt2abc.compiler.graph import AMTGraph
    from amt2abc.parser.amt_parser import AMTParser

    amts = AMTParser().load_all()
    amt_graph = AMTGraph()
    amt_graph.build(amts)
    path = amt_graph.find_path(source, target)

    if not path:
        click.echo(f"No path found from '{source}' to '{target}'.")
        return

    click.echo(f"Path: {' -> '.join(path)}")


@main.command()
@click.option("--export", "export_path", default=None, help="Write graph JSON to path")
def build(export_path: str) -> None:
    """Build the AMT graph and print a summary report."""
    from amt2abc.compiler.builder import GraphBuilder

    builder = GraphBuilder().from_directory()
    graph, report = builder.build_checked()

    click.echo(f"AMTs: {report.amt_count}")
    click.echo(f"Variables: {report.variable_count}")
    click.echo(f"Variable edges: {report.variable_edge_count}")
    click.echo(f"AMT edges: {report.amt_edge_count}")
    click.echo(f"Status: {'OK' if report.ok else 'WARNINGS'}")
    for warning in report.warnings:
        click.echo(f"  ! {warning}")

    if export_path:
        out = builder.export_json(export_path)
        click.echo(f"Exported: {out}")


@main.command()
@click.argument("goal_text")
@click.option("--format", "-f", "output_format", default="text")
def goal(goal_text: str, output_format: str) -> None:
    """Parse a natural-language goal statement."""
    from amt2abc.parser.gs_parser import GSParser

    gs = GSParser().parse_text(goal_text)

    if output_format == "json":
        click.echo(
            json.dumps(gs.model_dump(), ensure_ascii=False, indent=2)
        )
        return

    click.echo(f"Text: {gs.text}")
    click.echo(f"Target variable: {gs.target_variable}")
    click.echo(f"Desired direction: {gs.desired_direction}")
    click.echo(f"Keywords: {', '.join(gs.keywords) if gs.keywords else '-'}")


@main.command()
@click.argument("abl_path")
@click.option("--format", "-f", "output_format", default="text")
def abl(abl_path: str, output_format: str) -> None:
    """Inspect an Atomic Business Loop (ABL) definition."""
    from amt2abc.parser.abl_parser import ABLParseError, ABLParser

    try:
        loop = ABLParser().load(abl_path)
    except ABLParseError as exc:
        raise click.ClickException(str(exc)) from exc

    if output_format == "json":
        click.echo(
            json.dumps(loop.model_dump(), ensure_ascii=False, indent=2)
        )
        return

    click.echo(f"ABL: {loop.id} - {loop.name}")
    click.echo(f"Domain: {loop.domain}")
    click.echo(f"Goal: {loop.goal.text}")
    click.echo(f"Trigger: {loop.trigger}")
    click.echo(f"Steps: {len(loop.steps)}")
    for step in loop.steps:
        stage = step.secp_stage or "-"
        click.echo(
            f"  [{stage}] {step.name} ({step.actor or '-'})"
        )
    kpis = ", ".join(k.name for k in loop.kpis) if loop.kpis else "-"
    click.echo(f"KPIs: {kpis}")


@main.command()
@click.argument("abl_path")
@click.option("--format", "-f", "output_format", default="text")
def validate(abl_path: str, output_format: str) -> None:
    """Validate an ABL definition for completeness."""
    from amt2abc.compiler.validator import ABLValidator
    from amt2abc.parser.abl_parser import ABLParseError, ABLParser

    try:
        loop = ABLParser().load(abl_path)
    except ABLParseError as exc:
        raise click.ClickException(str(exc)) from exc

    report = ABLValidator().validate(loop)

    if output_format == "json":
        click.echo(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2)
        )
    else:
        click.echo(f"ABL: {loop.id}")
        click.echo(
            f"Status: {'OK' if report.is_valid else 'INVALID'}"
        )
        for finding in report.findings:
            click.echo(
                f"  [{finding.level.upper()}] {finding.code}: "
                f"{finding.message}"
            )
        click.echo(
            f"Errors: {len(report.errors)}, "
            f"Warnings: {len(report.warnings)}"
        )

    if not report.is_valid:
        raise click.exceptions.Exit(1)


@main.command()
@click.argument("goal", required=False)
@click.option("--abl", "abl_path", default=None, help="Compile an ABL YAML file")
@click.option("--format", "-f", "output_format", default="text")
def compile(  # noqa: A001
    goal: Optional[str],
    abl_path: Optional[str],
    output_format: str,
) -> None:
    """Compile a goal statement into recommended ABCs."""
    from amt2abc.compiler.pipeline import CompilerPipeline
    from amt2abc.parser.abl_parser import ABLParseError, ABLParser

    pipeline = CompilerPipeline()
    if abl_path:
        try:
            loop = ABLParser().load(abl_path)
        except ABLParseError as exc:
            raise click.ClickException(str(exc)) from exc
        result: Dict[str, Any] = pipeline.compile_abl(loop)
    elif goal:
        result = pipeline.compile(goal)
    else:
        raise click.UsageError("Provide GOAL text or --abl <path>")

    if output_format == "json":
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))
        return

    abl_info = result.get("abl")
    if abl_info:
        validation = abl_info["validation"]
        status = "OK" if validation["valid"] else "INVALID"
        click.echo(
            f"ABL: {abl_info['id']} (validation: {status}, "
            f"warnings={validation['warnings']})"
        )
    click.echo(f"Goal: {result['goal']}")
    if result["target_variable"]:
        click.echo(
            f"Target: {result['target_variable']} "
            f"({result['desired_direction']})"
        )
    click.echo(f"Matched AMTs: {len(result['matched_amts'])}")
    for amt in result["matched_amts"]:
        click.echo(f"  {amt['id']:<30} score={amt['score']}")
    subgraph = result["influencing_subgraph"]
    click.echo(
        f"Influencing AMTs: {len(subgraph['amts']) if subgraph else 0}"
    )
    abcs = result["recommended_abcs"]
    click.echo(f"Recommended ABCs: {len(abcs)}")
    for abc in abcs:
        click.echo(
            f"  {abc['id']:<30} category={abc['category']} "
            f"score={abc['score']} from={','.join(abc['source_amts'])}"
        )
