"""
Pytest configuration and fixtures for TCGPlayer Card Scraper tests.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from datetime import datetime

# Add project root to path for imports
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def temp_config_file():
    """Create a temporary config.yaml file for testing."""
    config_data = {
        'tcgplayer_pages_to_monitor': [
            'https://www.tcgplayer.com/product/123456/test-card',
            'https://www.tcgplayer.com/product/789012/another-card'
        ],
        'monitoring': {
            'interval_seconds': 30,
            'headless_mode': True,
            'max_price_alert': 50.0,
            'min_condition': 'Near Mint'
        },
        'alerts': {
            'discord_webhook_url': 'https://discord.com/api/webhooks/test/webhook',
            'alert_all_new_sales': True,
            'email_alerts': False,
            'alert_email': None
        },
        'storage': {
            'data_file': 'test_card_data.json',
            'log_file': 'test_monitor.log'
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        yield f.name
    
    # Cleanup
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def sample_last_sold_record():
    """Create a sample LastSoldRecord for testing."""
    from src.data_classes import LastSoldRecord
    
    return LastSoldRecord(
        title="Test Card",
        price=25.99,
        condition="Near Mint",
        sold_date="2024-01-15",
        url="https://www.tcgplayer.com/product/123456/test-card"
    )


@pytest.fixture
def mock_browser_context():
    """Create a mock browser context for testing."""
    context = AsyncMock()
    page = AsyncMock()
    context.new_page.return_value = page
    return context, page


@pytest.fixture
def mock_playwright():
    """Create a mock playwright instance for testing."""
    playwright = AsyncMock()
    browser = AsyncMock()
    context = AsyncMock()
    
    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context
    
    return playwright, browser, context
