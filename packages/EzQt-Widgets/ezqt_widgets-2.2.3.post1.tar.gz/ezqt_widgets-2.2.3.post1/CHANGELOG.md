# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
| **Project Management** | Quick project overview: `ezqt info` |
| **Error Recovery** | Robust error handling prevents crashes |

---

## [2.1.1] - 2025-07-27

### 📚 Documentation Reorganization

| Change | Description | Impact |
|--------|-------------|---------|
| **API Documentation Structure** | Reorganized technical documentation into `docs/api/` folder | Better organization |
| **Improved Navigation** | Better separation between general and API documentation | Enhanced usability |
| **Style Guide Integration** | Moved `STYLE_GUIDE.md` to API documentation section | Logical grouping |
| **Updated Links** | All documentation links updated to reflect new structure | Consistent navigation |

### 🔄 Structural Changes

| Component | Change | Details |
|-----------|--------|---------|
| **New API Documentation Folder** | `docs/api/` | For all widget API documentation |
| **Centralized Style Guide** | `docs/api/STYLE_GUIDE.md` | Coding standards location |
| **Updated MANIFEST.in** | Reflects new documentation structure | Distribution improvements |
| **Enhanced README** | Updated main documentation index | Better navigation |

### 📁 Updated Documentation Structure

```
docs/
├── README.md                    # Main documentation index
├── api/                        # 🎯 API Documentation
│   ├── README.md              # API documentation guide
│   ├── WIDGETS_DOCUMENTATION.md
│   ├── BUTTONS_DOCUMENTATION.md
│   ├── INPUTS_DOCUMENTATION.md
│   ├── LABELS_DOCUMENTATION.md
│   ├── MISC_DOCUMENTATION.md
│   └── STYLE_GUIDE.md         # Coding standards
└── tests/                      # 🧪 Test documentation
    ├── README.md
    ├── QUICK_START_TESTS.md
    └── ...
```

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Clearer Organization** | API documentation separated from general guides |
| **Better Navigation** | Intuitive structure for developers |
| **Professional Standards** | Follows industry conventions for API documentation |
| **Easier Maintenance** | Logical grouping of related documentation |

---

## [2.1.0] - 2025-07-27

### 🏗️ Architecture

| Component | Feature | Description |
|-----------|---------|-------------|
| **Project Reorganization** | Complete project restructuring | Better maintainability |
| **Documentation Centralization** | Centralized documentation structure | Improved accessibility |
| **Test Infrastructure** | Comprehensive test suite with 262 tests | Better code quality |

### 🧪 Testing Infrastructure

| Feature | Description | Impact |
|---------|-------------|---------|
| **Unit Tests** | Complete test coverage for all widgets | Better reliability |
| **Test Organization** | Structured test hierarchy | Easier maintenance |
| **Test Documentation** | Comprehensive test documentation | Better developer experience |

### 📁 New File Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration
├── run_tests.py             # Test runner
└── unit/                    # Unit tests
    ├── test_button/         # Button widget tests
    ├── test_input/          # Input widget tests
    ├── test_label/          # Label widget tests
    └── test_misc/           # Misc widget tests

docs/
├── README.md                # Main documentation
├── QUICK_START_TESTS.md     # Test quick start guide
├── STYLE_GUIDE.md          # Coding standards
└── tests/                   # Test documentation
    ├── README.md
    ├── test_button_README.md
    ├── test_input_README.md
    ├── test_label_README.md
    ├── test_misc_README.md
    └── unit_README.md
