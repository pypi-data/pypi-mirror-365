# Application entry point (starts the server)

import logging
import sys

from openmarkets.core.server import main

logging.basicConfig(
    level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_server():
    """Main entry point for the Open Markets application."""
    logger.info("Starting Open Markets server...")
    try:
        main()
    except Exception as e:
        logger.error(f"An error occurred during server startup: {e}", exc_info=True)
        sys.exit(1)
    logger.info("Open Markets server started successfully.")


if __name__ == "__main__":
    run_server()
