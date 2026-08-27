"""Public form extraction and accessible rendering."""

from __future__ import annotations

import html
import json
import re
import unicodedata
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from pypdf import PdfReader


FIELD_LINE = re.compile(r"^\s*(?:[-•]\s*)?(.{1,80}?)(\*|\s*\((?:필수|required)\))?\s*(?::|：|_{2,}|\[\s*\])\s*(.*)$", re.IGNORECASE)


def _hwpx_text(path: Path) -> str:
    parts = []
    with zipfile.ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.startswith("Contents/") and name.endswith(".xml"))
        if not names:
            raise ValueError("HWPX archive has no Contents XML files")
        for name in names:
            root = ElementTree.fromstring(archive.read(name))
            text = "".join(node.text or "" for node in root.iter() if node.tag.rsplit("}", 1)[-1] in {"t", "text"})
            if text.strip():
                parts.append(text)
    return "\n".join(parts)


def _html_text(path: Path) -> str:
    source = path.read_text(encoding="utf-8", errors="replace")
    source = re.sub(r"<(script|style)\b[\s\S]*?</\1>", " ", source, flags=re.IGNORECASE)
    source = re.sub(r"<br\s*/?>|</(?:p|div|label|li|tr)>", "\n", source, flags=re.IGNORECASE)
    return html.unescape(re.sub(r"<[^>]+>", " ", source))


def extract_text(path: Path) -> tuple[str, dict[str, Any]]:
    """Extract text and available native field metadata."""
    suffix = path.suffix.lower()
    metadata: dict[str, Any] = {"source": str(path), "format": suffix.lstrip("."), "native_fields": []}
    if suffix == ".pdf":
        reader = PdfReader(path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        fields = reader.get_fields() or {}
        metadata["native_fields"] = [str(name) for name in fields]
        return text, metadata
    if suffix == ".hwpx":
        return _hwpx_text(path), metadata
    if suffix == ".hwp":
        raise ValueError("legacy binary HWP is not supported; save or convert it to HWPX first")
    if suffix in {".html", ".htm"}:
        return _html_text(path), metadata
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8", errors="replace"), metadata
    raise ValueError(f"unsupported form format: {suffix or '<none>'}")


def _slug(label: str, index: int) -> str:
    normalized = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9]+", "_", normalized).strip("_")
    return value[:50] or f"field_{index}"


def _field_type(label: str) -> tuple[str, str | None]:
    lower = label.lower()
    if any(token in lower for token in ("email", "e-mail", "이메일")):
        return "string", "email"
    if any(token in lower for token in ("date", "birth", "생년", "일자", "날짜")):
        return "string", "date"
    if any(token in lower for token in ("phone", "mobile", "tel", "전화", "휴대폰")):
        return "string", "tel"
    if any(token in lower for token in ("amount", "count", "number", "금액", "수량", "인원")):
        return "number", None
    return "string", None


def infer_fields(text: str, native_fields: list[str] | None = None) -> list[dict[str, Any]]:
    """Infer reviewable fields from common printed-form patterns."""
    fields = []
    seen: set[str] = set()
    candidates = text.splitlines()
    candidates.extend(f"{name}:" for name in native_fields or [])
    for line in candidates:
        compact = re.sub(r"\s+", " ", line).strip()
        match = FIELD_LINE.match(compact)
        if not match:
            continue
        label = match.group(1).strip(" -•")
        if len(label) < 2:
            continue
        key = _slug(label, len(fields) + 1)
        while key in seen:
            key = f"{key}_{len(fields) + 1}"
        seen.add(key)
        value_type, input_type = _field_type(label)
        fields.append(
            {
                "name": key,
                "label": label,
                "type": value_type,
                "input_type": input_type,
                "required": bool(match.group(2)),
                "hint": match.group(3).strip() or None,
                "confidence": 0.8 if match.group(2) or ":" in compact else 0.65,
            }
        )
    return fields


def build_schema(title: str, fields: list[dict[str, Any]]) -> dict[str, Any]:
    properties = {}
    required = []
    for field in fields:
        value: dict[str, Any] = {"type": field["type"], "title": field["label"], "x-inference-confidence": field["confidence"]}
        if field["input_type"] == "email":
            value["format"] = "email"
        elif field["input_type"] == "date":
            value["format"] = "date"
        if field["hint"]:
            value["description"] = field["hint"]
        properties[field["name"]] = value
        if field["required"]:
            required.append(field["name"])
    schema: dict[str, Any] = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": title, "type": "object", "properties": properties, "additionalProperties": False}
    if required:
        schema["required"] = required
    return schema


def render_html(title: str, fields: list[dict[str, Any]]) -> str:
    controls = []
    for field in fields:
        required = " required aria-required=\"true\"" if field["required"] else ""
        description_id = f"{field['name']}-hint"
        describedby = f" aria-describedby=\"{description_id}\"" if field["hint"] else ""
        input_type = field["input_type"] or ("number" if field["type"] == "number" else "text")
        hint = f"\n      <p id=\"{description_id}\" class=\"hint\">{html.escape(field['hint'])}</p>" if field["hint"] else ""
        controls.append(
            f"    <div class=\"field\">\n      <label for=\"{field['name']}\">{html.escape(field['label'])}</label>{hint}\n      <input id=\"{field['name']}\" name=\"{field['name']}\" type=\"{input_type}\"{required}{describedby}>\n    </div>"
        )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="ko">',
            "<head>",
            '  <meta charset="utf-8">',
            '  <meta name="viewport" content="width=device-width,initial-scale=1">',
            f"  <title>{html.escape(title)}</title>",
            "  <style>body{font:16px/1.5 system-ui,sans-serif;max-width:48rem;margin:auto;padding:2rem}.field{margin:1rem 0}label{display:block;font-weight:650}input{box-sizing:border-box;font:inherit;width:100%;padding:.65rem}.hint{color:#475467;margin:.25rem 0}</style>",
            "</head>",
            "<body>",
            f"  <main><h1>{html.escape(title)}</h1>",
            "  <p><strong>Review required:</strong> fields were inferred automatically from a source document.</p>",
            "  <form method=\"post\">",
            *controls,
            "    <button type=\"submit\">제출</button>",
            "  </form></main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def convert_form(path: Path, output_dir: Path) -> dict[str, Any]:
    text, metadata = extract_text(path)
    fields = infer_fields(text, metadata["native_fields"])
    output_dir.mkdir(parents=True, exist_ok=True)
    title = path.stem.replace("_", " ").strip() or "Converted public form"
    schema = build_schema(title, fields)
    schema_path = output_dir / "form.schema.json"
    html_path = output_dir / "form.html"
    review_path = output_dir / "review.json"
    schema_path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_html(title, fields), encoding="utf-8")
    review = {**metadata, "fields": fields, "field_count": len(fields), "notice": "Every inferred field, label, type, required flag, and legal basis requires human review."}
    review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"schema": str(schema_path), "html": str(html_path), "review": str(review_path), "field_count": len(fields)}

