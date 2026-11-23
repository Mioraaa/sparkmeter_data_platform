

from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable

from sparkmeter_airflow.tasks.customer import CustomerOperations
from sparkmeter_airflow.utils.log_manager import setup_logging

default_args = {
    "owner": Variable.get("sparkmeter_owner"),
    "start_date": datetime.now()
}

@task(task_id="save_customers")
def save_customers():
    is_saved = True

    try:
        setup_logging().info(
            "Start to save all customers in the JSON file"
        )
        customers = CustomerOperations().save_customers()
        if customers:
            setup_logging().info(
                "All customers are saved in the JSON file"
            )

    except Exception as e:
        is_saved = False
        setup_logging().error(
            f"An error occurred while saving all customers {e}"
        )

    return is_saved

with DAG(
        dag_id='sparkmeter',
         default_args=default_args,
         schedule="@daily",
         catchup=False,
         ) as dag:
    sparkmeter_save_customers = save_customers()

# run tasks
sparkmeter_save_customers