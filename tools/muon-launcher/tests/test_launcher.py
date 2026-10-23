"""Tests for the muon launcher (ADR-012 §5): it finds the workspace and runs that workspace's muon."""

import pytest

from muon_launcher import launcher


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch):
    for var in ("MUON_WORKSPACE", "MUON_IMPL", "MUON_LAUNCHER"):
        monkeypatch.delenv(var, raising=False)


def make_ws(path, version="0.2.0", min_launcher=None):
    (path / "platform" / "repos").mkdir(parents=True)
    (path / "platform" / "repos" / "workspace.repos").write_text("repositories: {}\n")
    impl = path / "platform" / "tools" / "muon"
    impl.mkdir(parents=True)
    extra = f'\n[tool.muon]\nmin-launcher = "{min_launcher}"\n' if min_launcher else ""
    impl.joinpath("pyproject.toml").write_text(f'[project]\nname = "muon-cli"\nversion = "{version}"\n{extra}')
    return path


class Recorder:
    def __init__(self, rc=0):
        self.calls, self.rc = [], rc

    def __call__(self, cmd, env=None):
        self.calls.append((cmd, env))
        return self.rc


def test_each_workspace_runs_its_own_implementation(tmp_path, monkeypatch):
    a, b = make_ws(tmp_path / "a"), make_ws(tmp_path / "b")
    (a / "core").mkdir()
    monkeypatch.delenv("MUON_WORKSPACE", raising=False)
    for ws, cwd in ((a, a / "core"), (b, b)):
        run = Recorder()
        monkeypatch.chdir(cwd)
        assert launcher.main(["status"], run=run) == 0
        cmd, env = run.calls[0]
        assert cmd[:6] == ["uv", "run", "--quiet", "--frozen", "--project", str(ws / "platform" / "tools" / "muon")]
        assert cmd[-2:] == ["muon_cli", "status"]
        assert env["MUON_WORKSPACE"] == str(ws) and env["MUON_IMPL"] == "1"


def test_explicit_workspace_option(tmp_path, monkeypatch):
    a = make_ws(tmp_path / "a")
    monkeypatch.chdir(tmp_path)
    run = Recorder()
    assert launcher.main(["-C", str(a), "verify", "core"], run=run) == 0
    assert run.calls[0][1]["MUON_WORKSPACE"] == str(a) and run.calls[0][0][-2:] == ["verify", "core"]


def test_outside_a_workspace_only_bootstrap_works(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MUON_WORKSPACE", raising=False)
    run = Recorder()
    assert launcher.main(["status"], run=run) == 2
    assert "not inside a muon workspace" in capsys.readouterr().err and not run.calls
    assert launcher.main(["which"], run=run) == 0
    assert "workspace       none" in capsys.readouterr().out


def test_ws_init_clones_platform_then_delegates_to_the_new_workspace(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "new"

    def run(cmd, env=None):
        if cmd[:2] == ["git", "clone"]:                    # emulate the clone
            make_ws(target)
            (target / "platform" / ".git").mkdir()
        run.calls.append((cmd, env))
        return 0
    run.calls = []
    assert launcher.main(["ws", "init", str(target), "--data-root", "/d"], run=run) == 0
    clone, impl = run.calls
    assert clone[0][:4] == ["git", "clone", "-b", "main"]
    assert impl[0][-5:] == ["ws", "init", str(target), "--data-root", "/d"]
    assert impl[1]["MUON_WORKSPACE"] == str(target)


def test_old_launcher_warns_but_still_delegates(tmp_path, monkeypatch, capsys):
    a = make_ws(tmp_path / "a", min_launcher="99.0")
    monkeypatch.chdir(a)
    run = Recorder()
    assert launcher.main(["status"], run=run) == 0
    assert "wants muon launcher >= 99.0" in capsys.readouterr().err and run.calls
