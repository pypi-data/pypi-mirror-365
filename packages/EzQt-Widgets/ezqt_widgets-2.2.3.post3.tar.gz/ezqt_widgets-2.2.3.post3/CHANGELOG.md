# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.3.post3] - 2025-01-15

### 🔧 Package Distribution & Examples Integration Fix

| Component | Updates | Benefits |
|-----------|---------|----------|
| **Examples Directory** | Moved examples/ inside ezqt_widgets/ package | Examples properly embedded in package |
| **Package Data Configuration** | Fixed package-data to point to correct location | Examples available after installation |
| **PySide6 Compatibility** | Adjusted version constraint to `>=6.7.3,<7.0.0` | Compatible with ezqt-app's PySide6==6.7.3 requirement |
| **Dependency Resolution** | Fixed conflict with ezqt-app requirements | Seamless integration with ezqt-app |
| **PyYAML Dependency** | Added PyYAML>=6.0 to dependencies | Examples can load YAML configuration files |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **Directory Structure** | examples/ moved inside ezqt_widgets/ package | Proper package structure |
| **Package Data** | Corrected paths in setuptools.package-data | Examples included in distribution |
| **PySide6 Compatibility** | Adjusted version constraint to `>=6.7.3,<7.0.0` | Compatible with ezqt-app's PySide6==6.7.3 requirement |
| **Installation** | Examples available in installed package | Users can access examples directly |
| **Dependencies** | Added PyYAML>=6.0 | Required for loading app.yaml configuration files |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Complete Package** | Examples are now properly embedded in the package |
| **ezqt-app Compatibility** | No more dependency conflicts with ezqt-app |
| **Easy Access** | Users can find examples in the installed package |
| **Better Distribution** | All resources included in package installation |
| **Seamless Integration** | Can be installed alongside ezqt-app without issues |
| **Working Examples** | All examples can now run without missing dependency errors |

### 📦 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **PySide6** | `>=6.7.3,<7.0.0` | Core Qt framework (compatible with ezqt-app) |
| **PyYAML** | `>=6.0` | YAML file parsing for theme configuration |

---

## [2.2.3.post2] - 2025-01-15

### 🔧 Package Distribution Enhancement

| Component | Updates | Benefits |
|-----------|---------|----------|
| **Package Data Configuration** | Fixed package-data section in pyproject.toml | Proper embedding of examples and resources |
| **MANIFEST.in** | Optimized file inclusion patterns | More efficient package building |
| **Resource Embedding** | Ensured examples/, docs/, and tests/ are properly included | Complete package distribution |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **Package Data Structure** | Changed from wildcard "*" to specific "ezqt_widgets" package | Correct resource embedding |
| **Documentation Inclusion** | Added recursive-include for docs directory | All documentation files included |
| **Examples Embedding** | Fixed examples directory inclusion | Examples available in installed package |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Complete Package** | All examples, docs, and tests properly embedded |
| **Better Distribution** | Resources available after package installation |
| **Improved Build Process** | More reliable and efficient package building |
| **Enhanced User Experience** | Users have access to all project resources |

---

## [2.2.3.post1] - 2025-01-15

### 🔧 Package Distribution Fix

| Component | Updates | Benefits |
|-----------|---------|----------|
| **Package Data** | Added examples/ and tests/ directories to package distribution | Examples and tests included in installed package |
| **CLI Dependencies** | Moved click to main dependencies | CLI tools work without dev dependencies |

### 📦 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **click** | `>=8.2.1` | Command-line interface framework for CLI tools |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **Package Data Configuration** | Added setuptools.package-data section | Examples and tests included in distribution |
| **CLI Dependencies** | Moved click from dev to main dependencies | CLI functionality in production |
| **Development Status** | Updated to "Production/Stable" | Reflects project maturity |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Complete Package** | Examples and tests available after installation |
| **CLI Functionality** | CLI tools work in production environments |
| **Better Distribution** | All necessary files included in package |
| **Production Ready** | Project status reflects stability and maturity |

### 📋 Project Status Update

| Status | Description | Impact |
|--------|-------------|---------|
| **Development Status** | Changed from "Beta" to "Production/Stable" | Indicates project maturity and production readiness |
| **Stability Level** | Production-ready with comprehensive testing | Suitable for production use |
| **Maintenance Mode** | Active development with stable releases | Reliable for long-term projects |

---

## [2.2.3] - 2025-01-15

### 🔧 Dependencies Cleanup

| Component | Updates | Benefits |
|-----------|---------|----------|
| **pyproject.toml** | Removed unnecessary dependencies (requests-toolbelt, rich, pyyaml, flake8) | Cleaner dependency management |
| **Dependencies Optimization** | Moved requests and click to main dependencies, kept only essential dev dependencies | Reduced package size and complexity |

### 📦 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **PySide6** | `>=6.9.1,<7.0.0` | Core Qt framework |
| **requests** | `>=2.32.4` | HTTP requests for widget functionality |
| **click** | `>=8.2.1` | Command-line interface framework for CLI tools |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **Dependency Analysis** | Scanned project for actual usage | Identified and removed unused dependencies |
| **CLI Dependencies** | Moved click to main dependencies | CLI tools work without dev dependencies |
| **Version Management** | Updated to version 2.2.3 | Incremental patch release |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Cleaner Dependencies** | Only essential packages are listed |
| **CLI Functionality** | CLI tools work in production environments |
| **Reduced Complexity** | Easier maintenance and deployment |
| **Better Performance** | Smaller package footprint |

---

## [2.2.2] - 2025-07-27

### 🔧 Documentation Updates

