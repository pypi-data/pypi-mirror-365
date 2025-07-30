# MkDocs CC License Plugin - Multilingual Example

This example demonstrates how to use the `mkdocs-cc-license-plugin` in a multilingual setup with English and French content.

## Quick Setup

### 1. Install Dependencies

```bash
# Install example dependencies
pip install -r requirements.txt

# Install the CC License plugin from parent directory
pip install -e ..
```

### 2. Run the Example

```bash
# Single command for both languages
mkdocs serve

# Or build the static site
mkdocs build

# Or use the provided scripts
./build-multilingual.sh    # Unix/Linux/Mac
build-multilingual.bat     # Windows
```

### 3. View the Result

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to see:
- 🇬🇧 **English version** at `/` (default)  
- 🇫🇷 **French version** at `/fr/`
- 🔄 **Language selector** in the header

## Features

- ✅ **Multilingual Support**: English (default) and French versions
- ✅ **Language Selector**: Material theme with `extra.alternate` configuration  
- ✅ **Creative Commons Integration**: Automatic license badges and links
- ✅ **Responsive Design**: Works on all devices

## Structure

```
examples/
├── docs/                          # English content (default)
│   ├── index.md                   # English homepage
│   ├── with-license.md           # Page with custom license
│   ├── no-license.md             # Page with default license
│   └── fr/                       # French content
│       ├── index.md              # French homepage
│       ├── with-license.md       # Page avec licence personnalisée
│       └── no-license.md         # Page avec licence par défaut
├── theme_overrides/              # Custom theme templates
│   └── main.html                 # CC license badge display
├── mkdocs.yml                    # English configuration
├── mkdocs-fr.yml                 # French configuration
├── build-multilingual.sh         # Build script (Unix)
└── build-multilingual.bat        # Build script (Windows)
```

## Quick Start

### Option 1: English Only
```bash
cd examples
mkdocs serve
# Visit http://127.0.0.1:8000
```

### Option 2: French Only
```bash
cd examples
mkdocs serve --config-file mkdocs-fr.yml
# Visit http://127.0.0.1:8000
```

### Option 3: Full Multilingual Build
```bash
cd examples
# On Windows:
build-multilingual.bat
# On Unix/Linux/Mac:
./build-multilingual.sh

# Then serve the built site:
cd site
python -m http.server 8000
# Visit http://127.0.0.1:8000
```

## Language Selector

The language selector appears in the header and allows switching between:
- 🇬🇧 **English** (`/`) - Default version
- 🇫🇷 **Français** (`/fr/`) - French version

## License Examples

Each language version demonstrates:

1. **Custom License Page** (`license: "by-nc-sa"`)
   - Shows Attribution-NonCommercial-ShareAlike license
   - Icons: CC, BY, NC, SA

2. **Default License Page** (no license specified)
   - Uses default `by-sa` license from configuration
   - Icons: CC, BY, SA

## Configuration Details

### English (mkdocs.yml)
```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "en"          # English CC links
      target_blank: true
      show_icons: true

theme:
  language: en

extra:
  alternate:
    - name: English
      link: /
      lang: en
    - name: Français  
      link: /fr/
      lang: fr
```

### French (mkdocs-fr.yml)
```yaml
plugins:
  - cc-license:
      default_license: "by-sa"
      language: "fr"          # French CC links
      target_blank: true
      show_icons: true

theme:
  language: fr

extra:
  alternate:
    - name: English
      link: /
      lang: en
    - name: Français
      link: /fr/
      lang: fr
```

## Testing the Plugin

1. **Install the plugin** in development mode:
   ```bash
   cd ..  # Go back to plugin root
   pip install -e .
   ```

2. **Run the examples**:
   ```bash
   cd examples
   mkdocs serve
   ```

3. **Verify license display**:
   - Check that CC badges appear on pages
   - Click badges to verify correct language links
   - Test both custom and default licenses

## Deployment

For production deployment, build both versions and structure them as:

```
your-site.com/
├── index.html           # English version
├── with-license/
├── no-license/
└── fr/                  # French version
    ├── index.html
    ├── with-license/
    └── no-license/
```

## Customization

- **Add more languages**: Create additional config files and content directories
- **Modify license display**: Edit `theme_overrides/main.html`
- **Change default licenses**: Update the `default_license` setting per language
- **Add more license types**: The plugin supports all CC 4.0 licenses

## Troubleshooting

If licenses don't appear:
1. Check that the plugin is properly installed
2. Verify the `custom_dir: theme_overrides` is set
3. Ensure license values are valid (e.g., `"by-sa"`, `"by-nc-sa"`)
4. Check browser console for JavaScript errors
