# Contributing to GoSQL

Thank you for considering contributing to GoSQL! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, please include:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** with code samples
- **Describe the behavior you observed** and what you expected
- **Include environment details**: OS, Python version, Go version, database version
- **Add relevant logs or error messages**

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) when creating issues.

### Suggesting Features

Feature suggestions are welcome! Please use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- **Clear use case description**
- **Proposed API or interface**
- **Performance considerations**
- **Database compatibility requirements**

### Performance Issues

If you encounter performance problems, use the [performance issue template](.github/ISSUE_TEMPLATE/performance_issue.md) and include:

- **Benchmark results** comparing GoSQL with native drivers
- **System specifications** and database configuration
- **Profiling data** if available
- **Code samples** that demonstrate the issue

## Development Setup

### Prerequisites

- **Go 1.18+** with CGO enabled
- **Python 3.7+** with pip
- **Git** for version control
- **Database servers** for testing (MySQL, PostgreSQL, SQL Server)

### Setting Up Development Environment

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/your-username/gosql.git
   cd gosql
   ```

2. **Set up Python virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. **Install Go dependencies**:
   ```bash
   cd go
   go mod download
   go mod tidy
   ```

4. **Install GoSQL in development mode**:
   ```bash
   python setup.py develop
   ```

5. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Running Tests

#### Unit Tests
```bash
# Run all tests
pytest tests/

# Run tests with coverage
pytest tests/ --cov=gosql --cov-report=html

# Run specific test categories
pytest tests/ -m "not integration"  # Skip integration tests
pytest tests/ -m integration        # Only integration tests
```

#### Go Tests
```bash
cd go
go test -v ./...
go vet ./...
```

#### Integration Tests
Integration tests require running database servers. Use Docker:

```bash
# Start database containers
docker-compose up -d

# Run integration tests
pytest tests/ -m integration

# Cleanup
docker-compose down
```

#### Benchmarks
```bash
# Run performance benchmarks
gosql-benchmark

# Run specific database benchmarks
gosql-benchmark --database mysql
gosql-benchmark --database postgresql
gosql-benchmark --database mssql
```

### Code Style

We use several tools to maintain code quality:

#### Python Code Style
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **bandit** for security analysis

```bash
# Format code
black gosql tests
isort gosql tests

# Check code quality
flake8 gosql tests
mypy gosql
bandit -r gosql
```

#### Go Code Style
- **gofmt** for formatting
- **go vet** for linting
- **golangci-lint** for comprehensive analysis

```bash
cd go
go fmt ./...
go vet ./...
golangci-lint run
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Run the test suite** to ensure everything works

6. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m "feat: add connection pooling for PostgreSQL
   
   - Implement configurable connection pool
   - Add pool size and timeout parameters
   - Include connection health checks
   - Update documentation and examples
   
   Closes #123"
   ```

7. **Push to your fork** and create a pull request

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or modifications
- `ci`: CI/CD changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(mysql): add connection pooling support
fix(postgres): resolve memory leak in cursor handling
docs: update API documentation for new features
perf(core): optimize type conversion performance
test: add integration tests for SQL Server
```

## Pull Request Process

1. **Ensure tests pass** and code follows style guidelines
2. **Update documentation** for new features or API changes
3. **Add entries to CHANGELOG.md** for user-facing changes
4. **Fill out the PR template** completely
5. **Request review** from maintainers

### PR Review Criteria

Your pull request will be reviewed for:

- **Functionality**: Does it work as intended?
- **Code quality**: Is it readable, maintainable, and well-structured?
- **Performance**: Does it maintain or improve performance?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it properly documented?
- **Security**: Are there any security implications?
- **Breaking changes**: Are they justified and documented?

## Performance Guidelines

GoSQL's primary goal is high performance. When contributing:

1. **Benchmark your changes** using the provided benchmark suite
2. **Profile memory usage** for memory-intensive operations
3. **Avoid allocations** in hot paths when possible
4. **Use efficient data structures** and algorithms
5. **Consider database-specific optimizations**

### Performance Testing

```bash
# Before making changes
gosql-benchmark --output baseline.json

# After making changes  
gosql-benchmark --output changes.json

# Compare results
python scripts/compare_benchmarks.py baseline.json changes.json
```

## Documentation

### Code Documentation

- **Go code**: Use Go doc comments for exported functions and types
- **Python code**: Use docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- **Type hints**: Provide comprehensive type annotations

### User Documentation

- **README.md**: Keep examples current and accurate
- **API docs**: Update for any API changes
- **Migration guides**: Help users transition from other drivers
- **Examples**: Provide practical, real-world examples

## Security

### Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Instead, email us at security@coffeecms.com with:
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact assessment
- Suggested fix (if any)

### Security Guidelines

- **Input validation**: Always validate and sanitize inputs
- **SQL injection**: Use parameterized queries exclusively
- **Authentication**: Handle credentials securely
- **Dependencies**: Keep dependencies updated
- **Secrets**: Never commit credentials or secrets

## Release Process

Releases are managed by maintainers:

1. **Version bumping** follows semantic versioning
2. **Changelog updates** document all changes
3. **Testing** on multiple platforms and database versions
4. **PyPI publishing** through automated CI/CD
5. **GitHub releases** with detailed release notes

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the docs first
- **Email**: dev@coffeecms.com for other inquiries

## Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: List of all contributors
- **Release notes**: Major contributions highlighted
- **Git history**: Proper attribution maintained

Thank you for contributing to GoSQL! 🚀
