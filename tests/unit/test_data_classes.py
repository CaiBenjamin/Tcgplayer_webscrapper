"""
Unit tests for data classes.
"""

import pytest
from datetime import datetime
from src.data_classes import LastSoldRecord


class TestLastSoldRecord:
    """Test cases for LastSoldRecord class."""
    
    def test_init(self):
        """Test LastSoldRecord initialization."""
        record = LastSoldRecord(
            title="Test Card",
            price=25.99,
            condition="Near Mint",
            sold_date="2024-01-15",
            url="https://www.tcgplayer.com/product/123456/test-card"
        )
        
        assert record.title == "Test Card"
        assert record.price == 25.99
        assert record.condition == "Near Mint"
        assert record.sold_date == "2024-01-15"
        assert record.url == "https://www.tcgplayer.com/product/123456/test-card"
        assert isinstance(record.timestamp, datetime)
    
    def test_to_dict(self, sample_last_sold_record):
        """Test converting LastSoldRecord to dictionary."""
        record_dict = sample_last_sold_record.to_dict()
        
        expected_keys = {'title', 'price', 'condition', 'sold_date', 'url', 'timestamp'}
        assert set(record_dict.keys()) == expected_keys
        
        assert record_dict['title'] == "Test Card"
        assert record_dict['price'] == 25.99
        assert record_dict['condition'] == "Near Mint"
        assert record_dict['sold_date'] == "2024-01-15"
        assert record_dict['url'] == "https://www.tcgplayer.com/product/123456/test-card"
        assert isinstance(record_dict['timestamp'], str)
    
    def test_from_dict(self):
        """Test creating LastSoldRecord from dictionary."""
        record_data = {
            'title': 'Test Card',
            'price': 25.99,
            'condition': 'Near Mint',
            'sold_date': '2024-01-15',
            'url': 'https://www.tcgplayer.com/product/123456/test-card',
            'timestamp': '2024-01-15T10:30:00'
        }
        
        record = LastSoldRecord.from_dict(record_data)
        
        assert record.title == "Test Card"
        assert record.price == 25.99
        assert record.condition == "Near Mint"
        assert record.sold_date == "2024-01-15"
        assert record.url == "https://www.tcgplayer.com/product/123456/test-card"
        assert isinstance(record.timestamp, datetime)
        assert record.timestamp.isoformat() == '2024-01-15T10:30:00'
    
    def test_roundtrip_conversion(self, sample_last_sold_record):
        """Test converting to dict and back preserves data."""
        # Convert to dict
        record_dict = sample_last_sold_record.to_dict()
        
        # Create new record from dict
        new_record = LastSoldRecord.from_dict(record_dict)
        
        # Compare all fields except timestamp (which will be slightly different)
        assert new_record.title == sample_last_sold_record.title
        assert new_record.price == sample_last_sold_record.price
        assert new_record.condition == sample_last_sold_record.condition
        assert new_record.sold_date == sample_last_sold_record.sold_date
        assert new_record.url == sample_last_sold_record.url
    
    def test_price_types(self):
        """Test that price can handle different numeric types."""
        # Test with integer
        record_int = LastSoldRecord("Test", 25, "NM", "2024-01-15", "http://test.com")
        assert record_int.price == 25
        
        # Test with float
        record_float = LastSoldRecord("Test", 25.99, "NM", "2024-01-15", "http://test.com")
        assert record_float.price == 25.99
    
    def test_empty_strings(self):
        """Test handling of empty strings."""
        record = LastSoldRecord("", 0.0, "", "", "")
        
        assert record.title == ""
        assert record.price == 0.0
        assert record.condition == ""
        assert record.sold_date == ""
        assert record.url == ""
    
    def test_special_characters(self):
        """Test handling of special characters in strings."""
        record = LastSoldRecord(
            title="Test Card & More!",
            price=25.99,
            condition="Near Mint (NM)",
            sold_date="2024-01-15",
            url="https://www.tcgplayer.com/product/123456/test-card?param=value"
        )
        
        assert record.title == "Test Card & More!"
        assert record.condition == "Near Mint (NM)"
        assert "param=value" in record.url
