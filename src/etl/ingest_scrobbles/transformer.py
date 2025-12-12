from models.scrobble import Scrobble


class TransformScrobble:
    def __init__(self):
        pass

    def _extract_scrobble_data(self, scrobble: dict) -> Scrobble:
        return Scrobble(
            **{
                "uts": int(scrobble["date"]["uts"]),
                "artist": scrobble["artist"]["name"],
                "artist_mbid": scrobble["artist"]["mbid"],
                "album": scrobble["album"]["#text"],
                "album_mbid": scrobble["album"]["mbid"],
                "title": scrobble["name"],
                "track_mbid": scrobble["mbid"],
            }
        )

    def transform_tracks_list(self, tracks_list) -> list[Scrobble]:
        transformed_tracks_list = []
        for element in tracks_list:
            transformed_element = self._extract_scrobble_data(element)
            transformed_tracks_list.append(transformed_element)
        return transformed_tracks_list
