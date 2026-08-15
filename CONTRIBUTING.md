# Contributing to aws-security

Thank you for your interest in contributing to aws-security! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue on GitHub with:
- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the problem
- Expected behavior vs. actual behavior
- Your environment (OS, Python version, boto3 version)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please open an issue with:
- A clear, descriptive title
- A detailed description of the enhancement
- Why this enhancement would be useful
- Any alternative solutions or approaches you've considered

### Security Issues

**Do not** open a public issue for security vulnerabilities. Please refer to [SECURITY.md](SECURITY.md) for responsible disclosure.

## Development Setup

### Prerequisites

- Python 3.8+
- git
- AWS CLI configured (optional, only for live testing)
- boto3

### Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/aws-security.git
cd aws-security
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install boto3
```

### Running Tests

All contributions must pass existing tests. Run the test suite before submitting a pull request:

```bash
python3 -m unittest -q
```

For verbose test output:

```bash
python3 -m unittest -v
```

## Code Standards

### Style Guidelines

- Follow PEP 8 conventions
- Use meaningful variable and function names
- Keep functions focused and concise
- Add docstrings to classes and public methods
- Use type hints where practical

### Documentation

- Update README.md if your changes affect usage
- Add tests for new features or bug fixes
- Include clear commit messages

### Testing Requirements

- Write unit tests for new features
- Ensure all existing tests pass
- Mock AWS API calls (do not test against real AWS resources)
- Test edge cases and error conditions

## Submitting Changes

### Before You Start

1. Check existing issues and pull requests to avoid duplicate work
2. For major features, consider opening an issue first for discussion

### Making Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/my-feature
   ```

2. Make your changes following code standards above

3. Add or update tests:
   ```bash
   python3 -m unittest -v
   ```

4. Commit with clear messages:
   ```bash
   git commit -m "Add feature description"
   ```

### Creating a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/my-feature
   ```

2. Open a pull request on GitHub with:
   - A clear title describing the change
   - A description of what changed and why
   - Reference to any related issues (#123)
   - Confirmation that tests pass

3. Respond to review feedback promptly

## Important Principles

This project is intentionally focused on default VPC cleanup. We keep the scope narrow to:
- Reduce accidental deletion risk
- Maintain code clarity and reviewability
- Keep the utility focused and reliable

**Before proposing major new features, please open an issue for discussion.**

## License

By contributing to this project, you agree to license your contributions under the Apache License 2.0. See [LICENSE](LICENSE) for details.

## Questions?

Feel free to open an issue for questions or clarifications about contributing.

Thank you for helping make aws-security better! 🎉
