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
