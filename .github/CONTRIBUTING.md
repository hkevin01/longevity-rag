# Contributing to Longevity RAG

Thank you for your interest in contributing to the Longevity RAG project! This document provides guidelines for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. Use the bug report template
3. Include detailed steps to reproduce
4. Provide environment information

### Suggesting Features

1. Check if the feature has already been suggested
2. Use the feature request template
3. Explain the use case and benefits
4. Consider implementation approaches

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following our coding standards
4. Write or update tests
5. Ensure all tests pass
6. Update documentation
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest tests/`

## Coding Standards

### Python
- Follow PEP 8 style guide
- Use Black for formatting (line length: 88)
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Naming conventions:
  - Classes: PascalCase
  - Functions/methods: snake_case
  - Variables: snake_case
  - Constants: UPPER_CASE
  - Files: snake_case.py

### Code Quality
- Keep functions focused and small
- Add comments for complex logic
- Handle errors gracefully
- Include logging for debugging
- Write unit tests for new features
- Ensure boundary conditions are handled
- Add proper error messages

## Testing

- Write unit tests for all new code
- Maintain or improve code coverage
- Test edge cases and boundary conditions
- Run full test suite before submitting PR

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update project plan for major features
- Keep memory-bank up to date

## Questions?

Feel free to open an issue for any questions or clarifications.
