# Leaf Airflow Operator

This project provides custom Apache Airflow operators, hooks, and sensors to integrate Leaf's API into your data pipelines. It supports tasks like authentication, field creation, satellite monitoring setup, file uploads, and batch status monitoring.

Learn more about Leaf API here: https://learn.withleaf.io/docs/

This is a side project developed to streamline integration between Leaf's platform and ETL workflows orchestrated with Airflow.

## Installation

Install from PyPI:

```bash
pip install leaf-airflow-operator
```

## Example DAG

```python
from airflow import DAG
from airflow.operators.dummy import DummyOperator
from leaf_airflow_operator.operators.leaf_operator import (
    LeafAuthenticateOperator,
    LeafCreateFieldOperator,
    LeafCreateSatelliteFieldOperator,
    LeafBatchUploadOperator
)
from leaf_airflow_operator.sensors.leaf_sensor import LeafBatchStatusSensor
from datetime import datetime, timedelta

with DAG(
    dag_id="leaf_full_workflow",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=5)},
) as dag:

    auth = LeafAuthenticateOperator(
        task_id="auth_leaf",
        username="{{ var.value.LEAF_USERNAME }}",
        password="{{ var.value.LEAF_PASSWORD }}"
    )

    prepare = DummyOperator(task_id="prepare_tasks")

    create_field = LeafCreateFieldOperator(
        task_id="create_field",
        name="Field 001",
        geometry=YOUR_POLYGON,
        leaf_user_id="{{ var.value.LEAF_USER_ID }}"
    )

    create_sat = LeafCreateSatelliteFieldOperator(
        task_id="create_satellite",
        external_id="sat-001",
        geometry=YOUR_POLYGON,
        providers=["ProviderA"],
        days_before=7
    )

    upload = LeafBatchUploadOperator(
        task_id="upload_batch",
        file_path="/tmp/data.zip",
        leaf_user_id="{{ var.value.LEAF_USER_ID }}"
    )

    wait = LeafBatchStatusSensor(
        task_id="wait_processed",
        upload_task_id="upload_batch",
        expected_status="PROCESSED"
    )

    auth >> prepare
    prepare >> [create_field, create_sat, upload] >> wait
```

## Features
- LeafAuthenticateOperator: Authenticates against Leaf API and stores the token via XCom.
- LeafCreateFieldOperator: Creates a new field boundary.
- LeafCreateSatelliteFieldOperator: Creates a satellite-monitored field.
- LeafBatchUploadOperator: Uploads batch operation files to Leaf.
- LeafBatchStatusSensor: Polls the status of a batch upload until completion.

## How to test it locally

### Install Aiflow locally

python -m venv airflow-venv
source airflow-venv/bin/activate

pip install "apache-airflow[celery,postgres,redis]==2.7.3" --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.7.3/constraints-3.9.txt"

### Configure Airflow

export AIRFLOW_HOME=~/airflow
airflow db init

airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin

### Install the example DAG

export AIRFLOW__CORE__DAGS_FOLDER=<PATH TO YOUR DAGS FOLDER>

### Start Airflow

pkill -f airflow

airflow webserver --port 8080 &
airflow scheduler &

### List the DAGs
airflow dags list


# LICENSE (MIT)
MIT License
