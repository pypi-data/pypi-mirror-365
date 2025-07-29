"""Analyzes SQL query complexity metrics."""

from dataclasses import dataclass

import sqlglot
from sqlglot import expressions as exp


@dataclass
class ComplexityMetrics:
    """Query complexity metrics."""

    join_count: int
    subquery_count: int
    cte_count: int
    function_count: int
    nesting_depth: int
    table_count: int
    column_count: int
    complexity_score: float


class ComplexityAnalyzer:
    """Analyzes SQL query complexity."""

    def __init__(self, dialect: str = ""):
        self.dialect = dialect

    def analyze(self, sql: str) -> ComplexityMetrics:
        """Analyze SQL query complexity."""
        try:
            parsed = sqlglot.parse_one(sql, dialect=self.dialect)
        except Exception as e:
            raise ValueError(f"Failed to parse SQL: {e}")

        metrics = ComplexityMetrics(
            join_count=self._count_joins(parsed),
            subquery_count=self._count_subqueries(parsed),
            cte_count=self._count_ctes(parsed),
            function_count=self._count_functions(parsed),
            nesting_depth=self._calculate_nesting_depth(parsed),
            table_count=self._count_tables(parsed),
            column_count=self._count_columns(parsed),
            complexity_score=0.0,
        )

        metrics.complexity_score = self._calculate_complexity_score(metrics)
        return metrics

    def _count_joins(self, node: exp.Expression) -> int:
        """Count JOIN operations."""
        return len(list(node.find_all(exp.Join)))

    def _count_subqueries(self, node: exp.Expression) -> int:
        """Count subqueries."""
        return len(list(node.find_all(exp.Subquery)))

    def _count_ctes(self, node: exp.Expression) -> int:
        """Count CTEs (WITH clauses)."""
        with_nodes = list(node.find_all(exp.With))
        return sum(len(with_node.expressions) for with_node in with_nodes)

    def _count_functions(self, node: exp.Expression) -> int:
        """Count function calls."""
        return len(list(node.find_all(exp.Func)))

    def _count_tables(self, node: exp.Expression) -> int:
        """Count unique tables referenced."""
        tables = set()
        for table in node.find_all(exp.Table):
            if table.name:
                tables.add(table.name.lower())
        return len(tables)

    def _count_columns(self, node: exp.Expression) -> int:
        """Count column references."""
        return len(list(node.find_all(exp.Column)))

    def _calculate_nesting_depth(self, node: exp.Expression, depth: int = 0) -> int:
        """Calculate maximum nesting depth."""
        max_depth = depth

        for child in node.find_all(exp.Subquery):
            child_depth = self._calculate_nesting_depth(child, depth + 1)
            max_depth = max(max_depth, child_depth)

        return max_depth

    def _calculate_complexity_score(self, metrics: ComplexityMetrics) -> float:
        """Calculate overall complexity score (0-100)."""
        score = (
            metrics.join_count * 5
            + metrics.subquery_count * 10
            + metrics.cte_count * 3
            + metrics.function_count * 1
            + metrics.nesting_depth * 15
            + metrics.table_count * 2
            + metrics.column_count * 0.5
        )
        return min(score, 100.0)