```

### 🔧 Widget Improvements

| Widget | Enhancement | Description |
|--------|-------------|-------------|
| **TabReplaceTextEdit** | Enhanced functionality | Better text editing capabilities |
| **HoverLabel** | Improved hover detection | More responsive user interaction |
| **OptionSelector** | Enhanced selection logic | Better user experience |
| **ToggleSwitch** | Improved state management | More reliable operation |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Better Maintainability** | Organized project structure |
| **Improved Testing** | Comprehensive test coverage |
| **Enhanced Documentation** | Centralized and organized docs |
| **Developer Experience** | Better development workflow |

---

## [2.0.0] - 2025-07-27

### 🚀 Major Update: PySide6 Migration

| Feature | Description | Impact |
|---------|-------------|---------|
| **PySide6 6.9.1** | Migration from PyQt to PySide6 | Modern Qt framework |
| **Enhanced Widgets** | All widgets updated for PySide6 compatibility | Better performance |
| **Deployment Tools** | Improved build and deployment process | Easier distribution |

### 🔧 Widget Enhancements

| Widget | Enhancement | Description |
|--------|-------------|-------------|
| **DateButton** | Improved date handling | Better user experience |
| **IconButton** | Enhanced icon support | More flexible usage |
| **LoaderButton** | Better loading states | Improved feedback |
| **AutoCompleteInput** | Enhanced autocomplete | Better suggestions |
| **PasswordInput** | Improved security | Better password handling |
| **SearchInput** | Enhanced search functionality | Better search experience |
| **TabReplaceTextEdit** | Improved text editing | Better editing capabilities |
| **ClickableTagLabel** | Enhanced click handling | Better interaction |
| **FramedLabel** | Improved styling | Better appearance |
| **HoverLabel** | Enhanced hover effects | Better user feedback |
| **IndicatorLabel** | Improved indicators | Better status display |
| **CircularTimer** | Enhanced timing | Better timer functionality |
| **OptionSelector** | Improved selection | Better user choice |
| **ToggleIcon** | Enhanced toggling | Better state management |
| **ToggleSwitch** | Improved switching | Better user control |

### 📦 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **PySide6** | `>=6.9.1` | Modern Qt framework |
| **Enhanced pyproject.toml** | Updated configuration | Better package management |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Modern Framework** | Latest Qt technology |
| **Better Performance** | Improved widget performance |
| **Enhanced Features** | More widget capabilities |
| **Easier Deployment** | Streamlined distribution |

---

## [1.0.9] - 2025-07-26

### 🔧 OptionSelector Enhancement

| Feature | Description | Impact |
|---------|-------------|---------|
| **ID-based Selection** | Added support for selection by ID | More flexible selection |
| **Enhanced Properties** | New properties for ID-based selection | Better customization |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **OptionSelector** | ID Selection Support | Added methods for ID-based item selection |
| **Parameter Documentation** | Updated documentation | Better developer guidance |

---

## [1.0.8] - 2025-07-26

### 🎨 New Widget: ToggleSwitch

| Feature | Description | Impact |
|---------|-------------|---------|
| **ToggleSwitch Widget** | New toggle switch component | Enhanced user interaction |
| **Style Guide Integration** | Updated style guide with ToggleSwitch and ToggleIcon sections | Better documentation |

### 📁 File Structure Changes

```
ezqt_widgets/misc/
└── toggle_switch.py        # New ToggleSwitch widget

STYLE_GUIDE.md              # Updated with new widget documentation
```

---

## [1.0.7] - 2025-07-26

### 🔧 OptionSelector Enhancement

| Feature | Description | Impact |
|---------|-------------|---------|
| **Custom Animation Duration** | Added customizable animation duration | Better user experience |
| **Enhanced Parameters** | Improved parameter documentation | Better developer guidance |

---

## [1.0.6] - 2025-07-25

### 📝 Documentation Updates

| Change | Description | Impact |
|--------|-------------|---------|
| **License Description** | Updated project description in license | Better legal clarity |
| **MANIFEST.in** | Added STYLE_GUIDE.md to distribution | Better package distribution |

---

## [1.0.5] - 2025-07-25

### 🎨 New Widgets

| Widget | Description | Impact |
|--------|-------------|---------|
| **ClickableTagLabel** | New clickable tag label widget | Enhanced user interaction |
| **CircularTimer** | New circular timer widget | Better timing functionality |
| **OptionSelector** | New option selector widget | Better selection interface |
| **ToggleIcon** | New toggle icon widget | Enhanced visual feedback |

### 🔄 Structural Changes

| Component | Change | Details |
|-----------|--------|---------|
| **Package Reorganization** | Moved widgets to appropriate categories | Better organization |
| **Removed Obsolete Widgets** | Cleaned up old widget implementations | Reduced complexity |

### 📁 File Structure Changes

```
ezqt_widgets/
├── label/
│   └── clickable_tag_label.py  # New ClickableTagLabel widget
└── misc/
    ├── circular_timer.py       # New CircularTimer widget
    ├── option_selector.py      # New OptionSelector widget
    └── toggle_icon.py          # New ToggleIcon widget

