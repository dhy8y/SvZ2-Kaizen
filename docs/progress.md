# Kaizen project progress

**Snapshot:** 2026-11-22  
**Feature branch:** `chatgpt/unity-2022-migration`  
**Pull request:** [#1 — Prepare Unity 2022.3 Android migration](https://github.com/dhy8y/SvZ2-Kaizen/pull/1)  
**Rough overall completion estimate:** 9% (not a measured metric; the project is still not playable or build-verified).

## Completed this run
- Added `scripts/validate_kaizen_data.py` and `.github/workflows/validate-data.yml`, a no-license static check of story-wave data.
- Passed the latest static validation: **0 errors, 29 warnings**. The warnings represent unfinished endless/multiplayer/procedural wave tables, unused/unsupported rewards, and legacy enemy groups with missing IDs.
- Added a guard for a missing gate-marker container in `InGameImpl.InitializeWaveManager`.
- Added diagnostics for unused reward entries and reward fields not currently processed.
- Added `docs/legacy-enemy-resource-map.md`: a research-only map for 19 old enemy IDs that share resources with 11 Kaizen enemy records. It does not convert data or claim gameplay equivalence.
- Updated Android workflow so it skips with a clear notice when the legitimate `UNITY_LICENSE` secret is absent, instead of failing before Unity starts.

## Current verified baseline
- Kaizen: 10 authored story waves, 10 matching command tables, 13 enemy records, 1 active hero record. All current wave command enemy references and story scene/hero references resolve.
- Original public reference: 50 story waves, 9 endless waves, 3 endless boss waves, 78 command tables, 103 enemy IDs. Resource mapping shows no fully compatible waves 11–50: 29 partially mapped and 11 with no mapped enemy types.
- `ProjectSettings/ProjectVersion.txt` remains Unity 2017.4.40f1. Unity 2022.3 import/compile/runtime is not verified.
- Android workflow succeeded by **skipping the build** because `UNITY_LICENSE` is not configured. No APK exists.

## Remaining blockers / next work
1. Obtain a legitimate Unity license and configure it privately in GitHub Actions repository secrets; never paste it into chat.
2. Perform the Unity 2022.3 migration/import and resolve package/API/build errors using the Unity Editor/CI.
3. Inspect scene gate markers, especially the large scene files that cannot be retrieved through the current connector.
4. Finish the reward collection/banking path and wire safe authored wave rewards only after their intended values are reviewed.
5. Rebuild missing endless tables with a separate endless progression, scaling and periodic bosses. Do not use a repeat-the-last-story-wave fallback as the finished mode.
6. Design/adapt the missing story waves to reach 100 without fabricating author-authored content or blindly copying original enemy stats/commands.
7. Verify playability and the APK on a real Android device, including 20:9 and 21:9.

## Commits from this run
- `1aa8f9d` — static validator
- `adeaa23` — validator workflow
- `02e2fb3` — guard absent gate-marker container
- `eaef339` — reward audit warnings
- `55e90eb` — correct legacy enemy-reference regex
- `87b8835` — skip build when license secret is absent
- `3919c3f` — keep validator compatible with future wave-count expansion
- `a13c10b` — candidate enemy-resource mapping research


## 2026-11-23 security review
- Found a tracked Android keystore at repository root on both the feature branch and default branch. Its filename explicitly indicated a password. The binary was not downloaded or inspected.
- Removed it from the feature branch and added ignore rules for local signing material; added `docs/signing-key-remediation.md`.
- The default branch and Git history still contain the file until the PR is merged/owner performs cleanup. Treat the old signing key as compromised and rotate/revoke it if it was used. No history rewrite was performed.


## 2026-11-23 follow-up
- Added runtime guards for daily challenge data: missing/empty `ProceduralWaves`, no date schedule match, empty pools, disabled/missing challenge records, and invalid referenced waves now leave the challenge unavailable with a warning rather than indexing an empty list or dereferencing null. Non-daily profile cleanup no longer assumes helper/ability lists were allocated.
- `WaveManager` now refuses to load a selected wave when its data or scene is missing, and daily challenge lookup reports a missing cached challenge rather than dereferencing null.
- Security review found the Android signing keystore committed at the repository root (its filename exposed that it had an associated password). It was removed from this feature branch and ignored; a separate non-draft cleanup PR #2 targets `master`. Treat the signing key as compromised and rotate/revoke if used. The file still exists on `master` and in history until cleanup/merge; no history rewrite was performed.
- CI after the previous commit: static audit passed with 0 errors/29 warnings. Android job succeeded only by skipping Unity due to absent `UNITY_LICENSE`; no APK.
- Current C# guards are not compiler-verified because Unity import/build remains blocked by license/editor availability.

- Follow-up validation on feature-branch head `60db76d`: GitHub Actions data audit completed successfully (**0 errors, 29 warnings**); warnings remain the documented missing modes/reward/enemy-group references. Android workflow reports success because both Unity build and artifact upload were skipped (no `UNITY_LICENSE`).
- A delimiter-balance structural scan of the edited `Profile.cs` and `WaveManager.cs` passed; this is not a C# compile or Unity test.
- Opened non-draft security cleanup PR [#2](https://github.com/dhy8y/SvZ2-Kaizen/pull/2) against `master`. Both PR branches' tip trees no longer contain the keystore path, but default branch/history are still exposed until owner merges and handles history/key rotation.
- Latest feature-branch commits: `a37604a` (daily challenge guard), `56de331` (invalid wave launch guard), `60db76d` (progress/PR update).
- Rough project completion estimate updated to **10%**; this is a milestone estimate, not a measurable code coverage or playable-build score.


## 2026-11-24 daily-challenge safety and audit follow-up
- Hardened `Profile.RefreshDailyChallenge`: candidates are filtered to have an authored wave with a scene and commands plus at least one hero currently present in `HeroesDatabase`. The selection method now returns safely when no valid hero remains, rather than indexing an empty hero pool. Missing helper-list tables and stale helper IDs are skipped safely.
- Expanded the license-free validator to parse all Kaizen wave-command records, validate command types/enemy references/spawn counts and numeric fields, and audit daily-challenge schedule/pool/hero/helper references. Legacy enemy-group missing IDs are summarized to keep output manageable.
- These are defensive checks only: daily challenges remain unavailable because `ProceduralWaves` is absent; only `HeroBalanced` is active, while several challenge pools target commented-out heroes; only four helper records are currently active and many legacy challenge pools reference inactive allies.
- Static checks passed on the preceding validator revision with 0 errors; the current revision's Actions run is pending/being checked. The Python audit is not a Unity compile. 
- No campaign/endless data was fabricated and no story wave balance changed. Current completion estimate remains **10%** (not a test-coverage metric).
- Commits: `f7c600f` (daily-challenge runtime guard), `2c9ca1d` (command/challenge audit), `c15f1ca` (regex fix), `a0d9220` (spawn validation), `b500239` and `502c61a` (warning aggregation).
