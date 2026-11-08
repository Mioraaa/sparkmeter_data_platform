FROM apache/airflow:3.4.0

ADD requirements.txt .

RUN pip install apache-airflow==${AIRFLOW_VERSION} -r requirements.txt


COPY /dags/sparkmeter-dbt/profiles.yml /dags/sparkmeter-dbt/profiles.yml

CMD ["dbt", "--version"]