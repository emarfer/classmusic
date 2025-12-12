import pandas as pd

from database.mysql_manager import MysqlManager
from models.scrobble import Scrobble


class EnrichScrobble:
    def __init__(self, scrobbles_list: list[Scrobble], database_manager=MysqlManager):
        self.database_manager = database_manager
        self.scrobbles_list = scrobbles_list

    def _create_dataframe(self, scrobbles_list: list[Scrobble]) -> pd.DataFrame:
        scrobbles_dictionary_list = [
            scrobble.model_dump() for scrobble in scrobbles_list
        ]
        return pd.DataFrame(scrobbles_dictionary_list)

    def enrich_scrobble(self):
        scrobble_df = self._create_dataframe(self.scrobbles_list)
        scrobble_df["fechahora"] = pd.to_datetime(
            scrobble_df["uts"], unit="s"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")
        scrobble_df.loc[scrobble_df.album == "", "album"] = "[Desconocido]"
        return scrobble_df
