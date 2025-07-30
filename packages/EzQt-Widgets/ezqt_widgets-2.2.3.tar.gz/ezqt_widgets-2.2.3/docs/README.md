# EzQt Widgets Documentation

## Overview

This directory contains the complete documentation for the EzQt Widgets library. The documentation is organized in a modular way to facilitate navigation and usage.

## Documentation Structure

### 📋 Main Documentation
- **[WIDGETS_DOCUMENTATION.md](api/WIDGETS_DOCUMENTATION.md)** - Complete documentation of all widgets
  - Overview of all modules
  - Detailed documentation of each widget
  - Parameters, properties, signals and examples
  - Usage guide and best practices

### 🎨 Style Guide
- **[STYLE_GUIDE.md](api/STYLE_GUIDE.md)** - Style guide and best practices
  - Code conventions and standards
  - Usage best practices
  - QSS styles customization with links to widget documentation
  - Accessibility principles

### 🚀 Examples and CLI
- **[examples/README.md](examples/README.md)** - Complete usage examples
  - Interactive examples for all widgets
  - Real-world usage scenarios
  - Learning path and best practices
- **[cli/README.md](cli/README.md)** - Command-line interface
  - Quick example execution: `ezqt run --all`
  - Test management: `ezqt test --coverage`
  - Development utilities and tools

## Quick Navigation

### 🧪 Tests by Module

#### Buttons (`test_button/`)
- **DateButton** : 20 tests - Date selection with calendar
- **IconButton** : 17 tests - Button with advanced icon management
- **LoaderButton** : 22 tests - Button with loading states

#### Inputs (`test_input/`)
- **AutoCompleteInput** : 17 tests - Field with autocompletion
- **PasswordInput** : 35 tests - Password field with strength indicator
- **SearchInput** : 20 tests - Search field with history
- **TabReplaceTextEdit** : 25 tests - Editor with tab replacement

#### Labels (`test_label/`)
- **ClickableTagLabel** : Tests for clickable tag
- **FramedLabel** : Tests for framed label
- **HoverLabel** : Tests for label with hover
- **IndicatorLabel** : Tests for status indicator

#### Misc (`test_misc/`)
- **CircularTimer** : Tests for circular timer
- **DraggableList** : Tests for draggable list
- **OptionSelector** : Tests for option selector
- **ToggleIcon** : Tests for toggleable icon
- **ToggleSwitch** : Tests for modern toggle switch

## Usage

### 🔍 How to Navigate
1. **Start with** `WIDGETS_DOCUMENTATION.md` for a complete overview
2. **Use** the table of contents to access widgets directly
3. **Consult** `STYLE_GUIDE.md` for best practices and conventions

### 📚 Recommended Reading Order
- **Beginners** : Overview → Specific widget → Examples
- **Experienced users** : Specific widget → Integration → Custom styles
- **Developers** : Complete documentation → Advanced examples → Style guide

## Useful Links

### 📖 General Documentation
- **[../README.md](../README.md)** - Main documentation guide

### 🧪 Tests and Examples
- **[../api/](../api/)** - API documentation
- **[../examples/](../examples/)** - Complete usage examples
- **[../cli/](../cli/)** - Command-line interface

### 🔗 External Resources
- **Source code** : `../../ezqt_widgets/` - Widget implementation
- **Tests** : `../../tests/` - Unit and integration tests
- **CLI tool** : `ezqt` command (after `pip install -e ".[dev]"`)

---

**EzQt Widgets Documentation** - Complete and consolidated guide for using specialized widgets. 