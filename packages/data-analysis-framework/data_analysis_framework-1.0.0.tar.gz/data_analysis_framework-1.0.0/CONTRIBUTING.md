# Contributing to Data Analysis Framework

Thank you for your interest in contributing to the Data Analysis Framework! This guide will help you get started.

## 🚀 Quick Start

1. **Fork the repository** and clone your fork locally
2. **Set up your development environment**:
   ```bash
   cd data-analysis-framework
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
3. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🏗️ Development Setup

### Prerequisites
- Python 3.8 or higher
- Git

### Installation
```bash
# Clone your fork
git clone https://github.com/your-username/data-analysis-framework.git
cd data-analysis-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode with all dependencies
pip install -e ".[dev,database,advanced,visualization]"
```

## 🧪 Testing

Run the test suite to ensure everything works:

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=data_analysis_framework

# Run specific test categories
python -m pytest -m "not slow"  # Skip slow tests
python -m pytest -m "unit"      # Unit tests only
python -m pytest -m "integration"  # Integration tests only
```

### Test the examples
```bash
# Test basic functionality
python examples/01_basic_framework_demo.py

# Test car sales demo
python examples/00_car_sales_demo.py
```

## 📝 Code Style

We use several tools to maintain code quality:

```bash
# Format code with Black
black src/ tests/ examples/

# Check linting with flake8
flake8 src/ tests/ examples/

# Type checking with mypy
mypy src/
```

### Code Style Guidelines
- Follow PEP 8
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use type hints where possible

## 🎯 What to Contribute

### Priority Areas
1. **New Data Format Support** - Add handlers for additional structured data formats
2. **AI Integration** - Enhance natural language querying capabilities
3. **Performance Optimization** - Improve analysis speed for large datasets
4. **Documentation** - Examples, tutorials, and API documentation
5. **Testing** - Unit tests, integration tests, and edge case coverage

### Good First Issues
- Add support for new file formats (.tsv, .jsonl)
- Improve error messages and validation
- Add more comprehensive examples
- Write documentation for specific use cases

## 📋 Contribution Process

1. **Check existing issues** - Look for open issues or create a new one to discuss your idea
2. **Fork and branch** - Create a feature branch from `main`
3. **Implement changes** - Write code following our style guidelines
4. **Add tests** - Ensure your changes are well-tested
5. **Update documentation** - Update README.md, docstrings, and examples as needed
6. **Submit PR** - Create a clear pull request with description of changes

### Pull Request Guidelines

#### PR Title Format
- `feat: add support for TOML configuration files`
- `fix: resolve memory leak in large CSV parsing`
- `docs: update installation instructions`
- `test: add integration tests for Excel analysis`

#### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Tested examples still work

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced
```

## 🏛️ Architecture Guidelines

### Core Design Principles
1. **Safety First** - Always prioritize secure AI-agent interaction
2. **Format Agnostic** - Support multiple structured data formats uniformly
3. **Performance** - Optimize for large datasets and real-time analysis
4. **Extensibility** - Easy to add new formats and analysis capabilities
5. **Simple API** - One-line analysis with detailed results

### Adding New Data Formats

1. **Create Handler** - Add new handler in `src/handlers/`
2. **Update Analyzer** - Register format in `core/analyzer.py`
3. **Add Tests** - Create comprehensive tests
4. **Update Documentation** - Add format to README and examples

Example handler structure:
```python
from ..base import BaseHandler, AnalysisResult

class NewFormatHandler(BaseHandler):
    def can_handle(self, file_path: str) -> bool:
        # Detection logic
        
    def analyze(self, file_path: str, **kwargs) -> AnalysisResult:
        # Analysis implementation
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details** (OS, Python version, package version)
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Sample data** (if possible and non-sensitive)
5. **Error messages** and stack traces

## 💡 Feature Requests

For new features, please describe:

1. **Use case** - What problem does this solve?
2. **Proposed solution** - How should it work?
3. **Alternatives considered** - Other approaches you've thought about
4. **Impact** - Who would benefit from this feature?

## 📚 Documentation

Help improve our documentation:

- **API Reference** - Document new functions and classes
- **Examples** - Create real-world usage examples
- **Tutorials** - Step-by-step guides for common tasks
- **Architecture** - Explain design decisions and patterns

## 🌟 Recognition

Contributors are recognized in:
- `CHANGELOG.md` for each release
- GitHub contributors page
- Special mentions for significant contributions

## 📞 Getting Help

- **GitHub Issues** - For bugs and feature requests
- **GitHub Discussions** - For questions and community chat
- **Email** - wjackson@redhat.com for sensitive issues

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Data Analysis Framework! 🎉