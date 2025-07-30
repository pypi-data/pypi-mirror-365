# Contributing

We welcome contributions to the OpenWebUI client library! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/bemade/openwebui-client.git
   cd openwebui-client
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the package in development mode:

   ```bash
   pip install -e ".[dev]"
   ```

## Code Style

We use the following tools to maintain code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **mypy**: For static type checking
- **flake8**: For code style enforcement

You can run these tools using pre-commit:

```bash
pre-commit install  # Install the git hooks
pre-commit run --all-files  # Run on all files
```

## Running Tests

Run the tests with pytest:

```bash
pytest
```

For tests with coverage:

```bash
pytest --cov=openwebui_client
```

## Building Documentation

To build the documentation:

```bash
mkdocs build
```

The documentation will be available in the `site` directory.

## Submitting Changes

1. Create a branch for your changes:

   ```bash
   git checkout -b feature-branch-name
   ```

2. Make your changes and commit them:

   ```bash
   git commit -m "Description of changes"
   ```

3. Push your changes to your fork:

   ```bash
   git push origin feature-branch-name
   ```

4. Open a pull request against the main repository.