| Component | Updates | Benefits |
|-----------|---------|----------|
| **README.md** | Fixed documentation links | Better navigation |
| **Package Metadata** | Updated version information | Accurate package details |

### 📁 File Structure Changes

```
README.md                    # Updated documentation links
ezqt_widgets/__init__.py     # Version update
pyproject.toml              # Package metadata update
```

---

## [2.2.1] - 2025-07-27

### 🔧 Configuration Improvements

| Component | Updates | Benefits |
|-----------|---------|----------|
| **Git Configuration** | Updated .gitignore patterns | Better version control |
| **Package Distribution** | Enhanced MANIFEST.in | Improved package distribution |

### 📁 File Structure Changes

```
.gitignore                  # Updated ignore patterns
MANIFEST.in                 # Enhanced distribution configuration
ezqt_widgets/__init__.py    # Version update
pyproject.toml              # Package configuration
```

---

## [2.2.0] - 2025-07-27

### 🎨 Theme System Integration

| Feature | Description | Impact |
|---------|-------------|---------|
| **Dynamic Theme Loading** | All examples support dynamic theme loading from YAML configuration files | Enhanced customization |
| **QSS Variable System** | Implementation of variable-based styling with `$_variable` syntax | Consistent theming |
| **Theme Configuration** | New `bin/app.yaml` and `bin/main_theme.qss` files for centralized theme management | Professional appearance |
| **Multiple Theme Support** | Support for "dark" and "light" themes with easy extensibility | User preference support |

### 🔧 Enhanced Examples

| Component | Updates | Benefits |
|-----------|---------|----------|
| **Unified Theme System** | All example files now use the same theme loading mechanism | Consistent experience |
| **Automatic Theme Detection** | Examples automatically load themes from `examples/bin/` directory | Seamless integration |
| **Fallback Styling** | Graceful degradation to default styles when theme files are not available | Robust operation |
| **Error Handling** | Robust error handling for missing or corrupted theme files | Better reliability |

### 🚀 Command Line Interface (CLI)

| Feature | Description | Impact |
|---------|-------------|---------|
| **CLI Tool** | New `ezqt` command-line interface for managing examples and development | Enhanced developer experience |
| **Example Management** | `ezqt run --all`, `ezqt run --buttons`, `ezqt run --inputs`, etc. | Quick example execution |
| **Test Management** | `ezqt test --unit`, `ezqt test --coverage` | Streamlined testing workflow |
| **Documentation Tools** | `ezqt docs --serve` for local documentation server | Better documentation access |
| **Package Information** | `ezqt info` for package details and status | Quick project overview |

### 🔧 CLI Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **CLI Structure** | `ezqt_widgets/cli/` package with modular design | Clean architecture |
| **Example Runner** | `ExampleRunner` class with robust error handling | Reliable execution |
| **Command Groups** | `run`, `list`, `test`, `docs`, `info` commands | Comprehensive toolset |
| **Error Handling** | Graceful handling of missing files and import errors | Robust operation |
| **Verbose Mode** | `--verbose` flag for detailed execution information | Better debugging |

### 🎯 New Widget: DraggableList

| Feature | Description | Impact |
|---------|-------------|---------|
| **Drag and Drop** | Interactive list with drag and drop functionality | Enhanced user interaction |
| **Custom Items** | Support for custom draggable items | Flexible implementation |
| **Visual Feedback** | Visual indicators during drag operations | Better user experience |

### 📁 New File Structure

```
examples/
├── bin/
│   ├── app.yaml          # Theme configuration with color variables
│   ├── main_theme.qss    # QSS styles with variable placeholders
│   └── icons/            # Comprehensive icon collection (200+ icons)
├── button_example.py     # Updated with theme support
├── input_example.py      # Updated with theme support
├── label_example.py      # Updated with theme support
├── misc_example.py       # Updated with theme support
└── run_all_examples.py   # Updated with theme support

ezqt_widgets/
├── cli/                  # New CLI package
│   ├── __init__.py
│   ├── main.py          # CLI entry point
│   └── runner.py        # Example execution logic
└── misc/
    └── draggable_list.py # New widget

docs/
├── cli/                  # CLI documentation
│   └── README.md        # CLI usage guide
└── examples/            # Example documentation
    └── README.md        # Example usage guide
```

### 🔄 Backward Compatibility

| Aspect | Status | Details |
|--------|--------|---------|
| **Default Styling** | ✅ Maintained | Examples keep original appearance when theme files are not present |
| **No Breaking Changes** | ✅ Preserved | All existing functionality maintained |
| **Optional Feature** | ✅ Additive | Theme system is optional, not required |

### 🐛 Bug Fixes

| Issue | Fix | Impact |
|-------|-----|---------|
| **Icon URL Error** | Fixed invalid icon path `:https://img.icons8.com/` in `DraggableList` | Widget Misc now displays correctly |
| **Import Errors** | Added missing `sys` and `os` imports in CLI modules | CLI functions properly |
| **Directory Issues** | CLI runner changes to examples directory before execution | Proper file path resolution |
| **Widget Loading** | Robust error handling for widget imports in launcher | Graceful degradation |

### 📦 CLI Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **click** | `>=8.0.0` | Command-line interface framework |
| **Enhanced pyproject.toml** | Updated script entry points | CLI installation and registration |

### 🎯 CLI Benefits

| Benefit | Description |
|---------|-------------|
| **Developer Productivity** | Single command to run examples: `ezqt run --all` |
| **Testing Workflow** | Streamlined test execution: `ezqt test --coverage` |
| **Documentation Access** | Local documentation server: `ezqt docs --serve` |
| **Project Management** | Quick project overview: `ezqt info`