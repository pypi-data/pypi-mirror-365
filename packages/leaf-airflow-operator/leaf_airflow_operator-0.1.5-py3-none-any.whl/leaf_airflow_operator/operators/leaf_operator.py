from airflow.models import BaseOperator
from leaf_airflow_operator.hooks.leaf_hook import LeafHook

import requests

class LeafAuthenticateOperator(BaseOperator):
    def __init__(self, username, password, base_url="https://api.withleaf.io", **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.password = password
        self.base_url = base_url

    def execute(self, context):
        url = f"{self.base_url}/api/authenticate"
        headers = {"Content-Type": "application/json"}
        data = {"username": self.username, "password": self.password}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        token_info = response.json()
        context['ti'].xcom_push(key='leaf_token', value=token_info['id_token'])

class LeafBatchUploadOperator(BaseOperator):
    def __init__(self, file_path, leaf_user_id, provider="Other", base_url="https://api.withleaf.io", **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.leaf_user_id = leaf_user_id
        self.provider = provider
        self.base_url = base_url 

    def execute(self, context):
        ti = context['ti']
        token = ti.xcom_pull(key='leaf_token')
        headers = {'Authorization': f'Bearer {token}'}
        hook = LeafHook(base_url=self.base_url)
        return hook.upload_batch_file(self.file_path, self.leaf_user_id, self.provider, headers)

class LeafCreateSatelliteFieldOperator(BaseOperator):
    def __init__(self, external_id, geometry, providers, start_date=None, days_before=None, base_url="https://api.withleaf.io", **kwargs):
        super().__init__(**kwargs)
        self.external_id = external_id
        self.geometry = geometry
        self.providers = providers
        self.start_date = start_date
        self.days_before = days_before
        self.base_url = base_url 

    def execute(self, context):
        ti = context['ti']
        token = ti.xcom_pull(key='leaf_token')
        headers = {'Authorization': f'Bearer {token}'}

        hook = LeafHook(base_url=self.base_url)
        result = hook.create_satellite_field(
            geometry=self.geometry,
            external_id=self.external_id,
            providers=self.providers,
            headers=headers,
            start_date=self.start_date,
            days_before=self.days_before
        )
        self.log.info(f"Created satellite field: {result}")
        return result

class LeafCreateFieldOperator(BaseOperator):
    def __init__(self, name, geometry, leaf_user_id, base_url="https://api.withleaf.io", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.geometry = geometry
        self.leaf_user_id = leaf_user_id
        self.base_url = base_url 

    def execute(self, context):
        ti = context['ti']
        token = ti.xcom_pull(key='leaf_token')
        headers = {'Authorization': f'Bearer {token}'}

        hook = LeafHook(base_url=self.base_url)
        result = hook.create_field(
            self.name, 
            self.geometry, 
            self.leaf_user_id,
            headers)
        self.log.info(f"Created field: {result}")
        return result