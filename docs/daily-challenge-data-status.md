# Daily challenge data status (Kaizen)

This audit describes current data, not a content restoration. Daily challenges should remain unavailable rather than silently selecting an invalid hero, ally, or wave.

## Runtime blockers
- `ProceduralWaveSchema.txt` defines challenge records, but `WaveSchema.txt` has no `[ProceduralWaves]` table. The challenge records point to `ProceduralWaves.1` through `.6`, so none can launch.
- `HeroSchema.txt` currently activates only `HeroBalanced`. HeroAttack, HeroDefense, HeroAbility and other hero records are commented out.
- Hero lists such as `DailyChallengeHeroList_All`, `DC_HeroList_Sorceress`, `DC_HeroList_Ronin`, and `DC_HeroList_Kunoichi` still reference those disabled records.
- `HelperSchema.txt` currently has only four active helper records: Farmer, Samurai, SamuraiArcher, SpearSamurai. Many challenge ally pools contain old IDs for allies whose records are commented out.

## Defensive behavior added
`Profile.RefreshDailyChallenge` now filters challenge candidates by:
1. not disabled;
2. a referenced wave record that loads with a non-empty command array and scene;
3. at least one hero-list key that resolves to an active `HeroesDatabase` entry.

The hero selection method independently checks for an empty/invalid list and returns unavailable instead of indexing an empty list. Missing helper-list tables and helper IDs that no longer resolve are skipped.

## Re-enable requirements
- Author or restore the missing `ProceduralWaves` records and command tables.
- Review wave commands, scenes, difficulty and timers for Kaizen balance; original data is not automatically compatible.
- Restore/author hero and helper entries or curate challenge pools to the active Kaizen records.
- Run the static validator and Unity tests, then test challenge selection/launch on device.

No challenge waves or balance values were invented or changed in this audit.
