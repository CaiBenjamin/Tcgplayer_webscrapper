"""
Unit tests for text parsing utilities.
"""

import pytest
from src.utils.text_parsing import (
    extract_price_from_text,
    extract_date_from_text,
    extract_condition_from_text
)


class TestExtractPriceFromText:
    """Test cases for extract_price_from_text function."""
    
    def test_basic_price_formats(self):
        """Test basic price extraction formats."""
        test_cases = [
            ("$123.45", 123.45),
            ("$1,234.56", 1234.56),
            ("$123", 123.0),
            ("Price: $25.99", 25.99),
            ("Sold for $1,500.00", 1500.0),
        ]
        
        for text, expected in test_cases:
            result = extract_price_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_multiple_prices(self):
        """Test extraction when multiple prices are present."""
        text = "Listed at $50.00, sold for $45.99"
        result = extract_price_from_text(text)
        # Should return the first price found
        assert result == 50.0
    
    def test_no_price_found(self):
        """Test when no price is found in text."""
        test_cases = [
            "No price here",
            "Just text",
            "$",  # Dollar sign without number
            "123",  # Number without dollar sign
            "",
        ]
        
        for text in test_cases:
            result = extract_price_from_text(text)
            assert result == 0.0, f"Expected 0.0 for text: '{text}'"
    
    def test_edge_cases(self):
        """Test edge cases for price extraction."""
        test_cases = [
            ("$0.00", 0.0),
            ("$0", 0.0),
            ("$999,999.99", 999999.99),
            ("$1.00", 1.0),
        ]
        
        for text, expected in test_cases:
            result = extract_price_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_special_characters(self):
        """Test price extraction with special characters."""
        test_cases = [
            ("Price: $123.45 USD", 123.45),
            ("$123.45 + tax", 123.45),
            ("Final: $123.45!", 123.45),
        ]
        
        for text, expected in test_cases:
            result = extract_price_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"


class TestExtractDateFromText:
    """Test cases for extract_date_from_text function."""
    
    def test_date_formats(self):
        """Test various date format extraction."""
        test_cases = [
            ("Sold on 01/15/2024", "01/15/2024"),
            ("Date: 12/31/23", "12/31/23"),
            ("2024-01-15", "2024-01-15"),
            ("January 15, 2024", "January 15, 2024"),
            ("01/15", "01/15"),
            ("Jan 15", "Jan 15"),
        ]
        
        for text, expected in test_cases:
            result = extract_date_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_no_date_found(self):
        """Test when no date is found in text."""
        test_cases = [
            "No date here",
            "Just text",
            "123",  # Number that's not a date
            "",
        ]
        
        for text in test_cases:
            result = extract_date_from_text(text)
            assert result == "Unknown Date", f"Expected 'Unknown Date' for text: '{text}'"
    
    def test_multiple_dates(self):
        """Test extraction when multiple dates are present."""
        text = "Listed on 01/01/2024, sold on 01/15/2024"
        result = extract_date_from_text(text)
        # Should return the first date found
        assert result == "01/01/2024"


class TestExtractConditionFromText:
    """Test cases for extract_condition_from_text function."""
    
    def test_condition_formats(self):
        """Test various condition extraction."""
        test_cases = [
            ("Near Mint condition", "Near Mint"),
            ("NM card", "NM"),
            ("Lightly Played", "Lightly Played"),
            ("LP", "LP"),
            ("Moderately Played", "Moderately Played"),
            ("MP", "MP"),
            ("Heavily Played", "Heavily Played"),
            ("HP", "HP"),
            ("Damaged", "Damaged"),
            ("DMG", "DMG"),
            ("Mint", "Mint"),
        ]
        
        for text, expected in test_cases:
            result = extract_condition_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_language_variants(self):
        """Test language variant extraction."""
        test_cases = [
            ("Japanese card", "Japanese"),
            ("English version", "English"),
        ]
        
        for text, expected in test_cases:
            result = extract_condition_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_foil_variants(self):
        """Test foil variant extraction."""
        test_cases = [
            ("Foil card", "Foil"),
            ("Non-Foil", "Non-Foil"),
            ("Holo version", "Holo"),
            ("Non-Holo", "Non-Holo"),
        ]
        
        for text, expected in test_cases:
            result = extract_condition_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_case_insensitive(self):
        """Test that condition extraction is case insensitive."""
        test_cases = [
            ("near mint", "Near Mint"),
            ("LIGHTLY PLAYED", "Lightly Played"),
            ("nm", "NM"),
        ]
        
        for text, expected in test_cases:
            result = extract_condition_from_text(text)
            assert result == expected, f"Failed for text: '{text}'"
    
    def test_no_condition_found(self):
        """Test when no condition is found in text."""
        test_cases = [
            "No condition here",
            "Just text",
            "Random words",
            "",
        ]
        
        for text in test_cases:
            result = extract_condition_from_text(text)
            assert result == "Unknown Condition", f"Expected 'Unknown Condition' for text: '{text}'"
    
    def test_multiple_conditions(self):
        """Test extraction when multiple conditions are present."""
        text = "Near Mint condition, also available in Lightly Played"
        result = extract_condition_from_text(text)
        # Should return the first condition found
        assert result == "Near Mint"
