# AGENTS

## Development workflow
- Target Python 3.10+.
- Format code with `black` (line length 88) and `isort --profile black`.
- Lint with `ruff`.
- Type check with `mypy --strict`.
- Run tests with `pytest`.
- Use `./setup.sh` to bootstrap dependencies and virtual environment.

## Commit conventions
- Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages.
- Keep the first line under 72 characters and use present tense, imperative mood.
- Exclude virtual environments, data files, and other generated artifacts from commits.

## Documentation
- Write NumPy-style docstrings for all public functions, classes, and modules.
- Update `README.md` and other docs when behavior or interfaces change.

## Pull Requests
- Include a summary of changes and a test plan in the PR body.
- Provide file path citations for code changes and terminal citations for test output.

