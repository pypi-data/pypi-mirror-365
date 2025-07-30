---
name: Performance issue
about: Report performance problems or regressions
title: '[PERFORMANCE] '
labels: ['performance', 'needs-triage']
assignees: ''

---

**Performance issue description**
A clear and concise description of the performance problem.

**Expected performance**
What performance did you expect to see?

**Actual performance**
What performance are you actually seeing?

**Benchmark results**
Please run the GoSQL benchmark and provide results:
```bash
gosql-benchmark --database=your_database --queries=your_test_queries
```

```
Paste benchmark results here
```

**Comparison with native drivers**
If possible, compare with native Python drivers:

| Driver | Query Time | Memory Usage | Notes |
|--------|------------|--------------|-------|
| GoSQL | | | |
| Native (mysql-connector-python/psycopg2/pyodbc) | | | |

**Environment**
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12.0]
- Python version: [e.g. 3.9.7]
- Go version: [e.g. 1.21.0]
- GoSQL version: [e.g. 1.0.0]
- Database: [e.g. MySQL 8.0, PostgreSQL 15, SQL Server 2022]
- Hardware: [e.g. CPU model, RAM amount, storage type]

**Database configuration**
- Database version: [e.g. MySQL 8.0.33]
- Database configuration: [e.g. memory settings, query cache]
- Connection pooling settings
- Network configuration (local/remote)

**Query characteristics**
- Query type: [e.g. SELECT, INSERT, UPDATE, batch operations]
- Data size: [e.g. number of rows, data volume]
- Query complexity: [e.g. simple, complex joins, aggregations]
- Frequency: [e.g. one-time, repeated, concurrent]

**Code sample**
```python
# Please provide the code that demonstrates the performance issue
import gosql
import time

# Your performance test code here
```

**Profiling data**
If you have profiling data (CPU, memory), please attach or paste relevant excerpts:

```
Profiling output here
```

**Regression information**
- Did this work better in a previous version?
- Previous version that worked well: [version]
- When did you first notice this issue?

**Additional context**
Add any other context about the performance issue here:
- Network latency measurements
- Database server load during tests
- Other applications/processes running
- Any configuration changes made recently
