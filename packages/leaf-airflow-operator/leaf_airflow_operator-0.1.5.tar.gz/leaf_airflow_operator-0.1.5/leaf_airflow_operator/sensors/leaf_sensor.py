from airflow.sensors.base import BaseSensorOperator
from leaf_airflow_operator.hooks.leaf_hook import LeafHook

class LeafBatchStatusSensor(BaseSensorOperator):

    def __init__(
        self,
        upload_task_id: str,
        expected_status: str = "PROCESSED",
        headers: dict = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.upload_task_id = upload_task_id
        self.expected_status = expected_status
        self.headers = headers or {}

    def poke(self, context):

        ti = context['ti']
        token = ti.xcom_pull(key='leaf_token')
        headers = {'Authorization': f'Bearer {token}'}

        upload_result = ti.xcom_pull(task_ids=self.upload_task_id)
        batch_id = upload_result.get("id")

        hook = LeafHook()
        if not batch_id:
            raise ValueError("Batch ID not found in XCom from task: " + self.upload_task_id)

        self.log.info(f"Checking status for batch ID: {batch_id}")
        status_response = hook.run(
            endpoint=f"/services/operations/api/batch/{batch_id}",
            method="GET",
            headers=headers
        )

        status = status_response.get("status")
        self.log.info(f"Batch {batch_id} current status: {status}")

        if status == self.expected_status:
            return True
        if status == "FAILED":
            raise ValueError(f"Batch {batch_id} failed: {status_response}")
        return False
