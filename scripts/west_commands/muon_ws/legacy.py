"""Managed legacy projects (`west legacy`): checkouts and the L1 read-only lock (ADR-009 §15).

L1 is tool-neutral: it works for every AI coding tool and for humans.
  (a) working tree made read-only (`.git` excluded, so status/fetch still work)
  (b) push disabled on every remote
  (c) local pre-commit / pre-push hooks that refuse
"""

import os
import stat
import subprocess

LOCK_KEY = "muon.legacyLocked"
PUSH_DISABLED = "DISABLED-legacy-read-only"
HOOK_MARKER = "# muon-ws legacy lock"
HOOK_BODY = f"""#!/bin/sh
{HOOK_MARKER}
echo "This is a managed muon legacy project: read-only, no commits or pushes." >&2
echo "See platform/docs/workflow/WORKSPACE_GUIDE.md (Using legacy projects)." >&2
exit 1
"""
HOOKS = ("pre-commit", "pre-push")
WRITE_BITS = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH


def _git(path, *args, check=True):
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} in {path}: {r.stderr.strip()}")
    return r.stdout.strip()


def _walk_worktree(root):
    """Yield (path, is_dir) for every working-tree entry, skipping git metadata."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d != ".git"]
        yield dirpath, True
        for f in filenames:
            if f == ".git":           # submodule gitfile
                continue
            yield os.path.join(dirpath, f), False


def _set_writable(root, writable):
    changed = 0
    for path, _ in _walk_worktree(root):
        try:
            st = os.lstat(path)
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(st.st_mode):
            continue
        mode = stat.S_IMODE(st.st_mode)
        new = (mode | stat.S_IWUSR) if writable else (mode & ~WRITE_BITS)
        if new != mode:
            os.chmod(path, new)
            changed += 1
    return changed


def _hooks_dir(path):
    return os.path.join(path, _git(path, "rev-parse", "--git-path", "hooks"))


def is_locked(path):
    return _git(path, "config", "--get", LOCK_KEY, check=False) == "true"


def _submodule_paths(path):
    out = _git(path, "submodule", "foreach", "--quiet", "--recursive", "pwd", check=False)
    return [l for l in out.splitlines() if l]


def _lock_git(path):
    for remote in filter(None, _git(path, "remote").splitlines()):
        _git(path, "remote", "set-url", "--push", remote, PUSH_DISABLED)
    hooks = _hooks_dir(path)
    if _git(path, "config", "--get", "core.hooksPath", check=False):
        print(f"  warning: {path}: core.hooksPath is set; lock hooks in {hooks} may be bypassed")
    os.makedirs(hooks, exist_ok=True)
    for h in HOOKS:
        hp = os.path.join(hooks, h)
        if os.path.exists(hp) and HOOK_MARKER not in open(hp, encoding="utf-8", errors="replace").read():
            os.replace(hp, hp + ".pre-muon")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(HOOK_BODY)
        os.chmod(hp, 0o755)
    _git(path, "config", LOCK_KEY, "true")


def lock(path):
    """Apply L1 to a legacy checkout and its submodules. Idempotent; uncommitted work is preserved."""
    for p in [path, *_submodule_paths(path)]:
        _lock_git(p)
    return _set_writable(path, False)


def _unlock_git(path):
    for remote in filter(None, _git(path, "remote").splitlines()):
        if _git(path, "config", "--get", f"remote.{remote}.pushurl", check=False) == PUSH_DISABLED:
            _git(path, "config", "--unset", f"remote.{remote}.pushurl")
    hooks = _hooks_dir(path)
    for h in HOOKS:
        hp = os.path.join(hooks, h)
        if os.path.exists(hp) and HOOK_MARKER in open(hp, encoding="utf-8", errors="replace").read():
            os.remove(hp)
            if os.path.exists(hp + ".pre-muon"):
                os.replace(hp + ".pre-muon", hp)
    _git(path, "config", "--unset", LOCK_KEY, check=False)


def unlock(path):
    """Remove L1 (used internally by `west legacy sync --update`)."""
    _set_writable(path, True)
    for p in [path, *_submodule_paths(path)]:
        _unlock_git(p)


def status(path):
    """Return a dict describing the L1 state of a checkout."""
    if not os.path.exists(os.path.join(path, ".git")):
        return {"cloned": False}
    remotes = list(filter(None, _git(path, "remote").splitlines()))
    push_disabled = all(
        _git(path, "config", "--get", f"remote.{r}.pushurl", check=False) == PUSH_DISABLED for r in remotes)
    hooks = _hooks_dir(path)
    hooks_ok = all(os.path.exists(os.path.join(hooks, h)) and
                   HOOK_MARKER in open(os.path.join(hooks, h), encoding="utf-8", errors="replace").read()
                   for h in HOOKS)
    writable = next((p for p, _ in _walk_worktree(path)
                     if not os.path.islink(p) and os.lstat(p).st_mode & WRITE_BITS), None)
    head = _git(path, "rev-parse", "--short", "HEAD", check=False)
    branch = _git(path, "branch", "--show-current", check=False)
    dirty = len(_git(path, "status", "--porcelain", check=False).splitlines())
    return {
        "cloned": True,
        "locked": is_locked(path) and push_disabled and hooks_ok and writable is None,
        "flag": is_locked(path),
        "push_disabled": push_disabled,
        "hooks": hooks_ok,
        "first_writable": writable,
        "head": head,
        "branch": branch,
        "dirty": dirty,
    }


def clone(project):
    os.makedirs(os.path.dirname(project.abspath), exist_ok=True)
    cmd = ["git", "clone", project.url, project.abspath]
    if subprocess.run(cmd).returncode != 0:
        raise RuntimeError(f"clone failed: {project.url}")
    _checkout(project)


def _checkout(project):
    path = project.abspath
    rev = project.revision
    _git(path, "fetch", "--quiet", "origin")
    if _git(path, "rev-parse", "--verify", "--quiet", f"origin/{rev}", check=False):
        _git(path, "checkout", "--quiet", "-B", rev, f"origin/{rev}")
    else:
        _git(path, "checkout", "--quiet", rev)
    if project.submodules:
        _git(path, "submodule", "update", "--init", "--recursive")


def sync(project, update=False):
    """Ensure a legacy reference is present and locked. Returns a short action string."""
    if not project.cloned:
        clone(project)
        lock(project.abspath)
        return "cloned+locked"
    if update:
        st = status(project.abspath)
        if st["dirty"]:
            raise RuntimeError(f"{project.name}: has uncommitted changes; refusing to update (lock only without --update)")
        unlock(project.abspath)
        try:
            _checkout(project)
        finally:
            lock(project.abspath)
        return "updated+locked"
    changed = lock(project.abspath)
    return "locked" + (f" ({changed} entries made read-only)" if changed else "")
