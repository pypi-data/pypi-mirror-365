# Contributing to AgentWerkstatt

Thank you for your interest in contributing to AgentWerkstatt! This guide will help you get started with development and understand our contribution process.

## 🚀 Development Setup

### Prerequisites
- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Git

### Setup Development Environment

1. **Clone the repository:**
```bash
git clone https://github.com/hanneshapke/agentwerkstatt.git
cd agentwerkstatt
```

2. **Install dependencies:**
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

3. **Install pre-commit hooks (optional but recommended):**
```bash
uv run pre-commit install
```

## 🛠️ Development Workflow

### Code Style & Linting

We use **Ruff** for both linting and formatting to ensure consistent code style:

```bash
# Check code style and run lints
uv run ruff check

# Auto-fix issues where possible
uv run ruff check --fix

# Format code
uv run ruff format

# Run both together
uv run ruff check --fix && uv run ruff format
```

### Type Checking

We use **mypy** for static type checking:

```bash
uv run mypy .
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=agentwerkstatt

# Run specific test files
uv run pytest tests/test_specific.py
```

### Development Scripts

```bash
# Format and lint code
uv run format-and-lint

# Run full quality checks
uv run quality-check

# Run all checks before committing
uv run pre-commit
```

## 📁 Project Structure

```
agentwerkstatt/
├── agent.py              # Main agent implementation
├── llms/                  # LLM implementations
│   ├── base.py           # Base LLM interface
│   ├── claude.py         # Claude LLM implementation
│   └── __init__.py
├── tools/                 # Agent tools
│   ├── base.py           # Base tool interface
│   ├── discovery.py      # Tool discovery
│   ├── websearch.py      # Web search tool
│   └── __init__.py
├── tests/                 # Test suite
├── pyproject.toml         # Project configuration
├── README.md             # Project documentation
└── CONTRIBUTING.md       # This file
```

## 🔄 Contribution Process

### 1. Fork & Branch

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/agentwerkstatt.git
cd agentwerkstatt

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write clean, well-documented code
- Follow existing code patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run the full test suite
uv run pytest

# Check code quality
uv run ruff check --fix && uv run ruff format
uv run mypy .

# Or run everything at once
uv run pre-commit
```

### 4. Commit Guidelines

We follow conventional commit format:

```bash
# Feature
git commit -m "feat: add new web search functionality"

# Bug fix
git commit -m "fix: resolve issue with Claude API rate limiting"

# Documentation
git commit -m "docs: update README with new examples"

# Refactor
git commit -m "refactor: simplify tool discovery logic"
```

### 5. Submit Pull Request

1. Push your branch to your fork
2. Create a Pull Request on GitHub
3. Fill out the PR template
4. Wait for review and feedback

## 🧪 Testing Guidelines

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names: `test_claude_llm_handles_rate_limiting`
- Mock external API calls
- Test both success and error cases

### Test Structure

```python
def test_feature_description():
    # Arrange
    setup_test_data()

    # Act
    result = function_under_test()

    # Assert
    assert result == expected_value
```

## 📦 Releasing

We use automated versioning with `setuptools-scm`:

1. **Development versions** are automatically generated from git commits
2. **Release versions** are created by tagging:

```bash
# Create a release tag
git tag v0.2.0
git push origin v0.2.0

# The version will be automatically detected as 0.2.0
```

## 🆘 Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/hanneshapke/agentwerkstatt/discussions)
- **Bug reports?** Create an [Issue](https://github.com/hanneshapke/agentwerkstatt/issues)
- **Feature requests?** Start with a Discussion first

## 📋 Contribution Checklist

Before submitting your PR, make sure:

- [ ] Code follows project style (Ruff passes)
- [ ] Type checking passes (mypy)
- [ ] Tests are written and passing
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] PR description explains the changes

## 🎯 Areas We Need Help With

- **New LLM integrations** (OpenAI, Anthropic, etc.)
- **Additional tools** (file operations, API clients, etc.)
- **Documentation improvements**
- **Performance optimizations**
- **Test coverage improvements**

## 🙏 Thank You!

Every contribution, whether it's code, documentation, bug reports, or feature requests, helps make AgentWerkstatt better for everyone. We appreciate your time and effort!

---

**Happy coding!** 🚀
