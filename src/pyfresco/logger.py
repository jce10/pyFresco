from rich.console import Console

console = Console()

# --- color styles ---
TITLE_STYLE = "bold red"
BORDER_STYLE = "bright_cyan"
STEP_STYLE = "yellow"
SUCCESS_STYLE = "green"
INFO_STYLE = "cyan"
WARN_STYLE = "bold yellow"
ERROR_STYLE = "bold red"


def print_banner(run_dir) -> None:
    """
    Print a startup banner for pyFRESCO.
    """
    width = 80
    border = "# " + "=" * width + " #"
    title_text = f" Running pyFRESCO in directory: {run_dir} "
    title_line = "# " + title_text.center(width, "=") + " #"

    console.print()
    console.print(border, style=BORDER_STYLE)
    console.print(title_line, style=TITLE_STYLE)
    console.print(border, style=BORDER_STYLE)
    console.print()


def print_footer() -> None:
    """
    Print a completion footer.
    """
    width = 80
    border = "# " + "=" * width + " #"

    console.print()
    console.print("Complete! Check the output files in the current directory.", style=SUCCESS_STYLE)
    console.print(border, style=BORDER_STYLE)
    console.print()


def step(message: str) -> None:
    """
    Print a step that is about to be attempted.
    Stays on the same line so success/failure can follow.
    """
    console.print(f"{message} ...", style=STEP_STYLE, end="")


def success(message: str = " done ✓") -> None:
    """
    Print a success message, usually after step().
    """
    console.print(message, style=SUCCESS_STYLE)


def info(message: str) -> None:
    """
    Print a neutral informational message.
    """
    console.print(message, style=INFO_STYLE)


def warning(message: str) -> None:
    """
    Print a warning message.
    """
    console.print(f"Warning: {message}", style=WARN_STYLE)


def error(message: str) -> None:
    """
    Print an error message.
    """
    console.print(f"Error: {message}", style=ERROR_STYLE)


def step_success(message: str) -> None:
    """
    Convenience function for one-line success messages.
    """
    console.print(f"{message} ✓", style=SUCCESS_STYLE)


def step_fail(message: str) -> None:
    """
    Convenience function for one-line failure messages.
    """
    console.print(f"{message} ✗", style=ERROR_STYLE)