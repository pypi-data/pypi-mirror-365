---
title: Page with Custom License
license: "by-nc-sa"
author: Example Author
description: This page shows the usage of a custom license
tags:
  - example
  - license
---

# Page with Custom License

This page demonstrates the use of a **custom Creative Commons license**.

## License Configuration

In the YAML header of this page, we have specified:

```yaml
---
title: Page with Custom License
license: "by-nc-sa"   # Attribution-NonCommercial-ShareAlike
author: Example Author
---
```

## Result

The plugin automatically generates the appropriate icons and link for this license:

**License for this page:** {{ cc_license(page.meta) }}

## Direct Plugin Function Test

Here's a direct test of the plugin functions:

{% set license_info = get_license_info(page.meta) %}

- **License code:** `{{ license_info.license_code }}`
- **Full name:** {{ license_info.full_name }}
- **Elements:** {{ license_info.elements | join(', ') }}
- **URL:** [{{ license_info.url }}]({{ license_info.url }})

## Meaning of BY-NC-SA

This Creative Commons license means:

- **BY (Attribution)**: You must credit the original author
- **NC (NonCommercial)**: Non-commercial use only
- **SA (ShareAlike)**: Derivative works must use the same license

---

[Back to Home](index.md)
