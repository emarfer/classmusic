import os

from src.config.config import Config

class TestConfig:    
    def test_read_credentials(self, tmp_path, monkeypatch):
        fake_env_file = tmp_path / ".env"
        fake_env_file.write_text("FAKE_LASTFMKEY=fake_key")
        monkeypatch.delenv("FAKE_LASTFMKEY", raising=False)
        monkeypatch.chdir(tmp_path)

        Config().read_credentials(dotenv_path=fake_env_file)
        
        assert os.environ["FAKE_LASTFMKEY"] == "fake_key"