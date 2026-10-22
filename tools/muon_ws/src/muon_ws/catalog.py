"""Project catalog, verification and cross-repo branches (ADR-009 §8, §12)."""

import subprocess

COLUMNS = ["name", "path", "maturity", "groups", "remote", "state", "deploy", "reference_for"]
MD_COLUMNS = ["name", "path", "maturity", "groups", "state", "role", "spec", "reference_for"]


def catalog_rows(ws, projects):
    rows = []
    for p in projects:
        ud = p.userdata
        rows.append({
            "name": p.name,
            "path": p.path,
            "maturity": ud.get("maturity", "manifest" if p.is_manifest else "?"),
            "groups": ",".join(p.groups),
            "remote": f"{p.remote}@{p.revision}" if p.url else "(manifest repo)",
            "state": ("active" if ws.is_active(p) else "inactive") + ("" if p.cloned else ",missing"),
            "deploy": ud.get("deploy", ""),
            "role": ud.get("role", ""),
            "spec": ud.get("spec", ""),
            "reference_for": ",".join(p.reference_for),
        })
    return rows


def markdown_table(rows, columns=MD_COLUMNS):
    code = {"name", "path", "spec"}
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(f"`{r[c]}`" if c in code and r[c] else str(r[c]) for c in columns) + " |")
    return "\n".join(lines)


def text_table(rows, columns=COLUMNS):
    widths = {c: max([len(c)] + [len(r[c]) for r in rows]) for c in columns}
    out = ["  ".join(c.upper().ljust(widths[c]) for c in columns)]
    out += ["  ".join(r[c].ljust(widths[c]) for c in columns) for r in rows]
    return "\n".join(out)


def select(ws, names=(), groups=(), include_inactive=False):
    projects = ws.members()
    if names:
        wanted = set(names)
        projects = [p for p in projects if p.name in wanted or p.path in wanted]
        missing = wanted - {p.name for p in projects} - {p.path for p in projects}
        if missing:
            raise ValueError("unknown project(s): " + ", ".join(sorted(missing)))
    if groups:
        projects = [p for p in projects if set(p.groups) & set(groups)]
    elif not names and not include_inactive:
        projects = [p for p in projects if ws.is_active(p)]
    return projects


def verify(ws, projects, log=print):
    results = []
    for p in projects:
        cmd = p.userdata.get("verify")
        if not cmd:
            results.append((p.name, "no-verify"))
            continue
        if not p.cloned:
            results.append((p.name, "missing"))
            continue
        log(f"=== verify {p.name}: {cmd}")
        rc = subprocess.run(cmd, shell=True, cwd=p.abspath).returncode
        results.append((p.name, "PASS" if rc == 0 else f"FAIL({rc})"))
    log("=== summary")
    for name, status in results:
        log(f"  {status:10} {name}")
    return not any(s.startswith("FAIL") for _, s in results)


def xbranch(ws, projects, branch, dry_run=False, log=print):
    for p in projects:
        if p.is_legacy:
            log(f"{p.name}: legacy, skipped")
            continue
        if not p.cloned:
            log(f"{p.name}: not cloned, skipped")
            continue
        exists = subprocess.run(["git", "rev-parse", "--verify", "--quiet", f"refs/heads/{branch}"],
                                cwd=p.abspath, capture_output=True).returncode == 0
        cmd = ["git", "switch", branch] if exists else ["git", "switch", "-c", branch]
        if dry_run:
            log(f"{p.name}: {' '.join(cmd)}")
            continue
        if subprocess.run(cmd, cwd=p.abspath).returncode != 0:
            raise RuntimeError(f"{p.name}: '{' '.join(cmd)}' failed")
        log(f"{p.name}: on {branch}")
