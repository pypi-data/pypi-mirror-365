# docx-json-replacer

A Python library and CLI tool for replacing template text in DOCX files with values from JSON.

## Installation

```bash
pip install docx-json-replacer
# or
pip3 install docx-json-replacer
```


## Usage

### CLI

```bash
docx-json-replacer file.docx data.json
```

This will create `file_replaced.docx` with template placeholders like `{key}` replaced with values from your JSON file.

### Python Library

```python
from docx_json_replacer import DocxReplacer

replacer = DocxReplacer("template.docx")vb       
replacer.replace_from_json({"name": "John", "date": "2025-06-25"})
replacer.save("output.docx")
```

## Template Format

Use `{{key}}` placeholders in your DOCX file that match keys in your JSON:

**JSON:**
```json
{
  "name": "John Doe",
  "company": "Example Corp"
}
```

**DOCX template:**
```
Hello {{name}}, welcome to {{company}}!
```

**Result:**
```
Hello John Doe, welcome to Example Corp!
```

## Local Development

Run tests:
```bash
python -m pytest tests/ -v
```

Test CLI locally:
```bash
python docx_json_replacer/cli.py tests/fixtures/template.docx tests/fixtures/data.json -o output.docx
```


python docx_json_replacer/cli.py tests/fixtures/doc_template.docx tests/fixtures/data.json -o output.docx