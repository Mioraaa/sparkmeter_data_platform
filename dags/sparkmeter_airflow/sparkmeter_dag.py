

from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.models import variable

from tasks.customer import CustomerOperations
from utils.log_manager import setup_logging

default_args = {
    "owner": variable.Variable.get("sparkmeter_owner"),
    "start_date": datetime.now()
}

@task(task_id="save_customers")
def save_customers():
    customers = CustomerOperations().save_customers()
    if customers:
        setup_logging().info(
            "All customers saved successfully"
        )
    else:
        setup_logging().error("Failed when saving customers")


with DAG(
        dag_id='sparkmeter',
         default_args=default_args,
         schedule="@daily",
         catchup=False,
         ) as dag:
    sparkmeter_save_customers = save_customers()

# run the orders tasks
sparkmeter_save_customers