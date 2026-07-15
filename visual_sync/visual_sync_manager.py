from __future__ import annotations

from playback import PlaybackState


class VisualSyncManager:
    """
    Coordenador do módulo Visual Sync.

    Nesta fase apenas instancia o PlaybackState.
    """

    def __init__(self) -> None:
        self.playback_state = PlaybackState()