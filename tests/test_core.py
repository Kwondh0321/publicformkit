import tempfile
import unittest
import zipfile
from pathlib import Path

from publicformkit.cli import main
from publicformkit.core import convert_form, extract_text, infer_fields


class PublicFormKitTests(unittest.TestCase):
    def test_inferrs_required_and_typed_fields(self):
        fields = infer_fields("성명(필수):\n이메일*: user@example.org\n신청 금액: 원\n")
        by_label = {field["label"]: field for field in fields}
        self.assertTrue(by_label["성명"]["required"])
        self.assertEqual("email", by_label["이메일"]["input_type"])
        self.assertEqual("number", by_label["신청 금액"]["type"])

    def test_extracts_hwpx_xml(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "form.hwpx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr(
                    "Contents/section0.xml",
                    '<root xmlns:hp="urn:test"><hp:t>성명: ______</hp:t></root>',
                )
            text, metadata = extract_text(path)
            self.assertIn("성명", text)
            self.assertEqual("hwpx", metadata["format"])

    def test_converts_text_to_reviewable_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "application.txt"
            source.write_text(
                "성명(필수):\n이메일: example@example.org\n", encoding="utf-8"
            )
            result = convert_form(source, root / "out")
            self.assertEqual(2, result["field_count"])
            html = (root / "out" / "form.html").read_text(encoding="utf-8")
            self.assertIn("<label", html)
            self.assertIn("aria-required", html)
            self.assertEqual(0, main([str(source), "--output-dir", str(root / "cli")]))

    def test_redacts_filled_values_from_generated_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "filled.txt"
            source.write_text("이메일: private.person@example.org\n", encoding="utf-8")
            output = root / "out"
            result = convert_form(source, output)
            combined = (
                (output / "form.schema.json").read_text(encoding="utf-8")
                + (output / "form.html").read_text(encoding="utf-8")
                + (output / "review.json").read_text(encoding="utf-8")
            )
            self.assertNotIn("private.person@example.org", combined)
            self.assertTrue(result["field_count"])
            self.assertEqual(
                "filled.txt",
                __import__("json").loads(
                    (output / "review.json").read_text(encoding="utf-8")
                )["source"],
            )


if __name__ == "__main__":
    unittest.main()
