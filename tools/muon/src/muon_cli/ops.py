"""Workspace operations: sync, status, verify, branch, freeze, doctor (ADR-012).

vcs2l does the cloning; everything else is plain git so that a checkout is never rewritten
behind the developer's back: existing repositories are only fast-forwarded when clean.
"""

import os
import shutil
import subprocess
import sys
import tempfile

import yaml

from . import agents, legacy
from .workspace import REPOS_FILES

RULES_LIMITS = {"root": 3500, "repo": 2500}     # bytes; ADR-012 lean rules


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
    out = [f"{'REPO':26} {'BRANCH':28} {'DIRTY':>5} {'AHEAD':>5} {'BEHIND':>6}  NOTE"]
    for s in rows:
        if s["state"] == "missing":
            out.append(f"{s['path']:26} {'(not cloned)':28}")
            continue
        out.append(f"{s['path']:26} {s['branch'][:28]:28} {s['dirty'] or '':>5} {s['ahead'] or '':>5} "
                   f"{s['behind'] or '':>6}  {s['note']}")
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


# ---------------------------------------------------------------- doctor
def doctor(ws, log=print):
    problems = 0

    def check(ok, msg, hint=""):
        nonlocal problems
        log(f"  [{'ok' if ok else '!!'}] {msg}" + (f"  -> {hint}" if not ok and hint else ""))
        problems += 0 if ok else 1

    log(f"workspace: {ws.topdir}")
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
    root = agents.test_data_root(ws)
    check(bool(root) and os.path.isdir(root), f"golden test data root: {root or '-'}",
          "copy golden bytes or set MUON_DATA_ROOT (testdata/README.md)")
    for path, limit in rules_files(ws):
        size = os.path.getsize(path)
        check(size <= limit, f"{os.path.relpath(path, ws.topdir)} {size} B (limit {limit})", "keep AGENTS.md lean (ADR-012)")
    return problems == 0


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
