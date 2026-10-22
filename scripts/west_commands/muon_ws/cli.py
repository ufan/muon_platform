"""Internal argument dispatcher for the muon west extension commands (`west <cmd> ...`)."""

import argparse
import sys


from . import agents, catalog, legacy
from .workspace import Workspace, WorkspaceError


def _selection(parser):
    parser.add_argument("projects", nargs="*", metavar="PROJECT", help="project names or paths")
    parser.add_argument("-g", "--group", action="append", default=[], help="select projects in GROUP (repeatable)")


def build_parser():
    ap = argparse.ArgumentParser(prog="west", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("legacy", help="managed legacy projects: clone, read-only lock, status (ADR-009 §15)")
    rs = r.add_subparsers(dest="legacy_cmd", required=True)
    rs.add_parser("list", help="list managed legacy projects, what they inform, and their state")
    s = rs.add_parser("sync", help="clone and lock the legacy projects that inform the current project(s)")
    s.add_argument("names", nargs="*", help="legacy projects (default: those that inform the current project)")
    s.add_argument("--all", action="store_true", help="all legacy projects in the manifest")
    s.add_argument("--update", action="store_true", help="move clean checkouts to the pinned revision")
    st = rs.add_parser("status", help="show the lock state of legacy projects")
    st.add_argument("names", nargs="*")
    st.add_argument("--all", action="store_true")
    b = rs.add_parser("build-dir", help="print the out-of-tree build directory for a legacy project")
    b.add_argument("name")

    a = sub.add_parser("agents", help="generated agent files for all AI tools (ADR-009 §14)")
    asub = a.add_subparsers(dest="agents_cmd", required=True)
    sy = asub.add_parser("sync", help="generate shims, skill links and tool adapters")
    sy.add_argument("--check", action="store_true", help="exit non-zero if anything is stale")
    sy.add_argument("--force", action="store_true", help="replace a hand-written root AGENTS.md (kept as .orig)")
    asub.add_parser("adapters", help="list per-tool adapter status")

    c = sub.add_parser("catalog", help="list projects")
    _selection(c)
    c.add_argument("-a", "--all", action="store_true", help="include inactive projects")
    c.add_argument("--markdown", action="store_true")

    v = sub.add_parser("verify", help="run each project's userdata.verify command")
    _selection(v)

    x = sub.add_parser("xbranch", help="create or switch to a topic branch across projects")
    x.add_argument("branch")
    _selection(x)
    x.add_argument("-n", "--dry-run", action="store_true")
    return ap


def _legacy_targets(ws, args):
    if args.all:
        return ws.legacy_projects()
    if args.names:
        out = []
        for n in args.names:
            p = ws.get(n)
            if p is None or not p.is_legacy:
                raise ValueError(f"{n}: not a legacy project in this manifest")
            out.append(p)
        return out
    ctx = ws.context_projects()
    return ws.legacy_informing([p.name for p in ctx])


def cmd_legacy(ws, args):
    if args.legacy_cmd == "build-dir":
        p = ws.get(args.name)
        if p is None or not p.is_legacy:
            raise ValueError(f"{args.name}: not a legacy project")
        print(ws.legacy_build_dir(p))
        return 0
    if args.legacy_cmd == "list":
        for p in ws.legacy_projects():
            st = legacy.status(p.abspath)
            state = "missing" if not st["cloned"] else ("LOCKED" if st["locked"] else "UNLOCKED")
            print(f"  {p.name:24} {state:9} {p.path:26} informs: {', '.join(p.informs) or '-'}")
        print("  (host-local archive trees are not managed: see platform/docs/legacy_inventory.md)")
        return 0
    targets = _legacy_targets(ws, args)
    if not targets:
        print("no legacy projects inform this context (see `informs` in the manifest)")
        return 0
    if args.legacy_cmd == "status":
        for p in targets:
            s = legacy.status(p.abspath)
            if not s["cloned"]:
                print(f"  {p.name:24} missing    {p.path}")
                continue
            state = "LOCKED" if s["locked"] else "UNLOCKED"
            print(f"  {p.name:24} {state:9} {p.path}  push_disabled={s['push_disabled']} hooks={s['hooks']} "
                  f"read_only={s['first_writable'] is None} {s['branch'] or s['head']} (pinned {p.revision}) dirty={s['dirty']}")
        return 0 if all(legacy.status(p.abspath).get("locked", True) or not legacy.status(p.abspath)["cloned"]
                        for p in targets) else 1
    rc = 0
    for p in targets:
        try:
            print(f"  {p.name}: {legacy.sync(p, update=args.update)}  ({p.path})")
        except RuntimeError as e:
            print(f"  {p.name}: ERROR {e}")
            rc = 1
    return rc


def cmd_agents(ws, args):
    if args.agents_cmd == "adapters":
        for k, v in agents.ADAPTERS.items():
            print(f"  {k:12} {v}")
        return 0
    hub = agents.hub_source(ws)
    plan = agents.build_plan(ws, hub)
    stale = agents.run(plan, check=args.check, force=args.force)
    if args.check:
        if stale:
            print("stale:\n  " + "\n  ".join(stale) + "\n(run `west agents-sync`)")
            return 1
        print("agent files are up to date")
    elif not stale:
        print("agent files are up to date")
    return 0


def main(argv=None, start=None):
    args = build_parser().parse_args(argv)
    try:
        ws = Workspace(start)
        if args.cmd == "legacy":
            return cmd_legacy(ws, args)
        if args.cmd == "agents":
            return cmd_agents(ws, args)
        if args.cmd == "catalog":
            if args.all and not args.projects and not args.group:
                projects = ws.members()
            else:
                projects = catalog.select(ws, args.projects, args.group)
            rows = catalog.catalog_rows(ws, projects)
            print(catalog.markdown_table(rows) if args.markdown else catalog.text_table(rows))
            return 0
        if args.cmd == "verify":
            return 0 if catalog.verify(ws, catalog.select(ws, args.projects, args.group)) else 1
        if args.cmd == "xbranch":
            if not args.projects and not args.group:
                raise ValueError("name the projects or groups to branch (cross-repo changes are explicit)")
            catalog.xbranch(ws, catalog.select(ws, args.projects, args.group), args.branch, args.dry_run)
            return 0
    except (WorkspaceError, ValueError, RuntimeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
