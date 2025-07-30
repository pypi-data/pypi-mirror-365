---
title: Page without Specified License
author: Another Author
description: This page uses the default license
tags:
  - example
  - default
---

# Page without Specified License

This page demonstrates the plugin behavior when **no license is specified** in the YAML header.

## Configuration of This Page

In the YAML header of this page, we have **not** included a `license` property:

```yaml
---
title: Page without Specified License
author: Another Author
description: This page uses the default license
# No 'license' property here!
---
```

## Result

The plugin automatically uses the **default license** configured in `mkdocs.yml`:

**License for this page:** {{ cc_license(page.meta) }}

## Default Configuration

In the `mkdocs.yml` file, we have configured:

```yaml
plugins:
  - cc-license:
      default_license: "by-sa"  # ← Default license
      language: "en"
      target_blank: true
      show_icons: true
```

## Default License Details

{% set license_info = get_license_info(page.meta) %}

- **License code:** `{{ license_info.license_code }}`
- **Full name:** {{ license_info.full_name }}
- **Elements:** {{ license_info.elements | join(', ') }}

## Meaning of BY-SA

This default Creative Commons license means:

- **BY (Attribution)**: You must credit the original author
- **SA (ShareAlike)**: Derivative works must use the same license

This is a **permissive** license that allows commercial use while preserving attribution and share-alike requirements.

---

[Back to Home](index.md)
