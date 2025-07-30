# MkDocs Creative Commons License Plugin

A MkDocs plugin that automatically adds Creative Commons license icons and links based on the `license` property in page metadata.

## Features

- ✅ Automatic reading of the `license` property from YAML frontmatter
- ✅ Automatic generation of Creative Commons SVG icons
- ✅ Creation of links to official Creative Commons pages
- ✅ Support for all CC 4.0 licenses
- ✅ Display as an elegant badge in the top-right corner of pages
- ✅ Flexible configuration
- ✅ Easy integration with Jinja2 templates
- ✅ Compatible with Material for MkDocs theme

## Installation

### From source

```bash
git clone https://github.com/JM2K69/mkdocs-cc-license-plugin.git
cd mkdocs_cc_license_plugin
pip install -e .
```

### From PyPI

```bash
pip install mkdocs-cc-license-plugin
```

### Quick setup

1. Add the plugin to your `mkdocs.yml`
2. Create a `theme_overrides` folder (optional)
3. Add `license: "by-sa"` to your markdown pages
4. Run `mkdocs serve` to see the result

## Configuration

Add the plugin to your `mkdocs.yml` file:

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"      # Default license if not specified
      language: "en"                # Language for CC links (en, fr, etc.)
      target_blank: true            # Open links in new tab
      show_icons: true              # Display SVG icons

# Theme (for Material with custom template)
theme:
  name: material
  custom_dir: theme_overrides  # Optional for display customization
```

## Usage

### In page metadata

```yaml
---
title: My Exercise
author: John Doe
license: "by-nc-sa"  # Attribution-NonCommercial-ShareAlike
tags:
  - python
  - exercise
---
```

### In templates

The plugin automatically exposes Jinja2 functions for templates:

```html
<!-- Full display with icons and link -->
{{ cc_license(page.meta) }}

<!-- Or the complete function -->
{{ build_license_html(page.meta) }}

<!-- To get just license information -->
{% set license_info = get_license_info(page.meta) %}
<p>License: {{ license_info.full_name }}</p>
<p>URL: {{ license_info.url }}</p>
```

### Custom template (recommended)

For optimal display, create a custom template `theme_overrides/main.html`:

```html
{% extends "base.html" %}

{% block content %}
  <article class="md-content__inner md-typeset">
    <!-- License badge in top-right corner -->
    {% if page.meta.license %}
      <div class="cc-license-container" style="float: right; margin-left: 1em; margin-bottom: 1em; padding: 0.8em; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 1px solid #dee2e6; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        {{ cc_license(page.meta) | safe }}
      </div>
    {% endif %}
    
    {{ page.content }}
  </article>
{% endblock %}
```

## Visual rendering

The plugin displays Creative Commons licenses as **elegant badges** in the top-right corner of each page containing a `license` property. The badge includes:

- 🎨 **Modern design**: Color gradients and subtle shadows
- 🔗 **Official SVG icons**: Directly from Creative Commons servers
- 🎯 **Smart positioning**: Top-right corner, doesn't interfere with content
- 📱 **Responsive**: Adapts to all screen sizes
- 🖱️ **Interactive**: Clickable link to the official license page

### Display example

For a page with `license: "by-nc-sa"`, you'll see a badge containing CC, BY, NC, and SA icons that links to `https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en`.

## Supported licenses

- `by` - Attribution
- `by-sa` - Attribution-ShareAlike
- `by-nc` - Attribution-NonCommercial  
- `by-nc-sa` - Attribution-NonCommercial-ShareAlike
- `by-nd` - Attribution-NoDerivatives
- `by-nc-nd` - Attribution-NonCommercial-NoDerivatives
- `cc0` - CC0 Public Domain Dedication

## Example HTML output

For `license: "by-nc-sa"`, the plugin generates:

```html
<a class="cc-license-link" href="https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en" target="_blank" rel="license noopener noreferrer">
  <img src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt="Creative Commons" style="height:22px!important;margin-left:3px;vertical-align:text-bottom;">
  <img src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt="Attribution" style="height:22px!important;margin-left:3px;vertical-align:text-bottom;">
  <img src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt="NonCommercial" style="height:22px!important;margin-left:3px;vertical-align:text-bottom;">
  <img src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt="ShareAlike" style="height:22px!important;margin-left:3px;vertical-align:text-bottom;">
</a>
```

## Advanced configuration

### Available options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_license` | string | `"by-sa"` | License used if not specified |
| `language` | string | `"en"` | Language for CC links |
| `target_blank` | boolean | `true` | Open links in new tab |
| `show_icons` | boolean | `true` | Display SVG icons |
| `custom_template` | string | `None` | Custom template (future) |

### Complete configuration example

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "en"
      target_blank: false
      show_icons: true
```

## Development

### Project structure

```text
mkdocs_cc_license_plugin/
├── mkdocs_cc_license_plugin/  # Python package
│   ├── __init__.py
│   └── plugin.py              # Main plugin
├── examples/                  # Usage examples
│   ├── mkdocs.yml
│   ├── theme_overrides/       # Custom template
│   │   └── main.html
│   └── docs/
│       ├── index.md
│       ├── with-license.md
│       └── no-license.md
├── tests/                     # Unit tests
├── setup.py                   # Installation configuration
├── pyproject.toml            # Modern configuration
└── README.md                 # Documentation
```

### Testing

```bash
# Unit tests
python -m pytest tests/

# Manual test with example
cd examples
mkdocs serve
# Open http://127.0.0.1:8000/with-license/
```

## Troubleshooting

### Plugin doesn't load

- Check that the package is installed: `pip list | grep mkdocs-cc-license`
- Check the structure: files must be in `mkdocs_cc_license_plugin/`

### Icons don't appear

- Check that the `license` property is defined in the YAML frontmatter
- Use a custom template for Material (see Template section)
- Check logs: `[CC License Plugin] build_license_html called with: ...`

### Style not applied

- Restart `mkdocs serve` after template modification
- Check that `custom_dir: theme_overrides` is configured

## License

This plugin is distributed under the MIT license.

## Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature
3. Commit your changes
4. Push to the branch
5. Open a Pull Request
