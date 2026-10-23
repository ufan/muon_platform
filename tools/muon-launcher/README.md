# muon-launcher

The global `muon` command of the muon platform. It contains no workspace logic. It finds the
workspace you are in, then runs that workspace's own implementation
(`<workspace>/platform/tools/muon`, in its own uv environment). Several workspaces on one host can
therefore run different tool versions without interfering (platform ADR-012 §5).

Requirements: `git` and [uv](https://docs.astral.sh/uv/) on PATH.

```sh
muon ws init ~/src/muon_wkspc     # outside a workspace: bootstrap a new one
muon which                        # which launcher, workspace and implementation are in use
```
