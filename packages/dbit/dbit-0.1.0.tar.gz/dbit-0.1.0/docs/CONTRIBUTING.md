# dbit Development Guide

This document describes how to set up a development environment, run tests, and contribute code to dbit.

## Development Environment Setup

1. Clone the repository:

    git clone https://github.com/navaneetnr/dbit.git
    cd dbit

2. Create and activate a virtual environment:

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install development dependencies:

    pip install -e .[dev]

4. Install pre-commit hooks (recommended):

    pre-commit install

   This will automatically run code formatting, linting, and checks before each commit.

5. Run pre-commit on all files:

    pre-commit run --all-files

## Running Tests

- Run all tests:

      pytest tests

- Run a specific test file:

      pytest tests/commands/test_connect.py

## Documentation

- Update docstrings for all public functions and classes.
- Follow Google docstring format.
- Update CLI help text for command changes.
- Update README.md for significant changes.
- Add examples for new features.

## Submitting Changes

- Follow the steps in CONTRIBUTING.md for making and submitting changes.
- Use the provided pull request template.

For questions, see the README.md or open an issue on GitHub.
