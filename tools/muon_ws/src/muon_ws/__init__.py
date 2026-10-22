"""Muon platform workspace tool (ADR-009 §12-§15).

Works in three workspace shapes: a full west workspace (hub = `platform`),
a repo-rooted west workspace (e.g. `west init -m muon_daq`), and a standalone
clone of one repository without west. West is never required.
"""

__version__ = "0.1.0"
