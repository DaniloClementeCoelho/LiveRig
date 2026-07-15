from enum import Enum, auto


class PlaybackEventType(Enum):
    PLAY = auto()
    PAUSE = auto()
    SEEK = auto()
    SONG_CHANGED = auto()
    MARKER = auto()
    REGION = auto()