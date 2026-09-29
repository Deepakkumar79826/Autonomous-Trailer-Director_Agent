from typer.testing import CliRunner

from trailer_director.main import app


runner = CliRunner()


def test_version_command():
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Autonomous Trailer Director" in result.stdout


def test_help_lists_pipeline_commands():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "run" in result.stdout
    assert "validate" in result.stdout
    assert "recover" in result.stdout
    assert "version" in result.stdout
