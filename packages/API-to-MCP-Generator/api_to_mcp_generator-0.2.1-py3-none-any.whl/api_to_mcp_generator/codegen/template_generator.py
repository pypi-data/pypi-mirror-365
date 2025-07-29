"""
Template-based code generation utilities.
"""

from typing import Dict, Any, List


class TemplateGenerator:
    """Generates code from templates."""

    def __init__(self):
        self.templates = {}

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context."""
        # For now, we'll use simple string formatting
        # In the future, this could use Jinja2 or similar
        template = self.templates.get(template_name, "")
        try:
            return template.format(**context)
        except KeyError as e:
            raise ValueError(f"Missing template variable: {e}")

    def register_template(self, name: str, template: str):
        """Register a new template."""
        self.templates[name] = template
