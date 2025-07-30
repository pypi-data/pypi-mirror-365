import unittest
from unittest.mock import patch, mock_open, MagicMock
from leaf_airflow_operator.hooks.leaf_hook import LeafHook

class TestLeafHook(unittest.TestCase):

    @patch("requests.request")
    def test_run_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response

        hook = LeafHook()
        result = hook.run("/test", "GET", headers={})
        self.assertEqual(result, {"result": "ok"})
        mock_request.assert_called_once()

    @patch("requests.post")
    @patch("builtins.open", new_callable=mock_open, read_data=b"file content")
    def test_upload_batch_file(self, mock_file, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "upload123"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        hook = LeafHook()
        result = hook.upload_batch_file("dummy.zip", "user123", "Other", headers={})
        self.assertEqual(result, {"id": "upload123"})
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_create_satellite_field_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok"}
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"status": "ok"}'
        mock_post.return_value = mock_response

        hook = LeafHook()
        result = hook.create_satellite_field(
            "ext-id",
            {"type": "Polygon", "coordinates": []},
            ["Sentinel"],
            headers={},
            start_date="2024-01-01"
        )
        self.assertEqual(result, {"status": "ok"})

    def test_create_satellite_field_invalid_args(self):
        hook = LeafHook()
        with self.assertRaises(ValueError):
            hook.create_satellite_field(
                "ext-id",
                {"type": "Polygon", "coordinates": []},
                ["Sentinel"],
                headers={},
                start_date="2024-01-01",
                days_before=30
            )

    @patch("requests.post")
    def test_create_field_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "field123"}
        mock_response.raise_for_status.return_value = None
        mock_response.content = b'{"id": "field123"}'
        mock_post.return_value = mock_response

        hook = LeafHook()
        result = hook.create_field(
            "Field A",
            {"type": "Polygon", "coordinates": []},
            "user123",
            headers={}
        )
        self.assertEqual(result, {"id": "field123"})


if __name__ == '__main__':
    unittest.main()
