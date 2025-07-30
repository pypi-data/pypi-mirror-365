# MkDocs CC License Plugin

[![PyPI version](https://badge.fury.io/py/mkdocs-cc-license-plugin.svg)](https://badge.fury.io/py/mkdocs-cc-license-plugin)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/mkdocs-cc-license-plugin.svg)](https://pypi.org/project/mkdocs-cc-license-plugin/)

A MkDocs plugin that automatically adds Creative Commons license icons and links to pages based on the `license` property in their YAML frontmatter.

## Features

- ✅ **Automatic License Detection**: Reads `license` property from page metadata
- ✅ **Official CC Icons**: Uses SVG icons from Creative Commons servers
- ✅ **Multiple License Support**: All CC 4.0 licenses (BY, SA, NC, ND, CC0)
- ✅ **Multilingual Links**: Supports different languages for CC links
- ✅ **Elegant Badge Display**: Modern rounded badges with icons and letters
- ✅ **Material Theme Integration**: Custom templates for optimal display
- ✅ **Configurable**: Flexible options for customization

## Installation

```bash
pip install mkdocs-cc-license-plugin
```

## Quick Start

### 1. Add to your `mkdocs.yml`

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "en"
      target_blank: true
      show_icons: true

theme:
  name: material
  custom_dir: theme_overrides  # Optional for custom display
```

### 2. Add license to your pages

```yaml
---
title: My Document
license: "by-nc-sa"  # Attribution-NonCommercial-ShareAlike
---

# My Document Content
```

### 3. Create custom template (optional)

Create `theme_overrides/main.html`:

```html
{% extends "base.html" %}

{% block content %}
  <article class="md-content__inner md-typeset">
    <!-- License badge in top-right -->
    {% if page.meta.license %}
      <div class="cc-license-container" style="float: right; margin-left: 1em; margin-bottom: 1em; padding: 0.8em; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border: 1px solid #dee2e6; border-radius: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        {{ cc_license(page.meta) | safe }}
      </div>
    {% endif %}
    
    {{ page.content }}
  </article>
{% endblock %}
```

## Supported Licenses

| License Code | Full Name |
|--------------|-----------|
| `by` | Attribution |
| `by-sa` | Attribution-ShareAlike |
| `by-nc` | Attribution-NonCommercial |
| `by-nc-sa` | Attribution-NonCommercial-ShareAlike |
| `by-nd` | Attribution-NoDerivatives |
| `by-nc-nd` | Attribution-NonCommercial-NoDerivatives |
| `cc0` | CC0 Public Domain Dedication |

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_license` | string | `"by-sa"` | License used if not specified |
| `language` | string | `"en"` | Language for CC links (en, fr, es, etc.) |
| `target_blank` | boolean | `true` | Open links in new tab |
| `show_icons` | boolean | `true` | Display SVG icons |

## Visual Example

For a page with `license: "by-nc-sa"`, the plugin generates:

![CC License Badge Example](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)

- **Icons**: CC, BY, NC, SA with corresponding letters underneath
- **Link**: Points to official Creative Commons page
- **Styling**: Modern rounded badge design

## Template Functions

The plugin exposes Jinja2 functions for templates:

```html
<!-- Display license badge -->
{{ cc_license(page.meta) }}

<!-- Get license information -->
{% set license_info = get_license_info(page.meta) %}
<p>License: {{ license_info.full_name }}</p>
<p>URL: {{ license_info.url }}</p>
```

## Multilingual Support

Works perfectly with `mkdocs-static-i18n`:

```yaml
plugins:
  - i18n:
      languages:
        - locale: en
          name: English
        - locale: fr
          name: Français
  - cc-license:
      language: "en"  # Will be overridden per language
```

## Examples

See the [examples directory](examples/) for a complete multilingual setup with:
- English and French content
- Custom Material theme template
- Automated build scripts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This plugin is released under the MIT License.

## Changelog

### 1.0.0
- Initial release
- Support for all CC 4.0 licenses
- Material theme integration
- Multilingual support
- Custom template functions
