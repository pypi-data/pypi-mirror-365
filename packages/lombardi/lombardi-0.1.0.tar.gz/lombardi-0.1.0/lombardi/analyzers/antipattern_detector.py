"""Detects SQL antipatterns that hurt performance."""

from dataclasses import dataclass
from typing import List, Set
import sqlglot
from sqlglot import expressions as exp


@dataclass
class AntipatternIssue:
    """Represents a detected antipattern."""
    
    pattern: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggestion: str
    line_number: int = 0


class AntipatternDetector:
    """Detects common SQL antipatterns."""
    
    def __init__(self, dialect: str = ""):
        self.dialect = dialect
    
    def detect(self, sql: str) -> List[AntipatternIssue]:
        """Detect antipatterns in SQL query."""
        try:
            parsed = sqlglot.parse_one(sql, dialect=self.dialect)
        except Exception as e:
            raise ValueError(f"Failed to parse SQL: {e}")
        
        issues = []
        issues.extend(self._detect_select_star(parsed))
        issues.extend(self._detect_cartesian_joins(parsed))
        issues.extend(self._detect_missing_where_clause(parsed))
        issues.extend(self._detect_unnecessary_distinct(parsed))
        issues.extend(self._detect_subquery_in_select(parsed))
        issues.extend(self._detect_functions_in_where(parsed))
        issues.extend(self._detect_leading_wildcards(parsed))
        
        return issues
    
    def _detect_select_star(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect SELECT * usage."""
        issues = []
        
        for select in node.find_all(exp.Select):
            for expression in select.expressions:
                if isinstance(expression, exp.Star):
                    issues.append(AntipatternIssue(
                        pattern="select_star",
                        severity="medium",
                        description="SELECT * can be inefficient and fragile",
                        suggestion="Explicitly list required columns instead of using SELECT *"
                    ))
        
        return issues
    
    def _detect_cartesian_joins(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect potential cartesian joins."""
        issues = []
        
        for select in node.find_all(exp.Select):
            joins = list(select.find_all(exp.Join))
            tables_in_from = []
            
            # Check for comma-separated tables in FROM (implicit cartesian join)
            if select.args.get("from"):
                from_clause = select.args["from"]
                if hasattr(from_clause, "expressions") and len(from_clause.expressions) > 1:
                    issues.append(AntipatternIssue(
                        pattern="implicit_cartesian_join",
                        severity="critical",
                        description="Comma-separated tables create cartesian joins",
                        suggestion="Use explicit JOIN syntax with proper ON conditions"
                    ))
            
            # Check for JOINs without ON conditions
            for join in joins:
                if not join.args.get("on"):
                    issues.append(AntipatternIssue(
                        pattern="join_without_condition",
                        severity="critical",
                        description="JOIN without ON condition creates cartesian join",
                        suggestion="Add proper JOIN condition using ON clause"
                    ))
        
        return issues
    
    def _detect_missing_where_clause(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect queries that might benefit from WHERE clauses."""
        issues = []
        
        for select in node.find_all(exp.Select):
            # Skip if it's a subquery or has aggregations
            if (select.parent and isinstance(select.parent, (exp.Subquery, exp.CTE)) or
                select.find(exp.Group) or 
                any(isinstance(expr, exp.AggFunc) for expr in select.expressions)):
                continue
                
            if not select.args.get("where"):
                issues.append(AntipatternIssue(
                    pattern="missing_where_clause",
                    severity="medium",
                    description="Query without WHERE clause may scan entire table",
                    suggestion="Consider adding WHERE clause to limit data scanned"
                ))
        
        return issues
    
    def _detect_unnecessary_distinct(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect potentially unnecessary DISTINCT usage."""
        issues = []
        
        for select in node.find_all(exp.Select):
            if select.args.get("distinct"):
                # Check if there's already a GROUP BY (makes DISTINCT redundant)
                if select.args.get("group"):
                    issues.append(AntipatternIssue(
                        pattern="distinct_with_group_by",
                        severity="low",
                        description="DISTINCT is unnecessary when using GROUP BY",
                        suggestion="Remove DISTINCT when using GROUP BY"
                    ))
        
        return issues
    
    def _detect_subquery_in_select(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect subqueries in SELECT clause."""
        issues = []
        
        for select in node.find_all(exp.Select):
            for expression in select.expressions:
                if expression.find(exp.Subquery):
                    issues.append(AntipatternIssue(
                        pattern="subquery_in_select",
                        severity="medium",
                        description="Subqueries in SELECT can be slow",
                        suggestion="Consider using JOINs or window functions instead"
                    ))
        
        return issues
    
    def _detect_functions_in_where(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect functions applied to columns in WHERE clause."""
        issues = []
        
        for where in node.find_all(exp.Where):
            for func in where.find_all(exp.Func):
                # Check if function is applied to a column
                for col in func.find_all(exp.Column):
                    issues.append(AntipatternIssue(
                        pattern="function_on_column_in_where",
                        severity="high",
                        description="Functions on columns in WHERE prevent index usage",
                        suggestion="Rewrite to avoid applying functions to indexed columns"
                    ))
                    break  # One issue per function is enough
        
        return issues
    
    def _detect_leading_wildcards(self, node: exp.Expression) -> List[AntipatternIssue]:
        """Detect LIKE patterns with leading wildcards."""
        issues = []
        
        for like in node.find_all(exp.Like):
            pattern = like.args.get("this")
            if isinstance(pattern, exp.Literal) and pattern.this.startswith(('%', '_')):
                issues.append(AntipatternIssue(
                    pattern="leading_wildcard_like",
                    severity="medium",
                    description="LIKE with leading wildcard prevents index usage",
                    suggestion="Avoid leading wildcards in LIKE patterns when possible"
                ))
        
        return issues