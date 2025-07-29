# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-19

### 🚀 Added
- **PySide6 6.9.1 Support** : Complete migration to the latest stable version of PySide6
- **Type Hints Improvements** : Utilization of new PySide6 6.9.1 typing features
- **Windows ARM64 Support** : Compatibility with new Windows architectures
- **New APIs** : Support for `QMessageLogger` and other new features
- **Enhanced Deployment Tools** : Support for `--flatpak`, `--standalone` and `pyproject.toml`

### 🔧 Changed
- **Major Version** : Upgrade from 1.0.9 to 2.0.0 to reflect major changes
- **PySide6 Dependency** : Updated from `6.7.3` to `>=6.9.1,<7.0.0`
- **Development Status** : Moved from "Alpha" to "Beta" (3 → 4)
- **Code Structure** : Complete uniformization of all widgets

### 🧹 Cleaned
- **Unused Imports** : Removed all unused imports from all widgets
  - `Callable` removed from `icon_button.py`, `password_input.py`, `hover_label.py`, `search_input.py`, `toggle_switch.py`, `date_button.py`, `loader_button.py`
  - `QAction` removed from `password_input.py` and `search_input.py`
  - `QSizePolicy` removed from `date_button.py` and `loader_button.py`
  - `QPropertyAnimation` and `QEasingCurve` removed from `loader_button.py`
  - `datetime` removed from `date_button.py`

### 📝 Documentation
- **README.md** : Updated with new PySide6 version and added Changelog section
- **pyproject.toml** : Complete project configuration update
- **Uniformized Comments** : Standardization of all comments according to `icon_button.py` model

### 🔄 Refactored
- **Widget Structure** : Complete reorganization with standardized sections:
  - `# INITIALIZATION`
  - `# PROPERTIES`
  - `# UTILITY FUNCTIONS`
  - `# EVENT FUNCTIONS`
  - `# OVERRIDE FUNCTIONS`
  - `# STYLE FUNCTIONS`

### 🐛 Fixed
- **Error Handling** : Improved robustness of icon loading
- **Performance Optimizations** : Enhanced animations and rendering
- **Compatibility** : Fixed compatibility issues with PySide6 6.9.1

### 📦 Updated Widgets
All widgets have been uniformized and optimized:

#### Buttons (`button/`)
- ✅ `icon_button.py` - Reference model
- ✅ `date_button.py` - Comment uniformization
- ✅ `loader_button.py` - Import cleanup

#### Inputs (`input/`)
- ✅ `auto_complete_input.py` - Uniform structure
- ✅ `password_input.py` - Improved icon management
- ✅ `search_input.py` - Interface optimization
- ✅ `tab_replace_textedit.py` - Enhanced event handling

#### Labels (`label/`)
- ✅ `clickable_tag_label.py` - Improved user interface
- ✅ `framed_label.py` - Simplified structure
- ✅ `hover_label.py` - Optimized icon handling
- ✅ `indicator_label.py` - More maintainable code

#### Misc (`misc/`)
- ✅ `circular_timer.py` - Enhanced animations
- ✅ `option_selector.py` - Smoother interface
- ✅ `toggle_icon.py` - Optimized state management
- ✅ `toggle_switch.py` - Improved graphical rendering

### 🔧 Technical Improvements
- **Icon Management** : Enhanced support for SVG, URL and local icons
- **Animations** : Optimized transitions and visual effects
- **Events** : More robust user interaction handling
- **Styles** : Improved visual consistency

### 📋 Migration
- **Backward Compatibility** : Widgets remain compatible with existing applications
- **Stable API** : No public API changes, only internal improvements
- **Performance** : Performance improvements thanks to PySide6 6.9.1 optimizations

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
- Custom buttons (IconButton, DateButton, LoaderButton)
- Advanced inputs (PasswordInput, SearchInput, AutoCompleteInput, TabReplaceTextEdit)
- Interactive labels (ClickableTagLabel, FramedLabel, HoverLabel, IndicatorLabel)
- Utility components (CircularTimer, OptionSelector, ToggleIcon, ToggleSwitch)

---

## Change Types

- **🚀 Added** : New features
- **🔧 Changed** : Changes in existing functionality
- **🐛 Fixed** : Bug fixes
- **🧹 Cleaned** : Removal of obsolete or unnecessary code
- **📝 Documentation** : Documentation updates
- **🔄 Refactored** : Code restructuring without functional changes
- **📦 Updated Widgets** : Widget-specific modifications
- **🔧 Technical Improvements** : Optimizations and technical enhancements
- **📋 Migration** : Migration instructions and notes 