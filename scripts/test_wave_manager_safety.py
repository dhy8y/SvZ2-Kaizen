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


def method_body(method_name):
    match = re.search(r"\bpublic\s+void\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", TEXT)
    if not match:
        raise AssertionError(f"Method {method_name} was not found.")
    start = match.end() - 1
    depth = 0
    for index in range(start, len(TEXT)):
        if TEXT[index] == "{":
            depth += 1
        elif TEXT[index] == "}":
            depth -= 1
            if depth == 0:
                return TEXT[start:index + 1]
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


PROFILE_SOURCE = Path(__file__).resolve().parents[1] / "Assets/Scripts/Assembly-CSharp/Profile.cs"
PROFILE_TEXT = PROFILE_SOURCE.read_text(encoding="utf-8")


def profile_method_body(method_name):
    match = re.search(r"\bpublic\s+void\s+" + re.escape(method_name) + r"\s*\([^)]*\)\s*\{", PROFILE_TEXT)
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


if __name__ == "__main__":
    unittest.main()
