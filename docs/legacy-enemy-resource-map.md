# Original enemy resource mapping (research only)

This is a candidate cross-reference for adapting the public original data to Kaizen. It is **not** an approved wave-data conversion: matching a resource prefab does not prove identical health, damage, AI, spawn timing, armor, or balance.

## IDs whose resource paths match

| Original enemy ID | Kaizen enemy ID | Shared resource |
|---|---|---|
| `chochinobake` | `Chochinobake` | `Character.Chochinobake` |
| `evil_oni` | `OniBoss` | `Character.Oni` |
| `evil_oni_boss` | `OniBoss` | `Character.Oni` |
| `oni` | `OniBoss` | `Character.Oni` |
| `oni_boss` | `OniBoss` | `Character.Oni` |
| `evil_zombie_sword` | `LZombieSword` | `Character.LZombieSword` |
| `l_zombie_sword` | `LZombieSword` | `Character.LZombieSword` |
| `l_zombie_ax` | `LZombieAxe` | `Character.LZombieAxe` |
| `l_zombie_bow` | `LZombieArcher` | `Character.LZombieArcher` |
| `l_zombie_melee` | `LZombieMelee` | `Character.LZombie` |
| `l_zombie_spear` | `LZombieSpear` | `Character.LZombieSpear` |
| `nobusuma` | `Nobusuma` | `Character.Nobusuma` |
| `oni_small` | `OniSmall` | `Character.OniSmall` |
| `Zombie_Split` | `Unstoppable` | `Character.CrawlingBody` |
| `Zombie_Split_2` | `Unstoppable` | `Character.CrawlingBody` |
| `Zombie_Split_Tutorial` | `Unstoppable` | `Character.CrawlingBody` |
| `Zombie_Legs` | `ZombieLegs` | `Character.CrawlingLegs` |
| `Zombie_Legs_2` | `ZombieLegs` | `Character.CrawlingLegs` |
| `Zombie_Legs_Tutorial` | `ZombieLegs` | `Character.CrawlingLegs` |

The match is resource-name-based; original IDs do not directly match Kaizen IDs. The mapping collapses multiple original enemy variants to one Kaizen record, so converting commands this way would lose variant-specific tuning.

## Wave-coverage snapshot

Using only exact shared `EnemySchema.resources` values as a candidate mapping, the original story waves 11–50 have:
- **0/40 fully mapped** waves (each still references at least one enemy with no Kaizen resource match).
- **29/40 partially mapped** waves.
- **11/40** waves with no mapped enemy IDs.

Do not port those waves as-is. Missing enemy types and variant statistics need author-approved replacements or a balance pass. The current Kaizen ten-wave command tables are a separate redesign and remain untouched.

## Source files

- [Original EnemySchema](https://github.com/Decomp-And-Recomp/Samurai-Vs-Zombies-2/blob/master/DataBundles/English/EnemySchema.txt)
- [Original WaveSchema](https://github.com/Decomp-And-Recomp/Samurai-Vs-Zombies-2/blob/master/DataBundles/English/WaveSchema.txt)
- [Original WaveCommandSchema](https://github.com/Decomp-And-Recomp/Samurai-Vs-Zombies-2/blob/master/DataBundles/English/WaveCommandSchema.txt)
- [Kaizen EnemySchema (feature branch)](https://github.com/dhy8y/SvZ2-Kaizen/blob/chatgpt/unity-2022-migration/DataBundles/English/EnemySchema.txt)
- [Kaizen WaveCommandSchema (feature branch)](https://github.com/dhy8y/SvZ2-Kaizen/blob/chatgpt/unity-2022-migration/DataBundles/English/WaveCommandSchema.txt)
