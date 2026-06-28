import os
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "ui-sprite-generator" / "scripts" / "openai_image.py"


def load_script_module():
    spec = importlib.util.spec_from_file_location("openai_image_script", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OpenAIImageScriptTests(unittest.TestCase):
    def test_help_does_not_expose_api_key_argument(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("--env-file", result.stdout)
        self.assertIn("--base-url", result.stdout)
        self.assertIn("--mode", result.stdout)
        self.assertIn("--quality", result.stdout)
        self.assertIn("--response-format", result.stdout)
        self.assertNotIn("--api-key", result.stdout)

    def test_missing_api_key_fails_with_env_guidance(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            env_file = work / ".env"
            env_file.write_text("IMAGE_API_BASE_URL=https://example.test/v1/images/generations\n", encoding="utf-8")
            prompt = work / "prompt.txt"
            prompt.write_text("Generate a UI atlas.", encoding="utf-8")

            env = os.environ.copy()
            env.pop("IMAGE_API_KEY", None)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--env-file",
                    str(env_file),
                    "--prompt-file",
                    str(prompt),
                    "--output",
                    str(work / "out.png"),
                ],
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("IMAGE_API_KEY", result.stderr)
            self.assertIn("environment", result.stderr.lower())

    def test_generation_payload_includes_quality_and_response_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            prompt = work / "prompt.txt"
            prompt.write_text("Generate a UI atlas.", encoding="utf-8")
            module = load_script_module()
            args = module.parse_args(
                [
                    "--prompt-file",
                    str(prompt),
                    "--output",
                    str(work / "out.png"),
                    "--model",
                    "gpt-image-2",
                    "--size",
                    "1536x1024",
                    "--quality",
                    "high",
                    "--response-format",
                    "b64_json",
                ]
            )

            payload = module.build_json_payload(args, {})

            self.assertEqual(payload["model"], "gpt-image-2")
            self.assertEqual(payload["quality"], "high")
            self.assertEqual(payload["response_format"], "b64_json")
            self.assertNotIn("image", payload)

    def test_base_url_argument_overrides_env_file(self):
        module = load_script_module()
        args = module.parse_args(
            [
                "--base-url",
                "https://example.test/v1/images/edits",
                "--prompt-file",
                "prompt.txt",
                "--output",
                "out.png",
            ]
        )

        self.assertEqual(
            module.resolve_base_url(args, {"IMAGE_API_BASE_URL": "https://wrong.test/v1/images/generations"}),
            "https://example.test/v1/images/edits",
        )

    def test_edit_multipart_supports_repeated_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            prompt = work / "prompt.txt"
            prompt.write_text("Redraw the UI sprites.", encoding="utf-8")
            first = work / "reference.png"
            first.write_bytes(b"png-bytes")
            second = work / "mask.jpg"
            second.write_bytes(b"jpg-bytes")
            module = load_script_module()
            args = module.parse_args(
                [
                    "--mode",
                    "edits",
                    "--prompt-file",
                    str(prompt),
                    "--output",
                    str(work / "out.png"),
                    "--input-image",
                    str(first),
                    "--input-image",
                    str(second),
                    "--model",
                    "gpt-image-2",
                    "--size",
                    "1536x1024",
                    "--quality",
                    "high",
                    "--response-format",
                    "b64_json",
                ]
            )

            body, content_type = module.build_multipart_body(args, {}, boundary="BOUNDARY")

            body_text = body.decode("latin-1")
            self.assertIn("multipart/form-data; boundary=BOUNDARY", content_type)
            self.assertEqual(body_text.count('name="image";'), 2)
            self.assertIn('name="quality"', body_text)
            self.assertIn("\r\nhigh\r\n", body_text)
            self.assertIn('name="response_format"', body_text)
            self.assertIn("\r\nb64_json\r\n", body_text)
            self.assertNotIn("Bearer", body_text)


if __name__ == "__main__":
    unittest.main()
