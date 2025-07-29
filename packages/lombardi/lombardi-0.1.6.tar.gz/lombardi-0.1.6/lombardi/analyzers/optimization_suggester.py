"""Suggests SQL optimizations based on analysis."""

from dataclasses import dataclass

import sqlglot
from sqlglot import expressions as exp

from .antipattern_detector import AntipatternDetector, AntipatternIssue
from .complexity_analyzer import ComplexityAnalyzer, ComplexityMetrics


@dataclass
class OptimizationSuggestion:
    """Represents an optimization suggestion."""

    category: str  # "indexing", "rewriting", "structure", "performance"
    priority: str  # "low", "medium", "high", "critical"
    title: str
    description: str
    impact: str  # Expected performance impact
    sql_example: str = ""


class OptimizationSuggester:
    """Suggests SQL optimizations."""

    def __init__(self, dialect: str = ""):
        self.dialect = dialect
        self.complexity_analyzer = ComplexityAnalyzer(dialect)
        self.antipattern_detector = AntipatternDetector(dialect)

    def suggest(self, sql: str) -> list[OptimizationSuggestion]:
        """Generate optimization suggestions for SQL query."""
        try:
            parsed = sqlglot.parse_one(sql, dialect=self.dialect)
        except Exception as e:
            raise ValueError(f"Failed to parse SQL: {e}")

        suggestions = []

        # Analyze complexity and antipatterns
        complexity = self.complexity_analyzer.analyze(sql)
        antipatterns = self.antipattern_detector.detect(sql)

        # Generate suggestions based on analysis
        suggestions.extend(self._suggest_from_complexity(complexity, parsed))
        suggestions.extend(self._suggest_from_antipatterns(antipatterns))
        suggestions.extend(self._suggest_indexing(parsed))
        suggestions.extend(self._suggest_query_rewriting(parsed))

        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        suggestions.sort(key=lambda x: priority_order.get(x.priority, 3))

        return suggestions

    def _suggest_from_complexity(
        self, metrics: ComplexityMetrics, parsed: exp.Expression
    ) -> list[OptimizationSuggestion]:
        """Generate suggestions based on complexity metrics."""
        suggestions = []

        if metrics.complexity_score > 75:
            suggestions.append(
                OptimizationSuggestion(
                    category="structure",
                    priority="high",
                    title="High Query Complexity",
                    description=f"Query complexity score is {metrics.complexity_score:.1f}/100. Consider breaking into smaller queries.",
                    impact="Significant reduction in execution time and resource usage",
                )
            )

        if metrics.join_count > 5:
            suggestions.append(
                OptimizationSuggestion(
                    category="structure",
                    priority="medium",
                    title="Many JOINs Detected",
                    description=f"Query has {metrics.join_count} JOINs. Consider using materialized views or denormalization.",
                    impact="Reduced JOIN overhead and faster execution",
                )
            )

        if metrics.nesting_depth > 3:
            suggestions.append(
                OptimizationSuggestion(
                    category="rewriting",
                    priority="medium",
                    title="Deep Query Nesting",
                    description=f"Query nesting depth is {metrics.nesting_depth}. Consider using CTEs for readability.",
                    impact="Improved query plan and easier optimization",
                )
            )

        if metrics.subquery_count > 2:
            suggestions.append(
                OptimizationSuggestion(
                    category="rewriting",
                    priority="medium",
                    title="Multiple Subqueries",
                    description=f"Query has {metrics.subquery_count} subqueries. Consider converting to JOINs where possible.",
                    impact="Better query plan optimization and performance",
                )
            )

        return suggestions

    def _suggest_from_antipatterns(
        self, antipatterns: list[AntipatternIssue]
    ) -> list[OptimizationSuggestion]:
        """Generate suggestions from antipattern detection."""
        suggestions = []

        for issue in antipatterns:
            priority_map = {
                "critical": "critical",
                "high": "high",
                "medium": "medium",
                "low": "low",
            }

            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority=priority_map.get(issue.severity, "medium"),
                    title=issue.pattern.replace("_", " ").title(),
                    description=f"{issue.description}. {issue.suggestion}",
                    impact="Improved query performance and resource efficiency",
                )
            )

        return suggestions

    def _suggest_indexing(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Suggest indexing opportunities."""
        suggestions = []

        # Find columns used in WHERE clauses
        where_columns = set()
        for where in parsed.find_all(exp.Where):
            for col in where.find_all(exp.Column):
                if col.table and col.name:
                    where_columns.add(f"{col.table}.{col.name}")
                elif col.name:
                    where_columns.add(col.name)

        if where_columns:
            suggestions.append(
                OptimizationSuggestion(
                    category="indexing",
                    priority="medium",
                    title="Index Optimization Opportunity",
                    description=f"Consider adding indexes on columns used in WHERE clauses: {', '.join(list(where_columns)[:3])}{'...' if len(where_columns) > 3 else ''}",
                    impact="Dramatically faster WHERE clause evaluation",
                )
            )

        # Find columns used in JOIN conditions
        join_columns = set()
        for join in parsed.find_all(exp.Join):
            if join.args.get("on"):
                for col in join.args["on"].find_all(exp.Column):
                    if col.table and col.name:
                        join_columns.add(f"{col.table}.{col.name}")
                    elif col.name:
                        join_columns.add(col.name)

        if join_columns:
            suggestions.append(
                OptimizationSuggestion(
                    category="indexing",
                    priority="high",
                    title="JOIN Index Optimization",
                    description=f"Ensure indexes exist on JOIN columns: {', '.join(list(join_columns)[:3])}{'...' if len(join_columns) > 3 else ''}",
                    impact="Significantly faster JOIN operations",
                )
            )

        return suggestions

    def _suggest_query_rewriting(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Suggest query rewriting opportunities."""
        suggestions = []

        # Suggest EXISTS instead of IN with subqueries
        for predicate in parsed.find_all(exp.In):
            if predicate.find(exp.Subquery):
                suggestions.append(
                    OptimizationSuggestion(
                        category="rewriting",
                        priority="medium",
                        title="Use EXISTS Instead of IN",
                        description="Replace IN subquery with EXISTS for better performance",
                        impact="More efficient subquery execution",
                        sql_example="-- Instead of: WHERE id IN (SELECT ...)\n-- Use: WHERE EXISTS (SELECT 1 FROM ... WHERE ...)",
                    )
                )

        # Suggest UNION ALL instead of UNION when duplicates don't matter
        for union in parsed.find_all(exp.Union):
            if union.args.get("distinct") is not False:  # Default UNION is DISTINCT
                suggestions.append(
                    OptimizationSuggestion(
                        category="rewriting",
                        priority="low",
                        title="Consider UNION ALL",
                        description="Use UNION ALL instead of UNION if duplicate elimination is not needed",
                        impact="Avoids expensive duplicate removal step",
                        sql_example="-- Change: SELECT ... UNION SELECT ...\n-- To: SELECT ... UNION ALL SELECT ...",
                    )
                )

        # Suggest limiting results for development/testing
        has_limit = bool(parsed.find(exp.Limit))
        # Note: exp.Top may not exist in all SQLGlot versions
        has_top = False
        try:
            has_top = bool(parsed.find(getattr(exp, "Top", type(None))))
        except AttributeError:
            pass

        if not has_limit and not has_top:
            # Check if it's likely a development query (no aggregations, no specific WHERE conditions)
            has_aggregations = bool(parsed.find(exp.AggFunc))
            where_clauses = list(parsed.find_all(exp.Where))

            if not has_aggregations and len(where_clauses) == 0:
                suggestions.append(
                    OptimizationSuggestion(
                        category="performance",
                        priority="low",
                        title="Consider Adding LIMIT",
                        description="Add LIMIT clause for development and testing to avoid scanning large datasets",
                        impact="Prevents accidentally processing entire large tables",
                        sql_example="-- Add: LIMIT 1000",
                    )
                )

        return suggestions
