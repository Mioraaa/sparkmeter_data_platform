

import sys
import os
import requests
import json

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
        # try:
        setup_logging().info(
            "Start to fetch customers from Sprkmeter"
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
            "All customers saved successfully"
        )