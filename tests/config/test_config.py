import pytest

from unittest.mock import MagicMock

from src.config.config import Config

class TestConfig:
    @pytest.fixture
    def mock_config(self):
        mock_config = MagicMock()
        mock_config.LASTFN_KEY = 'fake_key'
        return mock_config
    
    def test_read_credentials(self, mock_config):
        
        Config(mock_config).read_credentials()
        assert mock_config.LASTFM_KEY == "fake_key"