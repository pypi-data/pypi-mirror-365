"""
Tests for the Creative Commons License Plugin
"""

import pytest
from mkdocs_cc_license_plugin.plugin import CreativeCommonsPlugin


class TestCreativeCommonsPlugin:
    
    def setup_method(self):
        """Setup test instance"""
        self.plugin = CreativeCommonsPlugin()
        # Set default config
        self.plugin.config = {
            'default_license': 'by-sa',
            'language': 'fr',
            'target_blank': True,
            'show_icons': True,
            'custom_template': None
        }
    
    def test_get_license_info_default(self):
        """Test license info with default license"""
        page_meta = {}
        result = self.plugin._get_license_info(page_meta)
        
        assert result['license_code'] == 'by-sa'
        assert result['elements'] == ['cc', 'by', 'sa']
        assert result['full_name'] == 'Attribution-ShareAlike'
        assert 'by-sa/4.0/deed.fr' in result['url']
    
    def test_get_license_info_custom(self):
        """Test license info with custom license"""
        page_meta = {'license': 'by-nc-sa'}
        result = self.plugin._get_license_info(page_meta)
        
        assert result['license_code'] == 'by-nc-sa'
        assert result['elements'] == ['cc', 'by', 'nc', 'sa']
        assert result['full_name'] == 'Attribution-NonCommercial-ShareAlike'
    
    def test_get_license_info_with_cc_prefix(self):
        """Test license info with cc prefix"""
        page_meta = {'license': 'cc-by-nc'}
        result = self.plugin._get_license_info(page_meta)
        
        assert result['license_code'] == 'by-nc'
        assert result['elements'] == ['cc', 'by', 'nc']
    
    def test_build_icons_html(self):
        """Test icons HTML generation"""
        elements = ['cc', 'by', 'sa']
        result = self.plugin._build_icons_html(elements)
        
        assert 'cc.svg' in result
        assert 'by.svg' in result
        assert 'sa.svg' in result
        assert 'alt="Creative Commons"' in result
        assert 'alt="Attribution"' in result
        assert 'alt="ShareAlike"' in result
    
    def test_build_license_html(self):
        """Test complete license HTML generation"""
        page_meta = {'license': 'by-nc-sa'}
        result = self.plugin._build_license_html(page_meta)
        
        assert 'class="cc-license-link"' in result
        assert 'by-nc-sa/4.0/deed.fr' in result
        assert 'target="_blank"' in result
        assert 'cc.svg' in result
        assert 'by.svg' in result
        assert 'nc.svg' in result
        assert 'sa.svg' in result
    
    def test_build_license_html_no_icons(self):
        """Test license HTML without icons"""
        self.plugin.config['show_icons'] = False
        page_meta = {'license': 'by-sa'}
        result = self.plugin._build_license_html(page_meta)
        
        assert 'class="cc-license-link"' in result
        assert 'by-sa/4.0/deed.fr' in result
        assert '.svg' not in result
    
    def test_build_license_html_no_target_blank(self):
        """Test license HTML without target blank"""
        self.plugin.config['target_blank'] = False
        page_meta = {'license': 'by'}
        result = self.plugin._build_license_html(page_meta)
        
        assert 'target="_self"' in result
    
    def test_get_license_full_name(self):
        """Test license full name mapping"""
        assert self.plugin._get_license_full_name('by') == 'Attribution'
        assert self.plugin._get_license_full_name('by-sa') == 'Attribution-ShareAlike'
        assert self.plugin._get_license_full_name('by-nc-sa') == 'Attribution-NonCommercial-ShareAlike'
        assert self.plugin._get_license_full_name('cc0') == 'CC0 Public Domain Dedication'
        assert self.plugin._get_license_full_name('unknown') == 'Creative Commons UNKNOWN'
    
    def test_get_element_description(self):
        """Test element description mapping"""
        assert self.plugin._get_element_description('cc') == 'Creative Commons'
        assert self.plugin._get_element_description('by') == 'Attribution'
        assert self.plugin._get_element_description('sa') == 'ShareAlike'
        assert self.plugin._get_element_description('nc') == 'NonCommercial'
        assert self.plugin._get_element_description('nd') == 'NoDerivatives'
        assert self.plugin._get_element_description('unknown') == 'UNKNOWN'


if __name__ == '__main__':
    pytest.main([__file__])
