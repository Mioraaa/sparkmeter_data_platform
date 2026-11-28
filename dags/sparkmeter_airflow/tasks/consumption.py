

import tempfile
import zipfile
import sys
import os
from pathlib import Path

import pandas as pd

sys.path.append(os.path.abspath(__file__ + "/../../../"))
from sparkmeter_airflow.utils.config_manager import ConfigManager
from sparkmeter_airflow.utils.log_manager import setup_logging

class ConsumptionOperations:

    def __init__(self):
        self.conf = ConfigManager()
        self.received_dir = self.conf.read_config("config_file", section="consumption")["received_dir"]


    def extract_all_zip_files(self):

        received_dir = Path(self.received_dir)

        tmp_dir = Path(
            tempfile.mkdtemp(
                prefix="sparkmeter_local_",
                dir=received_dir
            )
        )

        data = received_dir / "ReceivedFiles"
        zip_files = list(data.glob("*.zip"))

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

    def find_all_csv(self, root):

        csv_files = []

        for path, _, files in os.walk(root):

            for file in files:

                if file.lower().endswith(".csv"):
                    csv_files.append(
                        Path(path) / file
                    )

        setup_logging().info(
            f"{len(csv_files)} CSV found"
        )

        return csv_files

    def get_periode(self, hour):
        if pd.isna(hour):
            return "Unknown"
        elif 6 <= hour <= 17:
            return "jour"
        elif 18 <= hour <= 20:
            return "base"
        else:
            return "nuit"

