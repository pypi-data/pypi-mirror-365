# tapwire.py - Elegant cross-module variable access
import importlib.util
import os
import types
import sys
import hashlib
import time
import threading
from typing import Any, Callable, Dict, List, Optional, Type, Union

# Module-level state
_MODULE_CACHE = {}
_WATCHERS = {}
_DEBUG = False
_LOG_HANDLER = print

def set_debug(enabled: bool = True, handler: Callable[[str], None] = print) -> None:
    """
    Enable debug logging with custom handler
    
    Args:
        enabled: Turn debugging on/off
        handler: Function to handle log messages (default: print)
    
    Example:
        >>> tapwire.set_debug(True)
        >>> tapwire.watch_file(...)
        [tapwire] Started watching /path/to/config.py
    """
    global _DEBUG, _LOG_HANDLER
    _DEBUG = enabled
    _LOG_HANDLER = handler

def _log(message: str) -> None:
    """Internal logging function"""
    if _DEBUG:
        _LOG_HANDLER(f"[tapwire] {message}")

def _file_hash(file_path: str) -> str:
    """Compute SHA256 hash of file content for change detection"""
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(4096):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        raise IOError(f"Could not read {file_path}: {str(e)}")

def _load_module(file_path: str) -> types.ModuleType:
    """Load module from file path with hash-based caching"""
    file_path = os.path.abspath(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"Path is not a file: {file_path}")

    # Compute current file hash
    current_hash = _file_hash(file_path)
    
    # Check cache for existing entry with matching hash
    cache_entry = _MODULE_CACHE.get(file_path)
    if cache_entry and cache_entry['hash'] == current_hash:
        _log(f"Using cached module: {file_path}")
        return cache_entry['module']

    # Generate unique module name
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    module_name = base_name
    
    # Handle duplicate module names
    suffix = 1
    while module_name in sys.modules:
        module_name = f"{base_name}_{suffix}"
        suffix += 1

    # Load and execute module
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load spec for module: {file_path}")
        
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    
    try:
        _log(f"Executing module: {file_path}")
        spec.loader.exec_module(module)
    except Exception as e:
        # Cleanup on failure
        if module_name in sys.modules:
            del sys.modules[module_name]
        raise ImportError(f"Error executing module {file_path}: {str(e)}")

    # Update cache with new module and hash
    _MODULE_CACHE[file_path] = {
        'module': module,
        'hash': current_hash,
        'mtime': os.path.getmtime(file_path)
    }
    
    return module

def clear_cache(file_path: Optional[str] = None) -> None:
    """
    Clear cache for specific file or all files
    
    Args:
        file_path: Path to clear (None clears all)
        
    Example:
        >>> tapwire.clear_cache('config.py')
    """
    if file_path:
        abs_path = os.path.abspath(file_path)
        if abs_path in _MODULE_CACHE:
            del _MODULE_CACHE[abs_path]
            _log(f"Cleared cache for {abs_path}")
    else:
        _MODULE_CACHE.clear()
        _log("Cleared all cache")

def get_var(
    file_path: str, 
    var_name: str = "__all__", 
    as_dict: bool = False
) -> Union[Any, List[str], Dict[str, Any]]:
    """
    Get variable from module or list public variables
    
    Args:
        file_path: Path to Python file
        var_name: Variable name or "__all__" for public variables
        as_dict: Return dictionary instead of list when using "__all__"
    
    Returns:
        Variable value, list of names, or {name: value} dict
        
    Examples:
        # Get specific variable
        >>> port = get_var('config.py', 'PORT')
        
        # Get list of public variables
        >>> vars = get_var('settings.py')
        ['DB_HOST', 'TIMEOUT']
        
        # Get dictionary of public variables
        >>> var_dict = get_var('constants.py', as_dict=True)
        {'PI': 3.14, 'MAX_SIZE': 100}
    """
    module = _load_module(file_path)

    if var_name == "__all__":
        items = {
            k: v for k, v in vars(module).items()
            if not k.startswith("__")
            and not isinstance(v, types.ModuleType)
            and not callable(v)
        }
        return items if as_dict else list(items.keys())

    if hasattr(module, var_name):
        return getattr(module, var_name)
    raise AttributeError(f"Module '{file_path}' has no attribute '{var_name}'")

def list_vars(file_path: str) -> List[str]:
    """
    Get list of public variable names in module
    
    Example:
        >>> tapwire.list_vars('config.py')
        ['API_KEY', 'TIMEOUT']
    """
    return get_var(file_path, "__all__", as_dict=False)

def get_vars_dict(file_path: str) -> Dict[str, Any]:
    """
    Get dictionary of public variables in module
    
    Example:
        >>> tapwire.get_vars_dict('settings.py')
        {'DEBUG': True, 'LOG_LEVEL': 'INFO'}
    """
    return get_var(file_path, "__all__", as_dict=True)

