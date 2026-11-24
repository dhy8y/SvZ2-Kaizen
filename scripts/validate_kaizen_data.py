#!/usr/bin/env python3
"""Static sanity checks for Kaizen's authored wave data (no Unity/license required)."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "DataBundles" / "English"
WAVE_FILE = BUNDLE / "WaveSchema.txt"
COMMAND_FILE = BUNDLE / "WaveCommandSchema.txt"
ENEMY_FILE = BUNDLE / "EnemySchema.txt"
HERO_FILE = BUNDLE / "HeroSchema.txt"
REWARD_FILE = BUNDLE / "WaveRewardSchema.txt"
PLAYMODE_FILE = BUNDLE / "PlayModeSchema.txt"
GROUP_FILE = BUNDLE / "EnemyGroupSchema.txt"
PROCEDURAL_FILE = BUNDLE / "ProceduralWaveSchema.txt"
PROCEDURAL_LIST_FILE = BUNDLE / "ProceduralWaveListSchema.txt"
PROCEDURAL_SELECTION_FILE = BUNDLE / "ProceduralWaveSelectionSchema.txt"
HERO_LIST_FILE = BUNDLE / "HeroListSchema.txt"
HELPER_LIST_FILE = BUNDLE / "HelperListSchema.txt"
HELPER_FILE = BUNDLE / "HelperSchema.txt"

errors = []
warnings = []

def fail(message):
    errors.append(message)

def warn(message):
    warnings.append(message)

def sections(text):
    result = {}
    current = None
    buf = []
    for line in text.splitlines():
        match = re.match(r"^\[([^]]+)\]\s*$", line)
        if match:
            if current is not None:
                result[current] = "\n".join(buf)
            current = match.group(1)
            buf = []
        elif current is not None:
            buf.append(line)
    if current is not None:
        result[current] = "\n".join(buf)
    return result

def records(section):
    """Parse simple DataBundle record headings and key=value fields."""
    result = {}
    current = None
    for line in section.splitlines():
        match = re.match(r"^\s{1,8}([A-Za-z0-9_]+):\s*$", line)
        if match:
            current = match.group(1)
            result.setdefault(current, {})
            continue
        field = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
        if field and current is not None:
            result[current][field.group(1)] = field.group(2)
    return result

def read_required(path):
    if not path.is_file():
        fail(f"Missing required schema file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text(encoding="utf-8-sig")

wave_sections = sections(read_required(WAVE_FILE))
command_sections = sections(read_required(COMMAND_FILE))
enemy_sections = sections(read_required(ENEMY_FILE))
hero_sections = sections(read_required(HERO_FILE))
reward_sections = sections(read_required(REWARD_FILE))
playmode_sections = sections(read_required(PLAYMODE_FILE))
group_sections = sections(read_required(GROUP_FILE))
procedural_sections = sections(read_required(PROCEDURAL_FILE))
procedural_list_sections = sections(read_required(PROCEDURAL_LIST_FILE))
procedural_selection_sections = sections(read_required(PROCEDURAL_SELECTION_FILE))
hero_list_sections = sections(read_required(HERO_LIST_FILE))
helper_list_sections = sections(read_required(HELPER_LIST_FILE))
helper_sections = sections(read_required(HELPER_FILE))

waves = records(wave_sections.get("Waves", ""))
commands = {name: section for name, section in command_sections.items()}
enemies = {rec.get("id", key) for key, rec in records(enemy_sections.get("Enemies", "")).items()}
heroes = {rec.get("id", key) for key, rec in records(hero_sections.get("Heroes", "")).items()}
reward_defs = records(reward_sections.get("Reward_Table", ""))
reward_records = set(reward_defs)
play_modes = records(playmode_sections.get("PlayModes", ""))
procedural_records = records(procedural_sections.get("DailyChallenges", ""))
active_helpers = {rec.get("id", key) for key, rec in records(helper_sections.get("Helpers", "")).items()}
daily_schedule = records(procedural_selection_sections.get("DailyChallengeSchedule", ""))


scene_names = {p.stem for p in (ROOT / "Assets" / "Scenes").rglob("*.unity")}
wave_refs = []
wave_enemy_refs = []
wave_group_refs = []
for wave_id, wave in waves.items():
    commands_name = wave.get("commands", "")
    if commands_name and commands_name not in commands:
        fail(f"Wave {wave_id}: command table '{commands_name}' is missing.")
    scene = wave.get("scene", "")
    if scene and scene not in scene_names:
        fail(f"Wave {wave_id}: scene '{scene}' is missing under Assets/Scenes.")
    hero = wave.get("recommendedHero", "")
    if hero.startswith("Heroes."):
        hero = hero.split(".", 1)[1]
    if hero and hero not in heroes:
        fail(f"Wave {wave_id}: recommended hero '{hero}' is not in HeroSchema.")
    boss = wave.get("BossEnemy", "")
    if boss.startswith("Enemies."):
        boss = boss.split(".", 1)[1]
    if boss and boss not in enemies:
        fail(f"Wave {wave_id}: boss '{boss}' is not in EnemySchema.")
    reward = wave.get("rewards", "")
    if reward.startswith("Reward_Table."):
        reward = reward.split(".", 1)[1]
    if reward and reward not in reward_records:
        fail(f"Wave {wave_id}: reward record '{reward}' is missing.")
    wave_refs.append(commands_name)

    if commands_name in commands:
        for enemy in re.findall(r"^\s*enemy\s*=\s*Enemies\.([A-Za-z0-9_]+)\s*$", commands[commands_name], re.M):
            wave_enemy_refs.append(enemy)
            if enemy not in enemies:
                fail(f"Wave {wave_id}/{commands_name}: enemy '{enemy}' is not in EnemySchema.")
        if re.search(r"^\s*enemyGroup\s*=", commands[commands_name], re.M):
            wave_group_refs.append(commands_name)
            warn(f"{commands_name} uses enemyGroup; current WaveSpawnManager queues only direct enemy fields.")

# Validate mode references, but preserve warnings for intentionally unfinished multiplayer/endless tables.
for mode, fields in play_modes.items():
    base = fields.get("waves", "")
    if base and base not in wave_sections:
        warn(f"Play mode '{mode}' references missing wave table '{base}'.")
    for field in ("endlessWaves", "endlessBonusWaves"):
        table = fields.get(field, "")
        if table and table not in wave_sections:
            warn(f"Play mode '{mode}' references missing {field} table '{table}' (endless mode data is unfinished).")
    try:
        maximum = int(fields.get("maxBaseWave", "0"))
    except ValueError:
        fail(f"Play mode '{mode}' has a non-integer maxBaseWave.")
        continue
    if base == "Waves" and maximum > len(waves):
        fail(f"Play mode '{mode}' maxBaseWave={maximum}, but only {len(waves)} story records exist.")

# Procedural challenge definitions point into WaveSchema tables; report missing data without failing
# the story campaign checks, since this subsystem is marked unfinished in Kaizen.
for challenge, fields in procedural_records.items():
    ref = fields.get("wave", "")
    if ref:
        table = ref.split(".", 1)[0]
        if table not in wave_sections:
            warn(f"Daily challenge '{challenge}' points to missing wave table '{table}'.")

# Audit every Kaizen command table, not just the ten story tables.
def command_records(section):
    parsed = []
    current = None
    for line in section.splitlines():
        heading = re.match(r"^\s*(?:\*|[0-9]+):\s*$", line)
        if heading:
            if current is not None:
                parsed.append(current)
            current = {}
            continue
        field = re.match(r"^\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$", line)
        if field and current is not None:
            current[field.group(1)] = field.group(2)
    if current is not None:
        parsed.append(current)
    return parsed

valid_command_types = {"", "Default", "Spawn", "Delay", "Banner", "MoveGate", "Tutorial"}
for command_name, section in commands.items():
    parsed_commands = command_records(section)
    if not parsed_commands:
        warn(f"Command table '{command_name}' has no parseable commands.")
    for command_index, command in enumerate(parsed_commands, 1):
        command_type = command.get("type", "")
        if command_type not in valid_command_types:
            fail(f"{command_name} command {command_index}: unsupported type '{command_type}'.")
        enemy_ref = command.get("enemy", "")
        if enemy_ref:
            if not enemy_ref.startswith("Enemies."):
                fail(f"{command_name} command {command_index}: malformed enemy reference '{enemy_ref}'.")
            else:
                enemy_id = enemy_ref.split(".", 1)[1]
                if enemy_id not in enemies:
                    fail(f"{command_name} command {command_index}: enemy '{enemy_id}' is missing from EnemySchema.")
        group_ref = command.get("enemyGroup", "")
        if command_type == "Spawn" and not enemy_ref and not group_ref:
            fail(f"{command_name} command {command_index}: Spawn has neither an enemy nor an enemyGroup.")
        if group_ref and group_ref not in group_sections:
            warn(f"{command_name} command {command_index}: enemy group table '{group_ref}' is missing.")
        if command_type == "Spawn":
            try:
                spawn_count = int(command.get("count", "0") or "0")
                if spawn_count <= 0:
                    fail(f"{command_name} command {command_index}: Spawn count must be greater than zero.")
            except ValueError:
                fail(f"{command_name} command {command_index}: Spawn count is not an integer.")
        if command_type == "Delay":
            try:
                delay = float(command.get("duration", "0") or "0")
                if delay < 0:
                    fail(f"{command_name} command {command_index}: Delay duration cannot be negative.")
            except ValueError:
                fail(f"{command_name} command {command_index}: Delay duration is not numeric.")

# Audit the daily challenge schedules/pools and their active hero/helper references.
for schedule_id, schedule in daily_schedule.items():
    pool_name = schedule.get("proceduralWavePool", "")
    if not pool_name:
        warn(f"DailyChallengeSchedule '{schedule_id}' has no proceduralWavePool.")
        continue
    if pool_name not in procedural_list_sections:
        warn(f"DailyChallengeSchedule '{schedule_id}' references missing pool '{pool_name}'.")
        continue
    pool_records = records(procedural_list_sections[pool_name])
    if not pool_records:
        warn(f"Daily challenge pool '{pool_name}' is empty.")
    for pool_record_id, pool_record in pool_records.items():
        challenge_ref = pool_record.get("proceduralWave", "")
        if not challenge_ref.startswith("DailyChallenges."):
            warn(f"Daily challenge pool '{pool_name}/{pool_record_id}' has invalid reference '{challenge_ref}'.")
            continue
        challenge_id = challenge_ref.split(".", 1)[1]
        if challenge_id not in procedural_records:
            warn(f"Daily challenge pool '{pool_name}/{pool_record_id}' references missing challenge '{challenge_id}'.")

for challenge_id, challenge in procedural_records.items():
    if challenge.get("disabled", "False").lower() == "true":
        continue
    wave_ref = challenge.get("wave", "")
    if wave_ref:
        table_name, _, record_id = wave_ref.partition(".")
        if table_name not in wave_sections:
            warn(f"Enabled daily challenge '{challenge_id}' references missing wave table '{table_name}'.")
        elif record_id and record_id not in records(wave_sections[table_name]):
            warn(f"Enabled daily challenge '{challenge_id}' references missing wave '{wave_ref}'.")
    hero_table = challenge.get("possibleHeroes", "")
    if not hero_table or hero_table not in hero_list_sections:
        warn(f"Enabled daily challenge '{challenge_id}' has missing/empty possibleHeroes table '{hero_table}'.")
    else:
        hero_entries = records(hero_list_sections[hero_table])
        valid_hero_count = 0
        for hero_key, hero_entry in hero_entries.items():
            hero_ref = hero_entry.get("hero", f"Heroes.{hero_key}")
            hero_id = hero_ref.split(".", 1)[1] if hero_ref.startswith("Heroes.") else hero_ref
            if hero_id in heroes:
                valid_hero_count += 1
            else:
                warn(f"Daily challenge '{challenge_id}' hero pool '{hero_table}' references inactive/missing hero '{hero_id}'.")
        if valid_hero_count == 0:
            warn(f"Enabled daily challenge '{challenge_id}' has no active hero in pool '{hero_table}'.")
    helper_table = challenge.get("possibleHelpers", "")
    if not helper_table or helper_table not in helper_list_sections:
        warn(f"Enabled daily challenge '{challenge_id}' has missing possibleHelpers table '{helper_table}'.")
    else:
        for helper_key, helper_entry in records(helper_list_sections[helper_table]).items():
            helper_ref = helper_entry.get("ability", f"Helpers.{helper_key}")
            helper_id = helper_ref.split(".", 1)[1] if helper_ref.startswith("Helpers.") else helper_ref
            if helper_id not in active_helpers:
                warn(f"Daily challenge '{challenge_id}' helper pool '{helper_table}' references missing/inactive helper '{helper_id}'.")

# Aggregate legacy group mismatches to keep CI output readable.
group_missing_ids = set()
group_missing_slots = 0
for group_section in group_sections.values():
    for group in records(group_section).values():
        for slot in ("enemy_1", "enemy_2", "enemy_3"):
            enemy_ref = group.get(slot, "")
            if enemy_ref.startswith("Enemies."):
                enemy_id = enemy_ref.split(".", 1)[1]
                if enemy_id not in enemies:
                    group_missing_ids.add(enemy_id)
                    group_missing_slots += 1
if group_missing_ids:
    warn(f"Legacy enemy groups contain {group_missing_slots} missing enemy-reference slots across " +
         f"{len(group_missing_ids)} IDs: " + ", ".join(sorted(group_missing_ids)[:15]) +
         (" ..." if len(group_missing_ids) > 15 else ""))

# WaveRewardSchema has data, but the current story records do not assign any rewards.
assigned_reward_ids = set()
for wave in waves.values():
    reward = wave.get("rewards", "")
    if reward.startswith("Reward_Table."):
        assigned_reward_ids.add(reward.split(".", 1)[1])
unused_rewards = sorted(reward_records - assigned_reward_ids)
if unused_rewards:
    warn(f"{len(unused_rewards)} WaveRewardSchema records are not assigned to any current story wave.")
unsupported_reward_fields = {"souls", "revive", "power", "luck", "friendship", "wealth", "haste", "peace", "tea", "sushi"}
unsupported_reward_values = sorted({
    field for definition in reward_defs.values()
    for field in unsupported_reward_fields
    if definition.get(field, "0").strip() not in ("", "0", "False", "NULL")
})
if unsupported_reward_values:
    warn("Reward data contains values outside the currently processed coins/pachinkoBalls: " +
         ", ".join(unsupported_reward_values) + " (reward collection/banking code is unfinished).")

# EnemyGroupSchema retains legacy records. Only report missing IDs, do not fail the story check.
group_enemy_refs = re.findall(r"enemy_\d+\s*=\s*Enemies\.([A-Za-z0-9_]+)", "\n".join(group_sections.values()))
missing_group_enemies = sorted(set(group_enemy_refs) - enemies)
if missing_group_enemies:
    warn(f"Legacy enemy groups reference {len(missing_group_enemies)} enemy IDs absent from EnemySchema: " +
         ", ".join(missing_group_enemies[:12]) + (" ..." if len(missing_group_enemies) > 12 else ""))

if not waves:
    fail("No authored [Waves] records found.")
print(f"Kaizen static data audit: {len(waves)} story waves, {len(commands)} command tables, {len(enemies)} enemy IDs, {len(heroes)} active hero record(s).")
if errors:
    print("\nERRORS:")
    for item in errors:
        print(f"  - {item}")
if warnings:
    print("\nWARNINGS (unfinished/legacy references; not a story-wave failure):")
    for item in warnings:
        print(f"  - {item}")
print(f"\nResult: {len(errors)} error(s), {len(warnings)} warning(s).")
sys.exit(1 if errors else 0)
