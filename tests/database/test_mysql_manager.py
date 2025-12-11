from unittest.mock import MagicMock, patch

from src.config.config import Config
from src.database.mysql_manager import MysqlManager


class TestMysqlManager:
    def setup_method(self, method):
        mock_config = MagicMock(spec=Config)

        def get_credentials_side_effect(key):
            credentials = {
                "MYSQL_HOST": "fake_host",
                "MYSQL_PORT": "fake_port",
                "MYSQL_USER": "fake_user",
                "MYSQL_PASSWORD": "fake_password",
                "MYSQL_DATABASE": "fake_database",
            }
            return credentials[key]

        mock_config.get_credentials.side_effect = get_credentials_side_effect
        self.mysql_manager = MysqlManager(mock_config)

    def test_mysql_manager_gets_mysql_password(self):
        assert self.mysql_manager.PASSWORD == "fake_password"

    def test_mysql_manager_gets_credentials(self):
        assert self.mysql_manager.HOST == "fake_host"
        assert self.mysql_manager.PORT == "fake_port"
        assert self.mysql_manager.USER == "fake_user"
        assert self.mysql_manager.PASSWORD == "fake_password"
        assert self.mysql_manager.DATABASE == "fake_database"

    def test_create_mysql_uri_creates_valid_uri(self):
        uri_expected = (
            "mysql+pymysql://fake_user:fake_password@fake_host:fake_port/fake_database"
        )

        uri = self.mysql_manager._create_mysql_uri()

        assert uri == uri_expected

    @patch("src.database.mysql_manager.sqlalchemy")
    @patch("src.database.mysql_manager.MysqlManager._create_mysql_uri")
    def test_create_mysql_engine_calls_create_myql_uri(
        self, mock_create_mysql_uri, mock_sqlalchemy
    ):
        mock_create_mysql_uri.return_value = "fake_uri"

        self.mysql_manager.create_mysql_engine()

        mock_create_mysql_uri.assert_called_once()

    @patch("src.database.mysql_manager.MysqlManager._create_mysql_uri")
    @patch("src.database.mysql_manager.sqlalchemy.create_engine")
    def test_create_mysql_engine_calls_sqlalchemy_create_engine_with_uri(
        self, mock_sqlalchemy_create_engine, mock_create_mysql_uri
    ):
        mock_create_mysql_uri.return_value = "fake_uri"

        self.mysql_manager.create_mysql_engine()

        mock_sqlalchemy_create_engine.assert_called_once_with("fake_uri")

    @patch("src.database.mysql_manager.MysqlManager._create_mysql_uri")
    @patch("src.database.mysql_manager.sqlalchemy")
    def test_create_mysql_engine_creates_sqlalchemy_engine(
        self, mock_sqlalchemy, mock_create_mysql_uri
    ):
        mock_create_mysql_uri.return_value = "fake_uri"
        mock_engine = MagicMock()
        mock_sqlalchemy.create_engine.return_value = mock_engine

        engine = self.mysql_manager.create_mysql_engine()

        assert engine == mock_engine
