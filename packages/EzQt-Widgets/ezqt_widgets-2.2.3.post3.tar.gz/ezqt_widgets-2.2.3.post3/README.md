# 🎨 EzQt Widgets

[![Repository](https://img.shields.io/badge/Repository-GitHub-blue?style=for-the-badge&logo=github)](https://github.com/neuraaak/ezqt_widgets)
[![PyPI](https://img.shields.io/badge/PyPI-ezqt_widgets-green?style=for-the-badge&logo=pypi)](https://pypi.org/project/EzQt-Widgets/)
[![Tests](https://img.shields.io/badge/Tests-254%2F262%20passing-green?style=for-the-badge&logo=pytest)](https://github.com/neuraaak/ezqt_widgets/actions)

A collection of custom and reusable Qt widgets for PySide6, designed to simplify the development of modern and intuitive graphical interfaces.

## 📦 **Installation**

```bash
pip install ezqt_widgets
```

## 🚀 **Quick Start**

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from ezqt_widgets.button import DateButton
from ezqt_widgets.input import PasswordInput
from ezqt_widgets.misc import ToggleSwitch

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Create widgets
date_button = DateButton(placeholder="Select a date")
password_input = PasswordInput(show_strength=True)
toggle = ToggleSwitch(checked=True)

# Add to layout
layout.addWidget(date_button)
layout.addWidget(password_input)
layout.addWidget(toggle)

window.setLayout(layout)
window.show()
app.exec()
```

## 📚 **Documentation**

- **[📖 Complete Documentation](docs/README.md)** - Main documentation guide
- **[🎯 Widgets API](docs/api/WIDGETS_DOCUMENTATION.md)** - Complete documentation of all widgets
- **[🎨 Style Guide](docs/api/STYLE_GUIDE.md)** - QSS customization and best practices
- **[🧪 Tests](docs/tests/README.md)** - Test documentation and execution guide
- **[🖥️ CLI Documentation](docs/cli/README.md)** - Command-line interface guide
- **[📋 Changelog](CHANGELOG.md)** - Version history

## 🎯 **Available Widgets**

### 🎛️ **Buttons (3 widgets)**
- **DateButton** - Date picker with integrated calendar
- **IconButton** - Button with icon support and optional text
- **LoaderButton** - Button with integrated loading animation

### ⌨️ **Inputs (4 widgets)**
- **AutoCompleteInput** - Text field with autocompletion
- **PasswordInput** - Password field with strength indicator
- **SearchInput** - Search field with history
- **TabReplaceTextEdit** - Text editor with tab replacement

### 🏷️ **Labels (4 widgets)**
- **ClickableTagLabel** - Clickable tag with toggle state
- **FramedLabel** - Framed label for advanced styling
- **HoverLabel** - Label with hover icon
- **IndicatorLabel** - Status indicator with colored LED

### 🔧 **Misc (5 widgets)**
- **CircularTimer** - Animated circular timer
- **DraggableList** - List with draggable elements
- **OptionSelector** - Option selector with animation
- **ToggleIcon** - Toggleable icon open/closed
- **ToggleSwitch** - Modern toggle switch with animation

## ✨ **Features**

- **✅ PySide6 Compatibility** - All widgets based on PySide6
- **✅ Type Hints** - Complete type annotation support
- **✅ Qt Signals** - Native integration with Qt signal system
- **✅ QSS Styles** - Complete Qt stylesheet support
- **✅ Accessibility** - Accessibility features support
- **✅ Animations** - Smooth and configurable animations
- **✅ Tests** - Complete test suite (~246 tests, ~75% coverage)

## 🧪 **Tests**

### **Quick Execution**
```bash
# Quick verification
python tests/run_tests.py --type unit

# Tests with coverage
python tests/run_tests.py --coverage

# Or use CLI (after pip install -e ".[dev]")
ezqt test --unit
ezqt test --coverage
```

### **Test Documentation**
- **[🚀 Quick Start Guide](docs/tests/QUICK_START_TESTS.md)** - Quick verification
- **[📖 Complete Documentation](docs/tests/TESTS_DOCUMENTATION.md)** - Detailed guide

### **Statistics**
- **Total** : ~246 tests
- **Coverage** : ~75%
- **Status** : 🟢 **OPERATIONAL**

## 🔧 **Development**

### **Project Structure**
```
ezqt_widgets/
├── README.md                    # This file
├── docs/                        # Documentation
│   ├── README.md               # Documentation index
│   ├── api/                    # API documentation
│   │   ├── README.md          # Navigation guide
│   │   ├── WIDGETS_DOCUMENTATION.md # Complete documentation
│   │   └── STYLE_GUIDE.md     # Style guide
│   └── tests/                  # Test documentation
│       ├── README.md          # Navigation guide
│       ├── TESTS_DOCUMENTATION.md # Complete documentation
│       └── QUICK_START_TESTS.md # Quick start guide
├── tests/                       # Tests
│   ├── run_tests.py           # Test execution script
│   ├── conftest.py            # Pytest configuration
│   └── unit/                  # Unit tests
├── ezqt_widgets/               # Source code
└── pyproject.toml              # Project configuration
```

### **Development Installation**
```bash
git clone https://github.com/your-username/ezqt_widgets.git
cd ezqt_widgets
pip install -e ".[dev]"

# Verify CLI installation
ezqt --version
ezqt info
```

## 📄 **License**

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

**EzQt Widgets** - Simplify the development of modern and intuitive Qt interfaces.
