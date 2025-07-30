# EzQt Widgets Examples

This directory contains comprehensive usage examples for all available widgets in the EzQt Widgets library. Each example demonstrates real-world usage scenarios and best practices.

## 📁 Example Files

### 🚀 Main Launcher
- **`run_all_examples.py`** - Main script to launch all examples with a graphical interface

### 🎯 Examples by Category

| Category | File | Widgets | Description |
|----------|------|---------|-------------|
| **Buttons** | `button_example.py` | 3 widgets | Date selection, icon buttons, and loading states |
| **Inputs** | `input_example.py` | 4 widgets | Text fields, autocomplete, search, and password inputs |
| **Labels** | `label_example.py` | 4 widgets | Interactive labels, indicators, and hover effects |
| **Misc** | `misc_example.py` | 5 widgets | Timers, selectors, toggles, and draggable lists |

## 🎯 Widget Examples Overview

### 🎛️ Button Widgets (`button_example.py`)

| Widget | Features Demonstrated | Use Cases |
|--------|----------------------|-----------|
| **DateButton** | Date picker with calendar popup, format customization | Date selection forms, scheduling interfaces |
| **IconButton** | Icon support, text visibility, colorization | Action buttons, toolbar items, navigation |
| **LoaderButton** | Loading states, animations, success/error feedback | Form submissions, data processing, async operations |

### ⌨️ Input Widgets (`input_example.py`)

| Widget | Features Demonstrated | Use Cases |
|--------|----------------------|-----------|
| **AutoCompleteInput** | Suggestion filtering, case sensitivity, completion modes | Search forms, data entry, user input assistance |
| **PasswordInput** | Password masking, strength indicator, visibility toggle | Login forms, security settings, user registration |
| **SearchInput** | Search history, delayed search, clear functionality | Search interfaces, filtering, data exploration |
| **TabReplaceTextEdit** | Tab replacement, text sanitization, paste handling | Code editors, text processing, data cleaning |

### 🏷️ Label Widgets (`label_example.py`)

| Widget | Features Demonstrated | Use Cases |
|--------|----------------------|-----------|
| **ClickableTagLabel** | Toggle states, status colors, click events | Tag systems, category selection, status indicators |
| **FramedLabel** | Custom borders, text alignment, styling | Information display, section headers, decorative elements |
| **HoverLabel** | Hover effects, icon display, interactive feedback | Contextual actions, help tooltips, navigation hints |
| **IndicatorLabel** | Status mapping, color coding, dynamic updates | System status, process indicators, health monitoring |

### 🔧 Misc Widgets (`misc_example.py`)

| Widget | Features Demonstrated | Use Cases |
|--------|----------------------|-----------|
| **CircularTimer** | Visual progress, loop mode, click interactions | Progress tracking, countdown timers, activity indicators |
| **DraggableList** | Drag & drop reordering, item management, hover actions | Task lists, playlist management, priority ordering |
| **OptionSelector** | Smooth animations, orientation options, value selection | Settings panels, preference selection, mode switching |
| **ToggleIcon** | State switching, icon customization, click handling | Expand/collapse controls, mode toggles, status switches |
| **ToggleSwitch** | Modern design, smooth animations, state management | Settings toggles, feature enable/disable, binary choices |

## 🚀 Quick Start

### Launch All Examples
```bash
# Launch the main launcher with GUI
python run_all_examples.py

# Or run specific examples directly
python button_example.py
python input_example.py
python label_example.py
python misc_example.py
```

### Launcher Features
- **Graphical Interface** - Easy example selection and navigation
- **Individual Launch** - Run specific examples or categories
- **Batch Execution** - Launch all examples sequentially
- **Error Handling** - Informative error messages and troubleshooting

## 🎨 Example Characteristics

### User Interface
- **Modern Design** - Custom CSS styling with consistent theming
- **Organized Layouts** - Widgets grouped by category and functionality
- **Interactive Feedback** - Visual responses to user interactions
- **Integrated Documentation** - Inline comments and usage hints

### Demonstrated Features
- **Widget Configuration** - Various parameter combinations and settings
- **Event Handling** - Signal connections and callback implementations
- **Animations** - Smooth transitions and visual effects
- **State Management** - Multiple states and dynamic updates
- **Widget Integration** - Combining multiple widgets in practical scenarios

### Code Quality
- **Detailed Comments** - Comprehensive documentation in English
- **Modular Structure** - Reusable and maintainable code patterns
- **Error Handling** - Robust error management and validation
- **Best Practices** - PySide6 programming standards and conventions

## 📋 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.6+ | Runtime environment |
| **PySide6** | Latest | Qt framework for Python |
| **EzQt Widgets** | Latest | Custom widget library |

## 🔧 Installation

```bash
# Install dependencies
pip install PySide6

# Install EzQt Widgets (if not already installed)
pip install ezqt_widgets

# For development installation
pip install -e ".[dev]"
```

## 📖 Learning Path

Each example is designed to:

1. **Demonstrate** core widget functionality and capabilities
2. **Showcase** different configuration options and parameters
3. **Illustrate** typical use cases and integration patterns
4. **Provide** reusable reference code for your projects

### Recommended Learning Order
1. **Start with** `button_example.py` for basic interactions
2. **Continue with** `input_example.py` for data entry patterns
3. **Explore** `label_example.py` for display and feedback
4. **Finish with** `misc_example.py` for advanced functionality

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution | Prevention |
|-------|----------|------------|
| **ImportError** | Verify EzQt Widgets installation | Use `pip install ezqt_widgets` |
| **ModuleNotFoundError** | Check PySide6 installation | Install with `pip install PySide6` |
| **Style Errors** | Verify PySide6 version compatibility | Use latest stable version |
| **Widget Not Displaying** | Check Qt application initialization | Ensure QApplication is created |

### Support Resources
- **Main Documentation** - Complete API reference and guides
- **Console Logs** - Check for detailed error messages
- **Simple Examples** - Start with basic widget usage
- **GitHub Issues** - Report bugs and request features

## 📝 Version Notes

| Version | Compatibility | Updates | Status |
|---------|---------------|---------|--------|
| **2.1.1** | Latest EzQt Widgets | All widgets included and functional | ✅ Current |
| **2.1.0** | PySide6 6.0+ | Modern design and responsive interface | ✅ Stable |
| **2.0.0** | Python 3.6+ | Complete rewrite with English documentation | ✅ Stable |

## 🔗 Related Documentation

- **[📖 API Documentation](../api/WIDGETS_DOCUMENTATION.md)** - Complete widget reference
- **[🎨 Style Guide](../api/STYLE_GUIDE.md)** - QSS customization examples
- **[🧪 Test Examples](../tests/TESTS_DOCUMENTATION.md)** - Testing patterns and fixtures
- **[📋 Main README](../../README.md)** - Project overview and quick start

---

**Developed with ❤️ for EzQt Widgets** - Making Qt development easier and more enjoyable. 