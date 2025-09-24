"""
Unit tests for configuration loading.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open
from configs.config import (
    load_config,
    get_config_value,
    TCGPLAYER_PAGES_TO_MONITOR,
    MONITORING_INTERVAL_SECONDS,
    HEADLESS_MODE,
    MAX_PRICE_ALERT,
    MIN_CONDITION,
    DISCORD_WEBHOOK_URL,
    ALERT_ALL_NEW_SALES,
    EMAIL_ALERTS,
    ALERT_EMAIL,
    DATA_FILE,
    LOG_FILE
)


class TestLoadConfig:
    """Test cases for load_config function."""
    
    def test_load_config_success(self, temp_config_file):
        """Test successful config loading."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            config = load_config()
            
            assert isinstance(config, dict)
            assert 'tcgplayer_pages_to_monitor' in config
            assert 'monitoring' in config
            assert 'alerts' in config
            assert 'storage' in config
    
    def test_load_config_caching(self, temp_config_file):
        """Test that config is cached after first load."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            # First load
            config1 = load_config()
            
            # Second load should return cached version
            config2 = load_config()
            
            assert config1 is config2  # Same object reference
    
    def test_config_file_not_found(self):
        """Test handling when config file doesn't exist."""
        with patch('configs.config.CONFIG_FILE', Path('/nonexistent/config.yaml')):
            with pytest.raises(FileNotFoundError):
                load_config()
    
    def test_invalid_yaml(self):
        """Test handling of invalid YAML content."""
        invalid_yaml = "invalid: yaml: content: ["
        
        with patch('configs.config.CONFIG_FILE', Path('/tmp/test.yaml')):
            with patch('builtins.open', mock_open(read_data=invalid_yaml)):
                with pytest.raises(ValueError, match="Invalid YAML configuration"):
                    load_config()
    
    def test_file_read_error(self):
        """Test handling of file read errors."""
        with patch('configs.config.CONFIG_FILE', Path('/tmp/test.yaml')):
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(RuntimeError, match="Failed to load configuration"):
                    load_config()


class TestGetConfigValue:
    """Test cases for get_config_value function."""
    
    def test_get_simple_value(self, temp_config_file):
        """Test getting a simple config value."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('monitoring.interval_seconds')
            assert result == 30
    
    def test_get_nested_value(self, temp_config_file):
        """Test getting nested config values."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('alerts.discord_webhook_url')
            assert result == 'https://discord.com/api/webhooks/test/webhook'
    
    def test_get_nonexistent_value(self, temp_config_file):
        """Test getting a nonexistent config value."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('nonexistent.key')
            assert result is None
    
    def test_get_nonexistent_value_with_default(self, temp_config_file):
        """Test getting a nonexistent config value with default."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('nonexistent.key', 'default_value')
            assert result == 'default_value'
    
    def test_get_list_value(self, temp_config_file):
        """Test getting a list config value."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('tcgplayer_pages_to_monitor')
            assert isinstance(result, list)
            assert len(result) == 2
            assert 'test-card' in result[0]
    
    def test_get_partial_path(self, temp_config_file):
        """Test getting a value with partial path."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            result = get_config_value('monitoring')
            assert isinstance(result, dict)
            assert 'interval_seconds' in result
            assert 'headless_mode' in result


class TestConfigConstants:
    """Test cases for configuration constants."""
    
    def test_tcgplayer_pages_to_monitor(self, temp_config_file):
        """Test TCGPLAYER_PAGES_TO_MONITOR constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            # Clear the cached config to force reload
            import configs.config
            configs.config._config = None
            
            pages = TCGPLAYER_PAGES_TO_MONITOR
            assert isinstance(pages, list)
            assert len(pages) == 2
            assert 'test-card' in pages[0]
    
    def test_monitoring_interval_seconds(self, temp_config_file):
        """Test MONITORING_INTERVAL_SECONDS constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            interval = MONITORING_INTERVAL_SECONDS
            assert interval == 30
    
    def test_headless_mode(self, temp_config_file):
        """Test HEADLESS_MODE constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            headless = HEADLESS_MODE
            assert headless is True
    
    def test_max_price_alert(self, temp_config_file):
        """Test MAX_PRICE_ALERT constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            max_price = MAX_PRICE_ALERT
            assert max_price == 50.0
    
    def test_min_condition(self, temp_config_file):
        """Test MIN_CONDITION constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            condition = MIN_CONDITION
            assert condition == 'Near Mint'
    
    def test_discord_webhook_url(self, temp_config_file):
        """Test DISCORD_WEBHOOK_URL constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            webhook = DISCORD_WEBHOOK_URL
            assert webhook == 'https://discord.com/api/webhooks/test/webhook'
    
    def test_alert_all_new_sales(self, temp_config_file):
        """Test ALERT_ALL_NEW_SALES constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            alert_all = ALERT_ALL_NEW_SALES
            assert alert_all is True
    
    def test_email_alerts(self, temp_config_file):
        """Test EMAIL_ALERTS constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            email_alerts = EMAIL_ALERTS
            assert email_alerts is False
    
    def test_alert_email(self, temp_config_file):
        """Test ALERT_EMAIL constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            email = ALERT_EMAIL
            assert email is None
    
    def test_data_file(self, temp_config_file):
        """Test DATA_FILE constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            data_file = DATA_FILE
            assert data_file == 'test_card_data.json'
    
    def test_log_file(self, temp_config_file):
        """Test LOG_FILE constant."""
        with patch('configs.config.CONFIG_FILE', Path(temp_config_file)):
            import configs.config
            configs.config._config = None
            
            log_file = LOG_FILE
            assert log_file == 'test_monitor.log'
    
    def test_default_values_when_config_missing(self):
        """Test that default values are used when config is missing."""
        with patch('configs.config.CONFIG_FILE', Path('/nonexistent/config.yaml')):
            # These should use default values from the functions
            assert TCGPLAYER_PAGES_TO_MONITOR == []
            assert MONITORING_INTERVAL_SECONDS == 60
            assert HEADLESS_MODE is True
            assert MAX_PRICE_ALERT == 100.0
            assert MIN_CONDITION == "Lightly Played"
            assert DISCORD_WEBHOOK_URL == ""
            assert ALERT_ALL_NEW_SALES is True
            assert EMAIL_ALERTS is False
            assert ALERT_EMAIL is None
            assert DATA_FILE == "card_data.json"
            assert LOG_FILE == "monitor.log"
