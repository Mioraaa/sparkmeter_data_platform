import sys
import os
import json
import zipfile
from unittest.mock import MagicMock

import pytest

sys.path.append(os.path.abspath(__file__ + "/../../../"))

from sparkmeter_airflow.tasks.customer import CustomerOperations
from sparkmeter_airflow.tasks.consumption import ConsumptionOperations



class TestCustomer:

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



    def test_get_customers(self, monkeypatch):

        customer_ops = CustomerOperations()

        expected_customers = [
            {
                "id": 1,
                "name": "Client 1",
                "site": "client 1 site"
            }
        ]

        class MockResponse:

            def json(self):
                return {
                    "customers": expected_customers
                }

        def mock_get(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(
            customer_ops.session,
            "get",
            mock_get
        )

        result = customer_ops.get_customers(1)

        assert result == expected_customers



    def test_save_customers(
        self,
        customers,
        tmp_path,
        monkeypatch
    ):

        customer_ops = CustomerOperations()

        customer_file = tmp_path / "all_customers.json"

        customer_ops.all_customers = str(customer_file)
        customer_ops.org_id = "ORG_123"

        responses = [
            customers,
            []
        ]

        def mock_get_customers(page_number):
            return responses[page_number - 1]

        monkeypatch.setattr(
            customer_ops,
            "get_customers",
            mock_get_customers
        )

        customer_ops.save_customers()

        assert customer_file.exists()

        with open(
            customer_file,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        assert data["organization_id"] == "ORG_123"
        assert data["total_customers"] == 3
        assert data["customers"] == customers


    def test_save_customers_duplicates(
        self,
        customers,
        tmp_path,
        monkeypatch
    ):

        customer_ops = CustomerOperations()

        customer_file = tmp_path / "all_customers.json"

        customer_ops.all_customers = str(customer_file)
        customer_ops.org_id = "ORG_123"

        responses = [
            customers,
            [customers[0], customers[1]],
            []
        ]

        def mock_get_customers(page_number):
            return responses[page_number - 1]

        monkeypatch.setattr(
            customer_ops,
            "get_customers",
            mock_get_customers
        )

        customer_ops.save_customers()

        with open(
            customer_file,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        assert data["total_customers"] == 3
        assert len(data["customers"]) == 3

        customer_ids = [
            customer["id"]
            for customer in data["customers"]
        ]

        assert len(customer_ids) == len(set(customer_ids))



    def test_save_customers_api_error(
        self,
        customers,
        tmp_path,
        monkeypatch
    ):

        customer_ops = CustomerOperations()

        customer_file = tmp_path / "all_customers.json"

        customer_ops.all_customers = str(customer_file)
        customer_ops.org_id = "ORG_123"

        def mock_get_customers(page_number):

            if page_number == 1:
                return customers

            raise Exception("API connection error")

        monkeypatch.setattr(
            customer_ops,
            "get_customers",
            mock_get_customers
        )

        # Act / Assert
        with pytest.raises(Exception, match="API connection error"):
            customer_ops.save_customers()

        assert customer_file.exists()

        with open(
            customer_file,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        assert data["total_customers"] == 3
        assert data["customers"] == customers


    @pytest.fixture
    def customer_operations(self, tmp_path, monkeypatch):

        customers_file = tmp_path / "all_customers.json"

        customer = CustomerOperations.__new__(CustomerOperations)
        customer.all_customers = str(customers_file)

        monkeypatch.setattr(
            "sparkmeter_airflow.tasks.customer.setup_logging",
            lambda: MagicMock()
        )

        return customer, customers_file

    def test_load_customer(self, customer_operations):
        customer, customers_file = customer_operations
        data = {
            "customers": [
                {
                    "name": "Customer A",
                    "meters": [
                        {"serial": "meter001"},
                        {"serial": "METER001"}
                    ]
                },
                {
                    "name": "Customer B",
                    "meters": [
                        {"serial": "meter002"}
                    ]
                }
            ]
        }

        customers_file.write_text(
            json.dumps(data),
            encoding="utf-8"
        )

        df = customer.load_customer()

        assert len(df) == 2
        assert df["serial"].tolist() == [
            "METER001",
            "METER002"
        ]


class TestConsumption:

    @pytest.fixture
    def zip_file_data(self):

        return {
            "zip_file1.zip": {
                "customers.csv": (
                    "id,name\n"
                    "1,Client 1\n"
                    "2,Client 2"
                )
            },

            "zip_file2.zip": {
                "consumptions.csv": (
                    "id,consumption\n"
                    "1,150\n"
                    "2,200"
                )
            },

            "zip_file3.zip": {
                "meters.csv": (
                    "id,meter\n"
                    "1,Meter 1"
                )
            }
        }


    def test_extract_all_zip_files(
        self,
        zip_file_data,
        tmp_path
    ):

        consumption_ops = ConsumptionOperations()

        received_dir = tmp_path / "consumptions"
        received_dir.mkdir(parents=True)

        consumption_ops.received_dir = str(received_dir)

        received_files = received_dir / "ReceivedFiles"
        received_files.mkdir()

        for zip_name, files in zip_file_data.items():

            zip_path = received_files / zip_name

            with zipfile.ZipFile(
                zip_path,
                "w"
            ) as zip_file:

                for filename, content in files.items():

                    zip_file.writestr(
                        filename,
                        content
                    )

        result = consumption_ops.extract_all_zip_files()

        assert result.exists()
        assert result.is_dir()

        for files in zip_file_data.values():

            for filename in files:

                extracted_file = result / filename

                assert extracted_file.exists()

        assert len(list(result.glob("*.csv"))) == 3


    def test_extract_all_zip_files_empty(self, tmp_path):

        # Arrange
        consumption_ops = ConsumptionOperations()

        received_dir = tmp_path / "consumptions"
        received_dir.mkdir(parents=True)

        consumption_ops.received_dir = str(received_dir)

        received_files = received_dir / "ReceivedFiles"
        received_files.mkdir()

        result = consumption_ops.extract_all_zip_files()

        assert result.exists()
        assert result.is_dir()
        assert list(result.iterdir()) == []


    def test_find_all_csv(self, tmp_path):

        consumption_ops = ConsumptionOperations()

        root = tmp_path / "extracted"
        root.mkdir()

        (root / "customers.csv").write_text(
            "id,name\n1,Client 1",
            encoding="utf-8"
        )

        (root / "consumptions.CSV").write_text(
            "id,consumption\n1,150",
            encoding="utf-8"
        )

        sub_dir = root / "nested"
        sub_dir.mkdir()

        (sub_dir / "meters.csv").write_text(
            "id,meter\n1,Meter 1",
            encoding="utf-8"
        )

        (root / "data.json").write_text(
            '{"id": 1}',
            encoding="utf-8"
        )

        result = consumption_ops.find_all_csv(root)

        assert len(result) == 3

        filenames = {
            file.name
            for file in result
        }

        assert filenames == {
            "customers.csv",
            "consumptions.CSV",
            "meters.csv"
        }

