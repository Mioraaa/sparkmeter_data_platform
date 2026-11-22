
import sys
import os
import logging
# sys.path.append(os.path.abspath(__file__ + "/../../../"))

def setup_logging() -> logging.Logger:
    logging_format = "[%(asctime)s: %(levelname)s: [%(module)s]: %(message)s]"
    logging.basicConfig(
        level=logging.INFO,
        format=logging_format,
    )
    logger = logging.getLogger("SparkMeter Airflow")
    return logger