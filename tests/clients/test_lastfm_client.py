from unittest.mock import MagicMock, patch
from assertpy import assert_that
import pytest

import json

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

        mock_make_request.assert_any_call(method)

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_returns_list_of_tracks_when_totalpages_is_one(
        self, mock_make_request
    ):
        mock_make_request.return_value = self.read_json_test(
            "tests/clients/test_rt_1page.json"
        )
        expected = self.build_list_1_page()

        result = self.client.get_recenttracks()

        assert result == expected

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_returnslist_of_tracks_when_totalpages_is_more_than_one(
        self, mock_make_request
    ):
        mock_make_request.side_effect = [
            self.read_json_test(
                "tests/clients/test_rt_2_pages_1.json"
            ),  # first_call gets total_pages > 1
            self.read_json_test(
                "tests/clients/test_rt_2_pages_1.json"
            ),  # first_call page=1
            self.read_json_test(
                "tests/clients/test_rt_2_pages_2.json"
            ),  # second_call page=2
        ]
        expected = self.build_list_2_pages()

        result = self.client.get_recenttracks()

        assert result == expected

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_total_pages_attribute_is_zero_raises_error(self, mock_make_request):
        mock_make_request.return_value = {
            "recenttracks": {
                "@attr": {
                    "user": "indiferent_user",
                    "totalPages": "0",
                    "page": "1",
                    "perPage": "50",
                    "total": "0",
                }
            }
        }

        with pytest.raises(ValueError, match="No new scrobbles to add"):
            self.client.get_recenttracks()

    @pytest.mark.parametrize(
        "first_element, expected",
        [({"fake_attribue": "fake_value"}, False), ({"@attr": "attribute"}, True)],
    )
    def test_check_first_element_list(self, first_element, expected):
        first_element = first_element

        result = self.client._check_first_element_tracks_list(first_element)

        assert result == expected

    @patch("src.clients.lastfm_client.LastfmClient._check_first_element_tracks_list")
    def test_drops_first_element_if_attr_in_keys_calls_check_first_element_list(
        self, mock_check_first_element
    ):
        self.client._drop_first_element_if_attr_in_keys([{"key": "value"}])

        mock_check_first_element.assert_called_once()

    def test_drops_first_element_if_attr_in_keys(self):
        tracks_list = [{"@attr": "attribute"}, {"fake_attribue": "fake_value"}]
        expected = [{"fake_attribue": "fake_value"}]

        result = self.client._drop_first_element_if_attr_in_keys(tracks_list)

        assert result == expected

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    @patch("src.clients.lastfm_client.LastfmClient._drop_first_element_if_attr_in_keys")
    def test_get_recenttracks_calls_drops_first_element_if_attr_in_keys_with_correct_values(
        self, mock_drop_first_element, mock_make_request
    ):
        mock_make_request.side_effect = [
            {
                "recenttracks": {
                    "@attr": {
                        "totalPages": "1",
                    }
                }
            },
            {"recenttracks": {"track": [{"track": "track_1"}, {"track": "track_2"}]}},
        ]
        self.client.get_recenttracks()

        mock_drop_first_element.assert_called_with(
            [{"track": "track_1"}, {"track": "track_2"}]
        )

    @patch("src.clients.lastfm_client.LastfmClient._make_request")
    def test_get_recenttracks_drops_first_element_if_in_list_when_it_has_attr_in_keys(
        self, mock_make_request
    ):
        mock_make_request.side_effect = [
            {
                "recenttracks": {
                    "@attr": {
                        "totalPages": "1",
                    }
                }
            },
            {"recenttracks": {"track": [{"@attr": "track_1"}, {"track": "track_2"}]}},
        ]
        expected = [{"track": "track_2"}]
        result = self.client.get_recenttracks()

        assert result == expected

    def read_json_test(self, path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data

    def build_list_1_page(self):
        return [
            {
                "artist": {
                    "mbid": "9bacf78f-9132-43da-8873-8a9eb49da0e9",
                    "#text": "Alejandro Sanz",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                ],
                "mbid": "be6644e6-2a6d-31a7-b458-4e66ec274489",
                "album": {"mbid": "55b3afe2-c079-42e4-84d5-4a7e5bd4d8bb", "#text": "3"},
                "name": "Por Bandera",
                "url": "https://www.last.fm/music/Alejandro+Sanz/_/Por+Bandera",
                "date": {"uts": "1763133775", "#text": "14 Nov 2025, 15:22"},
            },
            {
                "artist": {
                    "mbid": "35aaf2e1-50fa-4bb6-9e12-1b8bbdeca266",
                    "#text": "Burning Witches",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                ],
                "mbid": "",
                "album": {
                    "mbid": "c09c36f3-11e5-4914-b21a-bd31e0ddb6c1",
                    "#text": "Inquisition",
                },
                "name": "Malus Maga",
                "url": "https://www.last.fm/music/Burning+Witches/_/Malus+Maga",
                "date": {"uts": "1762972384", "#text": "12 Nov 2025, 18:33"},
            },
        ]

    def build_list_2_pages(self):
        return [
            {
                "artist": {
                    "mbid": "9bacf78f-9132-43da-8873-8a9eb49da0e9",
                    "#text": "Alejandro Sanz",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/974c89a6b54444b1b0978cab3ddf283d.jpg",
                    },
                ],
                "mbid": "be6644e6-2a6d-31a7-b458-4e66ec274489",
                "album": {"mbid": "55b3afe2-c079-42e4-84d5-4a7e5bd4d8bb", "#text": "3"},
                "name": "Por Bandera",
                "url": "https://www.last.fm/music/Alejandro+Sanz/_/Por+Bandera",
                "date": {"uts": "1763133775", "#text": "14 Nov 2025, 15:22"},
            },
            {
                "artist": {
                    "mbid": "35aaf2e1-50fa-4bb6-9e12-1b8bbdeca266",
                    "#text": "Burning Witches",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/96986ec3d7419adb61cdc399a50a1262.jpg",
                    },
                ],
                "mbid": "",
                "album": {
                    "mbid": "c09c36f3-11e5-4914-b21a-bd31e0ddb6c1",
                    "#text": "Inquisition",
                },
                "name": "Malus Maga",
                "url": "https://www.last.fm/music/Burning+Witches/_/Malus+Maga",
                "date": {"uts": "1762972384", "#text": "12 Nov 2025, 18:33"},
            },
            {
                "artist": {
                    "mbid": "0b11f581-1a2e-4a4a-9b17-fafdeba59527",
                    "#text": "Envidia Kotxina",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/008e7918803949b49d24213b60d653e7.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/008e7918803949b49d24213b60d653e7.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/008e7918803949b49d24213b60d653e7.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/008e7918803949b49d24213b60d653e7.jpg",
                    },
                ],
                "mbid": "b5a35580-ea66-35aa-a7ee-2e3f0bd4814f",
                "album": {
                    "mbid": "0cb41855-3830-4c7a-a66b-e1a5206cbd4b",
                    "#text": "Kampos de Exterminio",
                },
                "name": "Rekuerdos",
                "url": "https://www.last.fm/music/Envidia+Kotxina/_/Rekuerdos",
                "date": {"uts": "1762949869", "#text": "12 Nov 2025, 12:17"},
            },
            {
                "artist": {
                    "mbid": "31745282-b1ea-4d62-939f-226b14d68e7c",
                    "#text": "In Flames",
                },
                "streamable": "0",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/89a116e18bde714ed5f7ebbb0f06a65a.jpg",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/89a116e18bde714ed5f7ebbb0f06a65a.jpg",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/89a116e18bde714ed5f7ebbb0f06a65a.jpg",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/89a116e18bde714ed5f7ebbb0f06a65a.jpg",
                    },
                ],
                "mbid": "01c3a06d-b9ad-3108-8082-0b2079c569f5",
                "album": {
                    "mbid": "15e79f7f-ae84-31fd-822a-aed9ad6a23ed",
                    "#text": "Colony",
                },
                "name": "Ordinary Story",
                "url": "https://www.last.fm/music/In+Flames/_/Ordinary+Story",
                "date": {"uts": "1762949222", "#text": "12 Nov 2025, 12:07"},
            },
        ]
