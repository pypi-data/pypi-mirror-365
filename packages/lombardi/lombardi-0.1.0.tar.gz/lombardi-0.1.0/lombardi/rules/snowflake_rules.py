"""Snowflake-specific optimization rules."""

from dataclasses import dataclass
from typing import List, Set
import sqlglot
from sqlglot import expressions as exp
from ..analyzers.optimization_suggester import OptimizationSuggestion


@dataclass
class SnowflakeOptimizationRule:
    """Snowflake-specific optimization rule."""
    
    name: str
    description: str
    category: str
    priority: str
    suggestion: str


class SnowflakeRules:
    """Snowflake-specific performance optimization rules."""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def analyze(self, sql: str) -> List[OptimizationSuggestion]:
        """Analyze SQL for Snowflake-specific optimizations."""
        try:
            parsed = sqlglot.parse_one(sql, dialect="snowflake")
        except Exception as e:
            raise ValueError(f"Failed to parse SQL: {e}")
        
        suggestions = []
        suggestions.extend(self._check_clustering_opportunities(parsed))
        suggestions.extend(self._check_result_caching(parsed))
        suggestions.extend(self._check_warehouse_sizing(parsed))
        suggestions.extend(self._check_time_travel(parsed))
        suggestions.extend(self._check_variant_usage(parsed))
        suggestions.extend(self._check_copy_optimization(parsed))
        
        return suggestions
    
    def _initialize_rules(self) -> List[SnowflakeOptimizationRule]:
        """Initialize Snowflake-specific rules."""
        return [
            SnowflakeOptimizationRule(
                name="cluster_key_recommendation",
                description="Large tables should have clustering keys",
                category="indexing",
                priority="medium",
                suggestion="Add clustering keys on frequently filtered columns"
            ),
            SnowflakeOptimizationRule(
                name="result_caching",
                description="Enable result caching for repeated queries",
                category="performance",
                priority="low",
                suggestion="Use result caching for dashboard queries"
            ),
            SnowflakeOptimizationRule(
                name="warehouse_sizing",
                description="Consider warehouse size for query complexity",
                category="performance", 
                priority="medium",
                suggestion="Use larger warehouses for complex analytics"
            ),
        ]
    
    def _check_clustering_opportunities(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check for clustering key opportunities."""
        suggestions = []
        
        # Find columns frequently used in WHERE and JOIN clauses
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
        
        # Suggest clustering on frequently used columns
        clustering_candidates = filter_columns.union(join_columns)
        if clustering_candidates:
            suggestions.append(OptimizationSuggestion(
                category="indexing",
                priority="medium",
                title="Clustering Key Opportunity",
                description=f"Consider adding clustering keys on frequently filtered columns: {', '.join(list(clustering_candidates)[:3])}",
                impact="Improved pruning and faster query execution on large tables",
                sql_example="-- ALTER TABLE your_table CLUSTER BY (column1, column2);"
            ))
        
        return suggestions
    
    def _check_result_caching(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check for result caching opportunities."""
        suggestions = []
        
        # Look for aggregations and complex calculations
        has_aggregations = bool(parsed.find(exp.AggFunc))
        has_window_functions = bool(parsed.find(exp.Window))
        has_complex_joins = len(list(parsed.find_all(exp.Join))) > 2
        
        if has_aggregations or has_window_functions or has_complex_joins:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                priority="low",
                title="Result Caching Opportunity",
                description="Complex query suitable for result caching",
                impact="Instant results for repeated identical queries",
                sql_example="-- Ensure USE_CACHED_RESULT = TRUE in session parameters"
            ))
        
        return suggestions
    
    def _check_warehouse_sizing(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check warehouse sizing recommendations."""
        suggestions = []
        
        # Count complexity indicators
        join_count = len(list(parsed.find_all(exp.Join)))
        subquery_count = len(list(parsed.find_all(exp.Subquery)))
        window_functions = len(list(parsed.find_all(exp.Window)))
        
        complexity_score = join_count * 2 + subquery_count * 3 + window_functions * 2
        
        if complexity_score > 10:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                priority="medium",
                title="Warehouse Sizing Recommendation",
                description="Complex query may benefit from larger warehouse",
                impact="Faster execution through increased compute resources",
                sql_example="-- Consider using LARGE or X-LARGE warehouse for this query"
            ))
        
        return suggestions
    
    def _check_time_travel(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check for time travel optimization opportunities."""
        suggestions = []
        
        # Look for timestamp-based queries that might benefit from AT/BEFORE
        time_functions = ["current_timestamp", "current_date", "dateadd", "datediff"]
        
        for func in parsed.find_all(exp.Func):
            if func.this and str(func.this).lower() in time_functions:
                suggestions.append(OptimizationSuggestion(
                    category="performance",
                    priority="low",
                    title="Time Travel Consideration",
                    description="Consider using AT or BEFORE clause for historical data",
                    impact="Access specific point-in-time data without full scan",
                    sql_example="-- SELECT * FROM table_name AT(TIMESTAMP => '2024-01-01'::timestamp)"
                ))
                break
        
        return suggestions
    
    def _check_variant_usage(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check for VARIANT data type optimization."""
        suggestions = []
        
        # Look for JSON/VARIANT operations (simplified heuristic)
        json_functions = ["parse_json", "get", "get_path", "flatten"]
        
        for func in parsed.find_all(exp.Func):
            if func.this and str(func.this).lower() in json_functions:
                suggestions.append(OptimizationSuggestion(
                    category="performance",
                    priority="medium",
                    title="VARIANT Query Optimization",
                    description="VARIANT queries can be optimized with proper techniques",
                    impact="Better performance for semi-structured data queries",
                    sql_example="-- Use FLATTEN() for array processing\\n-- Consider materializing frequently accessed paths"
                ))
                break
        
        return suggestions
    
    def _check_copy_optimization(self, parsed: exp.Expression) -> List[OptimizationSuggestion]:
        """Check for COPY command optimizations."""
        suggestions = []
        
        # This is primarily for ETL patterns
        # Look for INSERT patterns that might benefit from COPY
        for insert in parsed.find_all(exp.Insert):
            if insert.find(exp.Select):
                suggestions.append(OptimizationSuggestion(
                    category="performance", 
                    priority="low",
                    title="Bulk Loading Optimization",
                    description="Consider COPY command for large data loads",
                    impact="Much faster bulk data loading",
                    sql_example="-- Use COPY INTO instead of INSERT SELECT for large datasets"
                ))
                break
        
        return suggestions