# EzQt Widgets CLI

Command-line interface for running examples and managing EzQt Widgets development workflow.

## 🚀 Quick Start

### Installation
```bash
# Install in development mode
pip install -e ".[dev]"

# Verify installation
ezqt --version
```

### Basic Usage
```bash
# Run all examples with GUI launcher
ezqt run --all

# Run specific example categories
ezqt run --buttons
ezqt run --inputs
ezqt run --labels
ezqt run --misc

# List available examples
ezqt list

# Show package information
ezqt info
```

## 📋 Available Commands

### `ezqt run` - Run Examples

Launch interactive examples to explore widget functionality.

#### Options
| Option | Short | Description |
|--------|-------|-------------|
| `--all` | `-a` | Run all examples with GUI launcher |
| `--buttons` | `-b` | Run button examples (DateButton, IconButton, LoaderButton) |
| `--inputs` | `-i` | Run input examples (AutoComplete, Password, Search, TabReplace) |
| `--labels` | `-l` | Run label examples (ClickableTag, Framed, Hover, Indicator) |
| `--misc` | `-m` | Run misc examples (CircularTimer, DraggableList, OptionSelector, ToggleIcon, ToggleSwitch) |
| `--no-gui` | | Run examples sequentially without GUI launcher |
| `--verbose` | `-v` | Verbose output with detailed information |

#### Examples
```bash
# Run all examples with GUI
ezqt run --all

# Run only button examples
ezqt run --buttons

# Run input examples with verbose output
ezqt run --inputs --verbose

# Run all examples sequentially (no GUI)
ezqt run --all --no-gui

# Run misc examples with detailed output
ezqt run --misc -v
```

### `ezqt list` - List Examples

Show all available example files and their status.

```bash
ezqt list
```

**Output:**
```
📋 Available examples:
========================================
✅ button_example
✅ input_example
✅ label_example
✅ misc_example
✅ run_all_examples

Total: 5 examples found
```

### `ezqt test` - Run Tests

Execute the test suite for EzQt Widgets.

#### Options
| Option | Short | Description |
|--------|-------|-------------|
| `--unit` | `-u` | Run unit tests |
| `--coverage` | `-c` | Run tests with coverage |
| `--verbose` | `-v` | Verbose output |

#### Examples
```bash
# Run unit tests
ezqt test --unit

# Run tests with coverage
ezqt test --coverage

# Run both with verbose output
ezqt test --unit --coverage --verbose
```

### `ezqt docs` - Documentation Utilities

Access and manage EzQt Widgets documentation.

#### Options
| Option | Short | Description |
|--------|-------|-------------|
| `--serve` | `-s` | Serve documentation locally |
| `--port` | `-p` | Specify port (default: 8000) |

#### Examples
```bash
# Serve documentation on default port
ezqt docs --serve

# Serve documentation on custom port
ezqt docs --serve --port 8080
```

### `ezqt info` - Package Information

Display information about EzQt Widgets installation.

```bash
ezqt info
```

**Output:**
```
🎨 EzQt Widgets Information
========================================
Version: 2.2.0
Location: /path/to/ezqt_widgets/__init__.py
PySide6: 6.9.1
Examples: 5 found
========================================
```

## 🎯 Use Cases

### For Developers
```bash
# Quick testing during development
ezqt run --buttons --verbose

# Run tests before commit
ezqt test --coverage

# Check package status
ezqt info
```

### For Users
```bash
# Explore all widgets
ezqt run --all

# Focus on specific widget type
ezqt run --inputs

# See what's available
ezqt list
```

### For Documentation
```bash
# Serve documentation locally
ezqt docs --serve --port 8080

# Open browser to http://localhost:8080
```

## 🔧 Configuration

### Environment Variables
- `EZQT_VERBOSE` - Enable verbose mode by default
- `EZQT_EXAMPLES_DIR` - Custom examples directory path

### Configuration Files
The CLI automatically detects examples in the following locations:
1. Project root `/examples/` directory
2. Current working directory `/examples/`
3. Package directory `/ezqt_widgets/examples/`

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Command not found** | Install in dev mode: `pip install -e ".[dev]"` |
| **Examples not found** | Check if examples directory exists in project root |
| **Import errors** | Verify PySide6 installation: `pip install PySide6` |
| **Permission errors** | Run with appropriate permissions or use virtual environment |

### Debug Mode
```bash
# Enable verbose output
ezqt run --buttons --verbose

# Check package installation
ezqt info
```

## 📚 Integration

### With Development Workflow
```bash
# 1. Install in development mode
pip install -e ".[dev]"

# 2. Run examples for testing
ezqt run --buttons

# 3. Run tests
ezqt test --coverage

# 4. Serve documentation
ezqt docs --serve
```

### With CI/CD
```bash
# In CI pipeline
pip install -e ".[dev]"
ezqt test --coverage
```

## 🔗 Related Documentation

- **[📖 API Documentation](../api/WIDGETS_DOCUMENTATION.md)** - Complete widget reference
- **[🎨 Style Guide](../api/STYLE_GUIDE.md)** - QSS customization examples
- **[🧪 Test Documentation](../tests/TESTS_DOCUMENTATION.md)** - Testing patterns and fixtures
- **[📋 Examples Documentation](../examples/README.md)** - Example usage and learning

---

**EzQt Widgets CLI** - Making development and exploration easier with command-line tools. 