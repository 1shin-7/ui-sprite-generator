from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class SkillDocTests(unittest.TestCase):
    def test_external_image_generation_fallback_mentions_security_boundaries(self):
        content = (ROOT / "ui-sprite-generator" / "SKILL.md").read_text(encoding="utf-8").lower()

        self.assertIn("external image generation fallback", content)
        self.assertIn("base url", content)
        self.assertIn("api key", content)
        self.assertIn("token", content)
        self.assertIn("environment variable", content)
        self.assertIn("never write", content)
        self.assertIn("large images", content)
        self.assertIn("thumbnail", content)

    def test_atlas_prompt_forbids_crop_fallback_and_requires_redrawn_sprites(self):
        content = (ROOT / "ui-sprite-generator" / "prompts" / "03_generate_ui_atlas.md").read_text(
            encoding="utf-8"
        ).lower()

        self.assertIn("do not crop", content)
        self.assertIn("pillow", content)
        self.assertIn("redraw", content)
        self.assertIn("isolated sprite", content)
        self.assertIn("border decoration", content)
        self.assertIn("glow", content)
        self.assertIn("hollow", content)
        self.assertIn("bar_fill_texture", content)
        self.assertIn("rich texture", content)


if __name__ == "__main__":
    unittest.main()
