

import sys
import os
import requests
import json
import pandas as pd

sys.path.append(os.path.abspath(__file__ + "/../../../"))
from sparkmeter_airflow.utils.config_manager import ConfigManager
from sparkmeter_airflow.utils.log_manager import setup_logging


class CustomerOperations:
    
    def __init__(self):
        self.conf = ConfigManager()
        self.session = requests.Session()
        self.org_id = self.conf.read_config("config_file", section="session")["org_id"]
        self.url = self.conf.read_config("config_file", section="session")["url"]
        self.k_session = self.conf.read_config("config_file", section="session")["ksession"]
        self.referer = self.conf.read_config("config_file", section="session")["referer"]
        self.all_customers = self.conf.read_config("config_file", section="data")["customer_list"]

    def get_customers(self, page_number):
        setup_logging().info(
            "Start to fetch customers from Sparkmeter"
        )

        cookies = {
            "ksession": self.k_session,
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Referer": self.referer,
            "Origin": self.org_id
        }
        self.session.headers.update(headers)
        self.session.cookies.update(cookies)
        params = {
            "page": page_number,
            "rollupLevel": "portfolio",
            "meterIdNotNull": "true"
        }
        response = self.session.get(
            self.url,
            params=params,
            timeout=60,
            allow_redirects=True
        )
        data = response.json()
        customers = data.get("customers")

        if not isinstance(data, dict):
            raise Exception("JSON format invalid")

        if customers is None:
            raise Exception(
                f"Invalid customer key. Received key is: {list(data.keys())}"
            )

        return customers


    def save_json(self, customers):
        temporary_file = self.all_customers

        try:
            setup_logging().info(
                "Start to save all customers to temporary file"
            )
            with open(temporary_file, "w") as f:
                json.dump(
                    {
                        "organization_id": self.org_id,
                        "total_customers": len(customers),
                        "customers": customers
                    },
                    f,
                    ensure_ascii=False,
                    indent=2
                )
        except Exception as e:
            setup_logging().error(
                f"An error occurred while saving all customers to temporary file {e}"
            )

    def save_customers(self):

        all_customers = []

        seen_ids = set()
        MAX_PAGES = 500

        for page in range(1, MAX_PAGES + 1):

            try:

                customers = self.get_customers(page)

            except Exception as e:

                setup_logging().error(
                    f"An error occurred on page {e}"
                )

                if all_customers:
                    self.save_json(all_customers)
                    setup_logging().info(
                        "Client already saved"
                    )
                raise

            if not customers:
                setup_logging().info(
                    "Pagination finish"
                )
                break

            new_customers = 0

            for customer in customers:

                customer_id = customer.get("id")

                if customer_id is None:
                    all_customers.append(customer)
                    new_customers += 1
                    continue

                if customer_id not in seen_ids:
                    seen_ids.add(customer_id)

                    all_customers.append(customer)

                    new_customers += 1

            self.save_json(all_customers)

            if new_customers == 0 and not customers:
                break

        else:
            setup_logging().info(
                "Maximum pages reached"
            )

        if all_customers:
            print(
                json.dumps(
                    all_customers[0],
                    ensure_ascii=False,
                    indent=2
                )
            )

        setup_logging().info(
            "All customers are saved successfully"
        )

    def load_customer(self):

        setup_logging().info(
            "Start to load all SparkMerter client"
        )

        all_customers = self.all_customers
        frames = []

        try:
            with open(all_customers, "r", encoding="utf-8") as f:

                data = json.load(f)

            customers = data.get("customers", [])

            for customer in customers:

                customer_name = customer.get("name")

                meters = customer.get("meters", [])

                for meter in meters:

                    serial = meter.get("serial")

                    if not serial:
                        continue

                    frames.append({
                        "serial": serial,
                        "customer_name": customer_name
                    })

            df = pd.DataFrame(frames, columns=["serial", "customer_name"])

            if df.empty:
                setup_logging().warning(
                    "Clients counter empty"
                )
                return df

            df["serial"] = (
                df["serial"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

            df = df[
                df["serial"].notna() &
                (df["serial"] != "")
                ]

            df = df.drop_duplicates(
                subset=["serial"]
            ).reset_index(drop=True)

            setup_logging().info(
                f"{len(df)} counter found"
            )

            return df

        except (FileNotFoundError, json.JSONDecodeError) as e:

            setup_logging().error(
                f"Unable to load customer reference: {e}"
            )

            raise

        except Exception as e:

            setup_logging().exception(
                f"Unexpected error while loading customers: {e}"
            )

            raise


