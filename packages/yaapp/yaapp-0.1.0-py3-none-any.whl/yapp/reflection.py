"""
Click reflection functionality for yapp - refactored into focused classes.
"""

import inspect
import json
from typing import Any, Dict, Optional
from io import StringIO
import sys

try:
    import click
    HAS_CLICK = True
except ImportError:
    HAS_CLICK = False
    click = None


class CLIBuilder:
    """Handles creation of Click CLI groups and built-in commands."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
    
    def build_cli(self) -> Optional['click.Group']:
        """Build the main CLI group with built-in commands."""
        if not HAS_CLICK:
            print("Click not available. Install with: pip install click")
            return None

        @click.group()
        def cli():
            """YApp CLI with automatic function and class reflection."""
            pass

        # Add built-in commands
        self._add_server_command(cli)
        self._add_tui_command(cli)
        self._add_run_command(cli)
        self._add_list_command(cli)
        
        return cli
    
    def _add_server_command(self, cli):
        """Add the server command."""
        @cli.command()
        @click.option('--host', default='localhost', help='Host to bind to')
        @click.option('--port', default=8000, help='Port to bind to')
        @click.option('--reload', is_flag=True, help='Enable auto-reload')
        def server(host: str, port: int, reload: bool):
            """Start the web server."""
            from .runners import FastAPIRunner
            runner = FastAPIRunner(self.core)
            runner.run(host, port, reload)
    
    def _add_tui_command(self, cli):
        """Add the TUI command."""
        @cli.command()
        @click.option('--backend', default='prompt', 
                     type=click.Choice(['prompt', 'typer', 'rich', 'click']),
                     help='TUI backend to use')
        def tui(backend: str):
            """Start interactive TUI."""
            from .runners import ClickRunner, PromptRunner, RichRunner, TyperRunner
            
            print(f"Starting TUI with {backend} backend")

            if backend == "prompt":
                runner = PromptRunner(self.core)
            elif backend == "typer":
                runner = TyperRunner(self.core)
            elif backend == "rich":
                runner = RichRunner(self.core)
            elif backend == "click":
                runner = ClickRunner(self.core)
            else:
                print(f"Unknown backend: {backend}. Available: prompt, typer, rich, click")
                return

            runner.run()
    
    def _add_run_command(self, cli):
        """Add the run command."""
        @cli.command()
        @click.argument('function_name')
        @click.argument('args', nargs=-1)
        def run(function_name: str, args: tuple):
            """Execute a specific function."""
            if function_name not in self.core._registry:
                print(f"Function '{function_name}' not found. Available: {list(self.core._registry.keys())}")
                return

            try:
                # Use registry execution method with safe argument parsing
                from .reflection_utils import ArgumentParser
                parser = ArgumentParser()
                kwargs = parser.parse_args_to_kwargs(list(args))
                result = self.core._execute_from_registry(function_name, **kwargs)
                print(f"Result: {result}")
            except Exception as e:
                print(f"Error executing {function_name}: {e}")
    
    def _add_list_command(self, cli):
        """Add the list command."""
        @cli.command()
        def list():
            """List all exposed functions."""
            print("Available functions:")
            registry_items = self.core.get_registry_items()
            for name, func in sorted(registry_items.items()):
                func_type = "function"
                if inspect.isclass(func):
                    func_type = "class"
                doc = getattr(func, '__doc__', '') or 'No description'
                if doc:
                    doc = doc.split('\n')[0][:50] + ('...' if len(doc.split('\n')[0]) > 50 else '')
                print(f"  {name:<20} | {func_type:<8} | {doc}")


class CommandReflector:
    """Handles reflection of functions and classes into Click commands."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
    
    def add_reflected_commands(self, cli_group) -> None:
        """Add commands based on exposed objects with reflection."""
        registry_items = self.core.get_registry_items()
        for name, obj in registry_items.items():
            if '.' in name:
                # Handle nested objects (e.g., "math.add")
                self._add_nested_command(cli_group, name, obj)
            elif inspect.isclass(obj):
                # Handle classes - create command group with methods as subcommands
                self._add_class_command(cli_group, name, obj)
            elif callable(obj):
                # Handle functions - create direct command
                self._add_function_command(cli_group, name, obj)
    
    def _add_nested_command(self, cli_group, full_name: str, obj) -> None:
        """Add nested commands (e.g., math.add -> math group with add subcommand)."""
        parts = full_name.split('.')
        group_name = parts[0]
        command_name = '.'.join(parts[1:])
        
        # Get or create the group using a safer approach
        group = self._get_or_create_group(cli_group, group_name)
        
        if callable(obj):
            self._add_function_command(group, command_name, obj)
    
    def _get_or_create_group(self, cli_group, group_name: str):
        """Safely get or create a command group."""
        group_attr = f'_yapp_group_{group_name}'
        
        if not hasattr(cli_group, group_attr):
            @cli_group.group(name=group_name)
            def nested_group():
                f"""Commands in {group_name} namespace."""
                pass
            
            setattr(cli_group, group_attr, nested_group)
        
        return getattr(cli_group, group_attr)
    
    def _add_class_command(self, cli_group, name: str, cls) -> None:
        """Add a class as a command group with methods as subcommands."""
        @cli_group.group(name=name)
        def class_group():
            f"""Commands for {cls.__name__} class."""
            pass
        
        # Add methods as subcommands - inspect class directly without instantiation
        for method_name in dir(cls):
            if not method_name.startswith('_'):
                method = getattr(cls, method_name)
                if callable(method) and not isinstance(method, type):
                    # Create a bound method using a lazily instantiated class instance
                    # We'll handle the actual instantiation at execution time
                    self._add_function_command(class_group, method_name, method)
    
    def _add_function_command(self, cli_group, name: str, func) -> None:
        """Add a function as a click command with proper options."""
        # Get function signature
        sig = inspect.signature(func)
        
        def create_command():
            @cli_group.command(name=name)
            def command(**kwargs):
                f"""Execute {name}."""
                try:
                    # Filter out None values (unset options)
                    filtered_kwargs = {k: v for k, v in kwargs.items() if v is not None}
                    result = func(**filtered_kwargs)
                    if result is not None:
                        if isinstance(result, dict):
                            click.echo(json.dumps(result, indent=2))
                        else:
                            click.echo(str(result))
                except Exception as e:
                    click.echo(f"Error: {e}", err=True)
            
            # Add click options based on function parameters
            for param_name, param in sig.parameters.items():
                if param_name == 'self':
                    continue
                
                command = self._add_parameter_option(command, param_name, param)
            
            return command
        
        create_command()
    
    def _add_parameter_option(self, command, param_name: str, param):
        """Add a click option for a function parameter."""
        # Determine option type and default
        option_type = str  # Default to string
        default_value = None
        help_text = f"Parameter {param_name}"
        
        if param.default != inspect.Parameter.empty:
            default_value = param.default
            if isinstance(default_value, bool):
                # Boolean parameters become flags
                return click.option(
                    f"--{param_name.replace('_', '-')}", 
                    is_flag=True, 
                    default=default_value,
                    help=help_text
                )(command)
            elif isinstance(default_value, int):
                option_type = int
            elif isinstance(default_value, float):
                option_type = float
        
        # Add the option
        return click.option(
            f"--{param_name.replace('_', '-')}", 
            type=option_type, 
            default=default_value,
            help=help_text
        )(command)


