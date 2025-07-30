# Contributing to GoRequests

Thank you for your interest in contributing to GoRequests! This document provides guidelines and information for contributors.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/gorequests.git
   cd gorequests
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```
5. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

### Prerequisites
- Python 3.7+
- Go 1.21+ (for building the Go library)
- Git
- Make (optional, for convenience commands)

### Development Environment
```bash
# Install all development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

### Building the Go Library
```bash
# Navigate to the Go source directory
cd src/

# Build the shared library
go build -buildmode=c-shared -o ../python/libgorequests.dll gorequests.go
```

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=gorequests --cov-report=html

# Run specific test file
python -m pytest tests/test_basic.py

# Run with verbose output
python -m pytest -v
```

### Test Structure
```
tests/
├── test_basic.py          # Basic functionality tests
├── test_performance.py    # Performance benchmarks
├── test_compatibility.py  # Compatibility with requests
├── test_errors.py         # Error handling tests
└── conftest.py           # Test configuration
```

### Writing Tests
- Use pytest for all tests
- Follow the naming convention `test_*.py` for test files
- Use descriptive test function names: `test_get_request_returns_valid_response`
- Include both positive and negative test cases
- Test edge cases and error conditions

Example test:
```python
def test_get_request_success():
    """Test that GET requests return successful responses."""
    response = gorequests.get("https://httpbin.org/get")
    assert response.status_code == 200
    assert "headers" in response.json()
```

## 📝 Code Style

We follow Python PEP 8 and use automated formatting tools:

### Python Code Style
```bash
# Format code with black
black gorequests/ tests/

# Check style with flake8
flake8 gorequests/ tests/

# Type checking with mypy
mypy gorequests/
```

### Go Code Style
```bash
# Format Go code
go fmt ./src/...

# Vet Go code
go vet ./src/...
```

### Code Standards
- **Line length**: 88 characters (black default)
- **Imports**: Use isort for import organization
- **Type hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings
- **Comments**: Clear, concise comments for complex logic

## 🔄 Pull Request Process

### Before Submitting
1. **Update tests**: Add or update tests for your changes
2. **Run the test suite**: Ensure all tests pass
3. **Check code style**: Run formatting and linting tools
4. **Update documentation**: Update README or docs if needed
5. **Update changelog**: Add your changes to CHANGELOG.md

### Pull Request Guidelines
1. **Use a clear title**: Describe what your PR does
2. **Provide context**: Explain why the change is needed
3. **List changes**: Bullet point what was changed
4. **Link issues**: Reference any related issues
5. **Request review**: Tag relevant maintainers

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changelog updated
```

## 🐛 Bug Reports

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Test with latest version** to ensure bug still exists
3. **Minimal reproduction** - create the smallest example that reproduces the issue

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Step one
2. Step two
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g., Windows 10]
- Python version: [e.g., 3.9.0]
- GoRequests version: [e.g., 2.0.0]

**Additional Context**
Any other relevant information
```

## 💡 Feature Requests

### Before Requesting
1. **Check existing issues** for similar requests
2. **Consider the scope** - does it fit the project goals?
3. **Think about implementation** - how would it work?

### Feature Request Template
```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why would this feature be useful?

**Proposed Implementation**
How could this be implemented?

**Alternatives**
Any alternative solutions considered?
```

## 🏗️ Architecture

### Project Structure
```
gorequests/
├── src/                   # Go source code
│   └── gorequests.go     # Main Go implementation
├── gorequests/           # Python package
│   ├── __init__.py      # Main Python module
│   ├── exceptions.py    # Exception classes
│   └── libgorequests.dll # Compiled Go library
├── tests/               # Test suite
├── examples/            # Usage examples
├── docs/               # Documentation
└── scripts/            # Build and utility scripts
```

### Key Components
1. **Go Backend**: High-performance HTTP client using FastHTTP
2. **CGO Bridge**: C exports for Python integration
3. **Python Wrapper**: ctypes-based Python interface
4. **Session Management**: Connection pooling and state management

## 📚 Documentation

### Documentation Types
- **API Documentation**: Function/class documentation
- **User Guide**: How-to guides and tutorials
- **Developer Guide**: Architecture and contribution info
- **Examples**: Code samples and use cases

### Writing Documentation
- Use clear, concise language
- Include code examples
- Test all examples
- Follow consistent formatting
- Update when making changes

## 🔒 Security

### Reporting Security Issues
**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email: security@gorequests.io
2. Include: Detailed description and reproduction steps
3. Allow: Reasonable time for response before disclosure

### Security Best Practices
- Never commit secrets or credentials
- Validate all inputs
- Use secure default configurations
- Keep dependencies updated
- Follow OWASP guidelines

## 📋 Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
1. Update version number
2. Update CHANGELOG.md
3. Run full test suite
4. Build and test packages
5. Create git tag
6. Publish to PyPI
7. Create GitHub release

## 🤝 Community

### Code of Conduct
We are committed to providing a welcoming and inclusive environment. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: team@gorequests.io for direct contact

### Recognition
Contributors will be:
- Listed in the AUTHORS file
- Mentioned in release notes
- Acknowledged in documentation

## ❓ Getting Help

### Resources
1. **Documentation**: [https://gorequests.readthedocs.io](https://gorequests.readthedocs.io)
2. **Examples**: Check the `examples/` directory
3. **Tests**: Look at test files for usage patterns
4. **Issues**: Search existing issues and discussions

### Questions
For questions about contributing:
1. Check this guide first
2. Search existing issues
3. Open a new discussion
4. Email the maintainers

---

Thank you for contributing to GoRequests! 🚀

Every contribution, no matter how small, makes a difference and is greatly appreciated.
