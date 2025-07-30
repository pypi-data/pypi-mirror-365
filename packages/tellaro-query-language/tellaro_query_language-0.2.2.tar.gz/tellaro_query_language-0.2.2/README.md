# Tellaro Query Language

[![PyPI version](https://badge.fury.io/py/tellaro-query-language.svg)](https://badge.fury.io/py/tellaro-query-language)
[![Tests Status](./badges/test-badge.svg?dummy=8484744)](./reports/pytest/junit.xml) [![Coverage Status](./badges/coverage-badge.svg?dummy=8484744)](./reports/coverage/index.html) [![Flake8 Status](./badges/flake8-badge.svg?dummy=8484744)](./reports/flake8/index.html)
[![Python 3.11-3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is TQL?

Tellaro Query Language (TQL) is a flexible, human-friendly query language for searching and filtering structured data. TQL is designed to provide a unified, readable syntax for expressing complex queries, supporting both simple and advanced search scenarios. It is especially useful for environments where data may come from different backends (such as OpenSearch or JSON files) and where users want to write queries that are portable and easy to understand.

TQL supports:
- **Field selection** (including nested fields)
- **Comparison and logical operators**
- **String, number, and list values**
- **Collection operators** (ANY, ALL) for working with list fields
- **Mutators** for post-processing or transforming field values
- **Operator precedence and parenthetical grouping** (AND, OR, NOT, etc.)
- **Field extraction** for analyzing query dependencies
- **Multiple backends** (in-memory evaluation, OpenSearch, file operations)
- **Statistical aggregations** for data analysis

---

## TQL Syntax Overview

### Basic Query Structure

TQL queries are generally structured as:

```
field [| mutator1 | mutator2 ...] operator value
```

- **field**: The field to query (e.g., `computer.name`, `os.ver`).
- **mutator**: (Optional) One or more transformations to apply to the field before comparison (e.g., `| lowercase`).
- **operator**: The comparison operator (e.g., `eq`, `contains`, `in`, `>`, `regexp`).
- **value**: The value to compare against (string, number, identifier, or list).

#### Example

```
computer.name | lowercase eq 'ha-jhend'
os.ver > 10
os.dataset in ['windows_server', 'enterprise desktop']
```

### Mutators

Mutators allow you to transform field values before comparison. For example, `| lowercase` will convert the field value to lowercase before evaluating the condition.

```
user.email | lowercase eq 'admin@example.com'
```

### Operators

TQL supports a variety of comparison operators, including:

- `eq`, `=`, `ne`, `!=` (equals, not equals)
- `>`, `>=`, `<`, `<=` (greater/less than)
- `contains`, `in`, `regexp`, `startswith`, `endswith`
- `is`, `exists`, `range`, `between`, `cidr`

### Values

Values can be:
- **Strings**: `'value'` or `"value"`
- **Numbers**: `123`, `42`, `1.01`
- **Identifiers**: `computer01`, `admin`
- **Lists**: `["val1", "val2"]`

### Logical Expressions

TQL supports logical operators and grouping:

```
field1 eq 'foo' AND (field2 > 10 OR field3 in ['a', 'b'])
NOT field4 contains 'bar'
```

Operators supported: `AND`, `OR`, `NOT`, `ANY`, `ALL` (case-insensitive)

### Example Query

```
computer.name | lowercase eq 'ha-jhend' AND (os.ver > 10 OR os.dataset in ['windows_server', 'enterprise desktop'])
```

---

## Why TQL Matters

TQL provides a consistent, readable way to express queries across different data sources. It abstracts away backend-specific quirks (like OpenSearch's text vs. keyword fields) and lets users focus on what they want to find, not how to write backend-specific queries.

**Key benefits:**
- **Unified syntax**: Write one query, run it on many backends.
- **Mutators**: Easily transform data inline (e.g., lowercase, trim).
- **Readability**: Queries are easy to read and write, even for complex logic.
- **Extensible**: New operators and mutators can be added as needed.

---

## Example: TQL in Action

Suppose you want to find computers named "HA-JHEND" (case-insensitive), running Windows Server or Enterprise Desktop, and with an OS version greater than 10:

```
computer.name | lowercase eq 'ha-jhend' AND (os.ver > 10 OR os.dataset in ['windows_server', 'enterprise desktop'])
```

This query will:
- Convert `computer.name` to lowercase and compare to `'ha-jhend'`
- Check if `os.ver` is greater than 10
- Check if `os.dataset` is in the provided list

---

## Implementation Notes

TQL is implemented using [pyparsing](https://pyparsing-docs.readthedocs.io/en/latest/) to define the grammar and parse queries. The parser supports mutators, operator precedence, and both standard and reversed operator forms (e.g., `'value' in field`).

See `src/tql/` for the implementation, including the parser grammar and evaluation logic.

## Documentation

For comprehensive documentation, see the [`docs/`](./docs/) folder:

- **[Getting Started](./docs/getting-started.md)** - Learn TQL basics with development examples
- **[Development Guide](./docs/development-guide.md)** - File operations, testing, and common patterns
- **[OpenSearch Integration](./docs/opensearch-integration.md)** - Convert TQL to OpenSearch DSL and Lucene queries
- **[Syntax Reference](./docs/syntax-reference.md)** - Complete grammar and syntax specification  
- **[Operators](./docs/operators.md)** - All comparison and logical operators
- **[Mutators](./docs/mutators.md)** - Field transformation functions (25+ mutators available)
- **[Stats & Aggregations](./docs/stats.md)** - Statistical analysis and data aggregation functions
- **[Examples](./docs/examples.md)** - Real-world query examples for security, DevOps, and business use cases
- **[Best Practices](./docs/best-practices.md)** - Performance optimization and maintainability tips

## Quick Start

### Installation

```bash
# Install from PyPI
pip install tellaro-query-language

# Or install with OpenSearch support
pip install tellaro-query-language[opensearch]
```

### Basic Usage

```python
from tql import TQL

# Initialize TQL
tql = TQL()

# Query data
data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
results = tql.query(data, 'age > 27')
print(f'Found {len(results)} people over 27: {results}')
# Output: Found 1 people over 27: [{'name': 'Alice', 'age': 30}]
```

For OpenSearch integration examples and production usage patterns, see the [Package Usage Guide](docs/package-usage-guide.md).

### Development Setup

For contributors and developers who want to work on TQL itself:

```bash
# Clone the repository
git clone https://github.com/tellaro/tellaro-query-language.git
cd tellaro-query-language

# Install with poetry (includes all dev dependencies)
poetry install

# Load environment variables for integration tests
cp .env.example .env
# Edit .env with your OpenSearch credentials

# Run tests
poetry run tests
```

**Note**: The development setup uses `python-dotenv` to load OpenSearch credentials from `.env` files for integration testing. This is NOT required when using TQL as a package - see the [Package Usage Guide](docs/package-usage-guide.md) for production configuration patterns.

### TQL Playground

The repository includes an interactive web playground for testing TQL queries:

```bash
# Navigate to the playground directory
cd playground

# Start with Docker (recommended)
docker-compose up

# Or start with OpenSearch included
docker-compose --profile opensearch up
```

Access the playground at:
- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

The playground uses your local TQL source code, so any changes you make are immediately reflected. See [playground/README.md](playground/README.md) for more details.

### File Operations

```python
from tql import TQL

# Query JSON files directly
tql = TQL()
results = tql.query("data.json", "user.role eq 'admin' AND status eq 'active'")

# Query with field mappings for OpenSearch
mappings = {"hostname": "agent.name.keyword"}
tql_mapped = TQL(mappings)
opensearch_dsl = tql_mapped.to_opensearch("hostname eq 'server01'")

# Extract fields from a complex query
query = "process.name eq 'explorer.exe' AND (user.id eq 'admin' OR user.groups contains 'administrators')"
fields = tql.extract_fields(query)
print(fields)  # ['process.name', 'user.groups', 'user.id']
```

### Query Analysis and Health Evaluation

TQL provides context-aware query analysis to help you understand performance implications before execution:

```python
from tql import TQL

tql = TQL()

# Analyze for in-memory execution (default)
query = "field | lowercase | trim eq 'test'"
analysis = tql.analyze_query(query)  # or explicitly: analyze_query(query, context="in_memory")

print(f"Health: {analysis['health']['status']}")  # 'good' - fast mutators don't impact in-memory
print(f"Score: {analysis['health']['score']}")    # 100
print(f"Has mutators: {analysis['stats']['has_mutators']}")  # True

# Analyze the same query for OpenSearch execution
analysis = tql.analyze_query(query, context="opensearch")
print(f"Health: {analysis['health']['status']}")  # 'fair' - post-processing required
print(f"Score: {analysis['health']['score']}")    # 85

# Check mutator-specific health
if 'mutator_health' in analysis:
    print(f"Mutator health: {analysis['mutator_health']['health_status']}")
    for reason in analysis['mutator_health']['health_reasons']:
        print(f"  - {reason['reason']}")

# Slow mutators impact both contexts
slow_query = "hostname | nslookup contains 'example.com'"
analysis = tql.analyze_query(slow_query)
print(f"In-memory health: {analysis['health']['status']}")  # 'fair' or 'poor' - network I/O

# Query complexity analysis
complex_query = "(a > 1 OR b < 2) AND (c = 3 OR (d = 4 AND e = 5))"
analysis = tql.analyze_query(complex_query)
print(f"Depth: {analysis['complexity']['depth']}")
print(f"Fields: {analysis['stats']['fields']}")
print(f"Operators: {analysis['stats']['operators']}")
```

### Post-Processing with OpenSearch

TQL intelligently handles mutators based on field mappings. When OpenSearch can't perform certain operations (like case-insensitive searches on keyword fields), TQL applies post-processing:

```python
# Field mappings with only keyword fields
mappings = {"username": {"type": "keyword"}, "department": {"type": "keyword"}}
tql = TQL(mappings)

# This query requires post-processing since keyword fields can't do case-insensitive contains
query = "username | lowercase contains 'admin' AND department eq 'Engineering'"

# Analyze the query (analyze_opensearch_query is deprecated, use analyze_query instead)
analysis = tql.analyze_query(query, context="opensearch")
print(f"Health: {analysis['health']['status']}")  # 'fair' (post-processing required)

# Execute with automatic post-processing
result = tql.execute_opensearch(
    opensearch_client=client,
    index="users",
    query=query
)
# OpenSearch returns all Engineering users, TQL filters to only those with 'admin' in username

# Run the demo to see this in action
# poetry run python post_processing_demo.py
```

### Development Examples

```bash
# Run comprehensive demos
poetry run python demo.py                          # Basic functionality
poetry run python intelligent_mapping_demo.py      # Field mapping features
poetry run python test_requested_functionality.py  # Core functionality tests
poetry run python field_extraction_demo.py         # Field extraction
poetry run python post_processing_demo.py          # Post-processing filtering

# Run tests
poetry run pytest tests/ -v

# Run integration tests with OpenSearch (requires OpenSearch)
# 1. Copy .env.example to .env and configure connection settings
# 2. Set OPENSEARCH_INTEGRATION_TEST=true in .env
poetry run pytest tests/test_opensearch_integration.py -v
```

## Contributing

TQL supports 25+ mutators including string manipulation, encoding/decoding, DNS operations, and network analysis. See the [Mutators documentation](./docs/mutators.md) for the complete list.

To add new mutators or operators, see the implementation in `src/tql/mutators.py` and `src/tql/parser.py`.

### Statistical Aggregations

TQL supports powerful data analysis with stats expressions:

```tql
# Simple aggregation
| stats sum(revenue)

# Grouped analysis  
| stats count(requests), average(response_time) by server_name

# Top N analysis
| stats sum(sales, top 10) by product_category

# Complex analytics
status eq 'success' 
| stats count(requests), sum(bytes), average(response_time), max(cpu_usage) by endpoint
```

Stats functions include: `sum`, `min`, `max`, `count`, `unique_count`, `average`, `median`, `percentile_rank`, `zscore`, `std`

## Documentation

Comprehensive documentation is available in the [docs](./docs/) directory:

- [**Getting Started**](./docs/getting-started.md) - Quick introduction to TQL
- [**Syntax Reference**](./docs/syntax-reference.md) - Complete syntax guide
- [**Operators**](./docs/operators.md) - All comparison and logical operators
- [**Mutators**](./docs/mutators.md) - Field transformation functions
- [**Mutator Caching & Security**](./docs/mutator-caching.md) - Performance optimization and security controls
- [**OpenSearch Integration**](./docs/opensearch-integration.md) - Using TQL with OpenSearch
- [**Examples**](./docs/examples.md) - Real-world query examples
- [**Architecture**](./docs/architecture.md) - Modular architecture and design
- [**Migration Guide**](./docs/migration-guide.md) - Upgrading from older versions

## Development

### Installation

```bash
# Clone the repository
git clone https://github.com/tellaro/tellaro-query-language.git
cd tellaro-query-language

# Install with poetry
poetry install

# Or install with pip
pip install -e .
```

### Testing

This project supports Python 3.11, 3.12, 3.13, and 3.14. We use `nox` for automated testing across all versions.

```bash
# Install test dependencies
poetry install --with dev

# Run tests on all Python versions
poetry run nox -s tests

# Run tests on a specific version
poetry run nox -s tests-3.12

# Quick test run (fail fast, no coverage)
poetry run nox -s test_quick

# Run linting and formatting
poetry run nox -s lint
poetry run nox -s format

# Run all checks
poetry run nox -s all
```

For more detailed testing instructions, see [TESTING.md](TESTING.md).