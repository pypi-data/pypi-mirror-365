# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### 📦 Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| **PyYAML** | `>=6.0` | YAML configuration parsing |
| **Enhanced Requirements** | Updated `pyproject.toml` | Better dependency management |

### 🛠️ Technical Implementation

| Component | Feature | Description |
|-----------|---------|-------------|
| **Theme Loading Function** | `load_and_apply_qss()` | Dynamic theme application |
| **Variable Replacement** | Regex-based variable substitution | QSS customization |
| **Path Resolution** | Automatic detection of theme files | Relative to example locations |
| **Unicode Support** | Full UTF-8 encoding support | International theme configurations |

### 🎯 Benefits

| Benefit | Description |
|---------|-------------|
| **Consistent Styling** | All examples share the same visual theme system |
| **Easy Customization** | Simple YAML-based theme configuration |
| **Professional Appearance** | Modern, cohesive look across all examples |
| **Developer Experience** | Easy theme switching and customization |

### 📁 New File Structure

```
examples/
├── bin/
│   ├── app.yaml          # Theme configuration with color variables
│   ├── main_theme.qss    # QSS styles with variable placeholders
│   └── icons/            # Optional icon assets
├── button_example.py     # Updated with theme support
├── input_example.py      # Updated with theme support
├── label_example.py      # Updated with theme support
├── misc_example.py       # Updated with theme support
└── run_all_examples.py   # Updated with theme support
```

### 🔄 Backward Compatibility

| Aspect | Status | Details |
|--------|--------|---------|
| **Default Styling** | ✅ Maintained | Examples keep original appearance when theme files are not present |
| **No Breaking Changes** | ✅ Preserved | All existing functionality maintained |
| **Optional Feature** | ✅ Additive | Theme system is optional, not required |

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

### 📁 CLI File Structure

```
ezqt_widgets/
├── cli/                           # 🚀 CLI Package
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Main CLI entry point
│   └── runner.py                 # Example execution logic
├── docs/
│   └── cli/                      # 📖 CLI Documentation
│       └── README.md             # CLI usage guide
└── pyproject.toml                # Updated with CLI entry points
```

### 🔄 Backward Compatibility

| Aspect | Status | Details |
|--------|--------|---------|
| **CLI Installation** | ✅ Optional | CLI requires `pip install -e ".[dev]"` |
| **Existing Workflows** | ✅ Preserved | All existing scripts and examples work unchanged |
| **API Compatibility** | ✅ Maintained | No changes to widget APIs |
| **Documentation** | ✅ Enhanced | CLI documentation added without breaking existing docs |

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

| Component | Change | Impact |
|-----------|--------|---------|
| **Complete Project Reorganization** | Restructured project architecture | Better maintainability |
| **Documentation Centralization** | Moved all documentation to `docs/` folder | Improved organization |
| **Test Infrastructure** | Centralized test files and documentation | Enhanced testing |
| **Professional Structure** | Improved project organization | Industry best practices |

### 📚 Documentation

| File | Purpose | Status |
|------|---------|--------|
| `docs/README.md` | Central documentation index | ✅ New |
| `docs/CHANGELOG.md` | Version history | ✅ Moved |
| `docs/STYLE_GUIDE.md` | Code style guidelines | ✅ Moved |
| `docs/QUICK_START_TESTS.md` | Quick test guide | ✅ New |
| `docs/tests/` | Test documentation organized by category | ✅ New |

### 🧪 Testing Infrastructure

| Category | Widgets | Tests | Status |
|----------|---------|-------|--------|
| **Button Widgets** | 3 | 59 (56 pass, 3 skipped) | ✅ Complete |
| **Label Widgets** | 4 | 70 (67 pass, 3 skipped) | ✅ Complete |
| **Input Widgets** | 4 | 112 (111 pass, 1 skipped) | ✅ Complete |
| **Misc Widgets** | 4 | 41 | ✅ Complete |
| **Total** | 15 | 262 (254 pass, 8 skipped) | ✅ Complete |

#### Detailed Test Coverage

| Widget | Tests | Status | Coverage |
|--------|-------|--------|----------|
| **IconButton** | 17 (16 pass, 1 skipped) | ✅ | ~90% |
| **DateButton** | 20 (19 pass, 1 skipped) | ✅ | ~30% |
| **LoaderButton** | 22 (21 pass, 1 skipped) | ✅ | ~27% |
| **ClickableTagLabel** | 17 (14 pass, 3 skipped) | ✅ | ~85% |
| **FramedLabel** | 15 | ✅ | ~80% |
| **HoverLabel** | 20 | ✅ | ~75% |
| **IndicatorLabel** | 18 | ✅ | ~70% |
| **AutoCompleteInput** | 28 | ✅ | ~85% |
| **PasswordInput** | 35 | ✅ | ~85% |
| **SearchInput** | 30 | ✅ | ~80% |
| **TabReplaceTextEdit** | 19 (18 pass, 1 skipped) | ✅ | ~90% |
| **CircularTimer** | 11 | ✅ | ~60% |
| **OptionSelector** | 10 | ✅ | ~70% |
| **ToggleIcon** | 12 | ✅ | ~65% |
| **ToggleSwitch** | 8 | ✅ | ~75% |

