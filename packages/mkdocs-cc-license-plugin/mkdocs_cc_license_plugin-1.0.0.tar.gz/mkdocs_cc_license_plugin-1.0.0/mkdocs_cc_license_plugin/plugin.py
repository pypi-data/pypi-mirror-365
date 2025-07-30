"""
MkDocs Creative Commons License Plugin

This plugin automatically adds Creative Commons license icons and links
to pages based on the 'license' property in their YAML frontmatter.
"""

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin
import re


class CreativeCommonsPlugin(BasePlugin):
    """
    MkDocs plugin for automatic Creative Commons license management.
    
    This plugin reads the 'license' property from page metadata and automatically
    generates appropriate Creative Commons license icons and links.
    """
    
    config_scheme = (
        ('default_license', config_options.Type(str, default='by-sa')),
        ('language', config_options.Type(str, default='fr')),
        ('target_blank', config_options.Type(bool, default=True)),
        ('show_icons', config_options.Type(bool, default=True)),
        ('custom_template', config_options.Type(str, default=None)),
    )
    
    def __init__(self):
        super().__init__()
        self.licenses_used = set()
    
    # Templates for license HTML generation
    LICENCE_ICON_TEMPLATE = '''
    <div style="display: inline-block; text-align: center; margin: 0 4px;">
        <img src="https://mirrors.creativecommons.org/presskit/icons/{}.svg?ref=chooser-v1" alt="{}" style="height:24px!important; display: block;">
        <small style="font-size: 12px; color: #333; font-weight: bold; margin-top: 3px; display: block; text-transform: uppercase;">{}</small>
    </div>'''
    LICENCE_LINK_TEMPLATE = '<a class="cc-license-link" href="https://creativecommons.org/licenses/{}/4.0/deed.{}" target="{}" rel="license noopener noreferrer" style="text-decoration: none; display: inline-flex; align-items: center;">{}</a>'
    
    def on_env(self, env, **kwargs):
        """
        Add the license builder function to Jinja2 environment.
        """
        print("[CC License Plugin] Adding functions to Jinja2 environment")
        
        def build_license_html(page_meta):
            """
            Build HTML for Creative Commons license based on page metadata.
            """
            print(f"[CC License Plugin] build_license_html called with: {page_meta}")
            return self._build_license_html(page_meta)
        
        def get_license_info(page_meta):
            """
            Get structured license information.
            """
            print(f"[CC License Plugin] get_license_info called with: {page_meta}")
            return self._get_license_info(page_meta)
        
        # Add functions to Jinja2 environment
        env.globals['build_license_html'] = build_license_html
        env.globals['get_license_info'] = get_license_info
        env.globals['cc_license'] = build_license_html  # Alias for backwards compatibility
        
        print("[CC License Plugin] Functions added to Jinja2 environment")
        return env

    def on_page_markdown(self, markdown, page, config, files, **kwargs):
        """
        Process page markdown and track license usage.
        """
        if hasattr(page, 'meta') and page.meta and 'license' in page.meta:
            license_str = str(page.meta['license']).lower()
            self.licenses_used.add(license_str)

        return markdown

    def on_post_build(self, config, **kwargs):
        """
        Log summary of license usage.
        """
        if self.licenses_used:
            print(f"[CC License Plugin] Used licenses: {', '.join(sorted(self.licenses_used))}")
        else:
            print(f"[CC License Plugin] No explicit licenses found, using default: {self.config['default_license']}")

    def _build_license_html(self, page_meta: dict) -> str:
        """
        Build the complete HTML for Creative Commons license display.
        """
        license_info = self._get_license_info(page_meta)
        
        if self.config.get('custom_template'):
            # Use custom template if provided
            return self._render_custom_template(license_info)
        
        # Generate icons HTML
        icons_html = ""
        if self.config['show_icons']:
            icons_html = self._build_icons_html(license_info['elements'])
        
        # Generate link HTML
        target = "_blank" if self.config['target_blank'] else "_self"
        link_html = self.LICENCE_LINK_TEMPLATE.format(
            license_info['license_code'],
            self.config['language'],
            target,
            icons_html
        )
        
        return link_html
    
    def _get_license_info(self, page_meta: dict) -> dict:
        """
        Extract and process license information from page metadata.
        """
        # Get license from metadata or use default
        license_str = page_meta.get('license', self.config['default_license'])
        license_str = str(license_str).lower().strip()
        
        # Clean up license string
        license_str = re.sub(r'^cc-?', '', license_str)  # Remove cc- prefix if present
        license_str = re.sub(r'[^a-z-]', '', license_str)  # Keep only letters and hyphens
        
        # Always include 'cc' (Creative Commons) as first element
        elements = ['cc']
        if license_str:
            elements.extend(license_str.split('-'))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for elem in elements:
            if elem and elem not in seen:
                seen.add(elem)
                unique_elements.append(elem)
        
        return {
            'license_code': license_str or self.config['default_license'],
            'elements': unique_elements,
            'full_name': self._get_license_full_name(license_str or self.config['default_license']),
            'url': f"https://creativecommons.org/licenses/{license_str or self.config['default_license']}/4.0/deed.{self.config['language']}"
        }
    
    def _build_icons_html(self, elements: list) -> str:
        """
        Build HTML for license icons with letters underneath.
        """
        icons = []
        for element in elements:
            alt_text = self._get_element_description(element)
            letter_text = element.upper()  # Corresponding letters
            icon_html = self.LICENCE_ICON_TEMPLATE.format(element, alt_text, letter_text)
            icons.append(icon_html)
        
        return ''.join(icons)
    
    def _get_license_full_name(self, license_code: str) -> str:
        """
        Get full name for license code.
        """
        license_names = {
            'by': 'Attribution',
            'by-sa': 'Attribution-ShareAlike',
            'by-nc': 'Attribution-NonCommercial',
            'by-nc-sa': 'Attribution-NonCommercial-ShareAlike',
            'by-nd': 'Attribution-NoDerivatives',
            'by-nc-nd': 'Attribution-NonCommercial-NoDerivatives',
            'cc0': 'CC0 Public Domain Dedication'
        }
        
        return license_names.get(license_code, f'Creative Commons {license_code.upper()}')
    
    def _get_element_description(self, element: str) -> str:
        """
        Get description for license element.
        """
        descriptions = {
            'cc': 'Creative Commons',
            'by': 'Attribution',
            'sa': 'ShareAlike',
            'nc': 'NonCommercial',
            'nd': 'NoDerivatives'
        }
        
        return descriptions.get(element, element.upper())
    
    def _render_custom_template(self, license_info: dict) -> str:
        """
        Render custom template if provided.
        """
        # This could be expanded to support custom Jinja2 templates
        # For now, just return the default rendering
        return self._build_icons_html(license_info['elements'])
