"""Test the CLI."""
from click.testing import CliRunner


def test_cli_entry_error():
    from keep2roam.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli)
    assert result.exit_code == 2  # need source and dst
    assert "Usage: cli" in result.output


def test_cli_entry(monkeypatch):
    from keep2roam.cli import cli

    monkeypatch.setattr("keep2roam.convert", lambda x, y: 0)
    runner = CliRunner()
    result = runner.invoke(cli, args=[".", "."])
    assert result.exit_code == 0


def test_cli_version(monkeypatch):
    monkeypatch.setattr("keep2roam.cli.get_version", lambda: "0.x")
    from keep2roam.cli import cli

    runner = CliRunner()
    result = runner.invoke(cli, args=["--version"])
    assert result.exit_code == 0
    assert "0.x" in result.output
