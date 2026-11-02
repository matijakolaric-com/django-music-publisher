# Release ideas and audit matrix

This matrix combines the 26.12 planning notes, CWR research notes, and the code
audit. Audit findings were written against `master` at `0f598cb`; treat them as
unverified until checked against current code. Severity and effort are estimates.

Effort ranks are logarithmic: rank 1 = 1 unit, and each rank is four times the
previous rank. Thus rank 5 represents 256 units relative to rank 1.

| Description | Status | Severity / urgency | Effort rank |
|---|---|---:|---:|
| Admin permission bypass (CWR/ACK) | Done | Resolved | — |
| `DEBUG=false` parsing | Would not fix | Critical | 2 |
| CSRF exemption on royalty processing | Would not fix; calculation is read-only and permission-gated | High | 1 |
| Stored XSS in ISWC report | Done | Resolved | — |
| Royalty upload size cap | Deferred; revisit with internal batching design | High | 3 |
| Invalid writer import validation | Done | Resolved | — |
| Library-release import integrity | Done | Resolved | — |
| Writer control-state calculation | Done | Resolved | — |
| Royalty import with missing file | Done | Resolved | — |
| Invalid royalty amount handling | Done | Resolved | — |
| Invalid royalty right-type handling | Done | Resolved | — |
| Royalty division by zero | Done | Resolved | — |
| CWR 2.2 Rev 3 support | Deferred until the specification is final | High | 4 |
| R3 sender identifier | Deferred until the specification is final | High | 2 |
| Current R3 lookup tables | Deferred until the specification is final | High | 1 |
| Confirm target-society sender rules | Deferred until the specification is final | High | 1 |
| R3 revocation/anomaly/AI fields | Deferred until the specification is final | Medium | 3 |
| R3 relinquishment flag | Deferred until the specification is final | Medium | 2 |
| R3 header/GRH version updates | Deferred until the specification is final | Medium | 1 |
| R3 lowercase-title validation | Deferred until the specification is final | Medium | 2 |
| ACK XRF ISWC parsing | Candidate; untouched | Medium | 2 |
| Nullable library references | Recheck | Medium | 2 |
| Short import rows containing `None` | Done | Resolved | — |
| CWR 3.x ISR omits work ID | Deferred until the specification is final | Medium | 2 |
| OWT share-slot template | Recheck; potentially masked | Medium | 2 |
| CWR download corrupts non-ASCII | Done | Resolved | — |
| CWR 3.1 ISWC request records | Deferred until the specification is final | Medium | 2 |
| Boolean environment settings | Recheck; includes `OPTION_*` parsing | Medium | 2 |
| Backup Cache-Control header | Recheck; audit reported reproduced | Medium | 1 |
| Temp-file leak on royalty error | Done | Resolved | — |
| DataImport form model mismatch | Recheck | Medium | 2 |
| CWR generation sequence race | Deferred; address with CWR generation redesign | Medium | 4 |
| Split-export description length | Recheck | Low | 1 |
| Empty right-type result misreported | Done | Resolved | — |
| Lowercase import key rejected | Done | Resolved | — |
| Playlist ID set only in `clean()` | Recheck | Low | 1 |
| CWR 3.x WRI capacity field | Deferred until the specification is final | Low | 2 |
| CWR 3.1 GRH hardcoded type | Deferred until the specification is final | Low | 1 |
| Royalty form captures setting at import | Done | Resolved | — |
| Unicode numeric accepted as EAN | Recheck | Low | 1 |
| Release serialization N+1 queries | Recheck; audit measured 41 queries | Low | 3 |
| Work admin count queries | Recheck | Low | 2 |
| Recording track-count filter links | Recheck; audit reported reproduced | Low | 1 |
| Work-ID search zero padding | Recheck; possible overlap with later work | Low | 1 |
| Work admin formset variable shadowing | Recheck | Low | 1 |
| Release default ordering | Recheck; audit reported reproduced | Low | 1 |
| ISNI fields on writers/artists | Candidate; not implemented | Low | 2 |
| Society-code refresh | Suggested; not confirmed | Low | 1 |
| CWR-JSON export | Author-confirmed idea; draft standard | Low | 5 |
| Store ACK source files | Author-requested; untouched | Low | 4 |
| DB↔file migration commands | Proposed dependency of file storage | Low | 4 |
| Store imported CSV files | Proposed; storage/scope unresolved | Low | 3 |
| Move generated CWR files to storage | Proposed; lifecycle/sentinel unresolved | Low | 4 |
| Remove CWR 3.0/3.1 EDI | Author-confirmed intent; deprecation needed | Low | 3 |
| Other ACK XRF identifiers | Deliberately undecided; TGT boundary | Low | 3 |
| DDEX MWN support | Rejected for now: licence/data/support constraints | Not planned | 5 |
| Overlong import filename rejection | Done | Resolved | — |
| Work IDs without publisher code | Done | Resolved | — |
| CWR model-based generation | Deferred. Performance note: `WorkManager.get_dict_items()` reads works in batches of 100, but CWR generation remains one operation; moving work-ID persistence to export creation would shift DB writes earlier rather than eliminate them. Benchmark before changing when IDs are persisted. This refactor could also make it possible to chunk generation into meaningful, independently atomic units. | Planned feature | 3 |
| Work-ID list search | Already implemented in TGT; excluded from DMP scope | Out of scope | 1 |
