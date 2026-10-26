# Release Guide

Status: current.

How to release the parts of the muon platform that are versioned and distributed. Rules behind
this: [engineering process](engineering_process.md). Day-to-day work:
[developer guide](developer_guide.md).

| What | Where | Distributed as | Who uses which version |
|---|---|---|---|
| Launcher | `platform/tools/muon-workspace` | PyPI package [`muon-workspace`](https://pypi.org/project/muon-workspace/), command `muon` | one per host, upgraded rarely |
| Implementation (the workspace tool) | `platform/tools/muon` | **not published** | each workspace runs the copy in its own platform checkout |
| Product software (core, domains, instruments) | their repositories | tags; instrument BOM later (engineering process §5) | not covered here yet |

## 1. Release the launcher (`muon-workspace`)

Release only when the launcher itself changes (`tools/muon-workspace/`). Changes to the workspace tool
in `tools/muon/` never need a launcher release.

1. **Change and test:**
   ```sh
   uv run --project platform/tools/muon-workspace --extra test pytest -q platform/tools/muon-workspace/tests
   ```
2. **Bump the version** to the same value in both files (semver; while 0.x, bump the minor version for
   any change in behaviour):
   - `platform/tools/muon-workspace/pyproject.toml` (`version = "…"`)
   - `platform/tools/muon-workspace/src/muon_workspace/__init__.py` (`__version__ = "…"`)
3. **Check the package locally** (optional, but quick):
   ```sh
   uv build --project platform/tools/muon-workspace --out-dir /tmp/mw-dist
   uvx twine check /tmp/mw-dist/*
   ```
   The wheel must contain only `muon_workspace/` (launcher, `__init__`, `__main__`).
4. **Commit and push to `main`.** Wait for the `verify` workflow to pass.
5. **Tag and push the tag.** The tag must be `muon-workspace-v<version>`, exactly matching the version:
   ```sh
   git -C platform tag -a muon-workspace-v0.2.0 -m "muon-workspace 0.2.0: <one line>"
   git -C platform push origin muon-workspace-v0.2.0
   ```
6. **The workflow publishes it.** `.github/workflows/publish-muon-workspace.yml` checks the tag against
   the version, runs the tests, builds, and uploads to PyPI with trusted publishing (no token).
   Follow it with `gh run watch -R ufan/muon_platform`.
7. **Confirm and upgrade:**
   ```sh
   curl -s https://pypi.org/pypi/muon-workspace/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   uv tool upgrade muon-workspace && muon which
   ```
8. **Record it** in `platform/governance/decisions.md` if the change affects how people work.

A PyPI version can never be re-uploaded. If a release is broken, fix it and release the next
version. You can also "yank" the broken one on pypi.org, which hides it from new installs.

## 2. Compatibility between launcher and implementation

The launcher hands over with a fixed contract:
`uv run --frozen --project <ws>/platform/tools/muon python -m muon_cli <args>`, plus the variables
`MUON_IMPL=1`, `MUON_WORKSPACE`, `MUON_LAUNCHER`.

- **Keep the contract stable.** If the implementation needs something new from the launcher, release the
  launcher first. Then raise `[tool.muon] min-launcher` in `platform/tools/muon/pyproject.toml`.
  Hosts with an older launcher get a warning with the upgrade command (`uv tool upgrade muon-workspace`), and
  `muon doctor` reports it.
- **Never lower `min-launcher`**, and never remove what an older launcher relies on, without bumping the
  launcher's major version.
- **The implementation is versioned by its platform commit.** Bump `version` in `platform/tools/muon/pyproject.toml`
  and `src/muon_cli/__init__.py` when its behaviour changes, so that `muon which` shows it. After changing its
  dependencies, refresh `platform/tools/muon/uv.lock` (`uv lock --project platform/tools/muon`), because
  the launcher runs it with `--frozen`.

## 3. One-time PyPI setup (already done)

The project `muon-workspace` publishes through a **trusted publisher** on pypi.org (Account → Publishing).
PyPI matches these fields **exactly and case-sensitively** against the claims of the GitHub run:

| Field | Value |
|---|---|
| Owner | `ufan` |
| Repository name | `muon_platform` |
| Workflow name | `publish-muon-workspace.yml` (file name only) |
| Environment | `pypi` (the only case-insensitive field) |

A new host or a new developer does not need any of this to install the package.

## 4. Troubleshooting

- **`invalid-publisher: … Publisher with matching claims was not found`.** One of the fields above differs
  from the run's claims. The failed job log lists the claims it sent (`repository`, `repository_owner_id`,
  `job_workflow_ref`, `environment`). Compare them field by field. Typical causes:
  - the publisher was registered on TestPyPI instead of PyPI;
  - `muon-platform` with a hyphen;
  - `.yaml` instead of `.yml`;
  - a path in the workflow field;
  - a different environment name.

  After fixing it on PyPI, re-run only the failed job; no new tag is needed:
  `gh run rerun <run-id> -R ufan/muon_platform --failed`.
- **The `sub` claim looks like `repo:ufan@2208936/muon_platform@1313625050:…`.** This is GitHub's immutable
  subject format, mandatory for repositories created after 15 July 2026. PyPI does not check `sub`, so it is
  not the cause of a publishing failure.
- **"tag … != version …"** in the first workflow step. The tag and `pyproject.toml` disagree. Delete the
  wrong tag (`git push origin :refs/tags/<tag>`, plus the local tag), fix the version, and tag again.
- **A local build installs stale code.** setuptools reuses a `build/` directory. It is git-ignored; delete
  `platform/tools/muon-workspace/build/` before building or installing from the source directory.
