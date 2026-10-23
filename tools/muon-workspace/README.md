# muon-workspace

The global `muon` command for muon platform workspaces. It is only a **launcher**: it finds the
workspace you are in and runs *that workspace's own* muon tool (`<workspace>/platform/tools/muon`),
in the workspace's own uv environment. Several workspaces on one machine can therefore use different
tool versions without interfering. The approach is the same as Android's `repo` launcher or Bazelisk.

It has no dependencies. It needs `git` and [uv](https://docs.astral.sh/uv/) on PATH.

```sh
uv tool install muon-workspace
muon ws init ~/src/muon_wkspc          # outside a workspace: create one (clones its platform repository)
cd ~/src/muon_wkspc && muon which      # which launcher, workspace and implementation are in use
muon -C ~/src/other_wkspc status       # run in another workspace
```

The workspace tool itself (repositories, verification, agent files) lives in, and is versioned by,
each workspace's platform repository. This package contains none of it.
