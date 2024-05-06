from examples import vdsat
from examples import wiwb

import logging
import sys


def check_python_version():
    major = sys.version_info.major
    minor = sys.version_info.minor
    minor_min = 8
    minor_max = 12
    if major == 3 and minor_min <= minor <= minor_max:
        return
    raise AssertionError(f"your python version = {major}.{minor}. Please use python 3.{minor_min} to 3.{minor_max}")


def setup_logging():
    """Adds 2 configured handlers to the root logger: stream and log_rotating_file."""

    # handler: stream
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"))
    root_logger = logging.getLogger()
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(min([handler.level for handler in root_logger.handlers]))
    root_logger.info("setup logging done")


if __name__ == "__main__":
    check_python_version()
    setup_logging()
    wiwb.run_example()
    vdsat.run_example()
