from pydantic import BaseModel


class Scrobble(BaseModel):

    uts: int
    artist: str
    artist_mbid: str
    album: str
    album_mbid: str
    title: str
    track_mbid: str
