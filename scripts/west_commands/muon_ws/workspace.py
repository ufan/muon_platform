"""Workspace model: reads the west manifest(s) of the current west workspace as plain YAML.

Works in a full hub workspace (manifest repo = `platform`) and in a repo-rooted workspace
(`west init -m <repo url>`, e.g. daq). Outside a west workspace it raises WorkspaceError.
"""

import configparser
import os
from dataclasses import dataclass, field

import yaml

HUB_NAME = "platform"


class WorkspaceError(Exception):
    pass


@dataclass
class Project:
    name: str
    path: str                      # relative to topdir
    url: str = ""
    revision: str = "main"
    groups: list = field(default_factory=list)
    userdata: dict = field(default_factory=dict)
    submodules: bool = False
    remote: str = ""
    is_manifest: bool = False      # the manifest repository itself (west `self`)
    abspath: str = ""

    @property
    def maturity(self):
        return self.userdata.get("maturity", "?")

    @property
    def is_legacy(self):
        return "legacy" in self.groups or self.maturity == "legacy"

    @property
    def informs(self):
        """Projects this legacy project is a reference for (userdata.informs)."""
        return list(self.userdata.get("informs") or [])

    @property
    def cloned(self):
        return os.path.exists(os.path.join(self.abspath, ".git"))


