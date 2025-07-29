# EzQt-Widgets

## Description

EzQt-Widgets is a collection of custom Qt widgets designed to enhance applications built with [EzQt-App](https://pypi.org/project/EzQt-App/).
This module provides advanced, reusable, and stylish graphical components, making it easier to develop modern and user-friendly interfaces.

## Features

- Ready-to-use custom widgets for PySide6/Qt applications
- Consistent design and easy integration with EzQt-App projects
- Modular and extensible components (buttons, labels, loaders, etc.)
- Facilitates the creation of modern, ergonomic UIs

## Installation

Install via pip (recommended):

```bash
pip install ezqt_widgets
```

Or install locally:

```bash
git clone https://github.com/neuraaak/ezqt_widgets.git
cd ezqt_widgets
pip install .
```

## Dependencies

- PySide6 >= 6.9.1 (installed automatically)
- Compatible with Python 3.9 to 3.12

## Usage Example

```python
from ezqt_widgets.widgets.extended.icon_button import IconButton
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication([])
window = QMainWindow()

# Example: Add a custom IconButton to your window
icon_button = IconButton(icon_path="path/to/icon.png", text="Click Me")
window.setCentralWidget(icon_button)

window.show()
app.exec()
```

## Integration with EzQt-App

EzQt-Widgets is designed to be seamlessly integrated into any EzQt-App project.
Simply import the desired widgets and use them as you would with standard Qt widgets.

## Styling

For consistent styling across your application, refer to the [STYLE_GUIDE.md](STYLE_GUIDE.md) file.
This guide provides QSS (Qt Style Sheets) examples and best practices for all custom widgets in this library.

## Changelog

### Version 2.0.0
- **Major Update**: Upgraded to PySide6 6.9.1+
- **Improved Stability**: Better memory management and crash fixes
- **Enhanced Typing**: Improved type annotations and IDE support
- **Platform Support**: Extended platform compatibility
- **Development Status**: Moved from Alpha to Beta

### Migration from 1.x
This is a major version update that requires PySide6 6.9.1 or higher. Most existing code should work without changes, but we recommend testing your applications thoroughly.

## License

MIT License
