from unittest.mock import MagicMock, patch
from assertpy import assert_that
import pytest

from pandas.testing import assert_frame_equal
import pandas as pd

from models.scrobble import Scrobble
from src.etl.ingest_scrobbles.enricher import EnrichScrobble


class TestEnrichScrobble:

    def setup_method(self, method):
        database_manager = MagicMock()
        scrobbles_list = self.create_scrobbles_list()
        self.enricher = EnrichScrobble(scrobbles_list, database_manager)

    def test_create_dataframe_transform_scrobbles_list_in_pandas_df(self):
        scrobbles_list = self.create_scrobbles_list()
        expected = pd.DataFrame(
            [
                {
                    "uts": 1765549946,
                    "artist": "Extremoduro",
                    "artist_mbid": "",
                    "album": "Yo, Minoría Absoluta",
                    "album_mbid": "",
                    "title": "Standby",
                    "track_mbid": "2f04902e-2ffd-4fc2-b988-f9aaf36a029a",
                },
                {
                    "uts": 1765554377,
                    "artist": "Extremoduro",
                    "artist_mbid": "",
                    "album": "Deltoya",
                    "album_mbid": "38ae7156-5d88-43e7-a93c-58f824310634",
                    "title": "Papel Secante",
                    "track_mbid": "340b6ac9-51e8-4fbd-bd3e-0e888d93ad97",
                },
            ]
        )

        result = self.enricher._create_dataframe(scrobbles_list)

        assert_frame_equal(result, expected)

    def test_enrich_scrobbles_adds_fechahora_column(self):

        expected = pd.DataFrame(
            [
                {"uts": 1765549946, "fechahora": "2025-12-12 14:32:26"},
                {"uts": 1765554377, "fechahora": "2025-12-12 15:46:17"},
            ]
        )

        result = self.enricher.enrich_scrobble()

        assert_frame_equal(result[["uts", "fechahora"]], expected)

    def test_enrich_transform_empty_string_into_desconocido_in_album(self):
        database_manager = MagicMock()
        scrobble_list = [
            Scrobble(
                **{
                    "uts": 1765549946,
                    "artist": "Extremoduro",
                    "artist_mbid": "",
                    "album": "",
                    "album_mbid": "",
                    "title": "Canción de Extremoduro",
                    "track_mbid": "",
                }
            )
        ]
        expected = pd.DataFrame([{"uts": 1765549946, "album": "[Desconocido]"}])

        enricher = EnrichScrobble(scrobble_list, database_manager)
        result = enricher.enrich_scrobble()

        assert_frame_equal(result[["uts", "album"]], expected)

    def create_scrobbles_list(self):
        return [
            Scrobble(
                **{
                    "uts": 1765549946,
                    "artist": "Extremoduro",
                    "artist_mbid": "",
                    "album": "Yo, Minoría Absoluta",
                    "album_mbid": "",
                    "title": "Standby",
                    "track_mbid": "2f04902e-2ffd-4fc2-b988-f9aaf36a029a",
                }
            ),
            Scrobble(
                **{
                    "uts": 1765554377,
                    "artist": "Extremoduro",
                    "artist_mbid": "",
                    "album": "Deltoya",
                    "album_mbid": "38ae7156-5d88-43e7-a93c-58f824310634",
                    "title": "Papel Secante",
                    "track_mbid": "340b6ac9-51e8-4fbd-bd3e-0e888d93ad97",
                }
            ),
        ]
