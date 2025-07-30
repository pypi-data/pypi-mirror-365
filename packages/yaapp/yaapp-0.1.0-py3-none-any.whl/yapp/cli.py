"""
CLI entry point for yapp when installed via pip
"""


def main():
    """Main CLI entry point for installed yapp package."""
    print("yapp CLI - Yet Another Python Package")
    print("This is the global CLI entry point.")
    print("For application-specific functionality, use YApp in your code:")
    print()
    print("Example:")
    print("  from yapp import YApp")
    print("  app = YApp()")
    print("  @app.expose")
    print("  def my_function(): ...")
    print("  app.run()")
    print()
    print("See documentation for more information.")


if __name__ == "__main__":
    main()
