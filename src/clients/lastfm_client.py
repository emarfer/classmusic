from traitlets import Bool
from src.config.config import Config
import requests

LAST_FM_URI = "http://ws.audioscrobbler.com/2.0/"


class LastfmClient:
    def __init__(self, config: Config):
        self.LASTFM_KEY = config.get_credentials("LASTFM_KEY")
        self.uri = LAST_FM_URI
        self.params = {
            "user": "sinatxester",
            "api_key": self.LASTFM_KEY,
            "format": "json",
            "extended": "1",
        }

    def run(self):
        lista = self.get_recenttracks()
        print(lista)

    def _make_request(self, method: str, **kwargs):
        params = self.params.copy()
        params.update({"method": method})
        params.update(kwargs)

        response = requests.get(self.uri, params)

        if response.status_code == 200:
            return response.json()
        else:
            raise ValueError(
                f"status_code: {response.status_code}, message: {response.json()["message"]}"
            )

    def get_recenttracks(self, limit=200, from_uts=None, to_uts=None):
        total_pages_attribute = self._make_request(
            "user.getrecenttracks", limit=limit, **{"from": from_uts, "to": to_uts}
        )["recenttracks"]["@attr"]["totalPages"]
        if total_pages_attribute == "0":
            raise ValueError("No new scrobbles to add")
        else:
            total_pages_list = range(1, int(total_pages_attribute) + 1)
            tracks_list = []
            for i in total_pages_list:
                tracks_list_request = self._make_request(
                    "user.getrecenttracks",
                    page=i,
                    limit=limit,
                    **{"from": from_uts, "to": to_uts},
                )["recenttracks"]["track"]
                tracks_list_request = self._drop_first_element_if_attr_in_keys(
                    tracks_list_request
                )
                tracks_list = tracks_list + tracks_list_request
            return tracks_list

    def _check_first_element_tracks_list(self, first_element: dict) -> Bool:
        if "@attr" in first_element.keys():
            return True
        return False

    def _drop_first_element_if_attr_in_keys(self, tracks_list: list):
        first_element = tracks_list[0]
        if self._check_first_element_tracks_list(first_element):
            return tracks_list[1:]
        return tracks_list