def get_vars_by_type(
    file_path: str, 
    var_type: Type[Any]
) -> Dict[str, Any]:
    """
    Get variables of specific type
    
    Example:
        >>> tapwire.get_vars_by_type('config.py', int)
        {'PORT': 8080, 'MAX_CONNECTIONS': 100}
    """
    module = _load_module(file_path)
    return {
        k: v for k, v in vars(module).items()
        if isinstance(v, var_type)
    }

def watch_file(
    file_path: str,
    callback: Callable[[Dict[str, Any]], None],
    interval: float = 1.0,
    immediate: bool = True
) -> None:
    """
    Watch file for changes and trigger callback on update
    
    Args:
        file_path: File to watch
        callback: Function to call with new variables dict
        interval: Check interval in seconds
        immediate: Trigger callback immediately on watch start
        
    Example:
        def config_updated(vars):
            print("Config updated!", vars)
            
        tapwire.watch_file('config.py', config_updated)
    """
    abs_path = os.path.abspath(file_path)
    
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Cannot watch non-existent file: {abs_path}")
    
    # Create a stop event for this watcher
    stop_event = threading.Event()
    
    def watcher():
        # Get initial state
        initial_mtime = os.path.getmtime(abs_path) if os.path.exists(abs_path) else 0
        initial_triggered = not immediate  # Start as False if immediate requested
        
        while not stop_event.is_set():
            try:
                if not os.path.exists(abs_path):
                    _log(f"File disappeared: {abs_path}")
                    stop_event.wait(interval)
                    continue
                
                current_mtime = os.path.getmtime(abs_path)
                
                # Handle file changes
                if current_mtime > initial_mtime:
                    _log(f"File modified: {abs_path}")
                    initial_mtime = current_mtime
                    clear_cache(abs_path)
                    try:
                        new_vars = get_vars_dict(abs_path)
                        _log(f"Calling callback with {len(new_vars)} variables")
                        callback(new_vars)
                    except Exception as e:
                        _log(f"⚠️ Callback error: {str(e)}")
                
                # Handle initial trigger (only once)
                if not initial_triggered:
                    _log(f"Triggering initial callback")
                    initial_triggered = True
                    try:
                        new_vars = get_vars_dict(abs_path)
                        callback(new_vars)
                    except Exception as e:
                        _log(f"⚠️ Initial callback error: {str(e)}")
            
            except Exception as e:
                _log(f"⚠️ Watcher error: {str(e)}")
            
            # Wait with interruptible sleep
            stop_event.wait(interval)
    
    if abs_path in _WATCHERS:
        raise RuntimeError(f"Already watching {file_path}")
    
    thread = threading.Thread(target=watcher, daemon=True)
    thread.start()
    # Store both thread and stop event
    _WATCHERS[abs_path] = (thread, stop_event)
    _log(f"👀 Started watching {abs_path} (interval: {interval}s)")

def stop_watching(file_path: str) -> None:
    """Stop watching a file for changes"""
    abs_path = os.path.abspath(file_path)
    if abs_path in _WATCHERS:
        thread, stop_event = _WATCHERS[abs_path]
        _log(f"🛑 Stopping watcher for {abs_path}")
        stop_event.set()  # Signal the thread to stop
        thread.join(timeout=1.0)  # Wait a moment for clean exit
        if thread.is_alive():
            _log(f"⚠️ Watcher for {abs_path} didn't exit cleanly")
        del _WATCHERS[abs_path]
        _log(f"✅ Stopped watching {abs_path}")
    else:
        _log(f"ℹ️ Not watching {abs_path}")

def stop_all_watchers() -> None:
    """Stop all active file watchers"""
    _log("Stopping all watchers")
    for path in list(_WATCHERS.keys()):
        stop_watching(path)

# CLI Support
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(
        description="tapwire - Cross-module variable access tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("file", help="Python file to inspect")
    parser.add_argument("--var", help="Variable to retrieve")
    parser.add_argument("--list", action="store_true", help="List all variables")
    parser.add_argument("--dict", action="store_true", help="Get all variables as JSON")
    parser.add_argument("--type", help="Filter by type (e.g., int, str)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    
    args = parser.parse_args()
    
    if args.debug:
        set_debug(True)
    
    try:
        if args.type:
            # Type filtering
            type_map = {
                "int": int, "str": str, "float": float,
                "bool": bool, "list": list, "dict": dict
            }
            if args.type not in type_map:
                print(f"Unsupported type: {args.type}")
                print("Supported types: " + ", ".join(type_map.keys()))
                sys.exit(1)
                
            result = get_vars_by_type(args.file, type_map[args.type])
            print(json.dumps(result, indent=2))
            
        elif args.var:
            # Single variable
            print(get_var(args.file, args.var))
            
        elif args.list:
            # List variables
            print("\n".join(list_vars(args.file)))
            
        elif args.dict:
            # Dictionary output
            print(json.dumps(get_vars_dict(args.file), indent=2))
            
        else:
            # Default: list variables
            print("Variables in", args.file)
            for var in list_vars(args.file):
                print(f" - {var}")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)