"""
Main YApp class that combines core functionality with runners.
"""

from .core import YAppCore
from .runners import ClickRunner, PromptRunner, RichRunner, TyperRunner, FastAPIRunner


class YApp(YAppCore):
    """
    Main yapp application class that bridges CLI and web interfaces.
    """

    def __init__(self):
        """Initialize the yapp application."""
        super().__init__()

    def _run_server(self, host: str = "localhost", port: int = 8000, reload: bool = False) -> None:
        """Start FastAPI web server."""
        runner = FastAPIRunner(self)
        runner.run(host, port, reload)

    def _run_tui(self, backend: str = "prompt") -> None:
        """Start interactive TUI with specified backend."""
        print(f"Starting TUI with {backend} backend")
        print(f"Available functions: {list(self._registry.keys())}")

        if backend == "prompt":
            runner = PromptRunner(self)
        elif backend == "typer":
            runner = TyperRunner(self)
        elif backend == "rich":
            runner = RichRunner(self)
        elif backend == "click":
            runner = ClickRunner(self)
        else:
            print(f"Unknown backend: {backend}. Available: prompt, typer, rich, click")
            return

        runner.run()

    def _run_function(self, function_name: str, args: tuple) -> None:
        """Execute a specific function with arguments."""
        if function_name not in self._registry:
            print(f"Function '{function_name}' not found. Available: {list(self._registry.keys())}")
            return

        func = self._registry[function_name]
        try:
            # Convert args tuple to list for processing
            result = self._call_function_with_args(func, list(args))
            print(f"Result: {result}")
        except (KeyboardInterrupt, SystemExit):
            # Re-raise system exceptions to allow proper exit
            raise
        except Exception as e:
            print(f"Error executing {function_name}: {e}")

    def run_cli(self):
        """Run the main CLI interface."""
        from .reflection import ClickReflection
        
        reflection = ClickReflection(self)
        cli = reflection.create_reflective_cli()
        if cli:
            cli()
        else:
            # Fallback if Click is not available
            print("YApp CLI not available - install click package")
            print("\nAvailable functions:")
            for name, obj in self._registry.items():
                print(f"  - {name}")
            print("\nTo use functions, install click: pip install click")

    def run(self):
        """Run the main CLI interface (alias for run_cli)."""
        self.run_cli()