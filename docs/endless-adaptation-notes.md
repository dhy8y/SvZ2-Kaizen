# Endless-wave adaptation research

## Original reference structure
The public reference repository's current `main` contains:
- 9 `EndlessWaves` records, all referencing the same `EndlessWave_01` command table.
- 3 `EndlessWaves_Boss` records, all referencing `EndlessWave_Boss_01` and the same `ShutenDoji_Kin` boss ID.
- The two command tables contain 54 and 32 old-format command records. The endless table uses six enemy-group tables; expanding those groups exposes 27 unique enemy IDs.
- Only 3 of those 27 endless enemy IDs have a candidate matching Kaizen EnemySchema resource path. Resource equality is a research hint, not proof of identical stats or gameplay. The original Shuten Doji boss record is not a Kaizen EnemySchema ID.

## Kaizen systems already present
- Kaizen WaveCommandSchema uses `Spawn`, `Delay`, and `MoveGate` commands, with direct enemy IDs, counts, spacing and timing. The current ten story command tables contain 188 records (171 spawns), statically validated.
- The enemy-group bundle retains legacy entries: 140 enemy-reference slots across 36 IDs do not resolve to the current Kaizen EnemySchema.
- `PlayModeSchema` sets the endless bonus interval to 10 and references missing `EndlessWaves` / `EndlessWaves_Boss` tables.
- WaveManager already reads `waveLevelMultipliersEndless`: health and damage use a base factor of 1.05 per endless step, drops 1.0. `CalcMultiplier` is linear: `1 + (factor - 1) * times`, not exponential. This is the existing author's config/code, not newly tuned.
- Current GetWaveData safely falls back to the nearest authored story wave while endless tables are absent. That prevents division-by-zero but is not an endless implementation.

## Why the original tables are not copied
Old command records encode enemy-group, command/timing and direct-enemy fields incompatible with Kaizen's new WaveCommandSchema. The source groups reference enemy IDs/resources not available in Kaizen, and the original boss is absent. Blind copying or substituting similarly named IDs would change stats, spawn patterns and progression balance.

## Safe next implementation boundary
Endless data can be authored by reusing or creating Kaizen-format spawn patterns, with the existing linear scaling and a boss cadence, but it requires an explicit balance review. Reusing the ten story command tables would be repetitive and could reintroduce tutorial delays/gate moves; using OniBoss as a Shuten Doji replacement is not verified equivalence. No endless records are committed in this audit.
