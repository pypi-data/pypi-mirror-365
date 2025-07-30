# Contributing to GoAsyncIO

Thank you for your interest in contributing to GoAsyncIO! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.7+ (3.8+ recommended)
- Go 1.21+ (for server development)
- Git
- Basic knowledge of async programming

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/coffeecms/goasyncio.git
   cd goasyncio
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .[dev,test]
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

5. **Run Tests**
   ```bash
   pytest tests/ -v
   ```

## 📋 Development Guidelines

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **Go**: Follow Go conventions, use `gofmt`
- **Documentation**: Use Google-style docstrings
- **Type Hints**: Use type hints for Python code

### Code Formatting

```bash
# Format Python code
black goasyncio/

# Format Go code
cd go && gofmt -s -w .

# Lint Python code
flake8 goasyncio/

# Type check
mypy goasyncio/
```

### Testing

- Write tests for all new features
- Maintain 90%+ code coverage
- Use meaningful test names
- Include both unit and integration tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=goasyncio --cov-report=html

# Run specific test categories
pytest tests/ -m "performance"
pytest tests/ -m "integration"
```

## 🛠️ Types of Contributions

### 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment Information**
   - Python version
   - GoAsyncIO version
   - Operating system
   - Go version (if applicable)

2. **Bug Description**
   - Clear description of the issue
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages/stack traces

3. **Minimal Example**
   ```python
   # Minimal code to reproduce the issue
   import goasyncio
   
   async def reproduce_bug():
       # Your code here
       pass
   ```

### ✨ Feature Requests

For feature requests, please provide:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Performance Impact**: Will this affect performance?

### 🔧 Code Contributions

#### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write code following style guidelines
   - Add/update tests
   - Update documentation
   - Add changelog entry

3. **Test Changes**
   ```bash
   pytest tests/
   flake8 goasyncio/
   mypy goasyncio/
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Format

Use conventional commits:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `test:` - Test additions/changes
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `chore:` - Maintenance tasks

Examples:
```
feat: add WebSocket support for real-time communication
fix: handle connection timeout in client.submit_task()
docs: update README with new performance metrics
test: add integration tests for file operations
```

## 📚 Development Areas

### Python Client Library

Located in `goasyncio/`:
- Client implementation (`client.py`)
- Utility functions (`utils.py`)
- Server management (`server.py`)

### Go Backend Server

Located in `go/`:
- Core event loop (`core/event_loop.go`)
- Network operations (`core/network.go`)
- File I/O (`core/file_io.go`)
- HTTP server (`main.go`)

### Tests

Located in `tests/`:
- Unit tests (`test_client.py`)
- Performance tests (`test_performance.py`)
- Integration tests

### Examples

Located in `examples/`:
- Usage demonstrations
- Integration patterns
- Performance comparisons

## 🏗️ Architecture Overview

### Component Interaction

```
Python Client  ←→  HTTP API  ←→  Go Server
     ↓                              ↓
  aiohttp                    Goroutines
  asyncio                    Event Loop
                            Task Queue
```

### Key Design Principles

1. **Performance First**: Every change should maintain or improve performance
2. **Simplicity**: Keep APIs simple and intuitive
3. **Reliability**: Robust error handling and recovery
4. **Compatibility**: Maintain backward compatibility
5. **Documentation**: Document all public APIs

## 🔍 Code Review Process

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Backward compatibility is maintained
- [ ] Error handling is appropriate
- [ ] Type hints are included (Python)

### Review Criteria

1. **Functionality**: Does it work as intended?
2. **Performance**: Does it maintain/improve performance?
3. **Security**: Are there any security implications?
4. **Maintainability**: Is the code readable and maintainable?
5. **Testing**: Are there adequate tests?

## 📖 Documentation

### Types of Documentation

1. **API Documentation**: Docstrings for all public APIs
2. **User Guides**: How-to guides and tutorials
3. **Examples**: Working code examples
4. **Performance Docs**: Benchmarks and optimization guides

### Writing Documentation

- Use clear, concise language
- Include code examples
- Explain performance implications
- Update when APIs change

## 🚀 Release Process

### Version Numbers

We follow Semantic Versioning (SemVer):
- **Major** (X.0.0): Breaking changes
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.0.X): Bug fixes, backward compatible

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version numbers bumped
- [ ] Performance benchmarks run
- [ ] Examples tested

## 🤝 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: support@goasyncio.dev

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- Be respectful and inclusive
- Focus on what's best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

## 🏆 Recognition

Contributors will be:
- Listed in the README
- Mentioned in release notes
- Invited to join the core team (for significant contributions)

## ❓ Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Create a new discussion
3. Email support@goasyncio.dev

Thank you for contributing to GoAsyncIO! 🎉
