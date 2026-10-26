"""Workspace model: the vcs2l `.repos` files in platform/repos/ plus per-repo metadata (engineering process §6).

A workspace is a plain directory with `platform/` in it; no tool state. Repositories come from,
in order (later entries for the same path win):

  platform/repos/workspace.repos   active and support repositories (includes platform itself)
  platform/repos/legacy.repos      managed legacy repositories (read-only, locked)
  <topdir>/local.repos             optional per-host overrides, never committed

Metadata of a repository is its optional `muon:` block in the `.repos` entry, overridden by
`<repo>/.muon/repo.yml` when the repository carries one.
"""

import os
from dataclasses import dataclass, field

import yaml

HUB = "platform"
REPOS_FILES = ("platform/repos/workspace.repos", "platform/repos/legacy.repos", "local.repos")
META_FILE = os.path.join(".muon", "repo.yml")
CONFIG_FILE = os.path.join(".muon", "workspace.yml")   # per workspace, never committed (topdir is not a repo)
DEV_MATURITIES = ("incubating", "active", "stable")


class WorkspaceError(Exception):
    pass


@dataclass
class Repo:
    path: str                      # relative to topdir; the vcs2l key
    url: str = ""
    version: str = ""
    meta: dict = field(default_factory=dict)
    source: str = ""               # the .repos file that defined it
    abspath: str = ""

    @property
    def name(self):
        return self.meta.get("name") or os.path.basename(self.path)

    @property
    def maturity(self):
        return self.meta.get("maturity", "?")

    @property
    def is_legacy(self):
        return self.maturity == "legacy"

    @property
    def is_dev(self):
        return self.maturity in DEV_MATURITIES

    @property
    def informs(self):
        return list(self.meta.get("informs") or [])

    @property
    def cloned(self):
        return os.path.exists(os.path.join(self.abspath, ".git"))


def find_topdir(start=None):
    env = os.environ.get("MUON_WORKSPACE")
    if env:
        return os.path.abspath(env)
    d = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.isfile(os.path.join(d, REPOS_FILES[0])):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            return None
        d = parent


def load_repos_file(path):
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    repos = data.get("repositories")
    if not isinstance(repos, dict):
        raise WorkspaceError(f"{path}: no 'repositories' mapping (vcs2l format)")
    return repos


class Workspace:
    def __init__(self, start=None, topdir=None):
        self.start = os.path.abspath(start or os.getcwd())
        self.topdir = topdir or find_topdir(self.start)
        if not self.topdir:
            raise WorkspaceError("not inside a muon workspace (no platform/repos/workspace.repos above "
                                 "this directory); create one with `muon ws init <dir>`")
        self.repos = []
        self.config = {}
        cf = os.path.join(self.topdir, CONFIG_FILE)
        if os.path.isfile(cf):
            with open(cf, encoding="utf-8") as fh:
                self.config = yaml.safe_load(fh) or {}
        self._load()

    def _load(self):
        by_path = {}
        for rel in REPOS_FILES:
            f = os.path.join(self.topdir, rel)
            if not os.path.isfile(f):
                continue
            for path, entry in load_repos_file(f).items():
                entry = entry or {}
                r = by_path.get(path) or Repo(path=path)
                r.url = entry.get("url", r.url)
                r.version = str(entry.get("version", r.version) or "")
                r.meta = {**r.meta, **(entry.get("muon") or {})}
                r.source = rel
                by_path[path] = r
        for r in by_path.values():
            r.abspath = os.path.normpath(os.path.join(self.topdir, r.path))
            mf = os.path.join(r.abspath, META_FILE)
            if os.path.isfile(mf):
                with open(mf, encoding="utf-8") as fh:
                    r.meta = {**r.meta, **(yaml.safe_load(fh) or {})}
        self.repos = list(by_path.values())

    @property
    def data_root(self):
        """(path, source) of the golden test data (ADR-011): $MUON_DATA_ROOT, then
        .muon/workspace.yml `data_root`, then <testdata>/golden; path is None if none applies."""
        if os.environ.get("MUON_DATA_ROOT"):
            return os.path.abspath(os.environ["MUON_DATA_ROOT"]), "MUON_DATA_ROOT"
        if self.config.get("data_root"):
            return os.path.abspath(os.path.expanduser(str(self.config["data_root"]))), CONFIG_FILE
        td = self.get("testdata")
        if td:
            return os.path.join(td.abspath, "golden"), "testdata/golden (default)"
        return None, "none"

    # ---- queries -------------------------------------------------------
    def get(self, key):
        for r in self.repos:
            if key in (r.name, r.path):
                return r
        return None

    @property
    def hub(self):
        return self.get(HUB)

    def hub_dir(self):
        h = self.hub
        if h and os.path.isdir(os.path.join(h.abspath, ".agents", "skills")):
            return h.abspath
        return None

    def members(self):
        return [r for r in self.repos if r.path != HUB]

    def legacy_repos(self):
        return [r for r in self.repos if r.is_legacy]

    def legacy_informing(self, names):
        names = set(names)
        return [r for r in self.repos if r.is_legacy and names & set(r.informs)]

    def legacy_build_dir(self, r):
        return os.path.join(self.topdir, ".legacy-build", os.path.basename(r.path))

    def context_repos(self):
        """The non-legacy repo the user is working in, judged from the start directory;
        at the workspace root or in the hub: every cloned non-legacy repo."""
        best = None
        for r in self.repos:
            if (self.start + os.sep).startswith(r.abspath + os.sep) and (best is None or len(r.abspath) > len(best.abspath)):
                best = r
        if best is not None and not best.is_legacy and best.path != HUB:
            return [best]
        return [r for r in self.members() if not r.is_legacy and r.cloned]

    def select(self, keys=(), include_legacy=False):
        if keys:
            out = []
            for k in keys:
                r = self.get(k)
                if r is None:
                    raise ValueError(f"unknown repository: {k}")
                out.append(r)
            return out
        return [r for r in self.repos if include_legacy or not r.is_legacy]
