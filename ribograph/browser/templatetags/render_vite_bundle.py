# This template tag is needed for production
# Add it to one of your django apps (/appdir/templatetags/render_vite_bundle.py, for example)

import glob
import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def remove_prefix(text):
    prefix = "browser"
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text


@register.simple_tag
def render_vite_bundle():
    """
    Template tag to render a vite bundle.
    Supposed to only be used in production.
    For development, hot reloading modules should happen.

    Alternatively, we can use the manifest file
    https://vitejs.dev/guide/backend-integration.html
    """

    BUILD_DIRECTORY = "browser/static/browser/vuefiles/"

    with open(f"{BUILD_DIRECTORY}manifest.json") as f:
        manifest = json.load(f)

    # get the js and css files generated by vite according to the manifest file
    js_entry_file = manifest["src/main.ts"]["file"]
    css_files = manifest["src/main.ts"]["css"]

    css_imports = [
        f"""<link rel="stylesheet" href="{remove_prefix(BUILD_DIRECTORY)}{file}">"""
        for file in css_files
    ]

    return mark_safe(
        f"""
        <script type="module" crossorigin src="{remove_prefix(BUILD_DIRECTORY)}{js_entry_file}"></script>
        {"".join(css_imports)}
        """
    )