def _find_west_topdir(start):
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, ".west", "config")):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def _load_yaml(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "manifest" not in data:
        raise WorkspaceError(f"{path}: not a west manifest (no 'manifest' key)")
    return data["manifest"]


def _parse_projects(manifest, manifest_path):
    """Return (self_path, [Project], [import-candidates]) from one manifest dict."""
    remotes = {r["name"]: r["url-base"].rstrip("/") for r in manifest.get("remotes", []) or []}
    defaults = manifest.get("defaults", {}) or {}
    d_remote = defaults.get("remote")
    d_rev = defaults.get("revision", "master")
    projects, imports = [], []
    for p in manifest.get("projects", []) or []:
        name = p["name"]
        remote = p.get("remote", d_remote)
        if "url" in p:
            url = p["url"]
        else:
            if remote not in remotes:
                raise WorkspaceError(f"{manifest_path}: project {name}: unknown remote {remote!r}")
            url = f"{remotes[remote]}/{p.get('repo-path', name)}"
        proj = Project(
            name=name,
            path=p.get("path", p.get("repo-path", name)),
            url=url,
            revision=str(p.get("revision", d_rev)),
            groups=list(p.get("groups", []) or []),
            userdata=p.get("userdata") if isinstance(p.get("userdata"), dict) else {},
            submodules=bool(p.get("submodules", False)),
            remote=remote or "",
        )
        projects.append(proj)
        imp = p.get("import")
        if imp:
            imports.append((proj, imp))
    self_path = (manifest.get("self") or {}).get("path")
    group_filter = list(manifest.get("group-filter", []) or [])
    return self_path, projects, imports, group_filter


class Workspace:
    """Resolved view of the projects relevant from a starting directory."""

    def __init__(self, start=None):
        start = os.path.abspath(start or os.getcwd())
        self.start = start
        topdir = _find_west_topdir(start)
        if not topdir:
            raise WorkspaceError("not inside a west workspace; create one with "
                                 "`west init -m <hub or repo url> <dir>` and `west update`")
        self.topdir = topdir
        cfg = configparser.ConfigParser()
        cfg.read(os.path.join(topdir, ".west", "config"))
        mpath = cfg.get("manifest", "path")
        mfile = cfg.get("manifest", "file", fallback="west.yml")
        self.manifest_dir = os.path.join(topdir, mpath)
        self.manifest_file = os.path.join(self.manifest_dir, mfile)
        self.local_group_filter = [g for g in cfg.get("manifest", "group-filter", fallback="").split(",") if g]
        self.projects = []
        self._load()

    def _load(self):
        seen = {}
        manifest_self_name = None
        if os.path.isfile(self.manifest_file):
            m = _load_yaml(self.manifest_file)
            self_path, projects, imports, gf = _parse_projects(m, self.manifest_file)
            self.group_filter = gf
            rel = os.path.relpath(self.manifest_dir, self.topdir)
            manifest_self_name = os.path.basename(self_path or rel)
            selfp = Project(name=manifest_self_name, path=rel, is_manifest=True)
            seen[selfp.name] = selfp
            for p in projects:
                seen.setdefault(p.name, p)       # first definition wins (west semantics)
            # Resolve simple imports from the working tree of imported projects.
            for proj, imp in imports:
                fname = "west.yml" if imp is True else (imp if isinstance(imp, str) else imp.get("file", "west.yml"))
                block = set(imp.get("name-blocklist", [])) if isinstance(imp, dict) else set()
                ipath = os.path.join(self.topdir, proj.path, fname)
                if not os.path.isfile(ipath):
                    continue
                _, iprojects, _, _ = _parse_projects(_load_yaml(ipath), ipath)
                for p in iprojects:
                    if p.name not in block:
                        seen.setdefault(p.name, p)
        else:
            raise WorkspaceError(f"manifest file not found: {self.manifest_file}")
        for p in seen.values():
            p.abspath = os.path.normpath(os.path.join(self.topdir, p.path))
        self._borrow_hub_metadata(seen)
        self.projects = list(seen.values())
        self.manifest_self_name = manifest_self_name

    def _borrow_hub_metadata(self, seen):
        """In a repo-rooted workspace the hub is a plain project and its west.yml is not the
        manifest. West's `self` cannot carry userdata, so projects without userdata (e.g. the
        manifest repo daq) take role/maturity/verify/... from the hub's entry of the same name."""
        hub = seen.get(HUB_NAME)
        if hub is None or hub.is_manifest:
            return
        hub_manifest = os.path.join(hub.abspath, "west.yml")
        if not os.path.isfile(hub_manifest):
            return
        try:
            _, hub_projects, _, _ = _parse_projects(_load_yaml(hub_manifest), hub_manifest)
        except (WorkspaceError, KeyError):
            return
        by_name = {p.name: p for p in hub_projects}
        for p in seen.values():
            src = by_name.get(p.name)
            if src and not p.userdata and src.userdata:
                p.userdata = dict(src.userdata)
            if src and not p.groups and src.groups and not p.is_manifest:
                p.groups = list(src.groups)

    # ---- queries -------------------------------------------------------
    def get(self, name):
        for p in self.projects:
            if p.name == name or p.path == name:
                return p
        return None

    @property
    def hub(self):
        """The platform hub project, found by name (it may or may not be the manifest repo)."""
        return self.get(HUB_NAME)

    def hub_dir(self):
        h = self.hub
        if h and os.path.isdir(os.path.join(h.abspath, ".agents", "skills")):
            return h.abspath
        return None

    def members(self):
        """All projects except the hub, including a non-hub manifest repo."""
        return [p for p in self.projects if p.name != HUB_NAME]

    def is_active(self, p):
        """west group-filter semantics: a project is inactive if all its groups are disabled."""
        if p.is_manifest or not p.groups:
            return True
        enabled = {}
        for g in self.group_filter + self.local_group_filter:
            g = g.strip()
            if g.startswith("-"):
                enabled[g[1:]] = False
            elif g.startswith("+"):
                enabled[g[1:]] = True
        return any(enabled.get(g, True) for g in p.groups)

    def context_projects(self):
        """Non-legacy project(s) the user is working in, judged from the start directory."""
        best = None
        for p in self.projects:
            if (self.start + os.sep).startswith(p.abspath + os.sep) and (best is None or len(p.abspath) > len(best.abspath)):
                best = p
        if best is not None and not best.is_legacy and best.name != HUB_NAME:
            return [best]
        # At the workspace root (or in the hub): every cloned non-legacy project.
        return [p for p in self.members() if not p.is_legacy and p.cloned]

    def legacy_informing(self, names):
        names = set(names)
        return [p for p in self.projects if p.is_legacy and names & set(p.informs)]

    def legacy_projects(self):
        return [p for p in self.projects if p.is_legacy]

    def legacy_build_dir(self, p):
        return os.path.join(self.topdir, ".legacy-build", os.path.basename(p.path))
