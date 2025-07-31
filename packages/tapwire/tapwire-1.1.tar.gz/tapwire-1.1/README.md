# **tapwire**

[![PyPI version](https://badge.fury.io/py/tapwire.svg)](https://pypi.org/project/tapwire/)

A lightweight, robust module for reading variables from other Python files, with caching, file watching, and a command-line interface.

---

## **Features**

- **Variable Access**: Read variables from any Python file
- **Intelligent Caching**: SHA256-based caching with automatic invalidation
- **File Watching**: Monitor files for changes with callback notifications
- **Type Filtering**: Retrieve variables by specific type
- **Thread-Safe**: Designed for multi-threaded applications
- **CLI Support**: Command-line interface for quick inspections
- **Debug Logging**: Configurable debug output
- **Zero Dependencies**: Pure Python standard library implementation

---

## **Installation**

```bash
pip install tapwire
```

---

## **Basic Usage**

### **Reading Variables**
```python
import tapwire

# Read single variable
api_key = tapwire.get_var('config.py', 'API_KEY')

# List all public variables
var_names = tapwire.list_vars('settings.py')

# Get dictionary of variables
config = tapwire.get_vars_dict('config.py')

# Get variables by type
ints = tapwire.get_vars_by_type('constants.py', int)
```

### **Watching File Changes**
```python
def on_config_change(new_vars):
    print("Config updated:", new_vars)

# Start watching (triggers immediately by default)
tapwire.watch_file('config.py', on_config_change)

# ... later ...
tapwire.stop_watching('config.py')
```

### **Debugging**
```python
# Enable debug logging
tapwire.set_debug(True)

# Custom log handler
def my_logger(message):
    print(f"[CUSTOM] {message}")

tapwire.set_debug(True, handler=my_logger)
```

---

## **Advanced Usage**

### **Cache Management**
```python
# Clear specific file cache
tapwire.clear_cache('config.py')

# Clear all cache
tapwire.clear_cache()
```

### **Watching Multiple Files**
```python
files = {
    'config.py': lambda v: print("Config updated"),
    'theme.py': lambda v: print("Theme updated"),
}

for path, callback in files.items():
    tapwire.watch_file(path, callback)
```

### **CLI Interface**
```bash
# List variables
tapwire config.py

# Get specific variable
tapwire config.py --var API_KEY

# Get all variables as JSON
tapwire settings.py --dict

# Filter by type (e.g., int)
tapwire constants.py --type int
```

---

## **API Reference**

### **Core Functions**
| Function | Description |
|----------|-------------|
| `get_var(file_path, var_name="__all__", as_dict=False)` | Get variable, list of names, or dictionary |
| `list_vars(file_path)` | Get list of public variable names |
| `get_vars_dict(file_path)` | Get {variable: value} dictionary |
| `get_vars_by_type(file_path, var_type)` | Get variables by specific type |

### **File Watching**
| Function | Description |
|----------|-------------|
| `watch_file(file_path, callback, interval=1.0, immediate=True)` | Watch file for changes |
| `stop_watching(file_path)` | Stop watching a file |
| `stop_all_watchers()` | Stop all active watchers |

### **Cache & Debug**
| Function | Description |
|----------|-------------|
| `clear_cache(file_path=None)` | Clear cache for file(s) |
| `set_debug(enabled=True, handler=print)` | Configure debug logging |

---

## **Safety Notes**
1. **Execution Warning**: Files are executed when loaded. Only use with trusted files.
2. **Thread Safety**: Watchers use daemon threads for clean process exits.
3. **Sandboxing**: No built-in sandbox - use in secure environments.

---

## **Performance Characteristics**
| Operation | Complexity | Notes |
|-----------|------------|-------|
| First file load | O(n) | File size dependent |
| Cached access | O(1) | Constant time |
| File watching | O(1) per interval | Configurable interval |
| Variable filtering | O(n) | Number of variables |

---

## **Why tapwire?**
- **Lightweight**: No external dependencies
- **Robust**: Handles file changes, deletions, and errors gracefully
- **Flexible**: Supports both programmatic use and CLI inspection
- **Transparent**: Clear caching behavior with content-based validation

```python
# Example real-world usage
def load_config():
    return tapwire.get_vars_dict('config.py')

config = load_config()
```