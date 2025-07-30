"""
Core functionality for yaapp - exposure and reflection.
"""

import inspect
import json
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, Tuple
from .exposers import BaseExposer, FunctionExposer, ClassExposer, ObjectExposer, CustomExposer
from .context_tree import ContextTree
from .execution_strategy import ExecutionStrategy, ExecutionHint
from .config import YaappConfig, ConfigManager
from .result import Result, Ok, Err


class YaappCore:
    """Core functionality for yaapp - function exposure and reflection."""

    def __init__(self):
        """Initialize the core yaapp functionality."""
        self._config: Optional[YaappConfig] = None
        
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
                # For decorator usage, we need to handle this differently
                # since decorators can't return Result types
                print(f"Warning: Cannot expose object with empty name")
                return obj
            
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
            # For internal use, log error and continue gracefully
            print(f"Warning: Failed to expose {name}: {result.as_error}")
            return
        
        # Store (object, exposer) pair in registry for proper execution
        self._registry[name] = (obj, exposer)
        
        # Add to context tree for efficient navigation
        self._context_tree.add_item(name, obj)

    def _register_dict(self, obj_dict: Dict[str, Any], prefix: str = "", _depth: int = 0) -> None:
        """Register a dictionary of objects recursively."""
        # Prevent infinite recursion
        if _depth > 10:
            print(f"Warning: Dictionary nesting too deep (max 10 levels), skipping further nesting")
            return
        
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

    def _load_config(self) -> YaappConfig:
        """Load configuration using enhanced configuration system with environment variables and secrets support."""
        if self._config is not None:
            return self._config
        
        # Auto-detect config and secrets files
        config_file = None
        secrets_file = None
        
        # Look for main config files
        for config_path in ["yaapp.yaml", "yaapp.yml", "yaapp.json"]:
            if Path(config_path).exists():
                config_file = config_path
                break
        
        # Look for secrets files
        for secrets_path in ["yaapp.secrets.yaml", "yaapp.secrets.yml", "yaapp.secrets.json"]:
            if Path(secrets_path).exists():
                secrets_file = secrets_path
                break
        
        # Load configuration with full feature support:
        # - Environment variables (YAAPP_*)
        # - Config file with variable substitution
        # - Secrets file auto-merging
        # - Comprehensive defaults and validation
        self._config = YaappConfig.load(
            config_file=config_file,
            secrets_file=secrets_file,
            env_prefix="YAAPP_"
        )
        
        return self._config

    def _get_app_name(self) -> str:
        """Get the application name from config or default."""
        config = self._load_config()
        
        # Check custom config for app name first
        app_name = config.get("app.name") or config.custom.get("app_name")
        
        if app_name:
            return app_name

        # Try to infer from the calling script
        import sys
        if len(sys.argv) > 0:
            script_name = Path(sys.argv[0]).stem
            if script_name and script_name != "python":
                return script_name

        return "yaapp"  # Fallback

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
    
    def _execute_from_registry(self, name: str, **kwargs) -> Result[Any]:
        """
        Execute function from registry using its associated exposer.
        
        Args:
            name: Name of function in registry
            **kwargs: Arguments to pass to function
            
        Returns:
            Result containing function result or error
        """
        if name not in self._registry:
            return Result.error(f"Function '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        
        # Use exposer to execute the function
        if hasattr(exposer, 'run'):
            result = exposer.run(obj, **kwargs)
            if hasattr(result, 'is_ok') and hasattr(result, 'unwrap'):
                # It's already a Result object
                return result
            else:
                # Wrap result in Ok
                return Ok(result)
        else:
            # Fallback to direct execution
            try:
                result = obj(**kwargs)
                return Ok(result)
            except Exception as e:
                return Result.error(f"Execution failed: {str(e)}")
    
    def get_registry_item(self, name: str) -> Result[Any]:
        """
        Get raw object from registry (backward compatibility).
        
        Args:
            name: Name of item in registry
            
        Returns:
            Result containing raw object or error
        """
        if name not in self._registry:
            return Result.error(f"Item '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        return Ok(obj)
    
    def get_registry_exposer(self, name: str) -> Result[BaseExposer]:
        """
        Get exposer for item from registry.
        
        Args:
            name: Name of item in registry
            
        Returns:
            Result containing exposer object or error
        """
        if name not in self._registry:
            return Result.error(f"Item '{name}' not found in registry")
        
        obj, exposer = self._registry[name]
        return Ok(exposer)
    
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
                            # Graceful fallback to string
                            kwargs[python_key] = value
                    elif param.annotation == float or (
                        param.default is not None and isinstance(param.default, float)
                    ):
                        # Float parameter
                        try:
                            kwargs[python_key] = float(value)
                        except ValueError:
                            # Graceful fallback to string
                            kwargs[python_key] = value
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