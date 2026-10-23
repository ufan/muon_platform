"""muon: workspace tool of the muon platform (ADR-012).

This is the implementation pinned by each workspace (platform/tools/muon). Run it through the global
`muon` launcher (package muon-launcher), which picks the implementation of the workspace you are in.
The workspace is defined by vcs2l `.repos` files in platform/repos/. This tool clones them, keeps
legacy references locked read-only, runs verification, and generates agent files. Nothing here is
needed to build or test a single repository.
"""

import argparse
import datetime
import os
import subprocess
import sys

import yaml

from . import __version__, agents, legacy, ops
from .workspace import CONFIG_FILE, Workspace, WorkspaceError

IMPL_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_PLATFORM_URL = "git@github.com:ufan/muon_platform.git"


def build_parser():
    ap = argparse.ArgumentParser(prog="muon", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"implementation  muon {__version__:8} {IMPL_DIR}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    w = sub.add_parser("ws", help="create or update the workspace")
    ws = w.add_subparsers(dest="ws_cmd", required=True)
    i = ws.add_parser("init", help="create a workspace: clone platform, then everything in platform/repos")
    i.add_argument("dir")
    i.add_argument("--platform-url", default=DEFAULT_PLATFORM_URL)
    i.add_argument("--platform-version", default="main")
    i.add_argument("--legacy", action="store_true", help="also clone the legacy references")
    i.add_argument("--data-root", help="golden test data of this workspace (e.g. a copy shared on this host)")
    s = ws.add_parser("sync", help="clone missing repos, re-apply legacy locks")
    s.add_argument("--update", action="store_true", help="fast-forward clean repos that are on their pinned branch")
    s.add_argument("--legacy", action="store_true", help="also clone legacy references that are missing")

    st = sub.add_parser("status", help="branch, dirty, ahead/behind and pin drift of every repo")
    st.add_argument("repos", nargs="*")

    v = sub.add_parser("verify", help="run each repo's verify command (.muon/repo.yml)")
    v.add_argument("repos", nargs="*")

    b = sub.add_parser("branch", help="create or switch to the same branch in several repos")
    b.add_argument("name")
    b.add_argument("repos", nargs="+")

    f = sub.add_parser("freeze", help="print exact SHAs of all repos (vcs2l format)")
    f.add_argument("-o", "--output")
    f.add_argument("--legacy", action="store_true", help="include legacy references")

    sub.add_parser("doctor", help="check tools, workspace, locks, agent files and test data")
    sub.add_parser("which", help="show the launcher, workspace, implementation and data root in use")
    sub.add_parser("list", help="list repositories with maturity, role and informs")

    a = sub.add_parser("agents", help="generated agent files for all AI tools")
    asub = a.add_subparsers(dest="agents_cmd", required=True)
    sy = asub.add_parser("sync", help="generate shims, skill links and tool adapters")
    sy.add_argument("--check", action="store_true", help="exit non-zero if anything is stale")
    sy.add_argument("--force", action="store_true", help="replace a hand-written root AGENTS.md (kept as .orig)")
    asub.add_parser("adapters", help="list per-tool adapter status")

    lg = sub.add_parser("legacy", help="legacy references: list, status, build-dir")
    ls = lg.add_subparsers(dest="legacy_cmd", required=True)
    ls.add_parser("list")
    ls.add_parser("status")
    bd = ls.add_parser("build-dir", help="out-of-tree build directory for a legacy repo")
    bd.add_argument("name")

    td = sub.add_parser("testdata", help="pass-through to testdata/tools/testdata.py", add_help=False)
    td.add_argument("args", nargs=argparse.REMAINDER)
    return ap


def cmd_init(args):
    top = os.path.abspath(args.dir)
    os.makedirs(top, exist_ok=True)
    plat = os.path.join(top, "platform")
    if not os.path.isdir(os.path.join(plat, ".git")):
        if subprocess.run(["git", "clone", "-b", args.platform_version, args.platform_url, plat]).returncode:
            raise RuntimeError("cloning platform failed")
    cf = os.path.join(top, CONFIG_FILE)
    if not os.path.isfile(cf):
        os.makedirs(os.path.dirname(cf), exist_ok=True)
        cfg = {"name": os.path.basename(top), "created": datetime.date.today().isoformat()}
        if args.data_root:
            cfg["data_root"] = os.path.abspath(os.path.expanduser(args.data_root))
        with open(cf, "w", encoding="utf-8") as fh:
            fh.write("# This workspace's settings (ADR-012 §5); not committed anywhere.\n")
            yaml.safe_dump(cfg, fh, sort_keys=False)
    ws = Workspace(topdir=top)
    ok = ops.sync(ws, with_legacy=args.legacy)
    ws = Workspace(topdir=top)
    agents.run(agents.build_plan(ws))
    print(f"workspace ready: {top}\nnext: cd {top} && muon doctor")
    return 0 if ok else 1


def cmd_legacy(ws, args):
    if args.legacy_cmd == "build-dir":
        r = ws.get(args.name)
        if r is None or not r.is_legacy:
            raise ValueError(f"{args.name}: not a legacy repository")
        print(ws.legacy_build_dir(r))
        return 0
    rc = 0
    for r in ws.legacy_repos():
        if not r.cloned:
            print(f"  {r.path:26} missing    informs: {', '.join(r.informs) or '-'}")
            continue
        s = legacy.status(r.abspath)
        state = "LOCKED" if s["locked"] else "UNLOCKED"
        rc |= 0 if s["locked"] else 1
        extra = (f" push_disabled={s['push_disabled']} hooks={s['hooks']} read_only={s['first_writable'] is None}"
                 if args.legacy_cmd == "status" else "")
        print(f"  {r.path:26} {state:9} informs: {', '.join(r.informs) or '-'}{extra}")
    print("  (host-local archive/ trees are not managed: see platform/docs/legacy_inventory.md)")
    return rc


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.cmd == "ws" and args.ws_cmd == "init":
            return cmd_init(args)
        ws = Workspace()
        if args.cmd == "ws":
            return 0 if ops.sync(ws, update=args.update, with_legacy=args.legacy) else 1
        if args.cmd == "status":
            print(ops.format_status([ops.repo_status(r) for r in ws.select(args.repos, include_legacy=True)]))
            return 0
        if args.cmd == "verify":
            return 0 if ops.verify(ws.select(args.repos)) else 1
        if args.cmd == "branch":
            ops.branch(ws.select(args.repos), args.name)
            return 0
        if args.cmd == "freeze":
            text = ops.freeze(ws, ws.select(include_legacy=args.legacy))
            if args.output:
                with open(args.output, "w", encoding="utf-8") as fh:
                    fh.write(text)
            else:
                print(text, end="")
            return 0
        if args.cmd == "which":
            print(ops.which(ws, IMPL_DIR))
            return 0
        if args.cmd == "doctor":
            return 0 if ops.doctor(ws) else 1
        if args.cmd == "list":
            for r in sorted(ws.repos, key=lambda r: (r.is_legacy, r.path)):
                inf = f"  informs: {', '.join(r.informs)}" if r.informs else ""
                print(f"  {r.path:26} {r.maturity:11} {r.meta.get('role', '')}{inf}")
            return 0
        if args.cmd == "agents":
            if args.agents_cmd == "adapters":
                for k, v in agents.ADAPTERS.items():
                    print(f"  {k:12} {v}")
                return 0
            stale = agents.run(agents.build_plan(ws), check=args.check, force=args.force)
            if args.check and stale:
                print("stale:\n  " + "\n  ".join(stale) + "\n(run `muon agents sync`)")
                return 1
            if not stale or args.check:
                print("agent files are up to date")
            return 0
        if args.cmd == "legacy":
            return cmd_legacy(ws, args)
        if args.cmd == "testdata":
            td = ws.get("testdata")
            if td is None or not td.cloned:
                raise ValueError("testdata is not cloned (muon ws sync)")
            tool = os.path.join(td.abspath, "tools", "testdata.py")
            env = dict(os.environ)
            root, _ = ws.data_root
            if root:
                env["MUON_DATA_ROOT"] = root
            return subprocess.run([sys.executable, tool, *args.args], env=env).returncode
    except (WorkspaceError, ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
