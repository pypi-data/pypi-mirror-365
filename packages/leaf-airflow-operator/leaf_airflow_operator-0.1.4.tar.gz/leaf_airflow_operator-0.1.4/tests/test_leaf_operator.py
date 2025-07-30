import pytest
from unittest.mock import patch, MagicMock
from leaf_airflow_operator.operators.leaf_operator import (
    LeafAuthenticateOperator,
    LeafBatchUploadOperator,
    LeafCreateSatelliteFieldOperator,
    LeafCreateFieldOperator
)

@pytest.fixture
def context():
    ti_mock = MagicMock()
    return {"ti": ti_mock}

@patch("requests.post")
def test_leaf_authenticate_operator(mock_post, context):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id_token": "fake-token"}
    mock_response.raise_for_status = MagicMock()
    mock_post.return_value = mock_response

    operator = LeafAuthenticateOperator(username="user", password="pass", task_id="auth")
    operator.execute(context)
    context["ti"].xcom_push.assert_called_once_with(key="leaf_token", value="fake-token")

@patch("leaf_airflow_operator.operators.leaf_operator.LeafHook")
def test_leaf_batch_upload_operator(mock_hook_class, context):
    context["ti"].xcom_pull.return_value = "fake-token"
    mock_hook = mock_hook_class.return_value
    mock_hook.upload_batch_file.return_value = {"status": "ok"}

    operator = LeafBatchUploadOperator(
        file_path="/tmp/file.zip", leaf_user_id="user123", task_id="upload"
    )
    result = operator.execute(context)
    assert result == {"status": "ok"}
    mock_hook.upload_batch_file.assert_called_once()

@patch("leaf_airflow_operator.operators.leaf_operator.LeafHook")
def test_leaf_create_satellite_field_operator(mock_hook_class, context):
    context["ti"].xcom_pull.return_value = "fake-token"
    mock_hook = mock_hook_class.return_value
    mock_hook.create_satellite_field.return_value = {"fieldId": "abc123"}

    operator = LeafCreateSatelliteFieldOperator(
        external_id="ext1",
        geometry={"type": "Polygon", "coordinates": []},
        providers=["sentinel"],
        task_id="create_sat"
    )
    result = operator.execute(context)
    assert result == {"fieldId": "abc123"}
    mock_hook.create_satellite_field.assert_called_once()

@patch("leaf_airflow_operator.operators.leaf_operator.LeafHook")
def test_leaf_create_field_operator(mock_hook_class, context):
    context["ti"].xcom_pull.return_value = "fake-token"
    mock_hook = mock_hook_class.return_value
    mock_hook.create_field.return_value = {"fieldId": "xyz123"}

    operator = LeafCreateFieldOperator(
        name="Field A",
        geometry={"type": "Polygon", "coordinates": []},
        leaf_user_id="user123",
        task_id="create_field"
    )
    result = operator.execute(context)
    assert result == {"fieldId": "xyz123"}
    mock_hook.create_field.assert_called_once()
