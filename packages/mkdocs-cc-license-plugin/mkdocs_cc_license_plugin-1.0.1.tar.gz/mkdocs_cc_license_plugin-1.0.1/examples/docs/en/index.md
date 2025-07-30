---
title: Home
description: Example homepage
---

# MkDocs Creative Commons License Plugin - Example

Welcome to the **mkdocs-cc-license-plugin** usage example!

## Demonstrated Features

This example site shows how the plugin automatically handles Creative Commons licenses:

### 1. Pages with Custom License

- See the [With License](with-license.md) page that specifies `license: "by-nc-sa"`
- Appropriate CC icons are automatically generated

### 2. Pages without Specified License

- See the [No License](no-license.md) page that uses the default license
- The default `by-sa` license is automatically applied

### 3. License Display

Licenses appear as SVG icons with links to the official Creative Commons page.

## Current Configuration

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "en"
      target_blank: true
      show_icons: true
```

## License for This Page

This page uses the default license: {{ cc_license(page.meta) }}

---

*This example demonstrates the usage of the mkdocs-cc-license-plugin*
