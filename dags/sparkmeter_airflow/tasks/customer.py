

import sys
import os
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sparkmeter_airflow.utils.config_manager import ConfigManager
from sparkmeter_airflow.utils.log_manager import get_logger


class CustomerOperations:
    
    def __init__(self):
        self.conf = ConfigManager()
        self.session = requests.Session()
        self.org_id = self.conf.read_config("config_file", section="session")["org_id"]
        self.url = self.conf.read_config("config_file", section="session")["url"]
        self.k_session = self.conf.read_config("config_file", section="session")["ksession"]
        
    def get_customers(self, page_number) -> bool:
        is_success = True
        try:
            get_logger().info(
                "Start to fetch customers from Sprkmeter"
            )
            
            cookies = {
                "ksession": self.k_session,
            }
            headers = {
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json, text/plain, */*",
                "Referer": f"{self.url}/portfolio/{self.org_id}/",
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
                    f"Invalid customer key. Rceived key is: {list(data.keys())}"
                )

        except Exception as e:
            get_logger().error(f"Error occurred while fetching customers: {e}")
            is_success = False

        return is_success