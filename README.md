# EcoSim 5-year Decision Support — R162 Release Candidate

**Private, offline research and decision-support repository.**

- Source: [`ECOSIM_R162_INTEGRITY_REVIEW_RC/`](ECOSIM_R162_INTEGRITY_REVIEW_RC/)
- Entry guide: [`README_R162.md`](ECOSIM_R162_INTEGRITY_REVIEW_RC/README_R162.md)
- Original unmodified R162 ZIP attached under **GitHub Releases** as tag `r162-20261031`; its SHA-256 is pinned below.
- State: `PASS_OFFLINE_ONLY`; **game actions `STOP`**. There is no validated live five-year EcoSim forecast. The samples are based on the historical 2026-10-30 test round and/or synthetic market inputs.
- Does not access or change the live EcoSim service.

## Verify source

```bash
cd ECOSIM_R162_INTEGRITY_REVIEW_RC
./verify_release_r162.sh
```

For the original release archive, verify SHA-256:

```text
731c5b823099421e099b748102fac8ae93a2b41f72dd196cafaca2cafb2d5908  ECOSIM_R162_INTEGRITY_REVIEW_RC_20261031.zip
```

Historical observations, examples and reverse-engineered arithmetic should **not** be treated as authoritative live market parameters. No GitHub Actions or send/commit-to-game workflow is configured.
