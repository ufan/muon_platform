"""Muon platform west extension commands (ADR-009 §12, §14).

West is the single interface for workspace features. The implementation lives in the
internal package `muon_ws` next to this file; it is not a user-facing tool.
"""

import os
import sys

from west.commands import WestCommand

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from muon_ws import cli  # noqa: E402


class _Wrapper(WestCommand):
    PREFIX = ()

    def __init__(self, name, help_text):
        super().__init__(name, help_text, f"{help_text}.\n\n`--help` after the command shows its options.",
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
