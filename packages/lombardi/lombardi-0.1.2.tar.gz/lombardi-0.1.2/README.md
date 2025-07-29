# Lombardi 🎯

> SQL performance analysis and optimization advisor with SQLMesh integration

[![PyPI version](https://badge.fury.io/py/lombardi.svg)](https://badge.fury.io/py/lombardi)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lombardi is a powerful SQL performance analysis tool that helps you identify bottlenecks, detect antipatterns, and optimize your queries across different data warehouses. Built on top of SQLGlot's semantic parsing, it provides actionable insights for better query performance.

## ✨ Features

### 🔍 **Semantic SQL Analysis**
- **Complexity Scoring**: Quantitative assessment (0-100) based on joins, subqueries, nesting depth
- **Antipattern Detection**: Identifies common performance killers like SELECT *, cartesian joins, functions in WHERE clauses
- **Optimization Suggestions**: Actionable recommendations with specific examples

### 🏢 **Warehouse-Specific Rules**
- **Snowflake**: Clustering keys, result caching, VARIANT optimization, time travel suggestions
- **BigQuery**: Partitioning recommendations, slot efficiency, materialized views, array operations
- **Universal**: Cross-platform optimizations that work everywhere

### 🛠️ **Integration Ready**
- **SQLMesh Integration**: Custom audit for performance checks during `sqlmesh plan`
- **CLI Tool**: Rich terminal output with colors, tables, and formatting
- **Python API**: Programmatic access for custom workflows
- **Multiple Output Formats**: Rich terminal, JSON, plain text

## 🚀 Quick Start

### Installation

```bash
pip install lombardi
```

### CLI Usage

```bash
# Analyze a SQL file
lombardi analyze query.sql --dialect snowflake

# Analyze a query string
lombardi analyze --sql "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id"

# Get just complexity metrics
lombardi complexity --sql "SELECT COUNT(*) FROM large_table WHERE date_col >= '2024-01-01'"

# Export results as JSON
lombardi analyze query.sql --format json > analysis.json

# BigQuery-specific analysis
lombardi analyze --sql "SELECT * FROM dataset.table" --dialect bigquery
```

### Python API

```python
from lombardi import ComplexityAnalyzer, AntipatternDetector, OptimizationSuggester

# Analyze query complexity
analyzer = ComplexityAnalyzer(dialect="snowflake")
metrics = analyzer.analyze("SELECT * FROM orders JOIN customers ON orders.customer_id = customers.id")

print(f"Complexity Score: {metrics.complexity_score}/100")
print(f"Join Count: {metrics.join_count}")
print(f"Subqueries: {metrics.subquery_count}")

# Detect antipatterns
detector = AntipatternDetector()
issues = detector.detect("SELECT * FROM users WHERE UPPER(name) = 'JOHN'")

for issue in issues:
    print(f"❌ {issue.pattern}: {issue.description}")

# Get optimization suggestions
suggester = OptimizationSuggester(dialect="bigquery")
suggestions = suggester.suggest("SELECT * FROM large_table WHERE date_col >= '2024-01-01'")

for suggestion in suggestions:
    print(f"💡 {suggestion.title}: {suggestion.description}")
```

## 📊 Example Output

```bash
$ lombardi analyze --sql "SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id WHERE UPPER(c.name) LIKE '%ACME%'"
```

```
╭──────────────────────────── SQL Analysis Results ────────────────────────────╮
│ Complexity Score: 12.0/100                                                   │
╰──────────────────────────────────────────────────────────────────────────────╯

    Complexity Metrics    
┏━━━━━━━━━━━━━━━━┳━━━━━━━┓
┃ Metric         ┃ Value ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━┩
│ Join Count     │ 1     │
│ Subquery Count │ 0     │
│ CTE Count      │ 0     │
│ Function Count │ 1     │
│ Nesting Depth  │ 0     │
│ Table Count    │ 2     │
│ Column Count   │ 3     │
└────────────────┴───────┘

                                Detected Issues                                 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Pattern                     ┃ Severity ┃ Description                         ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Select Star                 │ MEDIUM   │ SELECT * can be inefficient        │
│ Function On Column In Where │ HIGH     │ Functions prevent index usage      │
└─────────────────────────────┴──────────┴─────────────────────────────────────┘

                            Optimization Suggestions                            
┏━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Category    ┃ Priority ┃ Suggestion                                          ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Performance │ HIGH     │ Function On Column In Where: Rewrite to avoid      │
│             │          │ applying functions to indexed columns               │
│ Indexing    │ HIGH     │ JOIN Index Optimization: Ensure indexes exist on   │
│             │          │ JOIN columns: o.customer_id, c.id                  │
│ Performance │ MEDIUM   │ Select Star: Explicitly list required columns      │
└─────────────┴──────────┴─────────────────────────────────────────────────────┘
```

## 🔌 SQLMesh Integration

Integrate Lombardi into your SQLMesh workflow for automated performance checks:

```python
# In your SQLMesh model
MODEL (
  name my_project.optimized_table,
  kind FULL,
  audits [performance_check]
);

SELECT 
  region_code,
  species_code,
  COUNT(*) as observation_count
FROM @DEV.my_project.raw_observations 
WHERE observation_date >= '2024-01-01'
GROUP BY 1, 2;
```

```python
# Configure the audit
from lombardi.integrations.sqlmesh_audit import create_performance_audit

performance_audit = create_performance_audit(
    complexity_threshold=30.0,
    min_severity="medium",
    dialect="snowflake"
)
```

## 🏗️ Architecture

```
lombardi/
├── analyzers/           # Core analysis engines
│   ├── complexity_analyzer.py      # Complexity scoring
│   ├── antipattern_detector.py     # Antipattern detection  
│   └── optimization_suggester.py   # Optimization recommendations
├── rules/               # Warehouse-specific optimizations
│   ├── snowflake_rules.py          # Snowflake optimizations
│   └── bigquery_rules.py           # BigQuery optimizations
├── integrations/        # Third-party integrations
│   └── sqlmesh_audit.py            # SQLMesh audit integration
└── cli.py              # Command-line interface
```

## 🎯 Detected Antipatterns

Lombardi identifies these common SQL performance issues:

| Pattern | Severity | Description |
|---------|----------|-------------|
| **SELECT *** | Medium | Can be inefficient and fragile |
| **Cartesian Joins** | Critical | Missing JOIN conditions |
| **Functions in WHERE** | High | Prevents index usage |
| **Leading Wildcards** | Medium | `LIKE '%pattern'` prevents indexes |
| **Missing WHERE** | Medium | Full table scans |
| **Subquery in SELECT** | Medium | Often better as JOINs |

## 🏢 Warehouse-Specific Optimizations

### Snowflake
- ❄️ **Clustering Keys**: Recommendations for large table partitioning
- 🚀 **Result Caching**: Identify cacheable query patterns  
- 📊 **Warehouse Sizing**: Complexity-based sizing suggestions
- 🕒 **Time Travel**: Optimize historical queries
- 📄 **VARIANT**: Semi-structured data query optimization

### BigQuery
- 📅 **Partitioning**: Date/timestamp partitioning opportunities
- 🗂️ **Clustering**: Multi-column clustering recommendations
- 💰 **Slot Efficiency**: Cost optimization suggestions
- 🔄 **Materialized Views**: Pre-aggregation opportunities
- 📊 **Array Operations**: UNNEST and array function optimization

## 🔧 Configuration

### CLI Options

```bash
lombardi analyze [OPTIONS] [SQL_FILE]

Options:
  --sql, -s TEXT              SQL query string to analyze
  --dialect, -d TEXT          SQL dialect (snowflake, bigquery, etc.)
  --threshold, -t FLOAT       Complexity threshold (0-100) [default: 50.0]
  --severity TEXT             Minimum severity (low, medium, high, critical) [default: medium]
  --format, -f TEXT           Output format (rich, json, plain) [default: rich]
  --suggestions/--no-suggestions  Include optimization suggestions [default: suggestions]
```

### Python API Configuration

```python
# Initialize with specific dialect
analyzer = ComplexityAnalyzer(dialect="snowflake")
detector = AntipatternDetector(dialect="bigquery")

# Configure thresholds and rules
suggester = OptimizationSuggester(dialect="snowflake")
suggestions = suggester.suggest(sql_query)

# Warehouse-specific analysis
from lombardi.rules.snowflake_rules import SnowflakeRules
snowflake_rules = SnowflakeRules()
sf_suggestions = snowflake_rules.analyze(sql_query)
```

## 🧪 Development

### Setup

```bash
git clone https://github.com/Doctacon/lombardi.git
cd lombardi
uv sync
```

### Testing

```bash
# Run tests
uv run pytest tests/ -v

# Test CLI
uv run lombardi analyze --sql "SELECT * FROM test_table"

# Test with coverage
uv run pytest tests/ --cov=lombardi
```

### Building

```bash
# Build package
uv build

# Test locally
pip install dist/lombardi-*.whl
```

## 📈 Performance Impact

Lombardi helps identify optimizations that can provide:

- **Query Speed**: 10x-100x faster execution through proper indexing
- **Cost Reduction**: 50-90% lower warehouse costs via efficient queries  
- **Resource Usage**: Reduced CPU, memory, and I/O through better query patterns
- **Maintainability**: Cleaner, more readable SQL through antipattern detection

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run tests: `uv run pytest`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SQLGlot**: Powers our semantic SQL parsing
- **SQLMesh**: Inspiration for the audit integration pattern
- **Rich**: Beautiful terminal output
- **Typer**: Excellent CLI framework

## 🔗 Links

- **Documentation**: [Coming Soon]
- **PyPI**: https://pypi.org/project/lombardi/
- **Issues**: https://github.com/Doctacon/lombardi/issues
- **Discussions**: https://github.com/Doctacon/lombardi/discussions

---

*Named after [Vince Lombardi](https://en.wikipedia.org/wiki/Vince_Lombardi), who believed "Perfection is not attainable, but if we chase perfection we can catch excellence" - the same philosophy we apply to SQL optimization.*