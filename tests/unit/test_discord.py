"""
Unit tests for Discord utilities.
"""

import pytest
from unittest.mock import Mock, patch
from src.utils.discord import send_discord_alert, send_startup_notification


class TestSendDiscordAlert:
    """Test cases for send_discord_alert function."""
    
    @patch('src.utils.discord.requests.post')
    def test_successful_alert(self, mock_post):
        """Test successful Discord alert sending."""
        # Setup mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        message = "Test alert message"
        
        # Call function
        send_discord_alert(message, webhook_url)
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        assert call_args[0][0] == webhook_url
        assert call_args[1]['json']['content'] == message
        assert call_args[1]['json']['username'] == "TCGPlayer Last Sold Monitor"
        assert call_args[1]['timeout'] == 10
    
    def test_empty_webhook_url(self):
        """Test that function returns early when webhook URL is empty."""
        with patch('src.utils.discord.requests.post') as mock_post:
            send_discord_alert("Test message", "")
            mock_post.assert_not_called()
    
    def test_none_webhook_url(self):
        """Test that function returns early when webhook URL is None."""
        with patch('src.utils.discord.requests.post') as mock_post:
            send_discord_alert("Test message", None)
            mock_post.assert_not_called()
    
    @patch('src.utils.discord.requests.post')
    def test_request_failure(self, mock_post):
        """Test handling of request failure."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("Network error")
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        message = "Test alert message"
        
        # Should not raise exception
        send_discord_alert(message, webhook_url)
        
        # Verify request was attempted
        mock_post.assert_called_once()
    
    @patch('src.utils.discord.requests.post')
    def test_http_error(self, mock_post):
        """Test handling of HTTP error response."""
        # Setup mock response that raises HTTP error
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("HTTP 400")
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        message = "Test alert message"
        
        # Should not raise exception
        send_discord_alert(message, webhook_url)
        
        # Verify request was made
        mock_post.assert_called_once()


class TestSendStartupNotification:
    """Test cases for send_startup_notification function."""
    
    @patch('src.utils.discord.requests.post')
    def test_successful_startup_notification(self, mock_post):
        """Test successful startup notification sending."""
        # Setup mock response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        pages_to_monitor = [
            "https://www.tcgplayer.com/product/123456/test-card",
            "https://www.tcgplayer.com/product/789012/another-card"
        ]
        monitoring_interval_seconds = 60
        
        # Call function
        send_startup_notification(webhook_url, pages_to_monitor, monitoring_interval_seconds)
        
        # Verify request was made correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        
        assert call_args[0][0] == webhook_url
        payload = call_args[1]['json']
        assert payload['username'] == "TCGPlayer Last Sold Monitor"
        assert "TCGPlayer Monitor Started!" in payload['content']
        assert "Monitoring 2 cards:" in payload['content']
        assert "Test Card" in payload['content']
        assert "Another Card" in payload['content']
        assert "Every 1 minutes" in payload['content']
    
    def test_empty_webhook_url(self):
        """Test that function returns early when webhook URL is empty."""
        with patch('src.utils.discord.requests.post') as mock_post:
            send_startup_notification("", [], 60)
            mock_post.assert_not_called()
    
    def test_none_webhook_url(self):
        """Test that function returns early when webhook URL is None."""
        with patch('src.utils.discord.requests.post') as mock_post:
            send_startup_notification(None, [], 60)
            mock_post.assert_not_called()
    
    @patch('src.utils.discord.requests.post')
    def test_card_name_extraction(self, mock_post):
        """Test card name extraction from URLs."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        pages_to_monitor = [
            "https://www.tcgplayer.com/product/123456/pokemon-charizard-base-set",
            "https://www.tcgplayer.com/product/789012/magic-the-gathering-black-lotus"
        ]
        monitoring_interval_seconds = 120
        
        send_startup_notification(webhook_url, pages_to_monitor, monitoring_interval_seconds)
        
        # Verify card names were extracted correctly
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        content = payload['content']
        
        assert "Pokemon Charizard Base Set" in content
        assert "Magic The Gathering Black Lotus" in content
        assert "Every 2 minutes" in content
    
    @patch('src.utils.discord.requests.post')
    def test_unknown_card_names(self, mock_post):
        """Test handling of URLs that don't match expected format."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        pages_to_monitor = [
            "https://example.com/not-tcgplayer",
            "https://www.tcgplayer.com/invalid-url"
        ]
        monitoring_interval_seconds = 60
        
        send_startup_notification(webhook_url, pages_to_monitor, monitoring_interval_seconds)
        
        # Verify unknown card names are handled
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        content = payload['content']
        
        assert "Unknown Card" in content
        assert content.count("Unknown Card") == 2
    
    @patch('src.utils.discord.requests.post')
    def test_request_failure(self, mock_post):
        """Test handling of request failure."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("Network error")
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        pages_to_monitor = ["https://www.tcgplayer.com/product/123456/test-card"]
        monitoring_interval_seconds = 60
        
        # Should not raise exception
        send_startup_notification(webhook_url, pages_to_monitor, monitoring_interval_seconds)
        
        # Verify request was attempted
        mock_post.assert_called_once()
    
    @patch('src.utils.discord.requests.post')
    def test_interval_conversion(self, mock_post):
        """Test monitoring interval conversion to minutes."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        webhook_url = "https://discord.com/api/webhooks/test/webhook"
        pages_to_monitor = ["https://www.tcgplayer.com/product/123456/test-card"]
        
        # Test various intervals
        test_cases = [
            (30, "Every 0 minutes"),  # 30 seconds = 0.5 minutes, rounded down
            (60, "Every 1 minutes"),  # 60 seconds = 1 minute
            (120, "Every 2 minutes"), # 120 seconds = 2 minutes
            (90, "Every 1 minutes"),  # 90 seconds = 1.5 minutes, rounded down
        ]
        
        for interval_seconds, expected_text in test_cases:
            mock_post.reset_mock()
            send_startup_notification(webhook_url, pages_to_monitor, interval_seconds)
            
            call_args = mock_post.call_args
            payload = call_args[1]['json']
            content = payload['content']
            
            assert expected_text in content, f"Failed for interval {interval_seconds} seconds"
