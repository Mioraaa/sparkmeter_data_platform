

import tempfile
import zipfile
import sys
import os
from pathlib import Path

sys.path.append(os.path.abspath(__file__ + "/../../../"))
from sparkmeter_airflow.utils.config_manager import ConfigManager
from sparkmeter_airflow.utils.log_manager import setup_logging

class ConsumptionOperations:
    def __init__(self):
        self.conf = ConfigManager()
        self.received_dir = self.conf.read_config("config_file", section="consumption")["received_dir"]

    def extract_all_zip_files(self):

        tmp_dir = Path(self.received_dir + tempfile.mkdtemp(prefix="sparkmeter_local_"))
        data = self.received_dir + "ReceivedFiles"
        zip_files = list(Path(data).glob("*.zip"))

        if not zip_files:
            setup_logging().info(
                "ZIP files not found"
            )
            return tmp_dir
        setup_logging().info(
            f"{len(zip_files)} ZIP files found"
        )

        for zip_file in zip_files:
            setup_logging().info(
                f"Extraction: {zip_file.name}"
            )
            with zipfile.ZipFile(zip_file, "r") as z:
                z.extractall(tmp_dir)

        return tmp_dir