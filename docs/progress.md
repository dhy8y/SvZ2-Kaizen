# Kaizen project progress

**Snapshot:** 2026-11-26  
**Feature branch:** `chatgpt/unity-2022-migration`  
**Pull request:** [#1 — Prepare Unity 2022.3 Android migration](https://github.com/dhy8y/SvZ2-Kaizen/pull/1)  
**Rough overall completion estimate:** 10% (not a measured metric; the project is still not playable or build-verified).

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
- GitHub Actions on the current branch head passed: **0 errors, 16 aggregated warnings**. It parsed 188 wave-command records (171 spawns), checked the active story wave references, and summarized unfinished modes/legacy data. The Python audit is not a Unity compile.
- No campaign/endless data was fabricated and no story wave balance changed. Current completion estimate remains **10%** (not a test-coverage metric).
- Commits: `f7c600f` (daily-challenge runtime guard), `2c9ca1d` (command/challenge audit), `c15f1ca` (regex fix), `a0d9220` (spawn validation), `b500239` and `502c61a` (warning aggregation).


## 2026-11-24 endless-source/security follow-up
- Research against the reference repository's current `main`: 9 endless entries share one legacy command table; 3 boss entries share another and use the old Shuten Doji ID. Expanding the six enemy groups gives 27 distinct enemy IDs, only 3 resource-path candidate matches in Kaizen. The legacy group audit still finds 140 missing enemy slots across 36 IDs. No endless data was copied.
- Confirmed existing endless scale config is linear: health/damage 1.05 per step, drops 1.0; `CalcMultiplier` is `1 + (factor - 1) * times`. Boss cadence is 10. See [endless adaptation notes](docs/endless-adaptation-notes.md).
- Security audit found credential-like service configuration values in tracked `ConfigSchema.txt` (monetization, matchmaking/platform, push and attribution integrations). Values were not copied or exposed. Added owner-remediation guidance to security PR #2; rotate/revoke if valid and remove/migrate after assessing integration dependencies.
- Tooling mistake: the endless research note was briefly committed to default branch by omitting a branch argument; I immediately deleted it from the default branch and re-created it on this feature branch. No code/data changed on default branch; the two documentation commits remain visible in history.


## 2026-11-24 scene gate-marker validation
- The static audit now reads referenced Unity scene YAML on CI and checks contiguous `RGatePosition1..N` markers against each authored story `MoveGate` command. The current story scenes passed this check with no gate-position warnings; this is a static YAML check, not scene import/play testing.
- Current branch CI commit `01def564`: **0 errors, 16 warnings**; 10 story waves, 10 command tables, 188 commands (171 spawns), 13 enemy IDs, one active hero. Warnings remain the missing endless/multiplayer/procedural records, inactive challenge roster references, legacy enemy groups, and incomplete rewards.
- Android CI still reports success by skipping Unity and APK upload because `UNITY_LICENSE` is not configured. No Unity compile, device run or APK is claimed.
- Commit: `01def564` scene marker audit, `8bd7a567` contiguous marker count correction. The endless research note is on this feature branch; the accidental default-branch documentation commit was removed immediately and verified absent at the branch tip (history retains the commits).


## 2026-11-25 follow-up
- Fixed a boundary bug in `WaveManager.SpawnRandomEnemy`: Unity integer `Random.Range` excludes its upper bound, so the prior `Count - 1` skipped the final pool entry. The method now guards a null/empty pool and selects over `[0, Count)`.
- `SpawnLegendaryStrikeEnemy` now treats a null/empty legendary list as unavailable and falls back to the ordinary guarded pool.
- `SpawnExtraEnemy` rejects null/empty IDs and skips failed enemy construction rather than adding a null character.
- `ReplaceHelperWithEnemy` now leaves the original helper alive when the replacement cannot be constructed; previously it could destroy the helper after a failed spawn.
- Added four source-level regression assertions in `scripts/test_wave_manager_safety.py`, wired into the license-free CI workflow. These checks verify the guard/bounds patterns only; they are **not** Unity compilation or runtime tests.
- Commits: `f1df109` (random/empty pool guard), `97bc494` (invalid extra enemy ID guard), `d558afb` (source-level regression checks), `b83e519` (CI integration).
- GitHub Actions for the new head `b83e519` were queued at the time of this log update; the earlier data audit at `97bc494` succeeded. The Android workflow still cannot run Unity without a legitimate `UNITY_LICENSE` secret and therefore produces no APK.
- Overall estimate remains **10%**: this is a small reliability improvement; story expansion, endless, Unity migration and play verification are still unstarted/blocked.

- Additional progression audit found a stale hard-coded save migration boundary at wave 50 in `Profile.PostLoadSyncing`. Replaced it with the configured play-mode `maxBaseWave`, so the migration follows the campaign length (10 now, planned 100) instead of an old original-game constant. This is a source change only; profile migration behavior is not runtime-tested.
- Added a source-level check for the configured campaign boundary. CI at `6bf4bfb` passed the five static regression checks and schema audit; this still does not prove runtime save behavior.


## 2026-11-26 malformed wave-data safety follow-up
- `WaveManager` now handles an unavailable wave schema or null command array as an empty wave rather than dereferencing it. Null command records are skipped so a malformed table cannot permanently stop command progression.
- Wave enemy-count analysis skips Spawn commands without a direct enemy reference (enemy-group commands are not implemented in the redesigned runtime), preventing a missing direct enemy key from causing a null dereference or leaving the expected count stuck.
- `WaveSpawnManager.QueueSpawns` validates the command, direct enemy key and manager before queueing. It uses the command's own `maxDelaySeconds` instead of dereferencing `NextCommand`, keeping the delay associated with the command and safe when there is no following command.
- Expanded source-level regression tests from 5 to 7 checks. The first run exposed a bug in the test helper (it searched the WaveManager file when testing WaveSpawnManager); fixed the helper and re-ran CI.
- Final CI run on commit `62c2c42` passed **7 source-level regression tests** and the data audit (**0 errors, 16 warnings; 10 story waves, 188 commands / 171 spawns, 13 enemy IDs, 1 active hero**). [Run](https://github.com/dhy8y/SvZ2-Kaizen/actions/runs/45807636055)
- Android workflow completed but skipped Unity compilation and APK upload because no legitimate `UNITY_LICENSE` secret is configured. No APK, Unity import, C# compilation, gameplay or device verification.
- Commits: `0bf9c5f` wave-data guards; `7c78cb5` spawn-queue guards; `272cd00` tests; `a7f6b6f` test source-selection fix; `62c2c42` regression helper correction.
- Estimate remains **10%**. This hardens failure behavior; it does not add campaign or endless content.


## 2026-11-27 spawn-construction hardening
- WaveManager.ConstructEnemy(string) now checks that the active stage has an enemiesSpawnArea collider before reading its size/position. A missing collider logs a clear error and returns null; the spawn manager's existing failed-spawn accounting lets the wave progress instead of crashing.
- SpawnEnemy now checks loaded CharacterData and CharactersManager before using them. Missing runtime dependencies fail cleanly and return null.
- Added two source-level regression checks for these guards; the method extractor now supports non-void C# return types.
- Expanded the static scene audit to inspect serialized enemiesSpawnAreaRight and helpersSpawnAreaLeft references, requiring non-zero local BoxCollider (Unity class ID 65) references when scene text is available. If a scene cannot be read by the static checker, it emits a warning rather than pretending it was inspected.
- CI on commit 08b1ebbb passed **9 source-level checks** and the data audit (**0 errors / 16 warnings; 10 story waves, 188 commands / 171 spawns, 13 enemy IDs, 1 active hero**). Validation run: https://github.com/dhy8y/SvZ2-Kaizen/actions/runs/45988159903. The follow-up scene-collider audit commit 37a8ae7 is awaiting CI at this update.
- Android CI again completed by skipping Unity and APK upload because no legitimate UNITY_LICENSE secret is configured. No Unity import/compile, gameplay test or APK.
- Commits: d0defd3 spawn-area/runtime-manager guards; 08b1ebb regression tests; 37a8ae7 scene collider validation.
- Estimate remains **10%**. Reliability work only; campaign/endless content and Unity migration remain unbuilt.


## 2026-11-27 validation complete
- The scene collider audit passed on commit 37a8ae7: the story scenes readable by CI have non-zero local BoxCollider references for both spawn-area fields. The validator does not import scenes into Unity.
- Hardened Profile.GoToNextWave: it no longer dereferences a missing wave schema or empty recommendedHero key when advancing; it logs a warning and preserves the current hero selection.
- Added a regression assertion for the progression guard. Latest CI at commit 13e36dc passed **10 source-level tests**, and static data audit passed (**0 errors / 16 warnings; 10 story waves, 188 commands / 171 spawns, 13 enemy IDs, 1 active hero**). [Validation run](https://github.com/dhy8y/SvZ2-Kaizen/actions/runs/45988476452)
- Android workflow completed with a skip notice: Unity build and APK upload did not run because UNITY_LICENSE is not configured. [Android workflow](https://github.com/dhy8y/SvZ2-Kaizen/actions/runs/45988469387)
- Commits from this run: d0defd3 (spawn area/dependency guards), 08b1ebb (tests), 37a8ae7 (serialized collider validation), 053c542 (next-wave hero guard), 13e36dc (regression test).
- No Unity compilation, scene import, gameplay or device test is claimed. Overall estimate remains **10%**.
