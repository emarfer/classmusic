from pydantic import ValidationError
import pytest
from src.models.scrobble import Scrobble


class TestScrobble:
    @pytest.fixture
    def valid_scrobble(self):
        valid_scrobble = {
            "uts": 1234567890,
            "artist": "fake_artist",
            "artist_mbid": "fake_artist_mbid",
            "album": "fake_album",
            "album_mbid": "fake_album_mbid",
            "title": "fake_title",
            "track_mbid": "fake_album_mbid",
        }

        return valid_scrobble

    def test_model_scrobble(self, valid_scrobble):
        scrobble = Scrobble(**valid_scrobble)
        assert scrobble.model_dump() == valid_scrobble

    def test_should_fail_if_field_is_missing(self, valid_scrobble):
        for key in valid_scrobble.keys():
            invalid_scrobble = valid_scrobble.copy()
            invalid_scrobble.pop(key)
            with pytest.raises(ValidationError):
                Scrobble(**invalid_scrobble)

    def test_mbid_fields_can_be_empty_string(self, valid_scrobble):
        valid_mbids = valid_scrobble.copy()
        valid_mbids["artist_mbid"] = ""
        valid_mbids["album_mbid"] = ""
        valid_mbids["track_mbid"] = ""
        scrobble = Scrobble(**valid_mbids)
        assert scrobble.artist_mbid == ""
        assert scrobble.album_mbid == ""
        assert scrobble.track_mbid == ""

    @pytest.mark.parametrize("invalid_uts", ("", "uts"))
    def test_uts_is_integer(self, valid_scrobble, invalid_uts):
        invalid_scrobble = valid_scrobble.copy()
        invalid_scrobble["uts"] = invalid_uts
        with pytest.raises(ValidationError):
            Scrobble(**invalid_scrobble)

    def test_pydantic_cast_integer_as_string_into_integer(self, valid_scrobble):
        valid_scrobble_copy = valid_scrobble.copy()
        valid_scrobble_copy["uts"] = "1234567890"
        scrobble = Scrobble(**valid_scrobble_copy)
        assert scrobble.uts == 1234567890
