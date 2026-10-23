# Contract changes

| Contract | Path in `contracts/` | Change | Compatibility |
|---|---|---|---|
| | | | breaking / additive |

While core is the only consumer, a contract and its consumer change in one commit in core. After extraction to `muon_contracts` (ADR-012 §6), contracts merge first and consumers pin the new tag.
