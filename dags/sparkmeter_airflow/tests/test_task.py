

import sys
import os

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