# this_file: src/tscprojpy/cli.py
"""Command-line interface for tscprojpy."""

from pathlib import Path

import fire
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from . import __version__
from .scaler import TscprojScaler

console = Console()


def version():
    """Display version information."""
    console.print(
        Panel.fit(
            f"[bold cyan]tscprojpy[/bold cyan] version [bold green]{__version__}[/bold green]",
            title="Version Info",
        )
    )


def hello(name: str = "World"):
    """Say hello to someone.

    Args:
        name: Name to greet (default: World)
    """
    console.print(f"[bold green]Hello, {name}![/bold green]")


def xyscale(input: str, scale: float, output: str | None = None, verbose: bool = False):
    """Scale a Camtasia .tscproj file by a given factor.

    Args:
        input: Path to the input .tscproj file
        scale: Scale factor in percent (e.g., 150.0 for 150%)
        output: Path to save the scaled file (auto-generated if not provided)
        verbose: Enable verbose logging
    """
    # Convert scale from percentage to factor
    scale_factor = scale / 100.0

    # Validate inputs
    input_path = Path(input)
    if not input_path.exists():
        console.print(f"[bold red]Error:[/bold red] Input file '{input}' does not exist")
        return

    if not input_path.suffix.lower() == ".tscproj":
        console.print(
            "[bold yellow]Warning:[/bold yellow] Input file does not have .tscproj extension"
        )

    if scale <= 0:
        console.print("[bold red]Error:[/bold red] Scale factor must be positive")
        return

    # Generate output filename if not provided
    if output is None:
        scale_str = (
            f"{int(scale)}pct" if scale == int(scale) else f"{scale:.1f}pct".replace(".", "_")
        )
        output_path = input_path.parent / f"{input_path.stem}_{scale_str}{input_path.suffix}"
    else:
        output_path = Path(output)

    # Display operation info
    console.print(
        Panel.fit(
            f"[bold]Scaling Camtasia Project[/bold]\n\n"
            f"Input:  {input_path.name}\n"
            f"Output: {output_path.name}\n"
            f"Scale:  {scale}% ({scale_factor}x)",
            title="[bold cyan]tscprojpy xyscale[/bold cyan]",
        )
    )

    # Create scaler and process file
    scaler = TscprojScaler(scale_factor=scale_factor, verbose=verbose)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Scaling project...", total=None)
            scaler.scale_file(input_path, output_path)
            progress.update(task, completed=True)

        console.print(
            f"\n[bold green]✓[/bold green] Successfully scaled project to '{output_path}'"
        )

    except Exception as e:
        console.print(f"\n[bold red]✗ Error:[/bold red] {e!s}")
        if verbose:
            console.print_exception()
        raise


def main():
    """Main entry point for the CLI."""
    fire.Fire(
        {
            "version": version,
            "hello": hello,
            "xyscale": xyscale,
        }
    )


if __name__ == "__main__":
    main()
