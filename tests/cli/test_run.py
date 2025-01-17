from pathlib import Path
from snk.cli.utils import flatten, convert_key_to_snakemake_format
from ..utils import CLIRunner


def test_config_override(local_runner: CLIRunner):
    res = local_runner(
        ["run", "--text", "passed from the cli to overwrite config", "--config", "tests/data/pipeline/config.yaml", "-f"]
    )
    assert res.code == 0, res.stderr
    assert "hello_world" in res.stderr
    assert "passed from the cli to overwrite config" in res.stdout


def test_exit_on_fail(local_runner: CLIRunner):
    res = local_runner(["run", "-f", "error"])
    assert res.code == 1, res.stderr