class ExecutionHandler:
    """Handles safe command execution without dangerous stream hijacking."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
        self.cli_builder = CLIBuilder(core)
        self.command_reflector = CommandReflector(core)
    
    def execute_command_safely(self, func_name: str, args: list, console=None) -> None:
        """Execute a command through click interface with safe output capture."""
        # Create the click CLI
        cli = self.cli_builder.build_cli()
        if not cli:
            raise Exception("Could not create click CLI")
        
        # Add reflected commands
        self.command_reflector.add_reflected_commands(cli)
        
        # Build command arguments based on context
        click_args = self._build_command_args(func_name, args)
        
        # Execute with safe output capture
        self._execute_with_safe_capture(cli, click_args, console)
    
    def _build_command_args(self, func_name: str, args: list) -> list:
        """Build command arguments based on current context."""
        click_args = []
        
        # Handle contextual commands using context tree
        context_path = self.core._context_tree.get_current_context_path()
        if context_path and len(context_path) == 1:
            class_name = context_path[0]
            # Check if this is a class command
            registry_items = self.core.get_registry_items()
            if class_name in registry_items and inspect.isclass(registry_items[class_name]):
                click_args = [class_name, func_name] + args
            else:
                # Handle nested namespaces
                click_args = [func_name] + args
        else:
            # Root context or deeply nested - direct command
            click_args = [func_name] + args
        
        return click_args
    
    def _execute_with_safe_capture(self, cli, click_args: list, console=None) -> None:
        """Execute command with safe output capture without stream hijacking."""
        handler = ClickOutputHandler()
        
        try:
            stdout_output, stderr_output = handler.capture_output(cli, click_args)
        except Exception as e:
            stdout_output = ""
            stderr_output = f"Execution error: {e}"
        
        # Display captured output
        self._display_output(stdout_output, stderr_output, console)
    
    def _display_output(self, stdout_output: str, stderr_output: str, console=None) -> None:
        """Display captured output to the appropriate console."""
        if stdout_output.strip():
            if console:
                console.print(stdout_output.strip())
            else:
                print(stdout_output.strip())
                
        if stderr_output.strip():
            if console:
                console.print(f"[bold red]Error:[/bold red] {stderr_output.strip()}")
            else:
                print(f"Error: {stderr_output.strip()}")


class ClickOutputHandler:
    """Handler for Click command output without dangerous stream hijacking."""
    
    def __init__(self):
        self.output_buffer = []
        self.error_buffer = []
    
    def capture_output(self, cli, click_args: list) -> tuple[str, str]:
        """Execute Click command and capture output safely."""
        try:
            # Use Click's built-in testing utilities instead of stream hijacking
            from click.testing import CliRunner
            runner = CliRunner()
            
            # Run the command in isolated environment
            result = runner.invoke(cli, click_args, catch_exceptions=False)
            
            return result.output, result.stderr_bytes.decode() if result.stderr_bytes else ""
            
        except ImportError:
            # Fallback: execute without capture if click.testing not available  
            try:
                ctx = click.Context(cli)
                with ctx:
                    cli.main(click_args, standalone_mode=False)
                return "Command executed successfully", ""
            except SystemExit:
                # Click uses SystemExit for --help and errors - this is expected
                return "Command completed", ""
            except Exception as e:
                return "", f"Execution error: {e}"
    
    def write_error(self, message: str) -> None:
        """Write an error message to error buffer."""
        self.error_buffer.append(message)


class ClickReflection:
    """Maintains backward compatibility with existing runners while using refactored components."""
    
    def __init__(self, core):
        """Initialize with reference to core functionality."""
        self.core = core
        self.execution_handler = ExecutionHandler(core)
    
    def create_reflective_cli(self):
        """Create enhanced CLI with reflection for objects and subcommands."""
        cli_builder = CLIBuilder(self.core)
        cli = cli_builder.build_cli()
        
        if cli:
            # Add reflected commands
            command_reflector = CommandReflector(self.core)
            command_reflector.add_reflected_commands(cli)
        
        return cli
    
    def execute_command_through_click(self, func_name: str, args: list, console=None) -> None:
        """Execute a command through the click interface with safe handling."""
        self.execution_handler.execute_command_safely(func_name, args, console)
    
    def _parse_args_to_kwargs(self, args: list) -> Dict[str, Any]:
        """Parse command line arguments to kwargs format."""
        from .reflection_utils import ArgumentParser
        parser = ArgumentParser()
        return parser.parse_args_to_kwargs(args)