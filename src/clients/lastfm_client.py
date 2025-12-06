from src.config.config import Config

class LastfmClient:
    def __init__(self, config: Config):
        self.LASTFM_KEY = config.get_credentials("LASTFM_KEY")
        self.LASTFM_SECRET = config.get_credentials("LASTFM_SECRET")
        self.uri = "http://ws.audioscrobbler.com/2.0/"