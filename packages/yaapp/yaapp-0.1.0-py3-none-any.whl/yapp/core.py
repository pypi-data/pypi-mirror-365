"""
Core functionality for yapp - exposure and reflection.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from .exposers import BaseExposer, FunctionExposer, ClassExposer, ObjectExposer, CustomExposer
from .context_tree import ContextTree
from .execution_strategy import ExecutionStrategy, ExecutionHint


class YAppCore:
    """Core functionality for yapp - function exposure and reflection."""

    def __init__(self):
        """Initialize the core yapp functionality."""
        self._config: Optional[Dict[str, Any]] = None
        
        # Context tree for navigation (replaces fragile string manipulation)
        self._context_tree = ContextTree()
        
        # Initialize exposer system with registry for reflection
        self._function_exposer = FunctionExposer()
        self._class_exposer = ClassExposer()
        self._object_exposer = ObjectExposer()
        self._custom_exposer = CustomExposer()
        
        # Registry stores (object, exposer) pairs for proper execution
        self._registry: Dict[str, Tuple[Any, BaseExposer]] = {}

    def expose(self, obj: Union[Callable, Dict[str, Any], object] = None, 
               name: Optional[str] = None, 
               custom: bool = False,
               execution: Optional[str] = None) -> Union[Callable, object]:
        """
        Expose a function, class, or dictionary of functions to the CLI/web interface.
        
        Args:
            obj: Function, class, or dictionary to expose
            name: Optional name to use (defaults to function/class name)
            custom: Whether to use custom exposure workflow
            execution: Execution strategy for sync functions in async context
                      Options: "direct", "thread", "process", "auto"
                      Default: None (preserves existing hints, uses "thread" if none)
            
        Returns:
            The original object (for use as decorator)
        """
        # Handle decorator usage: @app.expose or @app.expose(execution="thread")
        if obj is None:
            # This is decorator usage with parameters: @app.expose(execution="thread")
            def decorator(func):
                return self.expose(func, name=name, custom=custom, execution=execution)
            return decorator
        
        if isinstance(obj, dict):
            # Handle nested dictionaries - for now, keep old behavior
            self._register_dict(obj)
        else:
            # Use exposer system to handle the object
            if name is None:
                register_name = getattr(obj, '__name__', str(obj))
            else:
                register_name = name
            
            # Validate name
            if not register_name or not register_name.strip():
                raise ValueError("Cannot expose object with empty name")
            
            # Process and store the object with proper async compatibility and execution hint
            # Use "thread" as default if no execution strategy provided
            effective_execution = execution if execution is not None else "thread"
            execution_was_provided = execution is not None
            
            processed_obj = self._process_object_for_registry(obj, custom, effective_execution, execution_was_provided)
            self._expose_with_system(processed_obj, register_name, custom)
        
        return obj
    
    def _process_object_for_registry(self, obj: Any, custom: bool = False, execution: str = "thread", execution_was_provided: bool = False) -> Any:
        """Process object for registry storage, applying execution hints and async compatibility if needed."""
        # Add execution hint to callable objects (functions and methods)
        if callable(obj) and not inspect.isclass(obj) and not custom:
            # Set execution hint - preserve existing ones unless explicitly overridden
            should_set_hint = (
                not hasattr(obj, '__execution_hint__') or  # No existing hint
                execution_was_provided  # Explicitly provided by user
            )
            
            if should_set_hint:
                try:
                    # Create and attach execution hint
                    strategy = ExecutionStrategy(execution)
                    hint = ExecutionHint(strategy=strategy)
                    obj.__execution_hint__ = hint
                except ValueError:
                    # Invalid execution strategy, default to thread
                    hint = ExecutionHint(strategy=ExecutionStrategy.THREAD)
                    obj.__execution_hint__ = hint
            
            # Apply async compatibility if it's not a bound method
            if not hasattr(obj, '__self__'):
                try:
                    from .async_compat import async_compatible
                    return async_compatible(obj)
                except (ImportError, TypeError, AttributeError):
                    # If async_compatible fails, store original object with hint
                    return obj
        
        return obj

    def _expose_with_system(self, obj: Any, name: str, custom: bool = False) -> None:
        """Expose an object using the exposer system."""
        import inspect
        
        # Determine which exposer to use based on type
        if custom:
            exposer = self._custom_exposer
        elif inspect.isclass(obj):
            exposer = self._class_exposer
        elif callable(obj):
            exposer = self._function_exposer  
        else:
            exposer = self._object_exposer
        
        # Expose using the selected exposer and add to registry
        result = exposer.expose(obj, name, custom)
        if not result.is_ok():
            raise ValueError(f"Failed to expose {name}: {result.as_error}")
        
        # Store (object, exposer) pair in registry for proper execution
        self._registry[name] = (obj, exposer)
        
        # Add to context tree for efficient navigation
        self._context_tree.add_item(name, obj)

    def _register_dict(self, obj_dict: Dict[str, Any], prefix: str = "", _depth: int = 0) -> None:
        """Register a dictionary of objects recursively."""
        # Prevent infinite recursion
        if _depth > 10:
            raise ValueError("Dictionary nesting too deep (max 10 levels)")
        
        for key, value in obj_dict.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Nested dictionary - recurse
                self._register_dict(value, full_key, _depth + 1)
            else:
                # Process and expose the value using exposer system
                processed_value = self._process_object_for_registry(value, custom=False)
                self._expose_with_system(processed_value, full_key)
                # Note: _expose_with_system already adds to registry and context tree

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from yapp.yaml file."""
        if self._config is not None:
            return self._config
            
        config = {}
        
        # Try to load main config
        config_paths = ["yapp.yaml", "yapp.yml"]
        
        for config_path in config_paths:
            if Path(config_path).exists():
                try:
                    import yaml
                    with open(config_path, 'r') as f:
                        loaded_config = yaml.safe_load(f) or {}
                        config = self._merge_config(config, loaded_config)
                        break
                except ImportError:
                    print(f"Warning: PyYAML not installed. Cannot load {config_path}")
                except Exception as e:
                    print(f"Warning: Error loading {config_path}: {e}")
        
        # Try to load secrets
        secrets_paths = ["yapp.secrets.yaml", "yapp.secrets.yml"]
        
        for secrets_path in secrets_paths:
            if Path(secrets_path).exists():
                try:
                    import yaml
                    with open(secrets_path, 'r') as f:
                        secrets_config = yaml.safe_load(f) or {}
                        config = self._merge_config(config, secrets_config)
                        break
                except ImportError:
                    continue  # Already warned about PyYAML
                except Exception as e:
                    print(f"Warning: Error loading {secrets_path}: {e}")

        self._config = config
        return config

    def _get_app_name(self) -> str:
        """Get the application name from config or default."""
        config = self._load_config()
        app_config = config.get("app", {})
        app_name = app_config.get("name")

        if app_name:
            return app_name

        # Try to infer from the calling script
        import sys
        if len(sys.argv) > 0:
            script_name = Path(sys.argv[0]).stem
            if script_name and script_name != "python":
                return script_name

        return "yapp"  # Fallback

    def _get_current_context_commands(self) -> Dict[str, Any]:
        """Get available commands in the current context using context tree."""
        return self._context_tree.get_current_context_items()

    def _get_prompt_string(self) -> str:
        """Get the current prompt string based on context."""
        app_name = self._get_app_name()
        context_path = self._context_tree.get_current_context_path()
        if context_path:
            context_str = ":".join(context_path)
            return f"{app_name}:{context_str}> "
        return f"{app_name}> "

    def _is_leaf_command(self, command_name: str) -> bool:
        """Check if a command is a leaf (executable) or has subcommands using context tree."""
        return self._context_tree.is_leaf_command(command_name)

    def _enter_context(self, context_name: str) -> bool:
        """Enter a command context using context tree. Returns True if successful."""
        return self._context_tree.enter_context(context_name)

    def _exit_context(self) -> bool:
        """Exit current context using context tree. Returns True if successful."""
        return self._context_tree.exit_context()

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge configuration dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
                
        return result
    
    def _execute_from_registry(self, name: str, **kwargs) -> Any:
        """
        Execute function from registry using its associated exposer.
        
        Args:
            name: Name of function in registry
            **kwargs: Arguments to pass to function
            
        Returns:
            Function result
            
        Raises:
            KeyError: If function not found in registry
            Exception: If execution fails
        """
        if name not in self._registry:
            raise KeyError(f"Function '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        
        # Use exposer to execute the function
        if hasattr(exposer, 'run'):
            result = exposer.run(obj, **kwargs)
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                # It's a Result object
                if result.is_ok():
                    return result.unwrap()
                else:
                    raise Exception(result.error_message)
            else:
                return result
        else:
            # Fallback to direct execution
            return obj(**kwargs)
    
    def get_registry_item(self, name: str) -> Any:
        """
        Get raw object from registry (backward compatibility).
        
        Args:
            name: Name of item in registry
            
        Returns:
            Raw object
            
        Raises:
            KeyError: If item not found
        """
        if name not in self._registry:
            raise KeyError(f"Item '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        return obj
    
    def get_registry_exposer(self, name: str) -> BaseExposer:
        """
        Get exposer for item from registry.
        
        Args:
            name: Name of item in registry
            
        Returns:
            Exposer object
            
        Raises:
            KeyError: If item not found
        """
        if name not in self._registry:
            raise KeyError(f"Item '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        return exposer
    
    def get_registry_items(self) -> Dict[str, Any]:
        """
        Get all raw objects from registry (backward compatibility).
        
        Returns:
            Dictionary of name -> raw object
        """
        return {name: obj for name, (obj, exposer) in self._registry.items()}

    def _detect_execution_mode(self) -> str:
        """Detect the execution mode (cli, server, tui)."""
        # Simple implementation - defaults to CLI
        # In a real implementation, this might check environment variables,
        # command line arguments, or configuration files
        return "cli"

    def _call_function_with_args(self, func: Callable, args: list) -> Any:
        """Call a function with string arguments, attempting to parse them."""
        # Get function signature for parameter type inference
        sig = inspect.signature(func)
        param_info = {param.name: param for param in sig.parameters.values()}

        parsed_args = []
        kwargs = {}

        for arg in args:
            if arg.startswith("--"):
                if "=" in arg:
                    # Keyword argument: --key=value
                    key, value = arg[2:].split("=", 1)
                else:
                    # Boolean flag: --key (without value)
                    key = arg[2:]
                    value = "true"

                # Convert hyphenated key to underscore (click style -> python style)
                python_key = key.replace("-", "_")

                # Try to infer type from function signature
                if python_key in param_info:
                    param = param_info[python_key]
                    if param.annotation == bool or (
                        param.default is not None and isinstance(param.default, bool)
                    ):
                        # Boolean parameter
                        kwargs[python_key] = value.lower() in ("true", "1", "yes", "on")
                    elif param.annotation == int or (
                        param.default is not None and isinstance(param.default, int)
                    ):
                        # Integer parameter
                        try:
                            kwargs[python_key] = int(value)
                        except ValueError:
                            raise ValueError(f"Invalid integer value '{value}' for parameter '{python_key}'")
                    elif param.annotation == float or (
                        param.default is not None and isinstance(param.default, float)
                    ):
                        # Float parameter
                        try:
                            kwargs[python_key] = float(value)
                        except ValueError:
                            raise ValueError(f"Invalid float value '{value}' for parameter '{python_key}'")
                    else:
                        # String or other parameter
                        kwargs[python_key] = value
                else:
                    # Unknown parameter - try JSON parsing
                    try:
                        kwargs[python_key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        # JSON parsing failed, use as string
                        kwargs[python_key] = value
            else:
                # Positional argument - try to parse as JSON, fallback to string
                try:
                    parsed_args.append(json.loads(arg))
                except (json.JSONDecodeError, TypeError):
                    # JSON parsing failed, use as string
                    parsed_args.append(arg)

        # Call the function
        if kwargs:
            return func(*parsed_args, **kwargs)
        else:
            return func(*parsed_args)