#!/usr/bin/env python3
"""Source-level regression checks for guarded WaveManager spawn helpers.

These checks do not replace Unity compilation or gameplay tests. They protect
specific null/empty-pool and Random.Range boundary cases while Unity is blocked.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "Assets/Scripts/Assembly-CSharp/WaveManager.cs"
TEXT = SOURCE.read_text(encoding="utf-8")
SPAWN_SOURCE = Path(__file__).resolve().parents[1] / "Assets/Scripts/Assembly-CSharp/WaveSpawnManager.cs"
SPAWN_TEXT = SPAWN_SOURCE.read_text(encoding="utf-8")


def method_body(method_name, source_text=TEXT):
    match = re.search(r"\b(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\]]+\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", source_text)
    if not match:
        raise AssertionError(f"Method {method_name} was not found.")
    start = match.end() - 1
    depth = 0
    for index in range(start, len(source_text)):
        if source_text[index] == "{":
            depth += 1
        elif source_text[index] == "}":
            depth -= 1
            if depth == 0:
                return source_text[start:index + 1]
    raise AssertionError(f"Method {method_name} has unbalanced braces.")


class WaveManagerSpawnSafetyTests(unittest.TestCase):
    def test_random_enemy_pool_is_checked_and_last_item_is_reachable(self):
        body = method_body("SpawnRandomEnemy")
        self.assertRegex(body, r"mAllDifferentEnemies\s*==\s*null\s*\|\|\s*mAllDifferentEnemies\.Count\s*==\s*0")
        self.assertRegex(body, r"Random\.Range\(\s*0\s*,\s*mAllDifferentEnemies\.Count\s*\)")
        self.assertNotRegex(body, r"Random\.Range\(\s*0\s*,\s*mAllDifferentEnemies\.Count\s*-\s*1\s*\)")

    def test_empty_legendary_pool_falls_back(self):
        body = method_body("SpawnLegendaryStrikeEnemy")
        self.assertRegex(body, r"legendaryEnemies\s*!=\s*null\s*&&\s*legendaryEnemies\.Count\s*>\s*0")
        self.assertIn("SpawnRandomEnemy(position, spawnRange);", body)

    def test_extra_enemy_does_not_add_null_character(self):
        body = method_body("SpawnExtraEnemy")
        self.assertIn("string.IsNullOrEmpty(cmd)", body)
        null_guard = body.index("if (enemy == null)")
        add_character = body.index("AddCharacter(enemy)")
        self.assertLess(null_guard, add_character)
        self.assertIn("return;", body[null_guard:add_character])

    def test_failed_helper_replacement_preserves_helper(self):
        body = method_body("ReplaceHelperWithEnemy")
        null_guard = body.index("if (c == null)")
        destroy_helper = body.index("DestroyCharacter(h)")
        self.assertLess(null_guard, destroy_helper)
        self.assertIn("return;", body[null_guard:destroy_helper])

    def test_construct_enemy_checks_missing_spawn_area(self):
        body = method_body("ConstructEnemy")
        self.assertIn("if (mEnemiesSpawnArea == null)", body)
        self.assertLess(body.index("if (mEnemiesSpawnArea == null)"), body.index("mEnemiesSpawnArea.size.x"))
        self.assertIn("return null;", body)

    def test_enemy_construction_checks_character_data_and_manager(self):
        body = method_body("SpawnEnemy")
        self.assertIn("if (data == null)", body)
        self.assertIn("if (charactersManager == null)", body)
        self.assertLess(body.index("if (data == null)"), body.index("new Enemy(data"))

    def test_spawn_queue_guards_missing_enemy_and_manager(self):
        body = method_body("QueueSpawns", SPAWN_TEXT)
        self.assertIn("if (command == null)", body)
        self.assertIn("DataBundleRecordKey.IsNullOrEmpty(command.enemy)", body)
        self.assertIn("if (waveManager == null)", body)
        self.assertIn("mQueueTimer.Set(command.maxDelaySeconds);", body)

    def test_wave_manager_handles_missing_wave_or_command_data(self):
        next_command = re.search(r"private WaveCommandSchema mNextCommand\s*\{(.*?)\n\t\}", TEXT, re.S)
        self.assertIsNotNone(next_command)
        self.assertIn("areCommandsDone", next_command.group(1))
        done = method_body("AnalyseWaveCommandsForStats")
        self.assertIn("waveRootData == null || waveRootData.Commands == null", done)
        self.assertIn("DataBundleRecordKey.IsNullOrEmpty(command.enemy)", done)
        self.assertIn("Skipping an invalid null wave command", TEXT)

    def test_helper_replacement_checks_manager_before_constructing_or_destroying(self):
        body = method_body("ReplaceHelperWithEnemy")
        manager_check = body.index("if (charactersManager == null)")
        construct = body.index("ConstructEnemyWithEffect")
        add_character = body.index("charactersManager.AddCharacter(c)")
        destroy_helper = body.index("charactersManager.DestroyCharacter(h)")
        self.assertLess(manager_check, construct)
        self.assertLess(add_character, destroy_helper)
        self.assertIn("helper will remain alive", body[manager_check:construct])

    def test_extra_spawn_checks_manager_before_registration(self):
        body = method_body("SpawnExtraEnemy")
        manager_check = body.index("if (charactersManager == null)")
        construct = body.index("ConstructEnemy(cmd")
        add_character = body.index("charactersManager.AddCharacter(enemy)")
        self.assertLess(manager_check, construct)
        self.assertLess(construct, add_character)

    def test_boss_spawn_guards_manager_and_keeps_count_nonnegative(self):
        body = method_body("Update")
        self.assertIn("charactersManager != null ? ConstructEnemy(specialBossName) : null", body)
        self.assertIn("charactersManager.AddCharacter(boss)", body)
        self.assertIn("Mathf.Max(0, mTotalNumEnemies - 1)", body)

    def test_spawn_queue_update_handles_missing_managers_before_add(self):
        update_anchor = SPAWN_TEXT.index("public bool IsSpawning")
        outer_update_start = SPAWN_TEXT.index("public void Update()", update_anchor)
        body = method_body("Update", SPAWN_TEXT[outer_update_start:])
        manager_check = body.index("else if (charactersManager == null")
        construct = body.index("currentWaveManager.ConstructEnemy")
        add_character = body.index("charactersManager.AddCharacter(enemy)")
        self.assertLess(manager_check, construct)
        self.assertLess(construct, add_character)
        self.assertIn("currentWaveManager == null", body)
        self.assertIn("Mathf.Max(0, currentWaveManager.totalEnemies - 1)", body)

    def test_wave_reward_grant_guards_data_profile_and_manager(self):
        body = method_body("AddSpecialRewardsToCollectables")
        self.assertIn("waveRootData == null || waveRootData.Rewards == null", body)
        self.assertIn("profile == null", body)
        manager_check = body.index("if (collectableManager == null)")
        grant = body.index("collectableManager.GiveResource")
        self.assertLess(manager_check, grant)
        self.assertIn("Cannot grant wave rewards", body[manager_check:grant])


PROFILE_SOURCE = Path(__file__).resolve().parents[1] / "Assets/Scripts/Assembly-CSharp/Profile.cs"
PROFILE_TEXT = PROFILE_SOURCE.read_text(encoding="utf-8")


def profile_method_body(method_name):
    match = re.search(r"\bpublic\s+[\w<>\[\]]+\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", PROFILE_TEXT)
    if not match:
        raise AssertionError(f"Profile method {method_name} was not found.")
    start = match.end() - 1
    depth = 0
    for index in range(start, len(PROFILE_TEXT)):
        if PROFILE_TEXT[index] == "{":
            depth += 1
        elif PROFILE_TEXT[index] == "}":
            depth -= 1
            if depth == 0:
                return PROFILE_TEXT[start:index + 1]
    raise AssertionError(f"Profile method {method_name} has unbalanced braces.")


class ProfileProgressionSourceTests(unittest.TestCase):
    def test_save_progression_uses_configured_story_boundary(self):
        body = profile_method_body("PostLoadSyncing")
        self.assertIn("int finalStoryWave = maxBaseWave;", body)
        self.assertIn("CurrentStoryWave = finalStoryWave + 1;", body)
        self.assertNotRegex(body, r"highestUnlockedWave\s*==\s*50")


    def test_next_wave_keeps_current_hero_when_recommendation_is_missing(self):
        body = profile_method_body("GoToNextWave")
        self.assertIn("WaveSchema nextWaveData = WaveManager.GetWaveData", body)
        self.assertIn("nextWaveData != null && !DataBundleRecordKey.IsNullOrEmpty(nextWaveData.recommendedHero)", body)
        self.assertIn("keeping the current hero selection", body)

if __name__ == "__main__":
    unittest.main()
