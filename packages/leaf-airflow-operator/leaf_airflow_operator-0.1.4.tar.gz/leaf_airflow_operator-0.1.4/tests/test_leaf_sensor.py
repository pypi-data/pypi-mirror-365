import pytest
from unittest.mock import patch, MagicMock
from leaf_airflow_operator.sensors.leaf_sensor import LeafBatchStatusSensor

@pytest.fixture
def context():
    ti_mock = MagicMock()
    return {"ti": ti_mock}

@patch("leaf_airflow_operator.sensors.leaf_sensor.LeafHook")
def test_batch_sensor_status_processed(mock_hook_class, context):
    context["ti"].xcom_pull.side_effect = [
        "fake-token",  # token from xcom_pull(key='leaf_token')
        {"id": "batch123"}  # result from upload task
    ]
    mock_hook = mock_hook_class.return_value
    mock_hook.run.return_value = {"status": "PROCESSED"}

    sensor = LeafBatchStatusSensor(
        task_id="wait_batch",
        upload_task_id="upload_task"
    )
    assert sensor.poke(context) is True

@patch("leaf_airflow_operator.sensors.leaf_sensor.LeafHook")
def test_batch_sensor_status_not_ready(mock_hook_class, context):
    context["ti"].xcom_pull.side_effect = [
        "fake-token",
        {"id": "batch123"}
    ]
    mock_hook = mock_hook_class.return_value
    mock_hook.run.return_value = {"status": "UPLOADING"}

    sensor = LeafBatchStatusSensor(
        task_id="wait_batch",
        upload_task_id="upload_task"
    )
    assert sensor.poke(context) is False

@patch("leaf_airflow_operator.sensors.leaf_sensor.LeafHook")
def test_batch_sensor_status_failed(mock_hook_class, context):
    context["ti"].xcom_pull.side_effect = [
        "fake-token",
        {"id": "batch123"}
    ]
    mock_hook = mock_hook_class.return_value
    mock_hook.run.return_value = {"status": "FAILED"}

    sensor = LeafBatchStatusSensor(
        task_id="wait_batch",
        upload_task_id="upload_task"
    )
    with pytest.raises(ValueError, match="failed"):
        sensor.poke(context)

@patch("leaf_airflow_operator.sensors.leaf_sensor.LeafHook")
def test_batch_sensor_missing_batch_id(mock_hook_class, context):
    context["ti"].xcom_pull.side_effect = [
        "fake-token",
        {}  # missing 'id'
    ]
    sensor = LeafBatchStatusSensor(
        task_id="wait_batch",
        upload_task_id="upload_task"
    )
    with pytest.raises(ValueError, match="Batch ID not found"):
        sensor.poke(context)
