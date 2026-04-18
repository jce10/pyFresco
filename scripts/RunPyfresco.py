from pathlib import Path
from rich.console import Console
from pyfresco.pyfresco import main

console = Console()

if __name__ == "__main__":
    run_dir = Path.cwd()
    width = 80
    console.print("\n[cyan]" + "# " + "=" * width + " #" + "\n[/]")

    text = f" Running pyFRESCO in directory: {run_dir} "
    title_line = "[bold red]# " + text.center(width, "=") + " #[/]"
    console.print(title_line + "\n")

    console.print("[cyan]" + "# " + "=" * width + " #" + "[/]\n")

    main(run_dir=run_dir)

    console.print("[green]Complete! Check the output files in the output directory listed above.[/]\n")
    console.print("[cyan]" + "# " + "=" * width + " #" + "[/]\n")
