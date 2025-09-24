# TCGPlayer Card Scraper

A professional-grade monitoring system for TCGPlayer card prices and sales data.

## Project Structure

```
card_scraper/
├── src/                          # Source code package
│   ├── data_classes/             # Data models
│   │   ├── __init__.py
│   │   └── last_sold_record.py   # LastSoldRecord data class
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   ├── text_parsing.py       # Text extraction utilities
│   │   └── discord.py            # Discord integration
│   └── __init__.py
├── scripts/                      # Executable scripts
│   └── tcgplayer_last_sold_monitor.py  # Main monitoring script
├── configs/                      # Configuration files
│   ├── config.py                 # Configuration loader
│   └── config.yaml               # YAML configuration
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Features

- **Structured Configuration**: YAML-based configuration with hierarchical organization
- **Modular Design**: Clean separation of concerns with dedicated modules
- **Data Classes**: Type-safe data models for card records
- **Utility Functions**: Reusable text parsing and Discord integration
- **Professional Structure**: Follows Python packaging best practices

## Configuration

Edit `configs/config.yaml` to customize:

- **TCGPlayer URLs**: Add card pages to monitor
- **Monitoring Settings**: Check intervals, headless mode, price thresholds
- **Alert Settings**: Discord webhook, email notifications
- **Storage**: Data and log file locations

## Usage

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure**:
   Edit `configs/config.yaml` with your TCGPlayer URLs and Discord webhook

3. **Run Monitor**:
   ```bash
   python scripts/tcgplayer_last_sold_monitor.py
   ```

## Testing

The project includes comprehensive unit tests for all core functionality:

### Running Tests

**Quick Test (Core Functionality)**:
```bash
python tests/test_runner.py
```

**Full Test Suite**:
```bash
python -m pytest tests/ -v
```

**Specific Test Categories**:
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only  
python -m pytest tests/integration/ -v

# Specific test file
python -m pytest tests/unit/test_data_classes.py -v
```

### Test Coverage

- **✅ Data Classes**: `LastSoldRecord` serialization/deserialization
- **✅ Text Parsing**: Price, date, and condition extraction utilities
- **✅ Discord Integration**: Alert sending and startup notifications
- **✅ Configuration**: YAML loading and value retrieval
- **✅ Monitor Class**: Core monitoring functionality (partial)

### Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_data_classes.py
│   ├── test_text_parsing.py
│   ├── test_discord.py
│   ├── test_config.py
│   └── test_monitor.py
├── integration/             # Integration tests
│   └── test_config_integration.py
├── conftest.py             # Pytest fixtures and configuration
├── test_runner.py          # Simple test runner for core functionality
└── __init__.py
```

## Architecture

- **Data Classes**: `LastSoldRecord` for type-safe data handling
- **Utils**: Text parsing and Discord integration utilities
- **Config**: YAML-based configuration with Python loader
- **Scripts**: Main monitoring logic with clean imports

This structure follows software engineering best practices with clear separation of concerns, making the codebase maintainable and extensible.