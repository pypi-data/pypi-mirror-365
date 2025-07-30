# Contributing to GoBeautifulSoup

Thank you for your interest in contributing to GoBeautifulSoup! We welcome contributions from the community and are grateful for any help you can provide.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Set up the development environment**
4. **Make your changes**
5. **Test your changes**
6. **Submit a pull request**

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Style](#code-style)
- [Performance Considerations](#performance-considerations)
- [Documentation](#documentation)
- [Community](#community)

## 🛠️ Development Setup

### Prerequisites

- **Python 3.7+** with pip
- **Go 1.19+** for building the core library
- **Git** for version control
- **Make** (optional, for convenience commands)

### Setting Up the Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/gobeautifulsoup.git
cd gobeautifulsoup

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
cd pythonpackaging
pip install -e .[dev]

# Install additional tools
pip install pytest black flake8 mypy
```

### Building the Go Library

```bash
# Navigate to Go core
cd go-core

# Install Go dependencies
go mod tidy

# Build the shared library
make build  # Or: go build -buildmode=c-shared -o libgobeautifulsoup.so .

# Copy library to Python package
cp libgobeautifulsoup.* ../pythonpackaging/gobeautifulsoup/libs/linux/amd64/
```

## 📁 Project Structure

```
gobeautifulsoup/
├── go-core/                    # Go implementation
│   ├── core.go                # Main parsing logic
│   ├── bindings.go            # C bindings for Python
│   ├── selector.go            # CSS selector implementation
│   └── Makefile              # Build automation
├── pythonpackaging/           # Python package
│   ├── gobeautifulsoup/      # Main package
│   │   ├── __init__.py       # Package initialization
│   │   ├── soup.py           # BeautifulSoup class
│   │   ├── element.py        # Tag and NavigableString classes
│   │   ├── _bindings.py      # Go library interface
│   │   └── libs/             # Platform-specific libraries
│   ├── tests/                # Test suite
│   ├── examples/             # Usage examples
│   └── docs/                 # Documentation
├── benchmarks/               # Performance benchmarks
└── tests/                    # Integration tests
```

## 🔧 Making Changes

### Types of Contributions

We welcome several types of contributions:

1. **Bug fixes** - Fix issues in existing functionality
2. **Feature additions** - Add new BeautifulSoup4 compatible features
3. **Performance improvements** - Optimize parsing or querying speed
4. **Documentation** - Improve docs, examples, or comments
5. **Tests** - Add or improve test coverage
6. **Platform support** - Add support for new platforms/architectures

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** in small, logical commits

3. **Test thoroughly** (see Testing section)

4. **Document your changes** (update docstrings, README, etc.)

5. **Commit with descriptive messages**:
   ```bash
   git commit -m "Add support for custom CSS selectors"
   ```

### Go Development Guidelines

When modifying the Go core:

- **Follow Go conventions** (gofmt, golint)
- **Maintain C API compatibility** in bindings.go
- **Add tests** for new functionality
- **Consider performance impact** - profile changes when possible
- **Memory management** - ensure proper cleanup of allocated memory

Example Go function:
```go
//export NewFunction  
func NewFunction(input *C.char) *C.char {
    goInput := C.GoString(input)
    
    // Your logic here
    result := processInput(goInput)
    
    // Return allocated string (caller must free)
    return C.CString(result)
}
```

### Python Development Guidelines

When modifying Python wrapper:

- **Maintain BeautifulSoup4 API compatibility**
- **Add type hints** for better IDE support
- **Handle Go errors gracefully** with try/catch
- **Follow PEP 8** style guidelines
- **Add docstrings** for new methods

Example Python method:
```python
def new_method(self, param: str) -> Optional[Tag]:
    """
    Brief description of what this method does.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Example:
        >>> soup.new_method("example")
        <tag>result</tag>
    """
    if not self._doc_handle:
        return None
        
    try:
        result = self._go_lib.new_function(param)
        return Tag(result, self) if result else None
    except Exception as e:
        # Log error and return None for compatibility
        return None
```

## 🧪 Testing

### Running Tests

```bash
# Run Python tests
cd pythonpackaging
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_soup.py -v

# Run with coverage
python -m pytest tests/ --cov=gobeautifulsoup --cov-report=html
```

### Running Benchmarks

```bash
# Run performance benchmarks
cd benchmarks
python benchmark.py

# Compare with BeautifulSoup4
python benchmark.py --compare-bs4
```

### Integration Tests

```bash
# Run comprehensive integration tests
python test_comprehensive.py
python test_simple.py
```

### Writing Tests

When adding new features, please include tests:

```python
# tests/test_new_feature.py
import pytest
from gobeautifulsoup import BeautifulSoup

def test_new_feature():
    """Test description"""
    html = "<div class='test'>content</div>"
    soup = BeautifulSoup(html, 'html.parser')
    
    result = soup.new_method()
    assert result is not None
    assert result.name == "div"
```

## 📤 Submitting Changes

### Pull Request Process

1. **Ensure all tests pass** locally
2. **Update documentation** if needed
3. **Add entries to CHANGELOG.md** for significant changes
4. **Create a pull request** with:
   - Clear title and description
   - Reference any related issues
   - Include test results
   - Mention any breaking changes

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Performance improvement
- [ ] Documentation update
- [ ] Other (please describe)

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🎨 Code Style

### Python Style

We follow **PEP 8** with these specifics:

- **Line length**: 88 characters (Black formatter)
- **Import order**: Standard library, third-party, local imports
- **Type hints**: Required for public methods
- **Docstrings**: Required for public classes and methods

Format code with Black:
```bash
black gobeautifulsoup/ tests/
```

Check style with flake8:
```bash
flake8 gobeautifulsoup/ tests/ --max-line-length=88
```

### Go Style

Follow standard Go conventions:

- Use `gofmt` for formatting
- Follow Go naming conventions
- Add comments for exported functions
- Use Go modules for dependencies

```bash
# Format Go code
gofmt -w *.go

# Check with go vet
go vet
```

## ⚡ Performance Considerations

When contributing, please consider performance impact:

### Do's
- **Profile changes** using Go's built-in profiler
- **Benchmark critical paths** before and after changes
- **Minimize memory allocations** in hot paths
- **Use efficient algorithms** for parsing and querying
- **Cache results** when appropriate

### Don'ts
- **Avoid unnecessary string copying** between Go and Python
- **Don't block Go runtime** with long-running operations
- **Avoid recursive algorithms** that could cause stack overflow
- **Don't ignore memory leaks** - always free allocated memory

### Benchmarking Changes

```bash
# Benchmark specific functions
cd go-core
go test -bench=BenchmarkParsing -benchmem

# Profile memory usage
go test -bench=BenchmarkParsing -memprofile=mem.prof
go tool pprof mem.prof
```

## 📚 Documentation

### Types of Documentation

1. **Code comments** - Explain complex logic
2. **Docstrings** - API documentation  
3. **README updates** - For significant features
4. **Examples** - Practical usage examples
5. **API docs** - Comprehensive API reference

### Writing Good Documentation

- **Be clear and concise**
- **Include examples** when helpful
- **Explain the "why"** not just the "what"
- **Keep it up to date** with code changes
- **Use consistent terminology**

### Example Documentation

```python
def find_by_attribute(self, attr_name: str, attr_value: str) -> List[Tag]:
    """
    Find all elements with a specific attribute value.
    
    This method provides a convenient way to search for elements
    based on any attribute, not just common ones like class or id.
    
    Args:
        attr_name: The name of the attribute to search for
        attr_value: The value the attribute must have
        
    Returns:
        A list of Tag objects matching the criteria
        
    Example:
        Find all links to external sites:
        >>> external_links = soup.find_by_attribute('href', 'http')
        >>> for link in external_links:
        ...     print(link.get('href'))
        
    Note:
        This method is case-sensitive for both attribute names and values.
    """
```

## 🤝 Community

### Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: All contributions are reviewed by maintainers

### Communication Guidelines

- **Be respectful** and constructive
- **Search existing issues** before creating new ones
- **Provide minimal reproducible examples** for bug reports
- **Be patient** - maintainers are volunteers

### Reporting Issues

When reporting issues, please include:

1. **Python version** and operating system
2. **GoBeautifulSoup version**
3. **Minimal code example** that reproduces the issue
4. **Expected behavior** vs actual behavior
5. **Error messages** (full stack trace if applicable)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README.md acknowledgments section

---

Thank you for contributing to GoBeautifulSoup! Your efforts help make HTML parsing faster and more efficient for the entire Python community. 🎉
