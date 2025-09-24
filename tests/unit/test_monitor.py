"""
Unit tests for TCGPlayerLastSoldMonitor class.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open
from datetime import datetime

from src.data_classes import LastSoldRecord


class TestTCGPlayerLastSoldMonitor:
    """Test cases for TCGPlayerLastSoldMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a monitor instance for testing."""
        from scripts.tcgplayer_last_sold_monitor import TCGPlayerLastSoldMonitor
        return TCGPlayerLastSoldMonitor()
    
    @pytest.fixture
    def temp_data_file(self):
        """Create a temporary data file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({}, f)
            yield f.name
        
        # Cleanup
        Path(f.name).unlink(missing_ok=True)
    
    def test_init(self, monitor):
        """Test monitor initialization."""
        assert monitor.browser is None
        assert monitor.context is None
        assert isinstance(monitor.data_file, Path)
        assert isinstance(monitor.previous_records, dict)
    
    def test_load_previous_data_empty_file(self, monitor, temp_data_file):
        """Test loading previous data from empty file."""
        with patch.object(monitor, 'data_file', Path(temp_data_file)):
            monitor.load_previous_data()
            assert monitor.previous_records == {}
    
    def test_load_previous_data_with_data(self, monitor, temp_data_file):
        """Test loading previous data from file with data."""
        test_data = {
            "https://test.com/card1": [
                {
                    "title": "Test Card 1",
                    "price": 25.99,
                    "condition": "Near Mint",
                    "sold_date": "2024-01-15",
                    "url": "https://test.com/card1",
                    "timestamp": "2024-01-15T10:30:00"
                }
            ]
        }
        
        with open(temp_data_file, 'w') as f:
            json.dump(test_data, f)
        
        with patch.object(monitor, 'data_file', Path(temp_data_file)):
            monitor.load_previous_data()
            
            assert len(monitor.previous_records) == 1
            assert "https://test.com/card1" in monitor.previous_records
            assert len(monitor.previous_records["https://test.com/card1"]) == 1
            assert isinstance(monitor.previous_records["https://test.com/card1"][0], LastSoldRecord)
    
    def test_load_previous_data_file_not_exists(self, monitor):
        """Test loading previous data when file doesn't exist."""
        with patch.object(monitor, 'data_file', Path('/nonexistent/file.json')):
            monitor.load_previous_data()
            assert monitor.previous_records == {}
    
    def test_load_previous_data_invalid_json(self, monitor, temp_data_file):
        """Test loading previous data from invalid JSON file."""
        with open(temp_data_file, 'w') as f:
            f.write("invalid json content")
        
        with patch.object(monitor, 'data_file', Path(temp_data_file)):
            monitor.load_previous_data()
            assert monitor.previous_records == {}
    
    def test_save_data(self, monitor, temp_data_file):
        """Test saving data to file."""
        # Add some test data
        test_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        monitor.previous_records["https://test.com/card1"] = [test_record]
        
        with patch.object(monitor, 'data_file', Path(temp_data_file)):
            monitor.save_data()
            
            # Verify data was saved
            with open(temp_data_file, 'r') as f:
                saved_data = json.load(f)
            
            assert "https://test.com/card1" in saved_data
            assert len(saved_data["https://test.com/card1"]) == 1
            assert saved_data["https://test.com/card1"][0]["title"] == "Test Card"
    
    def test_save_data_empty_records(self, monitor, temp_data_file):
        """Test saving empty records."""
        with patch.object(monitor, 'data_file', Path(temp_data_file)):
            monitor.save_data()
            
            # Verify empty data was saved
            with open(temp_data_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == {}
    
    @pytest.mark.asyncio
    async def test_start_browser(self, monitor, mock_playwright):
        """Test browser startup."""
        playwright, browser, context = mock_playwright
        
        with patch('scripts.tcgplayer_last_sold_monitor.async_playwright', return_value=playwright):
            await monitor.start_browser()
            
            assert monitor.browser == browser
            assert monitor.context == context
            playwright.chromium.launch.assert_called_once()
            browser.new_context.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_browser(self, monitor):
        """Test browser cleanup."""
        # Setup mock browser and context
        monitor.browser = AsyncMock()
        monitor.context = AsyncMock()
        
        await monitor.close_browser()
        
        monitor.context.close.assert_called_once()
        monitor.browser.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_browser_none_objects(self, monitor):
        """Test browser cleanup when objects are None."""
        monitor.browser = None
        monitor.context = None
        
        # Should not raise exception
        await monitor.close_browser()
    
    def test_compare_records_new_sales(self, monitor):
        """Test comparing records with new sales."""
        # Setup previous records
        old_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        monitor.previous_records["https://test.com/card1"] = [old_record]
        
        # Setup current records with new sale
        new_record = LastSoldRecord(
            title="Test Card",
            price=30.00,
            condition="Near Mint",
            sold_date="2024-01-16",
            url="https://test.com/card1"
        )
        current_records = [old_record, new_record]
        
        changes = monitor.compare_records("https://test.com/card1", current_records)
        
        assert len(changes) == 1
        assert changes[0]['type'] == 'new_sale'
        assert changes[0]['record'] == new_record
        assert "New Sale" in changes[0]['message']
    
    def test_compare_records_no_new_sales(self, monitor):
        """Test comparing records with no new sales."""
        # Setup previous records
        old_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        monitor.previous_records["https://test.com/card1"] = [old_record]
        
        # Setup current records with same sale
        current_records = [old_record]
        
        changes = monitor.compare_records("https://test.com/card1", current_records)
        
        assert len(changes) == 0
    
    def test_compare_records_no_previous_data(self, monitor):
        """Test comparing records when no previous data exists."""
        new_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        current_records = [new_record]
        
        changes = monitor.compare_records("https://test.com/card1", current_records)
        
        assert len(changes) == 1
        assert changes[0]['type'] == 'new_sale'
    
    @pytest.mark.asyncio
    async def test_scrape_last_sold_no_context(self, monitor):
        """Test scraping when browser context is not initialized."""
        with pytest.raises(RuntimeError, match="Browser context not initialized"):
            await monitor.scrape_last_sold("https://test.com/card1")
    
    @pytest.mark.asyncio
    async def test_scrape_last_sold_success(self, monitor, mock_browser_context):
        """Test successful scraping of last sold data."""
        context, page = mock_browser_context
        monitor.context = context
        
        # Mock page interactions
        page.goto = AsyncMock()
        page.wait_for_timeout = AsyncMock()
        page.query_selector = AsyncMock(return_value=None)
        page.query_selector_all = AsyncMock(return_value=[])
        page.close = AsyncMock()
        
        # Mock title extraction
        title_element = AsyncMock()
        title_element.inner_text = AsyncMock(return_value="Test Card")
        page.query_selector.return_value = title_element
        
        # Mock price extraction
        price_element = AsyncMock()
        price_element.inner_text = AsyncMock(return_value="$25.99")
        page.query_selector_all.return_value = [price_element]
        
        with patch('scripts.tcgplayer_last_sold_monitor.extract_price_from_text', return_value=25.99):
            records = await monitor.scrape_last_sold("https://test.com/card1")
            
            assert len(records) == 1
            assert records[0].title == "Test Card"
            assert records[0].price == 25.99
            assert records[0].condition == "Most Recent Sale"
    
    @pytest.mark.asyncio
    async def test_scrape_last_sold_exception_handling(self, monitor, mock_browser_context):
        """Test exception handling during scraping."""
        context, page = mock_browser_context
        monitor.context = context
        
        # Mock page to raise exception
        page.goto = AsyncMock(side_effect=Exception("Network error"))
        page.close = AsyncMock()
        
        records = await monitor.scrape_last_sold("https://test.com/card1")
        
        assert records == []
        page.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_monitor_pages_success(self, monitor, mock_browser_context):
        """Test successful monitoring of pages."""
        context, page = mock_browser_context
        monitor.context = context
        
        # Mock scraping to return records
        test_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        
        with patch.object(monitor, 'scrape_last_sold', return_value=[test_record]):
            with patch.object(monitor, 'compare_records', return_value=[]):
                with patch.object(monitor, 'save_data'):
                    with patch('scripts.tcgplayer_last_sold_monitor.send_discord_alert'):
                        await monitor.monitor_pages()
                        
                        # Verify records were stored
                        assert "https://test.com/card1" in monitor.previous_records
                        assert len(monitor.previous_records["https://test.com/card1"]) == 1
    
    @pytest.mark.asyncio
    async def test_monitor_pages_with_alerts(self, monitor, mock_browser_context):
        """Test monitoring pages with alerts."""
        context, page = mock_browser_context
        monitor.context = context
        
        # Mock scraping to return records
        test_record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://test.com/card1"
        )
        
        # Mock comparison to return changes
        changes = [{
            'type': 'new_sale',
            'record': test_record,
            'message': '💰 New Sale: Test Card - $25.99 (Near Mint) - 2024-01-15'
        }]
        
        with patch.object(monitor, 'scrape_last_sold', return_value=[test_record]):
            with patch.object(monitor, 'compare_records', return_value=changes):
                with patch.object(monitor, 'save_data'):
                    with patch('scripts.tcgplayer_last_sold_monitor.send_discord_alert') as mock_alert:
                        await monitor.monitor_pages()
                        
                        # Verify alert was sent
                        mock_alert.assert_called_once_with(
                            '💰 New Sale: Test Card - $25.99 (Near Mint) - 2024-01-15',
                            'https://discord.com/api/webhooks/1420205527295721615/cevkt66p_FCRmPTkg1b4r0lUuejguOfZb4j1v_fo6u6Imb2AU3qVF2S6SdnAWbm6_oUP'
                        )
    
    @pytest.mark.asyncio
    async def test_monitor_pages_exception_handling(self, monitor, mock_browser_context):
        """Test exception handling during page monitoring."""
        context, page = mock_browser_context
        monitor.context = context
        
        with patch.object(monitor, 'scrape_last_sold', side_effect=Exception("Scraping error")):
            with patch.object(monitor, 'save_data'):
                # Should not raise exception
                await monitor.monitor_pages()
    
    @pytest.mark.asyncio
    async def test_run_monitoring_loop_keyboard_interrupt(self, monitor, mock_playwright):
        """Test monitoring loop with keyboard interrupt."""
        playwright, browser, context = mock_playwright
        
        with patch('scripts.tcgplayer_last_sold_monitor.async_playwright', return_value=playwright):
            with patch.object(monitor, 'monitor_pages', side_effect=KeyboardInterrupt()):
                with patch('scripts.tcgplayer_last_sold_monitor.send_startup_notification'):
                    # Should not raise exception
                    await monitor.run_monitoring_loop()
    
    @pytest.mark.asyncio
    async def test_run_monitoring_loop_general_exception(self, monitor, mock_playwright):
        """Test monitoring loop with general exception."""
        playwright, browser, context = mock_playwright
        
        with patch('scripts.tcgplayer_last_sold_monitor.async_playwright', return_value=playwright):
            with patch.object(monitor, 'monitor_pages', side_effect=Exception("General error")):
                with patch('scripts.tcgplayer_last_sold_monitor.send_startup_notification'):
                    # Should not raise exception
                    await monitor.run_monitoring_loop()
