## Description

Please include a summary of the changes and the related issue. Please also include relevant motivation and context.

Fixes # (issue)

## Type of change

Please delete options that are not relevant.

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Code refactoring (no functional changes)
- [ ] Test improvements
- [ ] CI/CD improvements

## Testing

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration.

### Test checklist
- [ ] Unit tests pass (`pytest tests/`)
- [ ] Integration tests pass (`pytest tests/ -m integration`)
- [ ] Benchmarks run without regression (`gosql-benchmark`)
- [ ] Code follows style guidelines (`black`, `flake8`, `mypy`)
- [ ] Go tests pass (`cd go && go test ./...`)

### Test environment
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.10]
- Go version: [e.g. 1.21]
- Database versions tested: [e.g. MySQL 8.0, PostgreSQL 15]

## Performance impact

If this change affects performance, please provide benchmark results:

### Before
```
Benchmark results before your changes
```

### After
```
Benchmark results after your changes
```

## Breaking changes

If this is a breaking change, please describe:
- What will break?
- How should users migrate their code?
- Are there backwards compatibility options?

## Documentation

- [ ] Code is well-commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation have been made
- [ ] New features are documented in README.md
- [ ] API changes are documented
- [ ] Migration guide updated (if breaking changes)

## Dependencies

List any new dependencies added:
- Go modules: [list any new Go dependencies]
- Python packages: [list any new Python dependencies]

## Security considerations

If applicable, describe any security implications of your changes:
- [ ] No security impact
- [ ] Security impact assessed and documented
- [ ] Security review requested

## Additional context

Add any other context about the pull request here:
- Screenshots (if UI changes)
- Related issues or PRs
- Future work planned
- Known limitations

## Reviewer checklist

For maintainers reviewing this PR:

- [ ] Code follows project conventions
- [ ] Tests are adequate and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities introduced
- [ ] Performance impact is acceptable
- [ ] Breaking changes are justified and documented
