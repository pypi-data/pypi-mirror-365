# Complete Test Documentation - EzQt Widgets

## Overview

This document presents all available tests for the EzQt library, organized by functional modules. Each widget has a complete test suite to ensure code quality and reliability.

## Table of Contents

- [🎛️ Button Tests](#️-button-tests)
  - [DateButton](#datebutton)
  - [IconButton](#iconbutton)
  - [LoaderButton](#loaderbutton)
- [⌨️ Input Tests](#️-input-tests)
  - [AutoCompleteInput](#autocompleteinput)
  - [PasswordInput](#passwordinput)
  - [SearchInput](#searchinput)
  - [TabReplaceTextEdit](#tabreplacetextedit)
- [🏷️ Label Tests](#️-label-tests)
  - [ClickableTagLabel](#clickabletaglabel)
  - [FramedLabel](#framedlabel)
  - [HoverLabel](#hoverlabel)
  - [IndicatorLabel](#indicatorlabel)
- [🔧 Misc Tests](#️-misc-tests)
  - [CircularTimer](#circulartimer)
  - [DraggableList](#draggablelist)
  - [OptionSelector](#optionselector)
  - [ToggleIcon](#toggleicon)
  - [ToggleSwitch](#toggleswitch)

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── unit/                          # Unit tests
│   ├── test_button/               # Button widget tests
│   ├── test_input/                # Input widget tests
│   ├── test_label/                # Label widget tests
│   └── test_misc/                 # Misc widget tests
└── integration/                   # Integration tests (optional)
```

## 🎛️ Button Tests

### DateButton
**File :** `test_button/test_date_button.py`  
**Tests :** 20 tests

Date picker button widget with integrated calendar.

**Covered tests :**
- ✅ Utility functions (`format_date`, `parse_date`, `get_calendar_icon`)
- ✅ `DatePickerDialog` class
- ✅ Creation with default and custom parameters
- ✅ Properties (date, format, show_calendar_icon, min_width, min_height)
- ✅ Signals (`dateChanged`, `dateSelected`)
- ✅ Methods (`clear_date`, `set_today`, `open_calendar`)
- ✅ Date handling (QDate, string, custom format)
- ✅ Mouse events and display
- ✅ Date format validation

**Statistics :**
- **Tests :** 20
- **Pass :** 19
- **Skip :** 1
- **Coverage :** ~30%

### IconButton
**File :** `test_button/test_icon_button.py`  
**Tests :** 17 tests

Button with icon support and optional text.

**Covered tests :**
- ✅ Utility functions (`colorize_pixmap`, `load_icon_from_source`)
- ✅ Creation with default and custom parameters
- ✅ Properties (icon, text, icon_size, icon_color, min_width, min_height)
- ✅ Icon handling (QIcon, file, SVG, URL)
- ✅ Signals (`iconChanged`, `textChanged`)
- ✅ Methods (`clear_icon`, `clear_text`, `toggle_text_visibility`)
- ✅ Pixmap colorization and opacity
- ✅ Icon loading from various sources
- ✅ Minimum dimensions and style

**Statistics :**
- **Tests :** 17
- **Pass :** 16
- **Skip :** 1
- **Coverage :** ~90%

### LoaderButton
**File :** `test_button/test_loader_button.py`  
**Tests :** 22 tests

Button with integrated loading animation.

**Covered tests :**
- ✅ Utility functions (`create_spinner_pixmap`, `create_loading_icon`, etc.)
- ✅ Creation with default and custom parameters
- ✅ Properties (loading, success, error, animation_speed, show_duration)
- ✅ Signals (`loadingStarted`, `loadingFinished`, `loadingFailed`)
- ✅ Loading states (loading, success, error)
- ✅ Animations and timers
- ✅ State transitions
- ✅ Configuration (speed, display time, auto-reset)
- ✅ Control methods (`start_loading`, `stop_loading`, `set_success`, `set_error`)

**Statistics :**
- **Tests :** 22
- **Pass :** 21
- **Skip :** 1
- **Coverage :** ~27%

## ⌨️ Input Tests

### AutoCompleteInput
**File :** `test_input/test_auto_complete_input.py`  
**Tests :** 17 tests

Text field with autocomplete.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (suggestions, case_sensitive, filter_mode, completion_mode)
- ✅ Suggestion handling (add, remove, clear)
- ✅ Integration with QCompleter
- ✅ Case sensitivity
- ✅ Filtering modes (MatchContains, MatchStartsWith, MatchEndsWith)
- ✅ Completion modes (PopupCompletion, InlineCompletion, UnfilteredPopupCompletion)
- ✅ Text and placeholder handling
- ✅ Multiple suggestions and special characters
- ✅ Duplicates and edge cases

**Statistics :**
- **Tests :** 17
- **Pass :** 17
- **Skip :** 0
- **Coverage :** ~85%

### PasswordInput
**File :** `test_input/test_password_input.py`  
**Tests :** 35 tests

Password field with strength indicator.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (password, show_strength, strength_bar_height, show_icon, hide_icon, icon_size)
- ✅ Methods (toggle_password, update_strength)
- ✅ Signals (strengthChanged, iconClicked)
- ✅ Password and icon size validation
- ✅ Multiple instances and dynamic changes
- ✅ Special characters and large passwords

**Utility functions tested :**
- ✅ `password_strength()` - Calculates password strength
- ✅ `get_strength_color()` - Colors based on strength
- ✅ `colorize_pixmap()` - Colors icons
- ✅ `load_icon_from_source()` - Loads icons from various sources

**Statistics :**
- **Tests :** 35
- **Pass :** 35
- **Skip :** 0
- **Coverage :** ~85%

### SearchInput
**File :** `test_input/test_search_input.py`  
**Tests :** 20 tests

Search field with history and integrated icons.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (search_icon, icon_position, clear_button, max_history)
- ✅ History handling (add, clear, set, trim)
- ✅ Icon and position handling
- ✅ Parameter validation
- ✅ Text and placeholder handling
- ✅ Signals (searchSubmitted)
- ✅ Large history and special characters
- ✅ Edge cases and validation

**Statistics :**
- **Tests :** 20
- **Pass :** 20
- **Skip :** 0
- **Coverage :** ~80%

### TabReplaceTextEdit
**File :** `test_input/test_tab_replace_textedit.py`  
**Tests :** 25 tests

Text editor with automatic tab replacement.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (tab_replacement, sanitize_on_paste, remove_empty_lines, preserve_whitespace)
- ✅ sanitize_text method with different cases
- ✅ Custom tab replacement
- ✅ Suppression/preservation of empty lines
- ✅ Preservation of whitespace
- ✅ Complex cases and mixed content
- ✅ Special characters and Unicode
- ✅ Edge cases (empty strings, multiple tabs)
- ✅ Text and property type handling
- ✅ Multiple instances and dynamic changes
- ✅ Large text and special replacement strings

**Statistics :**
- **Tests :** 25
- **Pass :** 25
- **Skip :** 0
- **Coverage :** ~90%

## 🏷️ Label Tests

### ClickableTagLabel
**File :** `test_label/test_clickable_tag_label.py`

Clickable tag with toggleable state.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (name, enabled, status_color, min_width, min_height)
- ✅ Signals (clicked, toggle_keyword, stateChanged)
- ✅ State handling (enabled/disabled)
- ✅ Customizable status colors
- ✅ Configurable minimum dimensions

### FramedLabel
**File :** `test_label/test_framed_label.py`

Framed label for advanced styling.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (text, alignment, min_width, min_height)
- ✅ Signal (textChanged)
- ✅ Text alignment
- ✅ Configurable minimum dimensions

### HoverLabel
**File :** `test_label/test_hover_label.py`

Label with icon on hover.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (opacity, hover_icon, icon_size, icon_color, icon_padding, icon_enabled)
- ✅ Signal (hoverIconClicked)
- ✅ Hover icon handling
- ✅ Opacity and dynamic/static activation

### IndicatorLabel
**File :** `test_label/test_indicator_label.py`

Status indicator with colored LED.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (status, status_map)
- ✅ Signal (statusChanged)
- ✅ Customizable status map
- ✅ Intuitive interface

## 🔧 Misc Tests

### CircularTimer
**File :** `test_misc/test_circular_timer.py`

Circular animated timer with complete customization.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (duration, ring_color, node_color, ring_width_mode, pen_width, loop)
- ✅ Signals (timerReset, clicked, cycleCompleted)
- ✅ Circular animated timer with visual progression
- ✅ Customizable colors for ring and node
- ✅ Optional loop mode

### OptionSelector
**File :** `test_misc/test_option_selector.py`

Modern option selector with animation and interface.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (options, current_value, current_value_id)
- ✅ Signals (valueChanged, valueIdChanged)
- ✅ Modern option selector with animation
- ✅ Modern and intuitive interface

### ToggleIcon
**File :** `test_misc/test_toggle_icon.py`

Toggleable icon with open/closed states.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (opened_icon, closed_icon, state, icon_size, icon_color)
- ✅ Signals (stateChanged, clicked)
- ✅ Toggleable icon between two states
- ✅ Customizable colors

### ToggleSwitch
**File :** `test_misc/test_toggle_switch.py`

Modern toggle switch with sliding animation.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (checked, width, height, animation)
- ✅ Signal (toggled)
- ✅ Modern toggle switch with animation
- ✅ Customizable colors

### DraggableList
**File :** `test_misc/test_draggable_list.py`

Reorderable list with drag & drop and deletion via HoverLabel.

**Covered tests :**
- ✅ Creation with default and custom parameters
- ✅ Properties (items, compact, min_width, icon_color)
- ✅ Signals (itemMoved, itemRemoved, itemAdded, itemClicked, orderChanged)
- ✅ Methods (add_item, remove_item, clear_items, move_item, get_item_position, refresh_style)
- ✅ Reorderable list by drag & drop
- ✅ Deletion of items via HoverLabel

## 🚀 Execution of Tests

### Installation of Dependencies

```bash
pip install -e ".[dev]"
```

### Quick Launch

```bash
# All tests
python run_tests.py

# Only unit tests
python run_tests.py --type unit

# Tests with coverage
python run_tests.py --coverage

# Verbose mode
python run_tests.py --verbose

# Exclude slow tests
python run_tests.py --fast
```

### With pytest directly

```bash
# Unit tests
pytest -m unit

# Integration tests
pytest -m integration

# With coverage
pytest --cov=ezqt_widgets --cov-report=html

# Specific tests
pytest tests/unit/test_button/test_icon_button.py
```

## 🧪 Types of Tests

### Unit Tests (`@pytest.mark.unit`)

- **Objective** : Test each component individually
- **Scope** : Functions, classes, methods
- **Isolation** : Use of mocks and fixtures
- **Speed** : Fast (< 1 second per test)

### Integration Tests (`@pytest.mark.integration`)

- **Objective** : Test interaction between components
- **Scope** : Widgets in an interface
- **Isolation** : Complete Qt interface
- **Speed** : Slower (1-5 seconds per test)

### Slow Tests (`@pytest.mark.slow`)

- **Objective** : Tests requiring time (network, files)
- **Exclusion** : `pytest -m "not slow"`

## 🔧 Available Fixtures

### `qt_application`
Shared QApplication instance for all tests.

### `qt_widget_cleanup`
Automatically cleans up widgets after each test.

### `wait_for_signal`
Waits for a Qt signal to be emitted with a timeout.

### `mock_icon_path`
Temporary icon file path.

### `mock_svg_path`
Temporary SVG file path.

## 📊 Code Coverage

Coverage is generated automatically with:
- Terminal report: `--cov-report=term-missing`
- HTML report: `--cov-report=html:htmlcov`
- XML report: `--cov-report=xml`

## 🎯 Best Practices

### 1. Test Naming
```python
def test_widget_creation_default():
    """Test of creation with default parameters."""
    pass

def test_widget_property_setter():
    """Test of property setter."""
    pass
```

### 2. Organization of Test Classes
```python
class TestWidgetName:
    """Tests for the WidgetName class."""
    
    def test_method_name_scenario(self):
        """Test of the method in a specific scenario."""
        pass
```

### 3. Use of Fixtures
```python
def test_widget_creation(self, qt_widget_cleanup, mock_icon_path):
    """Test with fixtures."""
    widget = Widget(icon=mock_icon_path)
    assert widget.icon is not None
```

### 4. Signal Tests
```python
def test_signal_emission(self, qt_widget_cleanup, wait_for_signal):
    """Test of signal emission."""
    widget = Widget()
    assert wait_for_signal(widget.someSignal)
```

## 🐛 Debugging

### Debug Mode
```bash
pytest --pdb
```

### Displaying Prints
```bash
pytest -s
```

### Specific Tests
```bash
pytest -k "test_icon_button"
```

## 📈 Metrics

- **Target Coverage** : > 90%
- **Execution Time** : < 30 seconds for all tests
- **Reliability** : 0% flaky tests

## 🔄 Continuous Integration

Tests are automatically executed:
- On each commit
- Before each merge
- Before each release

## 📝 Adding New Tests

1. Create the test file in the correct directory
2. Follow the naming convention
3. Use appropriate fixtures
4. Add necessary markers
5. Check coverage

## 🚨 Common Issues

### QApplication already created
```python
# Use the qt_application fixture
def test_widget(app):
    pass
```

### Tests failing randomly
- Add delays with `QTimer`
- Use `wait_for_signal`
- Check test isolation

### Memory leaks
- Use `qt_widget_cleanup`
- Explicitly delete widgets
- Check signal connections

## 📊 Global Statistics

| Category | Widgets | Tests | Coverage |
|-----------|---------|-------|------------|
| Button | 3 | 59 | ~50% |
| Input | 4 | 97 | ~85% |
| Label | 4 | ~40 | ~80% |
| Misc | 5 | ~50 | ~80% |
| **Total** | **16** | **~246** | **~75%** |

---

**Documentation of EzQt Widgets Tests** - Complete guide for running and maintaining tests. 