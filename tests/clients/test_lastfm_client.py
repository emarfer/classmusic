from unittest.mock import MagicMock, patch
import pytest

from src.clients.lastfm_client import LastfmClient
from src.config.config import Config


class TestLastfmClient():    
    def setup_method(self, method):
        mock_config = MagicMock(spec=Config)
        mock_config.get_credentials.return_value = "fake_lastfam_key"
        self.client = LastfmClient(mock_config)        
    
    def test_lastfm_client_gets_credentials(self):                
        assert self.client.LASTFM_KEY == "fake_lastfam_key"
        
    def test_lastfm_client_has_uri(self):        
        assert self.client.uri == "http://ws.audioscrobbler.com/2.0/"
        
    
    @patch("src.clients.lastfm_client.requests.get")
    def test_make_requests_api_gets_called(self,mock_requests_get):            
        self.client._make_request("")
        
        mock_requests_get.assert_called_once()
    
    @patch("src.clients.lastfm_client.requests.get")
    def test_make_requests_api_gets_called_with_correct_params(self, mock_requests_get):
        expected_params = {
            "user":"sinatxester",
            "api_key":"fake_lastfam_key",
            "format":"json",            
            "method":"test_method",
            "limit":0}
        self.client._make_request("test_method", limit=0)
        
        mock_requests_get.assert_called_once_with(self.client.uri, expected_params)
        