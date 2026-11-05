# P1 FACT source update — X-Challenge 2026 Selejtező I

This owner-provided P1 factual Excel export is the evidence source for the seven-team competitor comparison and the R3 business-count reconstruction. It is 198,250 bytes, distinct from the older ~105 KB qualifier file already present under `team-evidence/original-binaries-20261103/` on `main`. Treat this version as the source for P1 FACT figures discussed in the Nov 4–5 analyses, not as a P2 server snapshot.

The P2/5 server PLAN and the P1 FACT export must never be conflated. The P2 save-state remains UNKNOWN, and the P2 one-variable live preview/revert trial has been deferred. No game data was mutated during this publication.

The `verify_offline.sh` sibling script checks the original 49-file release SHA-256 manifest and runs the two independent offline model test suites (17+14). This P1 export and the new verifier are an addendum, not part of that historical manifest. The script writes only to a temporary directory, not the repo or game.
