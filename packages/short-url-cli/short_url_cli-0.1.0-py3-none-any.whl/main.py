from typing import Optional
from urllib.parse import urlparse

import pyshorteners
import typer
from rich.console import Console
from rich.table import Table

console = Console()

app = typer.Typer(add_completion=False)


def uri_validator(url: str) -> bool:
    """Validate if a URL has proper scheme and netloc."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except (TypeError, ValueError):
        return False


def shorten_url(url: str) -> Optional[str]:
    """Shorten a URL using TinyURL service."""
    try:
        s = pyshorteners.Shortener()
        return s.tinyurl.short(url)
    except Exception:
        return None


def process_multi_urls(multi: str):
    """Process multiple URLs for shortening."""
    if not multi.strip():
        console.print("[bold red]Error:[/bold red] No URLs provided with --multi.")
        raise typer.Exit(1)
    if " " in multi:
        console.print(
            "[bold red]Error:[/bold red] Space-separated URLs are not accepted. Use commas only."
        )
        raise typer.Exit(1)
    url_list = [u.strip() for u in multi.split(",")]
    if any(not u for u in url_list):
        console.print("[bold red]Error:[/bold red] Empty URL detected in the list.")
        raise typer.Exit(1)

    table = Table(title="Shortened URLs")
    table.add_column("Source URL", style="cyan", no_wrap=True)
    table.add_column("Short URL", style="green")
    table.add_column("Warning", style="yellow")

    for u in url_list:
        if not uri_validator(u):
            table.add_row(u, "N/A", "Invalid URL")
        else:
            short = shorten_url(u)
            if short:
                table.add_row(u, short, "")
            else:
                table.add_row(u, "N/A", "Shortening failed")
    console.print(table)


def process_single_url(url: str):
    """Process a single URL for shortening."""
    if not uri_validator(url):
        console.print(f"[bold red]Error:[/bold red] Invalid URL: {url}")
        raise typer.Exit(1)
    short = shorten_url(url)
    if short:
        console.print(f"[bold green]Short URL:[/bold green] {short}")
    else:
        console.print(f"[bold red]Error:[/bold red] Failed to shorten the URL: {url}")


@app.command()
def short_url_cli(
    url: Optional[str] = typer.Argument(
        None,
        help="The URL to shorten. Required unless using --multi.",
    ),
    multi: Optional[str] = typer.Option(
        None,
        "--multi",
        help="Comma-separated list of URLs to shorten. Example: 'https://a.com,https://b.com'",
    ),
):
    """
    A CLI tool to shorten URLs using TinyURL.

    Validation rules:\n
      - At a minimum the URLs must include a scheme (e.g., http, https) and a netloc (represents the domain itself and subdomain if present, the port number, along with an optional credentials in form of username:password.).\n
      - Only comma-separated lists are accepted for --multi (no spaces).\n
      - Whitespace is trimmed from each URL.\n
      - Space-separated URLs are not accepted.\n
    \n
    Examples:\n
      $ short-url-cli https://example.com\n
      $ short-url-cli --multi https://a.com,https://b.com\n
    """
    if multi is not None:
        process_multi_urls(multi)
    else:
        if not url:
            console.print(
                "[bold red]Error:[/bold red] A URL is required unless using --multi."
            )
            raise typer.Exit(1)
        process_single_url(url)


def main():
    """Main entry point for the application."""
    app()


if __name__ == "__main__":
    main()
