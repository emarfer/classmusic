from src.config.config import Config
import requests

LAST_FM_URI = "http://ws.audioscrobbler.com/2.0/"

class LastfmClient:
    def __init__(self, config: Config):
        self.LASTFM_KEY = config.get_credentials("LASTFM_KEY")
        self.uri = LAST_FM_URI
        self.params = {
            "user":"sinatxester",
            "api_key":self.LASTFM_KEY,
            "format":"json"
            }
        
    def _make_request(self, method:str, **kwargs):
        params = self.params.copy()
        params.update({"method":method})
        params.update(kwargs)
        return requests.get(self.uri, params)