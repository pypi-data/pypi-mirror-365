# Quick Start Tests - EzQt Widgets

## Quick Verification

### Essential Commands

```bash
# Quick verification
python tests/run_tests.py --type unit

# With coverage
python tests/run_tests.py --coverage

# Verbose mode
python tests/run_tests.py --verbose
```

### Direct pytest Execution

```bash
# Unit tests only
pytest -m unit

# With coverage
pytest --cov=ezqt_widgets --cov-report=html

# Specific test file
pytest tests/unit/test_button/test_icon_button.py -v
```

## Expected Results

### Quick Verification
- **Status** : 🟢 All tests passing
- **Total** : ~246 tests
- **Coverage** : ~75%
- **Duration** : < 30 seconds

### Common Issues

#### QApplication Already Created
```python
# Use the qt_application fixture
def test_widget(qt_application):
    pass
```

#### Random Test Failures
- Add delays with `QTimer`
- Use `wait_for_signal`
- Check test isolation

#### Memory Leaks
- Use `qt_widget_cleanup`
- Delete widgets explicitly
- Check signal connections

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── run_tests.py                   # Test execution script
└── unit/                          # Unit tests
    ├── test_button/               # Button widget tests
    ├── test_input/                # Input widget tests
    ├── test_label/                # Label widget tests
    └── test_misc/                 # Misc widget tests
```

## Troubleshooting

### Installation Issues
```bash
# Install in development mode
pip install -e ".[dev]"

# Install test dependencies
pip install pytest pytest-qt pytest-cov
```

### Test Execution Issues
```bash
# Debug mode
pytest --pdb

# Show prints
pytest -s

# Specific test
pytest -k "test_icon_button"
```

---

**Quick Start Tests** - Essential commands and troubleshooting for EzQt Widgets testing. 