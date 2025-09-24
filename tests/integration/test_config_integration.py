"""
Integration tests for configuration system.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch
from configs.config import load_config, get_config_value


class TestConfigIntegration:
    """Integration tests for configuration loading and usage."""
    
    def test_full_config_workflow(self):
        """Test complete configuration workflow with real YAML file."""
        # Create a comprehensive test config
        config_data = {
            'tcgplayer_pages_to_monitor': [
                'https://www.tcgplayer.com/product/123456/pokemon-charizard-base-set',
                'https://www.tcgplayer.com/product/789012/magic-black-lotus'
            ],
            'monitoring': {
                'interval_seconds': 45,
                'headless_mode': False,
                'max_price_alert': 75.50,
                'min_condition': 'Lightly Played'
            },
            'alerts': {
                'discord_webhook_url': 'https://discord.com/api/webhooks/123456789/test',
                'alert_all_new_sales': False,
                'email_alerts': True,
                'alert_email': 'test@example.com'
            },
            'storage': {
                'data_file': 'integration_test_data.json',
                'log_file': 'integration_test.log'
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file_path = f.name
        
        try:
            # Test loading config
            with patch('configs.config.CONFIG_FILE', Path(config_file_path)):
                config = load_config()
                
                # Verify all sections are present
                assert 'tcgplayer_pages_to_monitor' in config
                assert 'monitoring' in config
                assert 'alerts' in config
                assert 'storage' in config
                
                # Test getting various values
                assert get_config_value('monitoring.interval_seconds') == 45
                assert get_config_value('monitoring.headless_mode') is False
                assert get_config_value('alerts.alert_email') == 'test@example.com'
                assert get_config_value('storage.data_file') == 'integration_test_data.json'
                
                # Test getting nested values
                monitoring_config = get_config_value('monitoring')
                assert isinstance(monitoring_config, dict)
                assert monitoring_config['interval_seconds'] == 45
                assert monitoring_config['headless_mode'] is False
                
                # Test getting list values
                pages = get_config_value('tcgplayer_pages_to_monitor')
                assert isinstance(pages, list)
                assert len(pages) == 2
                assert 'charizard' in pages[0].lower()
                assert 'black-lotus' in pages[1].lower()
        
        finally:
            # Cleanup
            Path(config_file_path).unlink(missing_ok=True)
    
    def test_config_with_missing_sections(self):
        """Test configuration with missing optional sections."""
        # Create minimal config
        config_data = {
            'tcgplayer_pages_to_monitor': [
                'https://www.tcgplayer.com/product/123456/test-card'
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file_path = f.name
        
        try:
            with patch('configs.config.CONFIG_FILE', Path(config_file_path)):
                config = load_config()
                
                # Should still load successfully
                assert 'tcgplayer_pages_to_monitor' in config
                
                # Missing sections should return defaults
                assert get_config_value('monitoring.interval_seconds') is None
                assert get_config_value('alerts.discord_webhook_url') is None
                assert get_config_value('storage.data_file') is None
        
        finally:
            Path(config_file_path).unlink(missing_ok=True)
    
    def test_config_with_invalid_data_types(self):
        """Test configuration with invalid data types."""
        # Create config with wrong data types
        config_data = {
            'tcgplayer_pages_to_monitor': 'not_a_list',  # Should be list
            'monitoring': {
                'interval_seconds': 'not_a_number',  # Should be number
                'headless_mode': 'not_a_boolean',  # Should be boolean
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_file_path = f.name
        
        try:
            with patch('configs.config.CONFIG_FILE', Path(config_file_path)):
                config = load_config()
                
                # Should still load, but values will be as specified
                assert get_config_value('tcgplayer_pages_to_monitor') == 'not_a_list'
                assert get_config_value('monitoring.interval_seconds') == 'not_a_number'
                assert get_config_value('monitoring.headless_mode') == 'not_a_boolean'
        
        finally:
            Path(config_file_path).unlink(missing_ok=True)
