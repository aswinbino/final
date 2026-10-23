"""
Standard library logging shim for loguru.
Ensures zero external dependency issues.
"""

import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout
)

logger = logging.getLogger("ClauseGuard")
logger.success = logger.info
