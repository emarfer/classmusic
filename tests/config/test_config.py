from src.config.config import Config

class TestConfig:
    
    def test_read_credentials(self, tmp_path):
        fake_env_file = tmp_path / ".env"
        fake_env_file.write_text("FAKE_LASTFMKEY=fake_key")
        
        credential =  Config(fake_env_file).get_credentials("FAKE_LASTFMKEY")
        
        assert credential == "fake_key"