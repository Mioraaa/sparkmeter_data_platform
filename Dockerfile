FROM apache/airflow:3.4.0

ADD requirements.txt .

RUN pip install -r requirements.txt


CMD ["dbt", "--version"]