### 🔧 Configuration

| File | Updates | Impact |
|------|---------|---------|
| **pyproject.toml** | French description, improved keywords, enhanced classifiers | Better PyPI visibility |
| **Enhanced .gitignore** | Comprehensive coverage for Python projects | Cleaner repository |
| **Updated MANIFEST.in** | Proper file inclusion for distribution | Better packaging |

### 🐛 Bug Fixes

| Issue | Fix | Impact |
|-------|-----|---------|
| **Qt Event Handling** | Fixed issues with mock events in tests | Improved test reliability |
| **Import Errors** | Corrected QEvent import from PySide6.QtCore | Better compatibility |
| **Test Reliability** | Improved test stability and error handling | More robust testing |
| **Accessibility Tests** | Fixed focus policy validation in tests | Better accessibility |

### 🎯 Features Tested

| Category | Features | Coverage |
|----------|----------|----------|
| **Widget Properties** | Getters, setters, validation, signals | ✅ Complete |
| **Event Handling** | Mouse, keyboard, paint, resize events | ✅ Complete |
| **Qt Signals** | 6 different signals tested across widgets | ✅ Complete |
| **Widget Interactions** | Toggle behavior, hover effects, focus management | ✅ Complete |
| **Icon Management** | QIcon, files, SVG handling | ✅ Complete |
| **State Transitions** | Status changes, color updates, alignments | ✅ Complete |
| **Qt Integration** | Fixtures, mocks, isolation | ✅ Complete |

### 📁 New Project Structure

```
ezqt_widgets/
├── README.md                    # Main README
├── docs/                       # 📚 Centralized documentation
│   ├── README.md              # Documentation index
│   ├── CHANGELOG.md           # Version history
│   ├── STYLE_GUIDE.md         # Style guide
│   ├── QUICK_START_TESTS.md   # Quick test guide
│   └── tests/                 # Test documentation
├── tests/                      # 🧪 Centralized tests
│   ├── run_tests.py           # Test runner
│   ├── conftest.py            # Pytest configuration
│   └── unit/                  # Unit tests
└── ezqt_widgets/              # 📦 Source code
```

### 🚀 Usage

| Command | Purpose | Example |
|---------|---------|---------|
| **Test Execution** | Run unit tests | `python tests/run_tests.py --type unit` |
| **Documentation** | Navigate documentation | Via `docs/README.md` |
| **Development** | Install in development mode | `pip install -e ".[dev]"` |

### 📊 Statistics

| Metric | Value | Status |
|--------|-------|--------|
| **Total Tests** | 262 (254 pass, 8 skipped) | ✅ Complete |
| **Coverage Estimate** | 27-90% per widget | ✅ Good |
| **Widgets Tested** | 15 widgets (3 button, 4 label, 4 input, 4 misc) | ✅ Complete |
| **Test Categories** | Unit tests, property tests, event tests, signal tests | ✅ Complete |

---

## [2.0.0] - 2025-07-26

### 🚀 Added

| Feature | Description | Impact |
|---------|-------------|---------|
| **PySide6 6.9.1 Support** | Complete migration to the latest stable version | Enhanced compatibility |
| **Type Hints Improvements** | Utilization of new PySide6 6.9.1 typing features | Better code quality |
| **Windows ARM64 Support** | Compatibility with new Windows architectures | Extended platform support |
| **New APIs** | Support for `QMessageLogger` and other new features | Enhanced functionality |
| **Enhanced Deployment Tools** | Support for `--flatpak`, `--standalone` and `pyproject.toml` | Better deployment |

### 🔧 Changed

| Component | Change | Details |
|-----------|--------|---------|
| **Major Version** | Upgrade from 1.0.9 to 2.0.0 | Reflects major changes |
| **PySide6 Dependency** | Updated from `6.7.3` to `>=6.9.1,<7.0.0` | Latest stable version |
| **Development Status** | Moved from "Alpha" to "Beta" (3 → 4) | More mature status |
| **Code Structure** | Complete uniformization of all widgets | Consistent architecture |

### 🧹 Cleaned

| Widget | Removed Imports | Impact |
|--------|----------------|---------|
| **icon_button.py** | `Callable` | Cleaner imports |
| **password_input.py** | `Callable`, `QAction` | Reduced dependencies |
| **hover_label.py** | `Callable` | Simplified imports |
| **search_input.py** | `Callable`, `QAction` | Cleaner code |
| **toggle_switch.py** | `Callable` | Optimized imports |
| **date_button.py** | `Callable`, `QSizePolicy`, `datetime` | Streamlined code |
| **loader_button.py** | `Callable`, `QSizePolicy`, `QPropertyAnimation`, `QEasingCurve` | Performance improvements |

### 📝 Documentation

