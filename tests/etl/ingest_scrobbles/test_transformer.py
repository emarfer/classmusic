from etl.ingest_scrobbles.transformer import TransformScrobble
from models.scrobble import Scrobble
import pytest


class TestTransformScrobble:
    def test_extract_scrobble_data_extracts_valid_output(
        self, raw_scrobble, expected_raw_output
    ):
        result = TransformScrobble()._extract_scrobble_data(raw_scrobble)

        assert result == Scrobble(**expected_raw_output)

    def test_transform_scrobble_works_for_one_element_list(
        self, raw_scrobble, expected_raw_output
    ):
        one_element_tracks_list = [raw_scrobble]
        expected_output = [Scrobble(**expected_raw_output)]

        result = TransformScrobble().transform_tracks_list(one_element_tracks_list)

        assert result == expected_output

    def test_transform_scrobble_works_for_tracks_list_with_more_than_one_element(
        self, expected_raw_output, tracks_list_len_two
    ):
        raw_element_two = {
            "uts": 1765554377,
            "artist": "Extremoduro",
            "artist_mbid": "",
            "album": "Deltoya",
            "album_mbid": "38ae7156-5d88-43e7-a93c-58f824310634",
            "title": "Papel Secante",
            "track_mbid": "340b6ac9-51e8-4fbd-bd3e-0e888d93ad97",
        }
        expected_output = [Scrobble(**expected_raw_output), Scrobble(**raw_element_two)]

        result = TransformScrobble().transform_tracks_list(tracks_list_len_two)

        assert result == expected_output

    @pytest.fixture
    def raw_scrobble(self):
        return {
            "artist": {
                "url": "https://www.last.fm/music/Extremoduro",
                "name": "Extremoduro",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                ],
                "mbid": "",
            },
            "date": {"uts": "1765549946", "#text": "12 Dec 2025, 14:32"},
            "mbid": "2f04902e-2ffd-4fc2-b988-f9aaf36a029a",
            "name": "Standby",
            "image": [
                {
                    "size": "small",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/34s/cd1fb783201746ea4829151308f0afbd.png",
                },
                {
                    "size": "medium",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/64s/cd1fb783201746ea4829151308f0afbd.png",
                },
                {
                    "size": "large",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/174s/cd1fb783201746ea4829151308f0afbd.png",
                },
                {
                    "size": "extralarge",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/cd1fb783201746ea4829151308f0afbd.png",
                },
            ],
            "url": "https://www.last.fm/music/Extremoduro/_/Standby",
            "streamable": "0",
            "album": {"mbid": "", "#text": "Yo, Minoría Absoluta"},
            "loved": "1",
        }

    @pytest.fixture
    def expected_raw_output(self):
        return {
            "uts": 1765549946,
            "artist": "Extremoduro",
            "artist_mbid": "",
            "album": "Yo, Minoría Absoluta",
            "album_mbid": "",
            "title": "Standby",
            "track_mbid": "2f04902e-2ffd-4fc2-b988-f9aaf36a029a",
        }

    @pytest.fixture
    def tracks_list_len_two(self, raw_scrobble):
        another_raw_scrobble = {
            "artist": {
                "url": "https://www.last.fm/music/Extremoduro",
                "name": "Extremoduro",
                "image": [
                    {
                        "size": "small",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/34s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "medium",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/64s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "large",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/174s/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                    {
                        "size": "extralarge",
                        "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/2a96cbd8b46e442fc41c2b86b821562f.png",
                    },
                ],
                "mbid": "",
            },
            "date": {"uts": "1765554377", "#text": "12 Dec 2025, 15:46"},
            "mbid": "340b6ac9-51e8-4fbd-bd3e-0e888d93ad97",
            "name": "Papel Secante",
            "image": [
                {
                    "size": "small",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/34s/8db819a30686f664d0b1a9a9d9c61376.jpg",
                },
                {
                    "size": "medium",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/64s/8db819a30686f664d0b1a9a9d9c61376.jpg",
                },
                {
                    "size": "large",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/174s/8db819a30686f664d0b1a9a9d9c61376.jpg",
                },
                {
                    "size": "extralarge",
                    "#text": "https://lastfm.freetls.fastly.net/i/u/300x300/8db819a30686f664d0b1a9a9d9c61376.jpg",
                },
            ],
            "url": "https://www.last.fm/music/Extremoduro/_/Papel+Secante",
            "streamable": "0",
            "album": {
                "mbid": "38ae7156-5d88-43e7-a93c-58f824310634",
                "#text": "Deltoya",
            },
            "loved": "1",
        }
        return [raw_scrobble, another_raw_scrobble]
