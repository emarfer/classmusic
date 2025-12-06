from dotenv import load_dotenv

class Config:
    def read_credentials(self, dotenv_path=None):
        load_dotenv(dotenv_path=dotenv_path)