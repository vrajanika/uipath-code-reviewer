# Contributing to UiPath Code Reviewer Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/uipath-code-reviewer.git`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Run tests: `pytest tests/`
6. Commit your changes: `git commit -m "Description of changes"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a pull request

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip
- virtualenv (recommended)

### Installation

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-mock black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=bot --cov-report=html

# Run specific test file
pytest tests/test_azure_openai_client.py

# Run specific test
pytest tests/test_azure_openai_client.py::TestAzureOpenAIClient::test_init_with_env_vars
```

## Code Style

We follow PEP 8 guidelines. Please ensure your code:

- Uses 4 spaces for indentation
- Has descriptive variable and function names
- Includes docstrings for all public functions and classes
- Stays under 100 characters per line where reasonable

### Formatting

```bash
# Format code with black
black bot/ tests/

# Check linting with flake8
flake8 bot/ tests/

# Type checking with mypy
mypy bot/
```

## Adding New Features

### Adding Support for New File Types

To add support for a new file type:

1. Update `_get_file_type()` in `bot/azure_openai_client.py`
2. Add a new system prompt case in `_build_system_prompt()`
3. Update file filtering in `bot/reviewer.py` if needed
4. Add tests for the new file type

### Adding New Review Criteria

To add new review criteria:

1. Update the system prompt in `bot/azure_openai_client.py`
2. Consider if it's file-type specific or general
3. Add test cases to verify the new criteria

## Testing

### Test Coverage

We aim for >80% test coverage. Please add tests for:

- New features
- Bug fixes
- Edge cases

### Test Organization

- `tests/test_azure_openai_client.py` - Tests for Azure OpenAI integration
- `tests/test_github_client.py` - Tests for GitHub integration (if added)
- `tests/test_reviewer.py` - Tests for the main reviewer logic

## Documentation

When adding features, please update:

- README.md with usage examples
- Docstrings in the code
- This CONTRIBUTING guide if the development process changes

## Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Add a clear description of what your PR does
4. Reference any related issues
5. Request review from maintainers

## Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Relevant configuration (sanitize sensitive data!)

## Feature Requests

Feature requests are welcome! Please:

- Check if the feature already exists
- Describe the use case
- Explain why it would be useful
- Consider submitting a PR

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Follow the [Contributor Covenant](https://www.contributor-covenant.org/)

## Questions?

Feel free to open an issue for questions or discussions.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).
