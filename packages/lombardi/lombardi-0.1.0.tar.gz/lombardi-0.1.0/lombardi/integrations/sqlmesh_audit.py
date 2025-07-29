"""SQLMesh audit integration for performance analysis.

This module provides a simplified integration with SQLMesh audits.
For production use, you may need to adapt this to your specific SQLMesh version and setup.
"""

from typing import Dict, Any, List, Optional
from ..analyzers.complexity_analyzer import ComplexityAnalyzer
from ..analyzers.antipattern_detector import AntipatternDetector
from ..analyzers.optimization_suggester import OptimizationSuggester


class PerformanceAudit:
    """Performance audit for SQL queries.
    
    This is a simplified audit that can be adapted for SQLMesh integration.
    """
    
    def __init__(
        self,
        complexity_threshold: float = 50.0,
        min_severity: str = "medium",
        dialect: str = ""
    ):
        self.complexity_threshold = complexity_threshold
        self.min_severity = min_severity
        self.dialect = dialect
        
        self.complexity_analyzer = ComplexityAnalyzer(dialect)
        self.antipattern_detector = AntipatternDetector(dialect)
        self.optimization_suggester = OptimizationSuggester(dialect)
    
    def evaluate(self, sql: str, **kwargs) -> List[Dict[str, Any]]:
        """Evaluate SQL performance for the given SQL query."""
        try:
            
            # Analyze complexity
            complexity = self.complexity_analyzer.analyze(sql)
            
            # Detect antipatterns
            antipatterns = self.antipattern_detector.detect(sql)
            
            # Get optimization suggestions
            suggestions = self.optimization_suggester.suggest(sql)
            
            # Determine if audit passes
            issues = []
            
            # Check complexity threshold
            if complexity.complexity_score > self.complexity_threshold:
                issues.append(
                    f"High complexity score: {complexity.complexity_score:.1f} "
                    f"(threshold: {self.complexity_threshold})"
                )
            
            # Check for critical antipatterns
            severity_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            min_severity_level = severity_order.get(self.min_severity, 1)
            
            critical_antipatterns = [
                ap for ap in antipatterns 
                if severity_order.get(ap.severity, 0) >= min_severity_level
            ]
            
            if critical_antipatterns:
                issues.extend([
                    f"{ap.pattern}: {ap.description}" 
                    for ap in critical_antipatterns
                ])
            
            # Return audit results
            if issues:
                message = "Performance issues detected:\\n" + "\\n".join(f"• {issue}" for issue in issues)
                
                # Add optimization suggestions
                if suggestions:
                    message += "\\n\\nOptimization suggestions:\\n"
                    message += "\\n".join(f"• {s.title}: {s.description}" for s in suggestions[:5])
                
                return [{"message": message, "passed": False}]
            else:
                return [{"message": "No performance issues detected", "passed": True}]
                
        except Exception as e:
            return [{"message": f"Performance audit failed: {str(e)}", "passed": False}]


def create_performance_audit(
    complexity_threshold: float = 50.0,
    min_severity: str = "medium", 
    dialect: str = ""
) -> PerformanceAudit:
    """Factory function to create a performance audit."""
    return PerformanceAudit(
        complexity_threshold=complexity_threshold,
        min_severity=min_severity,
        dialect=dialect
    )