"""Command-line interface for Lombardi SQL performance advisor."""

import sys
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from .analyzers.complexity_analyzer import ComplexityAnalyzer
from .analyzers.antipattern_detector import AntipatternDetector
from .analyzers.optimization_suggester import OptimizationSuggester
from .rules.snowflake_rules import SnowflakeRules
from .rules.bigquery_rules import BigQueryRules

app = typer.Typer(
    name="lombardi",
    help="SQL performance analysis and optimization advisor",
    add_completion=False
)
console = Console()


@app.command()
def analyze(
    sql_file: Optional[Path] = typer.Argument(None, help="SQL file to analyze"),
    sql: Optional[str] = typer.Option(None, "--sql", "-s", help="SQL query string to analyze"),
    dialect: str = typer.Option("", "--dialect", "-d", help="SQL dialect (snowflake, bigquery, etc.)"),
    complexity_threshold: float = typer.Option(50.0, "--threshold", "-t", help="Complexity threshold (0-100)"),
    min_severity: str = typer.Option("medium", "--severity", help="Minimum severity to report (low, medium, high, critical)"),
    output_format: str = typer.Option("rich", "--format", "-f", help="Output format (rich, json, plain)"),
    include_suggestions: bool = typer.Option(True, "--suggestions/--no-suggestions", help="Include optimization suggestions"),
) -> None:
    """Analyze SQL query for performance issues and optimization opportunities."""
    
    # Get SQL content
    if sql_file:
        if not sql_file.exists():
            console.print(f"[red]Error: File {sql_file} not found[/red]")
            raise typer.Exit(1)
        sql_content = sql_file.read_text()
    elif sql:
        sql_content = sql
    else:
        console.print("[red]Error: Provide either --sql or a SQL file[/red]")
        raise typer.Exit(1)
    
    try:
        # Initialize analyzers
        complexity_analyzer = ComplexityAnalyzer(dialect)
        antipattern_detector = AntipatternDetector(dialect)
        optimization_suggester = OptimizationSuggester(dialect)
        
        # Run analysis
        complexity = complexity_analyzer.analyze(sql_content)
        antipatterns = antipattern_detector.detect(sql_content)
        
        # Filter antipatterns by severity
        severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        min_severity_level = severity_order.get(min_severity, 1)
        filtered_antipatterns = [
            ap for ap in antipatterns 
            if severity_order.get(ap.severity, 0) >= min_severity_level
        ]
        
        suggestions = []
        if include_suggestions:
            suggestions = optimization_suggester.suggest(sql_content)
            
            # Add warehouse-specific suggestions
            if dialect.lower() == "snowflake":
                snowflake_rules = SnowflakeRules()
                suggestions.extend(snowflake_rules.analyze(sql_content))
            elif dialect.lower() == "bigquery":
                bigquery_rules = BigQueryRules()
                suggestions.extend(bigquery_rules.analyze(sql_content))
        
        # Output results
        if output_format == "rich":
            _display_rich_output(complexity, filtered_antipatterns, suggestions, complexity_threshold)
        elif output_format == "json":
            _display_json_output(complexity, filtered_antipatterns, suggestions)
        else:
            _display_plain_output(complexity, filtered_antipatterns, suggestions)
            
    except Exception as e:
        console.print(f"[red]Error analyzing SQL: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def complexity(
    sql_file: Optional[Path] = typer.Argument(None, help="SQL file to analyze"),
    sql: Optional[str] = typer.Option(None, "--sql", "-s", help="SQL query string to analyze"),
    dialect: str = typer.Option("", "--dialect", "-d", help="SQL dialect"),
) -> None:
    """Analyze SQL query complexity metrics only."""
    
    # Get SQL content
    if sql_file:
        if not sql_file.exists():
            console.print(f"[red]Error: File {sql_file} not found[/red]")
            raise typer.Exit(1)
        sql_content = sql_file.read_text()
    elif sql:
        sql_content = sql
    else:
        console.print("[red]Error: Provide either --sql or a SQL file[/red]")
        raise typer.Exit(1)
    
    try:
        analyzer = ComplexityAnalyzer(dialect)
        metrics = analyzer.analyze(sql_content)
        
        # Display complexity metrics
        table = Table(title="SQL Complexity Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Complexity Score", f"{metrics.complexity_score:.1f}/100")
        table.add_row("Join Count", str(metrics.join_count))
        table.add_row("Subquery Count", str(metrics.subquery_count))
        table.add_row("CTE Count", str(metrics.cte_count))
        table.add_row("Function Count", str(metrics.function_count))
        table.add_row("Nesting Depth", str(metrics.nesting_depth))
        table.add_row("Table Count", str(metrics.table_count))
        table.add_row("Column Count", str(metrics.column_count))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error analyzing complexity: {e}[/red]")
        raise typer.Exit(1)


