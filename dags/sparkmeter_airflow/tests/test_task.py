

import sys
import os


sys.path.append(os.path.abspath(__file__ + "/../../../"))
from sparkmeter_airflow.tasks.customer import CustomerOperations
from sparkmeter_airflow.utils.config_manager import ConfigManager


class TestTask:
    def test_get_customers(self):
        customer_ops = CustomerOperations()
        page_number = 1
        result = customer_ops.get_customers(page_number)
        assert result is True