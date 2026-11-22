

import sys
import os
import json

import pytest

sys.path.append(os.path.abspath(__file__ + "/../../../"))
from sparkmeter_airflow.tasks.customer import CustomerOperations
from sparkmeter_airflow.utils.config_manager import ConfigManager


class TestTask:
    def test_get_customers(self):
        customer_ops = CustomerOperations()
        page_number = 1
        result = customer_ops.get_customers(page_number)
        assert result is True

    @pytest.fixture
    def customers(self):
        return [
            {
                "id": 1,
                "name": "Client 1",
                "site": "client 1 site"
            },
            {
                "id": 2,
                "name": "Client 2",
                "site": "client 2 site"
            },
            {
                "id": 3,
                "name": "Client 3",
                "site": "client 3 site"
            }
        ]

    def test_save_customers(self, customers):
        customer_ops = CustomerOperations()
        customer_file = "/media/miora/DONNEES1/project/sparkmeter_data_pipeline/sparkmeter_data_platform/dags/sparkmeter_airflow/data/customers/all_customers.json"
        customer_ops.all_customers =  customers
        customer_ops.org_id = "ORG_123"

        customer_ops.save_customers(customers)

        with open(customer_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data[0] == customers[0]
        assert data[1] == customers[1]