| File | Updates | Impact |
|------|---------|---------|
| **README.md** | Updated with new PySide6 version and added Changelog section | Better information |
| **pyproject.toml** | Complete project configuration update | Modern packaging |
| **Uniformized Comments** | Standardization of all comments according to `icon_button.py` model | Consistent documentation |

### 🔄 Refactored

| Widget Structure | Sections | Purpose |
|------------------|----------|---------|
| **INITIALIZATION** | Constructor and setup | Widget creation |
| **PROPERTIES** | Property definitions | Data management |
| **UTILITY FUNCTIONS** | Helper methods | Code organization |
| **EVENT FUNCTIONS** | Event handlers | User interaction |
| **OVERRIDE FUNCTIONS** | Qt overrides | Framework integration |
| **STYLE FUNCTIONS** | Styling methods | Visual appearance |

### 🐛 Fixed

| Issue | Fix | Impact |
|-------|-----|---------|
| **Error Handling** | Improved robustness of icon loading | Better reliability |
| **Performance Optimizations** | Enhanced animations and rendering | Smoother experience |
| **Compatibility** | Fixed compatibility issues with PySide6 6.9.1 | Better stability |

### 📦 Updated Widgets

| Category | Widget | Status | Updates |
|----------|--------|--------|---------|
| **Buttons** | `icon_button.py` | ✅ Reference model | Complete uniformization |
| **Buttons** | `date_button.py` | ✅ Comment uniformization | Consistent structure |
| **Buttons** | `loader_button.py` | ✅ Import cleanup | Optimized performance |
| **Inputs** | `auto_complete_input.py` | ✅ Uniform structure | Better organization |
| **Inputs** | `password_input.py` | ✅ Improved icon management | Enhanced functionality |
| **Inputs** | `search_input.py` | ✅ Interface optimization | Better UX |
| **Inputs** | `tab_replace_textedit.py` | ✅ Enhanced event handling | Improved reliability |
| **Labels** | `clickable_tag_label.py` | ✅ Improved user interface | Better interaction |
| **Labels** | `framed_label.py` | ✅ Simplified structure | Cleaner code |
| **Labels** | `hover_label.py` | ✅ Optimized icon handling | Better performance |
| **Labels** | `indicator_label.py` | ✅ More maintainable code | Easier maintenance |
| **Misc** | `circular_timer.py` | ✅ Enhanced animations | Smoother visuals |
| **Misc** | `option_selector.py` | ✅ Smoother interface | Better UX |
| **Misc** | `toggle_icon.py` | ✅ Optimized state management | Better performance |
| **Misc** | `toggle_switch.py` | ✅ Improved graphical rendering | Enhanced visuals |

### 🔧 Technical Improvements

| Area | Improvement | Impact |
|------|-------------|---------|
| **Icon Management** | Enhanced support for SVG, URL and local icons | More flexible |
| **Animations** | Optimized transitions and visual effects | Smoother experience |
| **Events** | More robust user interaction handling | Better reliability |
| **Styles** | Improved visual consistency | Professional appearance |

### 📋 Migration

| Aspect | Status | Details |
|--------|--------|---------|
| **Backward Compatibility** | ✅ Maintained | Widgets remain compatible with existing applications |
| **Stable API** | ✅ Preserved | No public API changes, only internal improvements |
| **Performance** | ✅ Improved | Performance improvements thanks to PySide6 6.9.1 optimizations |

---

## [1.0.9] - 2025-01-19

### 🔧 Changed
- Minor fixes and optimizations
- Documentation improvements

### 🐛 Fixed
- Fixed minor bugs in widgets
- Improved overall stability

---

## [1.0.0] - 2025-07-24

### 🚀 Added
- Initial version of EzQt_Widgets
- Complete collection of custom widgets for PySide6
- Comprehensive documentation and usage examples
- Support for PySide6 6.7.3

### 📦 Included Widgets

| Category | Widgets | Description |
|----------|---------|-------------|
| **Buttons** | IconButton, DateButton, LoaderButton | Custom button implementations |
| **Inputs** | PasswordInput, SearchInput, AutoCompleteInput, TabReplaceTextEdit | Advanced input components |
| **Labels** | ClickableTagLabel, FramedLabel, HoverLabel, IndicatorLabel | Interactive label widgets |
| **Misc** | CircularTimer, OptionSelector, ToggleIcon, ToggleSwitch | Utility components |

---

## Change Types

| Type | Description | Icon |
|------|-------------|------|
| **🚀 Added** | New features | 🚀 |
| **🔧 Changed** | Changes in existing functionality | 🔧 |
| **🐛 Fixed** | Bug fixes | 🐛 |
| **🧹 Cleaned** | Removal of obsolete or unnecessary code | 🧹 |
| **📝 Documentation** | Documentation updates | 📝 |
| **🔄 Refactored** | Code restructuring without functional changes | 🔄 |
| **📦 Updated Widgets** | Widget-specific modifications | 📦 |
| **🔧 Technical Improvements** | Optimizations and technical enhancements | 🔧 |
| **📋 Migration** | Migration instructions and notes | 📋 | 