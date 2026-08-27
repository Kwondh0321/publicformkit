# PublicFormKit

[한국어](README.md) | English

PublicFormKit converts public PDF, HWPX, HTML, Markdown, and text forms into a JSON Schema, an accessible HTML draft, and a field-level review report. It uses deterministic rules without a model so every inference remains reviewable.

## Install and run

```bash
git clone https://github.com/Kwondh0321/publicformkit.git
cd publicformkit
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install .
publicformkit examples/application.txt --output-dir converted-form
```

Generated files:

- `form.schema.json`: JSON Schema draft 2020-12
- `form.html`: keyboard-accessible labeled HTML form draft
- `review.json`: source metadata, inferred fields, confidence, and review notice

Values already filled into a source form may contain personal data. They are never copied to generated files; only `source_value_redacted` records that a value was present. HWPX XML processing is bounded to reduce decompression-bomb risk.

Legacy binary `.hwp` must first be converted to HWPX. Image-only PDFs require OCR. Every inferred field, required flag, data type, collection purpose, retention period, and legal basis needs human review. This project does not provide a submission server.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

Licensed under MIT.
