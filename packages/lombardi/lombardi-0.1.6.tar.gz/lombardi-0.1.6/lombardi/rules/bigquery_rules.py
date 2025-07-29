"""BigQuery-specific optimization rules."""

from dataclasses import dataclass

import sqlglot
from sqlglot import expressions as exp

from ..analyzers.optimization_suggester import OptimizationSuggestion


@dataclass
class BigQueryOptimizationRule:
    """BigQuery-specific optimization rule."""

    name: str
    description: str
    category: str
    priority: str
    suggestion: str


class BigQueryRules:
    """BigQuery-specific performance optimization rules."""

    def __init__(self):
        self.rules = self._initialize_rules()

    def analyze(self, sql: str) -> list[OptimizationSuggestion]:
        """Analyze SQL for BigQuery-specific optimizations."""
        try:
            parsed = sqlglot.parse_one(sql, dialect="bigquery")
        except Exception as e:
            raise ValueError(f"Failed to parse SQL: {e}")

        suggestions = []
        suggestions.extend(self._check_partitioning_opportunities(parsed))
        suggestions.extend(self._check_clustering_opportunities(parsed))
        suggestions.extend(self._check_slot_optimization(parsed))
        suggestions.extend(self._check_array_operations(parsed))
        suggestions.extend(self._check_standard_sql_usage(parsed))
        suggestions.extend(self._check_materialized_views(parsed))
        suggestions.extend(self._check_streaming_optimization(parsed))

        return suggestions

    def _initialize_rules(self) -> list[BigQueryOptimizationRule]:
        """Initialize BigQuery-specific rules."""
        return [
            BigQueryOptimizationRule(
                name="partition_recommendation",
                description="Large tables should be partitioned",
                category="indexing",
                priority="high",
                suggestion="Partition tables by date/timestamp columns",
            ),
            BigQueryOptimizationRule(
                name="clustering_recommendation",
                description="Partitioned tables benefit from clustering",
                category="indexing",
                priority="medium",
                suggestion="Add clustering on frequently filtered columns",
            ),
            BigQueryOptimizationRule(
                name="slot_optimization",
                description="Optimize for slot usage efficiency",
                category="performance",
                priority="medium",
                suggestion="Structure queries to minimize slot usage",
            ),
        ]

    def _check_partitioning_opportunities(
        self, parsed: exp.Expression
    ) -> list[OptimizationSuggestion]:
        """Check for table partitioning opportunities."""
        suggestions = []

        # Look for date/timestamp filtering
        date_columns = set()
        timestamp_columns = set()

        for where in parsed.find_all(exp.Where):
            for comparison in where.find_all((exp.GT, exp.GTE, exp.LT, exp.LTE, exp.EQ)):
                left = comparison.left
                right = comparison.right

                if isinstance(left, exp.Column):
                    # Check if right side looks like a date
                    if isinstance(right, exp.Literal):
                        value = str(right.this)
                        if any(
                            pattern in value.lower() for pattern in ["date", "timestamp", "-", "/"]
                        ):
                            if "timestamp" in value.lower() or "datetime" in value.lower():
                                timestamp_columns.add(left.name)
                            else:
                                date_columns.add(left.name)

        if date_columns or timestamp_columns:
            all_date_cols = date_columns.union(timestamp_columns)
            suggestions.append(
                OptimizationSuggestion(
                    category="indexing",
                    priority="high",
                    title="Table Partitioning Opportunity",
                    description=f"Consider partitioning large tables by date/timestamp columns: {', '.join(list(all_date_cols)[:2])}",
                    impact="Dramatic cost reduction and query performance improvement",
                    sql_example="-- CREATE TABLE dataset.partitioned_table\\n-- PARTITION BY DATE(timestamp_column)\\n-- CLUSTER BY (other_column)",
                )
            )

        return suggestions

    def _check_clustering_opportunities(
        self, parsed: exp.Expression
    ) -> list[OptimizationSuggestion]:
        """Check for clustering opportunities."""
        suggestions = []

        # Find frequently filtered columns (excluding partition candidates)
        filter_columns = set()
        join_columns = set()

        for where in parsed.find_all(exp.Where):
            for col in where.find_all(exp.Column):
                if col.name:
                    filter_columns.add(col.name.lower())

        for join in parsed.find_all(exp.Join):
            if join.args.get("on"):
                for col in join.args["on"].find_all(exp.Column):
                    if col.name:
                        join_columns.add(col.name.lower())

        clustering_candidates = filter_columns.union(join_columns)
        if clustering_candidates:
            suggestions.append(
                OptimizationSuggestion(
                    category="indexing",
                    priority="medium",
                    title="Clustering Opportunity",
                    description=f"Consider clustering on frequently filtered columns: {', '.join(list(clustering_candidates)[:4])}",
                    impact="Improved query performance through better data locality",
                    sql_example="-- ALTER TABLE dataset.table_name\\n-- CLUSTER BY (column1, column2, column3, column4)",
                )
            )

        return suggestions

    def _check_slot_optimization(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Check for slot usage optimization."""
        suggestions = []

        # Look for patterns that might cause slot waste
        join_count = len(list(parsed.find_all(exp.Join)))
        len(list(parsed.find_all(exp.Subquery)))
        len(list(parsed.find_all(exp.Window)))

        # Check for SELECT * which can waste slots
        has_select_star = any(
            isinstance(expr, exp.Star)
            for select in parsed.find_all(exp.Select)
            for expr in select.expressions
        )

        if has_select_star:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="medium",
                    title="Slot Efficiency - Column Selection",
                    description="SELECT * wastes slots by processing unnecessary columns",
                    impact="Reduced slot usage and lower costs",
                    sql_example="-- Select only needed columns instead of SELECT *",
                )
            )

        # Check for inefficient JOINs
        if join_count > 3:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="medium",
                    title="Slot Efficiency - JOIN Optimization",
                    description="Multiple JOINs may benefit from pre-aggregation or materialized views",
                    impact="Better slot utilization and performance",
                    sql_example="-- Consider pre-aggregating data or using materialized views",
                )
            )

        return suggestions

    def _check_array_operations(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Check for array operation optimizations."""
        suggestions = []

        # Look for UNNEST operations
        unnest_functions = []
        for func in parsed.find_all(exp.Func):
            if func.this and str(func.this).lower() == "unnest":
                unnest_functions.append(func)

        if unnest_functions:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="medium",
                    title="Array Operation Optimization",
                    description="UNNEST operations can be optimized for better performance",
                    impact="More efficient array processing",
                    sql_example="-- Use UNNEST with WITH OFFSET for position tracking\\n-- Consider array functions like ARRAY_AGG for reverse operations",
                )
            )

        return suggestions

    def _check_standard_sql_usage(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Check for Standard SQL best practices."""
        suggestions = []

        # Look for legacy SQL patterns (this is simplified)
        # In practice, you'd check for specific BigQuery legacy functions

        # Check for proper use of STRUCT and ARRAY types
        has_structs = any("struct" in str(node).lower() for node in parsed.find_all(exp.DataType))

        if has_structs:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="low",
                    title="STRUCT Usage Optimization",
                    description="Optimize STRUCT field access patterns",
                    impact="Better performance for nested data queries",
                    sql_example="-- Use dot notation for STRUCT field access\\n-- Consider flattening frequently accessed nested fields",
                )
            )

        return suggestions

    def _check_materialized_views(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Check for materialized view opportunities."""
        suggestions = []

        # Look for aggregation patterns that could benefit from materialized views
        has_aggregations = bool(parsed.find(exp.AggFunc))
        has_group_by = bool(parsed.find(exp.Group))
        join_count = len(list(parsed.find_all(exp.Join)))

        if has_aggregations and has_group_by and join_count > 1:
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="medium",
                    title="Materialized View Opportunity",
                    description="Complex aggregation query could benefit from materialized view",
                    impact="Pre-computed results for faster query response",
                    sql_example="-- CREATE MATERIALIZED VIEW dataset.mv_name AS\\n-- (your aggregation query)",
                )
            )

        return suggestions

    def _check_streaming_optimization(self, parsed: exp.Expression) -> list[OptimizationSuggestion]:
        """Check for streaming insert optimizations."""
        suggestions = []

        # Look for INSERT patterns
        for _insert in parsed.find_all(exp.Insert):
            suggestions.append(
                OptimizationSuggestion(
                    category="performance",
                    priority="low",
                    title="Streaming Insert Consideration",
                    description="For high-frequency inserts, consider streaming optimizations",
                    impact="Better performance for real-time data ingestion",
                    sql_example="-- Use insertId for deduplication\\n-- Batch inserts when possible\\n-- Consider BigQuery Storage Write API",
                )
            )
            break  # Only suggest once

        return suggestions
