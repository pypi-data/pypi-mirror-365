# Complete Widget Documentation - EzQt Widgets

## Overview

This documentation presents all available widgets in the EzQt library, organized by functional modules. Each widget is designed to provide specialized functionality while maintaining API and design consistency.

## Table of Contents

- [🎛️ Button Module](#️-button-module-ezqt_widgetsbutton)
  - [DateButton](#datebutton)
  - [IconButton](#iconbutton)
  - [LoaderButton](#loaderbutton)
- [⌨️ Input Module](#️-input-module-ezqt_widgetsinput)
  - [AutoCompleteInput](#autocompleteinput)
  - [PasswordInput](#passwordinput)
  - [SearchInput](#searchinput)
  - [TabReplaceTextEdit](#tabreplacetextedit)
- [🏷️ Label Module](#️-label-module-ezqt_widgetslabel)
  - [ClickableTagLabel](#clickabletaglabel)
  - [FramedLabel](#framedlabel)
  - [HoverLabel](#hoverlabel)
  - [IndicatorLabel](#indicatorlabel)
- [🔧 Misc Module](#️-misc-module-ezqt_widgetsmisc)
  - [CircularTimer](#circulartimer)
  - [DraggableList](#draggablelist)
  - [OptionSelector](#optionselector)
  - [ToggleIcon](#toggleicon)
  - [ToggleSwitch](#toggleswitch)

## Module Structure

### 🎛️ Button Module (`ezqt_widgets.button`)
Specialized button widgets with advanced functionality.

### ⌨️ Input Module (`ezqt_widgets.input`)
Data input widgets with validation and extended functionality.

### 🏷️ Label Module (`ezqt_widgets.label`)
Interactive label widgets and visual indicators.

### 🔧 Misc Module (`ezqt_widgets.misc`)
Utility widgets and specialized components.

## Widgets by Module

### 🎛️ Button Widgets

#### DateButton 
**File :** `button/date_button.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#datebutton)

Date picker button widget with integrated calendar.

**Features :**
- Date selection via popup calendar
- Customizable date format
- Configurable placeholder and icon
- Date validation
- Date change signals

**Main parameters :**
- `date_format` : Date display format
- `placeholder` : Help text
- `show_calendar_icon` : Show calendar icon
- `min_width/min_height` : Minimum dimensions

**Signals :**
- `dateChanged(QDate)` : Date changed
- `dateSelected(QDate)` : Date selected

#### IconButton
**File :** `button/icon_button.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#iconbutton)

Button with icon support and optional text.

**Features :**
- Icon support from various sources
- Optional text with configurable visibility
- Customizable size and spacing
- Hover and click effects
- Icon colorization

**Main parameters :**
- `icon` : Icon (QIcon, path, URL, SVG)
- `text` : Button text
- `icon_size` : Icon size
- `text_visible` : Text visibility
- `spacing` : Icon-text spacing

**Signals :**
- `iconChanged(QIcon)` : Icon changed
- `textChanged(str)` : Text changed

#### LoaderButton
**File :** `button/loader_button.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#loaderbutton)

Button with integrated loading animation.

**Features :**
- Loading, success, and error states
- Animated spinner during loading
- Configurable texts and icons by state
- Smooth transitions between states
- Auto-reset configurable

**Main parameters :**
- `loading_text` : Text during loading
- `loading_icon` : Loading icon
- `success_icon` : Success icon
- `error_icon` : Error icon
- `animation_speed` : Animation speed

**Signals :**
- `loadingStarted()` : Loading started
- `loadingFinished()` : Loading finished
- `loadingFailed(str)` : Loading failed

### ⌨️ Input Widgets

#### AutoCompleteInput
**File :** `input/auto_complete_input.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#autocompleteinput)

Text field with autocomplete.

**Features :**
- Autocomplete suggestions
- Case-sensitive configurable
- Filtering and completion modes
- Intuitive user interface

**Main parameters :**
- `suggestions` : List of suggestions
- `case_sensitive` : Case sensitivity
- `filter_mode` : Filtering mode
- `completion_mode` : Completion mode

**Properties :**
- `suggestions` : List of suggestions
- `case_sensitive` : Case sensitivity
- `filter_mode` : Filtering mode
- `completion_mode` : Completion mode

#### PasswordInput
**File :** `input/password_input.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#passwordinput)

Password field with strength indicator.

**Features :**
- Password mode with masking
- Password strength bar
- Right-side visibility icon
- Customizable icons
- Animated and colored strength bar

**Main parameters :**
- `show_strength` : Show strength bar
- `strength_bar_height` : Strength bar height
- `show_icon` : Display icon
- `hide_icon` : Hide icon
- `icon_size` : Icon sizes

**Signals :**
- `strengthChanged(int)` : Password strength changed
- `iconClicked()` : Icon clicked

#### SearchInput
**File :** `input/search_input.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#searchinput)

Search field with history.

**Features :**
- Search history
- Navigation in history
- Optional search icon
- Clear button
- Submission signal

**Main parameters :**
- `search_icon` : Search icon
- `icon_position` : Icon position
- `clear_button` : Show clear button
- `max_history` : Maximum history size

**Signals :**
- `searchSubmitted(str)` : Search submitted

#### TabReplaceTextEdit
**File :** `input/tab_replace_textedit.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#tabreplacetextedit)

Text editor with tab replacement.

**Features :**
- Automatic tab replacement
- Text cleaning on paste
- Removal of empty lines
- Preservation of whitespace

**Main parameters :**
- `tab_replacement` : Tab replacement character
- `sanitize_on_paste` : Sanitize pasted text
- `remove_empty_lines` : Remove empty lines
- `preserve_whitespace` : Preserve whitespace

### 🏷️ Label Widgets

#### ClickableTagLabel
**File :** `label/clickable_tag_label.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#clickabletaglabel)

Clickable tag with toggleable state.

**Features :**
- Clickable tag with enabled/disabled state
- Customizable status color
- Click and state change signals
- QSS-friendly interface
- Configurable minimum dimensions

**Main parameters :**
- `name` : Tag name
- `enabled` : Initial state
- `status_color` : Status color
- `min_width/min_height` : Minimum dimensions

**Signals :**
- `clicked()` : Tag clicked
- `toggle_keyword(str)` : State changed
- `stateChanged(bool)` : State changed

#### FramedLabel
**File :** `label/framed_label.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#framedlabel)

Framed label for advanced styling.

**Features :**
- Label based on QFrame for more flexibility
- Access based on text and alignment properties
- Text change signal
- Custom stylesheet injection
- Configurable minimum dimensions

**Main parameters :**
- `text` : Label text
- `alignment` : Text alignment
- `min_width/min_height` : Minimum dimensions

**Signals :**
- `textChanged(str)` : Text changed

#### HoverLabel
**File :** `label/hover_label.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#hoverlabel)

Label with icon on hover.

**Features :**
- Interactive label with floating icon on hover
- Click signal on hover icon
- Cursor changes
- Dynamic icon activation/deactivation
- Multiple icon sources

**Main parameters :**
- `opacity` : Hover icon opacity
- `hover_icon` : Hover icon
- `icon_size` : Icon size
- `icon_color` : Icon color
- `icon_padding` : Icon padding
- `icon_enabled` : Enabled icon

**Signals :**
- `hoverIconClicked()` : Hover icon clicked

#### IndicatorLabel
**File :** `label/indicator_label.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#indicatorlabel)

Status indicator with colored LED.

**Features :**
- Dynamic status indicator
- Customizable status card
- Access based on status properties
- Status change signal
- Intuitive interface

**Main parameters :**
- `status_map` : Status map
- `initial_status` : Initial status

**Properties :**
- `status` : Current status

**Signals :**
- `statusChanged(str)` : Status changed

### 🔧 Misc Widgets

#### CircularTimer
**File :** `misc/circular_timer.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#circulartimer)

Animated circular timer with complete customization.

**Features :**
- Animated circular timer with visual progress
- Customizable colors for ring and node
- Optional loop mode
- Signals for cycle and click events
- Configurable line width

**Main parameters :**
- `duration` : Total duration in milliseconds
- `ring_color` : Ring color
- `node_color` : Node color
- `ring_width_mode` : Width mode
- `pen_width` : Line width
- `loop` : Loop mode

**Signals :**
- `timerReset()` : Timer reset
- `clicked()` : Widget clicked
- `cycleCompleted()` : Cycle completed

#### OptionSelector
**File :** `misc/option_selector.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#optionselector)

Modern option selector with animation and interface.

**Features :**
- Smooth option selection
- Single selection mode
- Configurable orientation (horizontal/vertical)
- Customizable animation
- Value change signals

**Main parameters :**
- `options` : List of options
- `default_id` : Default option ID
- `orientation` : Selector orientation
- `animation_duration` : Animation duration

**Signals :**
- `clicked()` : Selector clicked
- `valueChanged(str)` : Value changed
- `valueIdChanged(int)` : Value ID changed

#### ToggleIcon
**File :** `misc/toggle_icon.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#toggleicon)

Toggleable icon to represent open/closed states.

**Features :**
- Toggleable icon between two states
- Customizable colors
- Multiple icon sources (file, URL, SVG)
- State change signals
- Clickable interface

**Main parameters :**
- `opened_icon` : Icon for open state
- `closed_icon` : Icon for closed state
- `state` : Initial state
- `icon_size` : Icon size
- `icon_color` : Icon color

**Signals :**
- `stateChanged(str)` : State changed
- `clicked()` : Icon clicked

#### ToggleSwitch
**File :** `misc/toggle_switch.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#toggleswitch)

Modern switch with sliding animation.

**Features :**
- Modern switch with animation
- Customizable colors
- Configurable size
- Smooth animation
- State change signal

**Main parameters :**
- `checked` : Initial state
- `width` : Switch width
- `height` : Switch height
- `animation` : Enable animation

**Signals :**
- `toggled(bool)` : State changed

#### DraggableList
**File :** `misc/draggable_list.py`  
**Style Guide :** [See QSS styles](STYLE_GUIDE.md#draggablelist)

Reorderable list with drag & drop and removal via HoverLabel.

**Features :**
- Reorderable list by drag & drop
- Removal of items via HoverLabel (delete icon on hover)
- Consistent interface with HoverLabel for all items
- Signals for reordering and removal
- Fluid and intuitive interface
- Personalizable appearances
- Automatic item order management
- Compact mode for vertical space saving
- Adaptive width based on actual content
- Advanced sizeHint for optimal size

**Main parameters :**
- `items` : Initial list of items
- `allow_drag_drop` : Allow drag & drop
- `allow_remove` : Allow item removal
- `max_height` : Maximum widget height
- `min_width` : Minimum widget width (default: 150)
- `compact` : Compact mode to reduce height
- `icon_color` : Icon color for deletion

**Signals :**
- `itemMoved(str, int, int)` : Item moved (item_id, old_position, new_position)
- `itemRemoved(str, int)` : Item removed (item_id, position)
- `itemAdded(str, int)` : Item added (item_id, position)
- `itemClicked(str)` : Item clicked (item_id)
- `orderChanged(List[str])` : Order changed

**Methods :**
- `add_item(item_id, text=None)` : Add an item
- `remove_item(item_id)` : Remove an item
- `clear_items()` : Clear the list
- `move_item(item_id, new_position)` : Move an item
- `get_item_position(item_id)` : Get item position
- `refresh_style()` : Refresh widget style

**Properties :**
- `items` : List of items in current order
- `compact` : Compact mode
- `min_width` : Minimum widget width
- `icon_color` : Icon color for deletion

## Utility Functions

### Button Module
- `format_date(date, format_str)` : Format a date
- `parse_date(date_str, format_str)` : Parse a date
- `get_calendar_icon()` : Get calendar icon
- `colorize_pixmap(pixmap, color, opacity)` : Colorize a pixmap
- `load_icon_from_source(source)` : Load an icon

### Input Module
- `password_strength(password)` : Calculate password strength
- `get_strength_color(strength)` : Get strength color
- `colorize_pixmap(pixmap, color, opacity)` : Colorize a pixmap
- `load_icon_from_source(source)` : Load an icon

### Label Module
- `colorize_pixmap(pixmap, color, opacity)` : Colorize a pixmap
- `load_icon_from_source(source)` : Load an icon

### Misc Module
- `parse_css_color(color_str)` : Parse a CSS color

## Example Integrations

### Complete Configuration Interface

```python
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from ezqt_widgets.button import DateButton, IconButton, LoaderButton
from ezqt_widgets.input import AutoCompleteInput, PasswordInput, SearchInput
from ezqt_widgets.label import ClickableTagLabel, FramedLabel, HoverLabel, IndicatorLabel
from ezqt_widgets.misc import CircularTimer, OptionSelector, ToggleIcon, ToggleSwitch, DraggableList

app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

# Section des boutons
button_layout = QHBoxLayout()
date_button = DateButton(placeholder="Sélectionner une date")
icon_button = IconButton(text="Mon Bouton", icon="📝")
loader_button = LoaderButton(text="Charger", loading_text="Chargement...")
button_layout.addWidget(date_button)
button_layout.addWidget(icon_button)
button_layout.addWidget(loader_button)
layout.addLayout(button_layout)

# Section des entrées
input_layout = QHBoxLayout()
auto_input = AutoCompleteInput(suggestions=["Option 1", "Option 2", "Option 3"])
password_input = PasswordInput(show_strength=True)
search_input = SearchInput()
input_layout.addWidget(auto_input)
input_layout.addWidget(password_input)
input_layout.addWidget(search_input)
layout.addLayout(input_layout)

# Section des labels
label_layout = QHBoxLayout()
tag_label = ClickableTagLabel(name="Tag", enabled=True)
framed_label = FramedLabel(text="Label encadré")
hover_label = HoverLabel(text="Survolez-moi", icon="ℹ️")
indicator_label = IndicatorLabel(
    status_map={
        "ok": {"text": "OK", "state": "ok", "color": "#28a745"},
        "error": {"text": "Erreur", "state": "error", "color": "#dc3545"}
    },
    initial_status="ok"
)
label_layout.addWidget(tag_label)
label_layout.addWidget(framed_label)
label_layout.addWidget(hover_label)
label_layout.addWidget(indicator_label)
layout.addLayout(label_layout)

# Section des widgets divers
misc_layout = QHBoxLayout()
timer = CircularTimer(duration=5000, loop=True)
selector = OptionSelector(options=["A", "B", "C"])
toggle = ToggleIcon(opened_icon="📂", closed_icon="📁")
switch = ToggleSwitch(checked=True)
draggable_list = DraggableList(items=["Item 1", "Item 2", "Item 3"], compact=True)
misc_layout.addWidget(timer)
misc_layout.addWidget(selector)
misc_layout.addWidget(toggle)
misc_layout.addWidget(switch)
misc_layout.addWidget(item_list)
layout.addLayout(misc_layout)

window.setLayout(layout)
window.show()
app.exec()
```

### Interactive Dashboard

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
from ezqt_widgets.misc import CircularTimer, DraggableList, ToggleSwitch
from ezqt_widgets.label import IndicatorLabel

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard - EzQt Widgets")
        self.setGeometry(100, 100, 1000, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Panneau de contrôle
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        
        # Timer de session
        self.session_timer = CircularTimer(
            duration=3600000,  # 1 heure
            ring_color="#007bff",
            loop=True
        )
        control_layout.addWidget(QLabel("Temps de session:"))
        control_layout.addWidget(self.session_timer)
        
        # Indicateurs de statut
        self.service_status = IndicatorLabel(
            status_map={
                "running": {"text": "Service actif", "state": "ok", "color": "#28a745"},
                "stopped": {"text": "Service arrêté", "state": "error", "color": "#dc3545"}
            },
            initial_status="running"
        )
        control_layout.addWidget(QLabel("Statut du service:"))
        control_layout.addWidget(self.service_status)
        
        # Commutateurs
        self.auto_save = ToggleSwitch(checked=True)
        control_layout.addWidget(QLabel("Sauvegarde automatique:"))
        control_layout.addWidget(self.auto_save)
        
        self.notifications = ToggleSwitch(checked=False)
        control_layout.addWidget(QLabel("Notifications:"))
        control_layout.addWidget(self.notifications)
        
        layout.addWidget(control_panel)
        
        # Panneau de tâches
        task_panel = QWidget()
        task_layout = QVBoxLayout(task_panel)
        
        self.task_list = DraggableList(
            items=["Analyze data", "Generate report", "Send notifications"],
            compact=True,
            icon_color="#28a745",
            max_height=300
        )
        
        # Connect signals
        self.task_list.itemMoved.connect(self._on_task_moved)
        self.task_list.itemRemoved.connect(self._on_task_removed)
        self.task_list.orderChanged.connect(self._on_order_changed)
        
        task_layout.addWidget(QLabel("Current tasks:"))
        task_layout.addWidget(self.task_list)
        
        layout.addWidget(task_panel)
        
        # Start timer
        self.session_timer.start()
    
    def _on_task_moved(self, item_id, old_pos, new_pos):
        print(f"Task moved: '{item_id}' from {old_pos} to {new_pos}")
    
    def _on_task_removed(self, item_id, position):
        print(f"Task removed: '{item_id}' at position {position}")
    
    def _on_order_changed(self, new_order):
        print(f"New task order: {new_order}")

if __name__ == "__main__":
    app = QApplication([])
    dashboard = Dashboard()
    dashboard.show()
    app.exec()
```

## Best Practices

### 🎯 Widget Selection
1. **Buttons** : For user actions (DateButton for dates, IconButton for actions with icons, LoaderButton for asynchronous operations)
2. **Inputs** : For data entry (AutoCompleteInput for suggestions, PasswordInput for passwords, SearchInput for search)
3. **Labels** : For displaying information (ClickableTagLabel for tags, HoverLabel for contextual actions, IndicatorLabel for statuses)
4. **Misc Widgets** : For specialized functionality (CircularTimer for progress, DraggableList for reorderable lists)

### 🎨 Personalization
```python
# Consistent style for all widgets
widget.setStyleSheet("""
    QWidget {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 4px;
        padding: 8px;
    }
    
    QWidget:hover {
        background-color: #e9ecef;
        border-color: #adb5bd;
    }
    
    QWidget:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
    }
""")
```

### 🔧 Event Handling
```python
# Connect signals for all widgets
date_button.dateChanged.connect(lambda date: print(f"Date selected: {date}"))
icon_button.clicked.connect(lambda: print("Button clicked"))
loader_button.loadingStarted.connect(lambda: print("Loading started"))
auto_input.textChanged.connect(lambda text: print(f"Text entered: {text}"))
password_input.strengthChanged.connect(lambda strength: print(f"Strength: {strength}"))
tag_label.clicked.connect(lambda: print("Tag clicked"))
hover_label.hoverIconClicked.connect(lambda: print("Hover icon clicked"))
indicator_label.statusChanged.connect(lambda status: print(f"Status: {status}"))
timer.cycleCompleted.connect(lambda: print("Timer completed"))
selector.valueChanged.connect(lambda value: print(f"Selection: {value}"))
toggle.stateChanged.connect(lambda state: print(f"State: {state}"))
switch.toggled.connect(lambda checked: print(f"Switch: {checked}"))
item_list.itemMoved.connect(lambda item_id, old_pos, new_pos: print(f"Move: {item_id}"))
```

### 📱 Responsive Design
```python
# Use flexible layouts
layout = QHBoxLayout()  # or QVBoxLayout depending on orientation
layout.addWidget(widget1, 1)  # Stretch factor 1
layout.addWidget(widget2, 2)  # Stretch factor 2 (more space)
layout.addWidget(widget3, 1)  # Stretch factor 1
```

---

**EzQt Widgets** - Complete collection of specialized Qt widgets for modern and intuitive interfaces. 