# Removed obsolete widgets:
# - ezqt_widgets/loader/
# - ezqt_widgets/toggle/
```

---

## [1.0.4] - 2025-07-25

### 🎨 New Button Widgets

| Widget | Description | Impact |
|--------|-------------|---------|
| **DateButton** | New date selection button | Better date input |
| **LoaderButton** | New loading state button | Better user feedback |
| **IconButton** | Enhanced icon button | Better visual design |

### 📁 File Structure Changes

```
ezqt_widgets/button/
├── date_button.py         # New DateButton widget
├── icon_button.py         # Enhanced IconButton
└── loader_button.py       # New LoaderButton widget
```

---

## [1.0.3] - 2025-07-24

### 🎨 New Input Widgets

| Widget | Description | Impact |
|--------|-------------|---------|
| **AutoCompleteInput** | New autocomplete input field | Better text input |
| **PasswordInput** | New password input field | Secure password entry |
| **SearchInput** | New search input field | Better search functionality |
| **TabReplaceTextEdit** | Enhanced text editor | Better text editing |

### 📚 Documentation

| Feature | Description | Impact |
|---------|-------------|---------|
| **Style Guide** | New comprehensive style guide | Better development standards |
| **Widget Documentation** | Detailed widget usage guide | Better developer experience |

### 📁 File Structure Changes

```
ezqt_widgets/input/
├── auto_complete_input.py     # New AutoCompleteInput widget
├── password_input.py          # New PasswordInput widget
├── search_input.py            # New SearchInput widget
└── tab_replace_textedit.py    # Enhanced TabReplaceTextEdit

STYLE_GUIDE.md                 # New comprehensive style guide
```

---

## [1.0.2] - 2025-07-24

### 🔧 Label Widget Enhancements

| Enhancement | Description | Impact |
|-------------|-------------|---------|
| **Advanced Icon Handling** | Enhanced icon support with SVG/URL | More flexible icons |
| **Dynamic Padding** | Configurable padding options | Better layout control |
| **Enable/Disable Support** | Widget state management | Better user control |
| **Improved Comments** | Better code documentation | Enhanced maintainability |

---

## [1.0.1] - 2025-07-24

### 🔧 Label Widget Refactoring

| Improvement | Description | Impact |
|-------------|-------------|---------|
| **Robustness** | Enhanced error handling | Better reliability |
| **Documentation** | Improved docstrings | Better developer guidance |
| **Icon Handling** | Better icon management | More reliable icon display |

---

## [1.0.0] - 2025-07-24

### 🏗️ Initial Release

| Feature | Description | Impact |
|---------|-------------|---------|
| **Package Structure** | Initial package organization | Foundation for development |
| **Basic Widgets** | Core widget implementations | Basic functionality |
| **Documentation** | Initial documentation setup | Developer guidance |

### 📁 Initial File Structure

```
ezqt_widgets/
├── button/
│   └── icon_button.py         # Icon button widget
├── input/
│   └── untab_textedit.py      # Text editor widget
├── label/
│   ├── framed_label.py        # Framed label widget
│   ├── hover_label.py         # Hover label widget
│   └── indicator_label.py     # Indicator label widget
├── loader/
│   └── circular_loader.py     # Circular loader widget
└── toggle/
    ├── clickable_tag_label.py # Clickable tag label
    ├── toggle_label.py        # Toggle label widget
    └── toggle_radio.py        # Toggle radio widget
```

### 📦 Initial Dependencies

| Dependency | Purpose |
|------------|---------|
| **PyQt/PySide** | Qt framework for widgets |
| **Basic Configuration** | Package setup and distribution |

---

## [0.1.0] - 2025-07-24

### 🚀 Project Initialization

| Feature | Description | Impact |
|---------|-------------|---------|
| **Repository Setup** | Initial git repository | Version control foundation |
| **Basic README** | Initial project documentation | Project overview |

### 📁 Project Foundation

```
README.md                    # Initial project documentation
```

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Version Control** | Git repository for tracking changes |
| **Documentation** | Basic project documentation |
| **Foundation** | Base for future development | 