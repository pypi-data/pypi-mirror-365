import requests

class LeafHook:
    def __init__(self, base_url="https://api.withleaf.io"):
        self.base_url = base_url

    def run(self, endpoint, method, headers, data=None):
        url = f"{self.base_url}{endpoint}"
        resp = requests.request(method=method, url=url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()

    def upload_batch_file(self, file_path, leaf_user_id, provider, headers):
        url = f"{self.base_url}/services/operations/api/batch"
        params = {
            "leafUserId": leaf_user_id,
            "provider": provider
        }
        with open(file_path, 'rb') as f:
            files = {'file': f}
            resp = requests.post(url, headers=headers, files=files, params=params)
            resp.raise_for_status()
            return resp.json()
        
    def create_satellite_field(self, external_id, geometry, providers, headers, start_date=None, days_before=None):
        url = f"{self.base_url}/services/satellite/api/fields"

        payload = {
            "externalId": external_id,
            "geometry": geometry,
            "providers": providers
        }

        if start_date and days_before:
            raise ValueError("Use either 'start_date' or 'days_before', not both.")
        if start_date:
            payload["startDate"] = start_date
        elif days_before:
            payload["daysBefore"] = days_before

        response = requests.post(url, json=payload, headers=headers)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                error_json = response.json()
            except Exception:
                error_json = response.text
            raise Exception(f"HTTPError: {e}, Response: {error_json}")

        if not response.content:
            return {}

        return response.json()
    
    def create_field(self, name, geometry, leaf_user_id, headers):
        url = f"{self.base_url}/services/fields/api/users/{leaf_user_id}/fields"

        payload = {
            "name": name,
            "geometry": geometry
        }

        response = requests.post(url, json=payload, headers=headers)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            try:
                error_json = response.json()
            except Exception:
                error_json = response.text
            raise Exception(f"HTTPError: {e}, Response: {error_json}")

        if not response.content:
            return {}

        return response.json()