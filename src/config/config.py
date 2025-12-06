from dotenv import dotenv_values

class Config:
    def __init__(self, dotenv_path):
        self.credentials = dotenv_values(dotenv_path)
        
    def get_credentials(self, key_name):
        return self.credentials[key_name]