from multiprocessing import Value
from unittest.mock import MagicMock, patch
from assertpy import assert_that
import pytest

from src.clients.lastfm_client import LastfmClient
from src.config.config import Config


class TestLastfmClient:
    def setup_method(self, method):
        mock_config = MagicMock(spec=Config)
        mock_config.get_credentials.return_value = "fake_lastfam_key"
        self.client = LastfmClient(mock_config)
        self.mock_response = MagicMock()
        self.mock_response.status_code = 200
        self.mock_response.json.return_value = {}

    def test_lastfm_client_gets_credentials(self):
        assert self.client.LASTFM_KEY == "fake_lastfam_key"

    def test_lastfm_client_has_uri(self):
        assert self.client.uri == "http://ws.audioscrobbler.com/2.0/"

    @patch("src.clients.lastfm_client.requests.get")
    def test_make_requests_api_gets_called(self, mock_requests_get):
        mock_requests_get.return_value = self.mock_response
        self.client._make_request("")

        mock_requests_get.assert_called_once()

    @patch("src.clients.lastfm_client.requests.get")
    def test_make_requests_api_gets_called_with_correct_params(self, mock_requests_get):
        mock_requests_get.return_value = self.mock_response
        expected_params = {
            "user": "sinatxester",
            "api_key": "fake_lastfam_key",
            "format": "json",
            "method": "test_method",
            "limit": 0,
        }
        self.client._make_request("test_method", limit=0)

        mock_requests_get.assert_called_once_with(self.client.uri, expected_params)

    # def test_make_request_builds_correct_url(self):
    #     # este test no tiene sentido porque no nos interesa saber como funciona request.get por dentro, solo como la usamos nosotros en producción
    #     # es decir, con qué argumentos la llamamos y qué respuesta nos y/o como se comporta _make_request en funcion de la respuesta de requests.get
    #     method = "fake_method"
    #     expected_url = "http://ws.audioscrobbler.com/2.0/?user=sinatxester&api_key=fake_lastfam_key&format=json&method=fake_method&limit=10"

    #     r = self.client._make_request(method, limit=10)

    #     assert r.url == expected_url

    @patch("src.clients.lastfm_client.requests.get")
    def tests_make_request_returns_json_if_status_code_is_200(self, mock_requests_get):
        mock_requests_get.return_value = self.mock_response

        result = self.client._make_request("")

        assert result == {}

    @pytest.mark.parametrize(
        "status_code, message",
        [(201, "message201"), (404, "message404 "), (501, "message501")],
    )
    @patch("src.clients.lastfm_client.requests.get")
    def tests_make_request_raises_error_if_status_code_is_not_200(
        self, mock_requests_get, status_code, message
    ):
        self.mock_response.status_code = status_code
        self.mock_response.json.return_value = {"message": message}
        mock_requests_get.return_value = self.mock_response
        expected_message = f"status_code: {status_code}, message: {message}"

        with pytest.raises(ValueError, match=expected_message):
            self.client._make_request("")

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_calls_make_request(self, mock_make_request):

        self.client.get_recenttracks()

        mock_make_request.assert_called_once()

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_should_failed_if_get_recenttracks_calls_make_request_with_invalid_method(
        self, mock_make_request
    ):
        method = "fake_method"

        self.client.get_recenttracks()

        with pytest.raises(AssertionError):
            mock_make_request.assert_called_once_with(method)

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_calls_make_request_with_valid_method(
        self, mock_make_request
    ):
        method = "user.getrecenttracks"

        self.client.get_recenttracks()

        mock_make_request.assert_called_once_with(method)

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_returns_value(self, mock_make_request):
        mock_make_request.return_value = {"key_name": "key_value"}

        result = self.client.get_recenttracks()

        assert result == mock_make_request.return_value
