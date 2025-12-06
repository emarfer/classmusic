from unittest.mock import MagicMock
import pytest

from src.clients.lastfm_client import LastfmClient
from src.config.config import Config


class TestLastfmClient():
    @pytest.fixture
    def mock_config(self):
        mock_config = MagicMock(spec=Config)
        def side_effect_credentials(key_name):            
            keys_dict = {
                "LASTFM_KEY":"fake_lastfam_key",
                "LASTFM_SECRET":"fake_lastfm_secret"}
            return keys_dict[key_name]
        mock_config.get_credentials.side_effect = side_effect_credentials
        return mock_config
    
    def test_lastfm_client_gets_credentials(self, mock_config):        
        client = LastfmClient(mock_config)
        
        assert client.LASTFM_KEY == "fake_lastfam_key"
        assert client.LASTFM_SECRET == "fake_lastfm_secret"
        
    def test_lastfm_client_has_uri(self, mock_config):
        client = LastfmClient(mock_config)
        
        assert client.uri == "http://ws.audioscrobbler.com/2.0/"

        