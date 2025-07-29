import pytest
from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_single_valid_url(monkeypatch):
    monkeypatch.setattr(
        "main.shorten_url",
        lambda url: (
            "http://tinyurl.com/short" if url == "https://example.com" else None
        ),
    )
    result = runner.invoke(app, ["https://example.com"])
    assert "Short URL:" in result.output
    assert "http://tinyurl.com/short" in result.output
    assert result.exit_code == 0


def test_single_invalid_url():
    result = runner.invoke(app, ["not-a-url"])
    assert "Invalid URL" in result.output
    assert result.exit_code != 0


def test_no_url_provided():
    result = runner.invoke(app, [])
    assert "A URL is required" in result.output
    assert result.exit_code != 0


def test_multi_valid(monkeypatch):
    monkeypatch.setattr(
        "main.shorten_url",
        lambda url: (
            f"http://tinyurl.com/{url[-1]}"
            if url.startswith("https://a.com") or url.startswith("https://b.com")
            else None
        ),
    )
    urls = "https://a.com,https://b.com"
    result = runner.invoke(app, ["--multi", urls])
    assert "Shortened URLs" in result.output
    assert "https://a.com" in result.output
    assert "https://b.com" in result.output
    assert "N/A" not in result.output
    assert result.exit_code == 0


def test_multi_with_invalid(monkeypatch):
    monkeypatch.setattr(
        "main.shorten_url",
        lambda url: "http://tinyurl.com/ok" if url == "https://good.com" else None,
    )
    urls = "https://good.com,not-a-url"
    result = runner.invoke(app, ["--multi", urls])
    assert "Shortened URLs" in result.output
    assert "https://good.com" in result.output
    assert "not-a-url" in result.output
    assert "N/A" in result.output
    assert "Invalid URL" in result.output
    assert result.exit_code == 0


def test_multi_empty():
    result = runner.invoke(app, ["--multi", ""])
    assert "No URLs provided" in result.output
    assert result.exit_code != 0


def test_multi_space_separated():
    result = runner.invoke(app, ["--multi", "https://a.com https://b.com"])
    assert "Space-separated URLs are not accepted" in result.output
    assert result.exit_code != 0


def test_multi_with_empty_url():
    result = runner.invoke(app, ["--multi", "https://a.com,"])
    assert "Empty URL detected" in result.output
    assert result.exit_code != 0


def test_help():
    result = runner.invoke(app, ["--help"])
    assert "usage" in result.output.lower()
    assert "multi" in result.output.lower()
    assert "validation" in result.output.lower()
    assert "examples" in result.output.lower()
