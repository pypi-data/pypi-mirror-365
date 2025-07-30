import json
from typing import Dict, Any
from docxtpl import DocxTemplate, RichText

try:
    from .utility.html_parse import clean_html_content
except ImportError:
    from utility.html_parse import clean_html_content


class DocxReplacer:
    def __init__(self, docx_path: str):
        self.docx_path = docx_path
        self.template = DocxTemplate(docx_path)
    
    
    def replace_from_json(self, json_data: Dict[str, Any]) -> None:
        # Convert dot notation keys to nested dictionary structure
        context = {}
        for key, value in json_data.items():
            # Clean HTML content from values
            cleaned_value = clean_html_content(value)
            
            if '.' in key:
                # Split key like "input.name" into ["input", "name"]
                parts = key.split('.')
                current = context
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                current[parts[-1]] = cleaned_value
            else:
                context[key] = cleaned_value
        
        # Render the template with the context
        self.template.render(context)
    
    def replace_from_json_file(self, json_path: str) -> None:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        self.replace_from_json(json_data)
    
    def save(self, output_path: str) -> None:
        self.template.save(output_path)


def replace_docx_template(docx_path: str, json_data: Dict[str, Any], output_path: str) -> None:
    replacer = DocxReplacer(docx_path)
    replacer.replace_from_json(json_data)
    replacer.save(output_path)