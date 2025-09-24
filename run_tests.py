#!/usr/bin/env python3
"""
Test runner script for TCGPlayer Card Scraper.
"""

import sys
import subprocess
from pathlib import Path


def run_tests(test_type="all", verbose=True):
    """
    Run tests for the TCGPlayer Card Scraper.
    
    Args:
        test_type: Type of tests to run ('unit', 'integration', 'all')
        verbose: Whether to run in verbose mode
    """
    project_root = Path(__file__).parent
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test path based on type
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        print("Available types: unit, integration, all")
        return False
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage if available
    try:
        import coverage
        cmd.extend(["--cov=src", "--cov=configs", "--cov-report=term-missing"])
    except ImportError:
        print("Coverage not available, running without coverage")
    
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, cwd=project_root)
    return result.returncode == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run TCGPlayer Card Scraper tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Run in quiet mode"
    )
    
    args = parser.parse_args()
    
    success = run_tests(args.type, verbose=not args.quiet)
    
    if success:
        print(f"\n✅ {args.type.title()} tests passed!")
        sys.exit(0)
    else:
        print(f"\n❌ {args.type.title()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
