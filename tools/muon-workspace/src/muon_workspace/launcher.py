"""The `muon` launcher (developer guide §1): find the workspace, then run *that workspace's* muon.

The globally installed `muon` is only a launcher. Inside a workspace it hands the command to the
implementation in `<workspace>/platform/tools/muon`, run in that project's own uv environment, so
every workspace uses exactly the tool version its platform checkout pins (like Android's `repo`
launcher or Bazelisk). Outside a workspace it only bootstraps (`muon ws init <dir>`).

Standard library only. The hand-over contract is kept stable so the launcher rarely needs upgrading:
`uv run --frozen --project <ws>/platform/tools/muon python -m muon_cli <argv>` with MUON_IMPL=1,
MUON_WORKSPACE=<ws> and MUON_LAUNCHER="<version> <path>" in the environment.
"""

import os
import re
import subprocess
import sys

from . import __version__

IMPL_ENV = "MUON_IMPL"
WS_ENV = "MUON_WORKSPACE"
LAUNCHER_ENV = "MUON_LAUNCHER"            # "<version> <path>", for `muon which` / doctor
MARKER = os.path.join("platform", "repos", "workspace.repos")
IMPL_DIR = os.path.join("platform", "tools", "muon")
DEFAULT_PLATFORM_URL = "git@github.com:ufan/muon_platform.git"
UPGRADE_HINT = "uv tool upgrade muon-workspace"

USAGE = f"""muon {__version__} (launcher)

Outside a workspace:
  muon ws init <dir> [--platform-url URL] [--platform-version REV] [--data-root PATH] [--legacy]
  muon which | --version
Inside a workspace every command runs that workspace's own muon (platform/tools/muon);
`muon --help` there lists them. `-C/--workspace DIR` selects a workspace explicitly.
"""


def find_topdir(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, MARKER)):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def min_launcher(project):
    """`[tool.muon] min-launcher` from the implementation's pyproject.toml, or None."""
    try:
        text = open(os.path.join(project, "pyproject.toml"), encoding="utf-8").read()
    except OSError:
        return None
    section = re.search(r"^\[tool\.muon\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    if not section:
        return None
    m = re.search(r'^min-launcher\s*=\s*"([^"]+)"', section.group(1), re.M)
    return m.group(1) if m else None


def impl_command(project, argv):
    return ["uv", "run", "--quiet", "--frozen", "--project", project, "python", "-m", "muon_cli", *argv]


def delegate(ws, argv, run=subprocess.call):
    project = os.path.join(ws, IMPL_DIR)
    if not os.path.isfile(os.path.join(project, "pyproject.toml")):
        print(f"error: {ws} has no {IMPL_DIR} (is platform cloned?)", file=sys.stderr)
        return 2
    need = min_launcher(project)
    if need and _version_tuple(__version__) < _version_tuple(need):
        print(f"warning: this workspace wants muon launcher >= {need}, you have {__version__}; "
              f"upgrade with: {UPGRADE_HINT}", file=sys.stderr)
    env = dict(os.environ, **{IMPL_ENV: "1", WS_ENV: ws,
                              LAUNCHER_ENV: f"{__version__} {os.path.dirname(os.path.abspath(__file__))}"})
    sys.stdout.flush()                                     # keep our own lines before the implementation's
    return run(impl_command(project, argv), env=env)


def _split_workspace_option(argv):
    """Remove a leading `-C DIR` / `--workspace DIR` and return (dir or None, rest)."""
    if len(argv) >= 2 and argv[0] in ("-C", "--workspace"):
        return os.path.abspath(argv[1]), argv[2:]
    if argv and argv[0].startswith("--workspace="):
        return os.path.abspath(argv[0].split("=", 1)[1]), argv[1:]
    return None, argv


def bootstrap_init(args, run=subprocess.call):
    """`muon ws init <dir> …` outside a workspace: clone platform, then let the new workspace's own
    implementation finish the job (clone the other repos, write .muon/workspace.yml, agent files)."""
    if not args or args[0].startswith("-"):
        print("usage: muon ws init <dir> [--platform-url URL] [--platform-version REV] [--data-root PATH] [--legacy]",
              file=sys.stderr)
        return 2
    top = os.path.abspath(args[0])
    rest = args[1:]
    url, rev = DEFAULT_PLATFORM_URL, "main"
    if "--platform-url" in rest:
        url = rest[rest.index("--platform-url") + 1]
    if "--platform-version" in rest:
        rev = rest[rest.index("--platform-version") + 1]
    plat = os.path.join(top, "platform")
    if not os.path.isdir(os.path.join(plat, ".git")):
        os.makedirs(top, exist_ok=True)
        if run(["git", "clone", "-b", rev, url, plat]) != 0:
            print("error: cloning platform failed", file=sys.stderr)
            return 1
    return delegate(top, ["ws", "init", top, *rest], run=run)


def main(argv=None, run=subprocess.call):
    argv = list(sys.argv[1:] if argv is None else argv)
    explicit, argv = _split_workspace_option(argv)
    if argv[:2] == ["ws", "init"]:
        return bootstrap_init(argv[2:], run=run)
    ws = explicit or (os.path.abspath(os.environ[WS_ENV]) if os.environ.get(WS_ENV) else None) \
        or find_topdir(os.getcwd())
    if argv[:1] in (["--version"], ["which"]):
        print(f"launcher        muon {__version__:8} {os.path.dirname(os.path.abspath(__file__))}")
        if not ws:
            print("workspace       none (not inside a muon workspace)")
            return 0
        return delegate(ws, ["which"], run=run)
    if not ws:
        if not argv or argv[0] in ("-h", "--help"):
            print(USAGE, end="")
            return 0
        print("error: not inside a muon workspace (cd into one, pass -C <dir>, or create one with "
              "`muon ws init <dir>`)", file=sys.stderr)
        return 2
    return delegate(ws, argv, run=run)


if __name__ == "__main__":
    sys.exit(main())
