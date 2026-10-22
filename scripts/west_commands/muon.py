"""Muon platform west extension commands: thin wrappers over `muon_ws` (ADR-009 §14, P8).

All logic lives in platform/tools/muon_ws so that the same commands work without
west (`muon-ws ...`), e.g. in a standalone clone of a single repository.
"""

import os
import sys

from west.commands import WestCommand

_SRC = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "tools", "muon_ws", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from muon_ws import cli  # noqa: E402


class _Wrapper(WestCommand):
    PREFIX = ()

    def __init__(self, name, help_text):
        super().__init__(name, help_text, f"{help_text}.\n\nSame as `muon-ws {' '.join(self.PREFIX)} ...`; "
                                          f"`--help` after the command shows its options.",
                         accepts_unknown_args=True)

    def do_add_parser(self, parser_adder):
        # All arguments are passed through unparsed, in order, to muon_ws.
        return parser_adder.add_parser(self.name, help=self.help, description=self.description,
                                       add_help=False)

    def do_run(self, args, unknown_args):
        rc = cli.main([*self.PREFIX, *unknown_args], start=os.getcwd())
        if rc:
            sys.exit(rc)


class Catalog(_Wrapper):
    PREFIX = ("catalog",)

    def __init__(self):
        super().__init__("catalog", "list projects with maturity, role, groups and reference_for")


class Verify(_Wrapper):
    PREFIX = ("verify",)

    def __init__(self):
        super().__init__("verify", "run each project's userdata.verify command")


class AgentsSync(_Wrapper):
    PREFIX = ("agents", "sync")

    def __init__(self):
        super().__init__("agents-sync", "generate agent files for all AI tools (rules, skills, adapters)")


class XBranch(_Wrapper):
    PREFIX = ("xbranch",)

    def __init__(self):
        super().__init__("xbranch", "create or switch to the same topic branch across projects")


class Refs(_Wrapper):
    PREFIX = ("refs",)

    def __init__(self):
        super().__init__("refs", "legacy references: sync (clone + read-only lock), status, build-dir")
