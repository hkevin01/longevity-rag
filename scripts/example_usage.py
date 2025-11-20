#!/usr/bin/env python3
"""
Example usage script for Longevity RAG system.

Demonstrates basic functionality and API usage.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logger import setup_logger, get_logger
from utils.timing import measure_time, Timer, print_timing_report

# Initialize logger
logger = setup_logger(name="example", log_level="INFO")


@measure_time()
def example_timed_function(duration: float = 0.1) -> str:
    """Example function with timing decorator."""
    import time
    time.sleep(duration)
    logger.info(f"Completed sleep for {duration} seconds")
    return "Success"


def main():
    """Main example function."""
    logger.info("Starting Longevity RAG Example")
    logger.info("=" * 60)
    
    # Example 1: Timed function
    logger.info("\nExample 1: Timed Function")
    result = example_timed_function(0.1)
    logger.info(f"Result: {result}")
    
    # Example 2: Timer context manager
    logger.info("\nExample 2: Timer Context Manager")
    with Timer("data_processing"):
        import time
        time.sleep(0.2)
        logger.info("Processing data...")
    
    # Example 3: Multiple calls for statistics
    logger.info("\nExample 3: Multiple Timed Calls")
    for i in range(3):
        example_timed_function(0.05)
    
    # Print timing report
    logger.info("\n" + "=" * 60)
    print_timing_report()
    logger.info("=" * 60)
    
    logger.info("\n✅ Example completed successfully!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        sys.exit(1)
