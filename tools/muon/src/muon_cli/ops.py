"""Workspace operations: sync, status, verify, branch, freeze, doctor (ADR-012).

vcs2l does the cloning; everything else is plain git so that a checkout is never rewritten
behind the developer's back: existing repositories are only fast-forwarded when clean.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

from . import __version__, agents, legacy
from .workspace import REPOS_FILES

RULES_LIMITS = {"root": 3500, "repo": 2500}     # bytes; ADR-012 lean rules
DECISIONS_LIMIT = 30                            # active entries in docs/decisions.md; ADR-012 §8


def git(path, *args, check=False):
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {path}: {r.stderr.strip()}")
    return r.stdout.strip() if r.returncode == 0 else ""


# ---------------------------------------------------------------- sync
def _repos_yaml(repos):
    return yaml.safe_dump({"repositories": {
        r.path: {"type": "git", "url": r.url, "version": r.version} for r in repos}}, sort_keys=False)


def clone_missing(ws, repos, log=print):
    """Clone repositories that are not present yet (vcs import --skip-existing)."""
    missing = [r for r in repos if not r.cloned and r.url]
    if not missing:
        return True
    with tempfile.NamedTemporaryFile("w", suffix=".repos", delete=False) as f:
        f.write(_repos_yaml(missing))
        tmp = f.name
    try:
        log(f"cloning {len(missing)} repositor{'y' if len(missing) == 1 else 'ies'} with vcs2l")
        rc = subprocess.run(["vcs", "import", "--skip-existing", "--recursive", "--input", tmp, ws.topdir]).returncode
    finally:
        os.unlink(tmp)
    return rc == 0


def fast_forward(r, log=print):
    """Fast-forward a clean checkout whose current branch is the pinned branch."""
    if git(r.abspath, "status", "--porcelain"):
        return "dirty, skipped"
    branch = git(r.abspath, "branch", "--show-current")
    if not branch:
        return "detached, skipped"
    if branch != r.version:
        return f"on {branch} (pinned {r.version}), skipped"
    if subprocess.run(["git", "-C", r.abspath, "pull", "--ff-only", "--quiet"]).returncode != 0:
        return "pull --ff-only failed"
    return "fast-forwarded"


def sync(ws, update=False, with_legacy=None, log=print):
    ok = clone_missing(ws, [r for r in ws.repos if not r.is_legacy], log)
    if update:
        for r in ws.repos:
            if not r.is_legacy and r.cloned:
                log(f"  {r.path}: {fast_forward(r)}")
    targets = ws.legacy_repos() if with_legacy else [r for r in ws.legacy_repos() if r.cloned]
    for r in targets:
        try:
            log(f"  {r.path}: {legacy.sync(r, update=update)}")
        except RuntimeError as e:
            log(f"  {r.path}: ERROR {e}")
            ok = False
    return ok


# ---------------------------------------------------------------- status
def repo_status(r):
    if not r.cloned:
        return {"path": r.path, "state": "missing"}
    branch = git(r.abspath, "branch", "--show-current") or "(detached " + git(r.abspath, "rev-parse", "--short", "HEAD") + ")"
    dirty = len(git(r.abspath, "status", "--porcelain").splitlines())
    ahead = behind = ""
    counts = git(r.abspath, "rev-list", "--left-right", "--count", "@{upstream}...HEAD")
    if counts:
        b, a = counts.split()
        ahead, behind = int(a), int(b)
    drift = ""
    if r.version and not r.is_legacy and git(r.abspath, "branch", "--show-current") != r.version:
        drift = f"pinned {r.version}"
    if r.is_legacy:
        st = legacy.status(r.abspath)
        drift = "LOCKED" if st["locked"] else "UNLOCKED"
    return {"path": r.path, "state": "ok", "branch": branch, "dirty": dirty, "ahead": ahead, "behind": behind,
            "note": drift}


def format_status(rows):
    """One line per repo; counts are spelled out so that people and agents cannot misread empty columns."""
    out = []
    for s in rows:
        if s["state"] == "missing":
            out.append(f"{s['path']:26} not cloned")
            continue
        facts = [f"{n} {k}" for k, n in (("dirty", s["dirty"]), ("ahead", s["ahead"]), ("behind", s["behind"])) if n]
        facts += [s["note"]] if s["note"] else []
        out.append(f"{s['path']:26} {s['branch']:24} {', '.join(facts) or 'clean'}")
    return "\n".join(out)


# ---------------------------------------------------------------- verify
def verify(repos, log=print):
    results = []
    for r in repos:
        cmd = r.meta.get("verify")
        if not cmd:
            results.append((r.path, "no-verify"))
            continue
        if not r.cloned:
            results.append((r.path, "missing"))
            continue
        log(f"=== verify {r.path}: {cmd}")
        rc = subprocess.run(cmd, shell=True, cwd=r.abspath).returncode
        results.append((r.path, "PASS" if rc == 0 else f"FAIL({rc})"))
    log("=== summary")
    for path, status in results:
        log(f"  {status:10} {path}")
    return not any(s.startswith("FAIL") for _, s in results)


# ---------------------------------------------------------------- branch
def branch(repos, name, log=print):
    for r in repos:
        if r.is_legacy:
            log(f"{r.path}: legacy, skipped")
            continue
        if not r.cloned:
            log(f"{r.path}: not cloned, skipped")
            continue
        exists = bool(git(r.abspath, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}"))
        cmd = ["switch", name] if exists else ["switch", "-c", name]
        if subprocess.run(["git", "-C", r.abspath, *cmd]).returncode != 0:
            raise RuntimeError(f"{r.path}: 'git {' '.join(cmd)}' failed")
        log(f"{r.path}: on {name}")


# ---------------------------------------------------------------- freeze
def freeze(ws, repos):
    """Exact SHAs of the given repositories in vcs2l format (a platform snapshot / BOM)."""
    out = {}
    for r in repos:
        if not r.cloned:
            continue
        url = git(r.abspath, "remote", "get-url", "origin") or r.url
        out[r.path] = {"type": "git", "url": url, "version": git(r.abspath, "rev-parse", "HEAD")}
        if git(r.abspath, "status", "--porcelain"):
            out[r.path]["muon"] = {"dirty": True}
    return yaml.safe_dump({"repositories": out}, sort_keys=False)


# ---------------------------------------------------------------- which / launcher
def _version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def launcher_info():
    """(version, path) of the launcher that started us, or (None, None) when run directly."""
    raw = os.environ.get("MUON_LAUNCHER", "")
    return tuple(raw.split(" ", 1)) if " " in raw else (None, None)


def min_launcher(ws):
    try:
        text = open(os.path.join(ws.topdir, "platform", "tools", "muon", "pyproject.toml"), encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(r'^min-launcher\s*=\s*"([^"]+)"', text, re.M)
    return m.group(1) if m else None


def which(ws, impl_dir):
    lv, lp = launcher_info()
    plat = os.path.join(ws.topdir, "platform")
    rev = git(plat, "rev-parse", "--short", "HEAD") or "?"
    dirty = "dirty" if git(plat, "status", "--porcelain") else "clean"
    root, source = ws.data_root
    lines = []
    if not lv:
        lines.append("launcher        none (implementation run directly)")
    lines += [
        f"workspace       {ws.topdir}",
        f"implementation  muon {__version__:8} {impl_dir}  (platform {rev}, {dirty})",
        f"data root       {root or '-'}  ({source}{'' if root and os.path.isdir(root) else ', missing'})",
    ]
    return "\n".join(lines)


AGY_SETTINGS = os.path.expanduser("~/.gemini/antigravity-cli/settings.json")


# ---------------------------------------------------------------- doctor
def doctor(ws, log=print):
    problems = 0

    def check(ok, msg, hint=""):
        nonlocal problems
        log(f"  [{'ok' if ok else '!!'}] {msg}" + (f"  -> {hint}" if not ok and hint else ""))
        problems += 0 if ok else 1

    def advise(ok, msg, hint):
        log(f"  [{'ok' if ok else '--'}] {msg}" + ("" if ok else f"  -> {hint}"))

    log(f"workspace: {ws.topdir}")
    impl = os.path.dirname(os.path.abspath(__file__))
    own = os.path.join(ws.topdir, "platform", "tools", "muon")
    check(os.path.commonpath([impl, own]) == own, f"implementation is this workspace's ({impl})",
          "run muon through the launcher (muon-workspace), not an installed copy")
    lv, _ = launcher_info()
    need = min_launcher(ws)
    if lv:
        check(not need or _version_tuple(lv) >= _version_tuple(need), f"launcher {lv} (workspace needs >= {need or '-'})",
              "uv tool upgrade muon-workspace")
    else:
        advise(False, "started without the launcher", "install muon-workspace (DEVELOPER_GUIDE §1)")
    for tool in ("git", "vcs", "cmake"):
        check(shutil.which(tool) is not None, f"{tool} on PATH", "see DEVELOPER_GUIDE §1")
    check(sys.version_info >= (3, 9), f"python {sys.version.split()[0]}")
    for rel in REPOS_FILES[:2]:
        check(os.path.isfile(os.path.join(ws.topdir, rel)), rel)
    for r in ws.repos:
        if r.is_legacy:
            if r.cloned:
                check(legacy.status(r.abspath)["locked"], f"{r.path} locked", "muon ws sync")
            continue
        check(r.cloned, f"{r.path} cloned", "muon ws sync")
    stale = agents.run(agents.build_plan(ws), check=True, log=lambda *_: None)
    check(not stale, "agent files up to date", "muon agents sync")
    root, source = ws.data_root
    check(bool(root) and os.path.isdir(root), f"golden test data root: {root or '-'} ({source})",
          "copy golden bytes, or set data_root in .muon/workspace.yml (DEVELOPER_GUIDE §1)")
    if os.path.isfile(AGY_SETTINGS):
        try:
            allow = json.load(open(AGY_SETTINGS, encoding="utf-8")).get("permissions", {}).get("allow", [])
        except ValueError:
            allow = []
        rule = f"read_file({ws.topdir})"
        advise(rule in allow, "Antigravity (agy) may read this workspace",
               f'add "{rule}" to permissions.allow in {AGY_SETTINGS}')
    for path, limit in rules_files(ws):
        size = os.path.getsize(path)
        check(size <= limit, f"{os.path.relpath(path, ws.topdir)} {size} B (limit {limit})", "keep AGENTS.md lean (ADR-012)")
    active = active_decisions(ws)
    if active is not None:
        advise(active <= DECISIONS_LIMIT, f"docs/decisions.md {active} active entries (limit {DECISIONS_LIMIT})",
               "fold entries into their home documents and docs/decisions/<year>.md (ADR-012 §8)")
    return problems == 0


def active_decisions(ws):
    """Number of dated entries in the active decision log, or None without a platform checkout."""
    if not ws.hub:
        return None
    try:
        text = open(os.path.join(ws.hub.abspath, "docs", "decisions.md"), encoding="utf-8").read()
    except OSError:
        return None
    return len(re.findall(r"^- \d{4}-\d{2}-\d{2}\b", text, re.M))


def rules_files(ws):
    hub = ws.hub
    out = []
    if hub and os.path.isfile(os.path.join(hub.abspath, "AGENTS.md")):
        out.append((os.path.join(hub.abspath, "AGENTS.md"), RULES_LIMITS["root"]))
    for r in ws.repos:
        if not (r.is_dev and r.cloned) or r is hub:
            continue
        # The repo's own rules and one level of module rules (e.g. core/daq/AGENTS.md).
        candidates = [os.path.join(r.abspath, "AGENTS.md")] + sorted(
            os.path.join(r.abspath, d, "AGENTS.md") for d in os.listdir(r.abspath)
            if not d.startswith(".") and os.path.isdir(os.path.join(r.abspath, d)))
        out += [(p, RULES_LIMITS["repo"]) for p in candidates if os.path.isfile(p)]
    return out