def _display_rich_output(complexity, antipatterns, suggestions, threshold):
    """Display results in rich format."""
    
    # Complexity score with color coding
    score_color = "green" if complexity.complexity_score < threshold else "red"
    console.print(Panel(
        f"[{score_color}]Complexity Score: {complexity.complexity_score:.1f}/100[/{score_color}]",
        title="SQL Analysis Results"
    ))
    
    # Complexity metrics table
    complexity_table = Table(title="Complexity Metrics")
    complexity_table.add_column("Metric", style="cyan")
    complexity_table.add_column("Value", style="yellow")
    
    complexity_table.add_row("Join Count", str(complexity.join_count))
    complexity_table.add_row("Subquery Count", str(complexity.subquery_count))
    complexity_table.add_row("CTE Count", str(complexity.cte_count))
    complexity_table.add_row("Function Count", str(complexity.function_count))
    complexity_table.add_row("Nesting Depth", str(complexity.nesting_depth))
    complexity_table.add_row("Table Count", str(complexity.table_count))
    complexity_table.add_row("Column Count", str(complexity.column_count))
    
    console.print(complexity_table)
    
    # Antipatterns
    if antipatterns:
        antipattern_table = Table(title="Detected Issues")
        antipattern_table.add_column("Pattern", style="cyan")
        antipattern_table.add_column("Severity", style="red")
        antipattern_table.add_column("Description")
        
        for ap in antipatterns:
            severity_color = {
                "low": "yellow",
                "medium": "orange1", 
                "high": "red",
                "critical": "bright_red"
            }.get(ap.severity, "white")
            
            antipattern_table.add_row(
                ap.pattern.replace("_", " ").title(),
                f"[{severity_color}]{ap.severity.upper()}[/{severity_color}]",
                ap.description
            )
        
        console.print(antipattern_table)
    else:
        console.print("[green]✓ No antipatterns detected[/green]")
    
    # Suggestions
    if suggestions:
        suggestions_table = Table(title="Optimization Suggestions")
        suggestions_table.add_column("Category", style="cyan")
        suggestions_table.add_column("Priority", style="yellow")
        suggestions_table.add_column("Suggestion")
        
        for suggestion in suggestions[:10]:  # Limit to top 10
            priority_color = {
                "low": "green",
                "medium": "yellow",
                "high": "orange1",
                "critical": "red"
            }.get(suggestion.priority, "white")
            
            suggestions_table.add_row(
                suggestion.category.title(),
                f"[{priority_color}]{suggestion.priority.upper()}[/{priority_color}]",
                f"[bold]{suggestion.title}[/bold]\\n{suggestion.description}"
            )
        
        console.print(suggestions_table)


def _display_json_output(complexity, antipatterns, suggestions):
    """Display results in JSON format."""
    import json
    
    result = {
        "complexity": {
            "score": complexity.complexity_score,
            "metrics": {
                "join_count": complexity.join_count,
                "subquery_count": complexity.subquery_count,
                "cte_count": complexity.cte_count,
                "function_count": complexity.function_count,
                "nesting_depth": complexity.nesting_depth,
                "table_count": complexity.table_count,
                "column_count": complexity.column_count,
            }
        },
        "antipatterns": [
            {
                "pattern": ap.pattern,
                "severity": ap.severity,
                "description": ap.description,
                "suggestion": ap.suggestion
            }
            for ap in antipatterns
        ],
        "suggestions": [
            {
                "category": s.category,
                "priority": s.priority,
                "title": s.title,
                "description": s.description,
                "impact": s.impact,
                "sql_example": s.sql_example
            }
            for s in suggestions
        ]
    }
    
    console.print(json.dumps(result, indent=2))


def _display_plain_output(complexity, antipatterns, suggestions):
    """Display results in plain text format."""
    console.print(f"Complexity Score: {complexity.complexity_score:.1f}/100")
    console.print(f"Joins: {complexity.join_count}, Subqueries: {complexity.subquery_count}")
    console.print(f"CTEs: {complexity.cte_count}, Functions: {complexity.function_count}")
    console.print(f"Nesting Depth: {complexity.nesting_depth}")
    console.print(f"Tables: {complexity.table_count}, Columns: {complexity.column_count}")
    
    if antipatterns:
        console.print("\\nIssues Found:")
        for ap in antipatterns:
            console.print(f"- [{ap.severity.upper()}] {ap.pattern}: {ap.description}")
    
    if suggestions:
        console.print("\\nSuggestions:")
        for s in suggestions[:5]:
            console.print(f"- [{s.priority.upper()}] {s.title}: {s.description}")


def main():
    """Main entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()