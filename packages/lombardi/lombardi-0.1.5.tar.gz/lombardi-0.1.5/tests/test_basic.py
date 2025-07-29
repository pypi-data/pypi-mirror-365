"""Basic tests for Lombardi package."""

from lombardi import AntipatternDetector, ComplexityAnalyzer, OptimizationSuggester


def test_package_imports():
    """Test that core classes can be imported."""
    assert ComplexityAnalyzer is not None
    assert AntipatternDetector is not None
    assert OptimizationSuggester is not None


def test_complexity_analyzer():
    """Test complexity analyzer with simple query."""
    analyzer = ComplexityAnalyzer()
    sql = "SELECT id, name FROM users WHERE status = 'active'"

    metrics = analyzer.analyze(sql)
    assert metrics.complexity_score >= 0
    assert metrics.table_count == 1
    assert metrics.join_count == 0


def test_antipattern_detector():
    """Test antipattern detection."""
    detector = AntipatternDetector()
    sql = "SELECT * FROM users"  # SELECT * is an antipattern

    issues = detector.detect(sql)
    assert len(issues) >= 1
    assert any("select_star" in issue.pattern for issue in issues)


def test_optimization_suggester():
    """Test optimization suggestions."""
    suggester = OptimizationSuggester()
    sql = "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id"

    suggestions = suggester.suggest(sql)
    assert len(suggestions) > 0
    assert any("index" in s.category.lower() for s in suggestions)


def test_warehouse_rules():
    """Test warehouse-specific rules."""
    from lombardi.rules.bigquery_rules import BigQueryRules
    from lombardi.rules.snowflake_rules import SnowflakeRules

    sql = "SELECT * FROM large_table WHERE date_col >= '2024-01-01'"

    sf_rules = SnowflakeRules()
    bq_rules = BigQueryRules()

    sf_suggestions = sf_rules.analyze(sql)
    bq_suggestions = bq_rules.analyze(sql)

    assert isinstance(sf_suggestions, list)
    assert isinstance(bq_suggestions, list)


def test_cli_import():
    """Test that CLI can be imported."""
    from lombardi.cli import main

    assert main is not None
