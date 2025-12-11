from src.config.config import Config
import sqlalchemy


class MysqlManager:
    def __init__(self, config: Config):
        self.HOST = config.get_credentials("MYSQL_HOST")
        self.PORT = config.get_credentials("MYSQL_PORT")
        self.USER = config.get_credentials("MYSQL_USER")
        self.PASSWORD = config.get_credentials("MYSQL_PASSWORD")
        self.DATABASE = config.get_credentials("MYSQL_DATABASE")

    def _create_mysql_uri(self):
        return f"mysql+pymysql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DATABASE}"

    def create_mysql_engine(self):
        uri = self._create_mysql_uri()
        return sqlalchemy.create_engine(uri)
