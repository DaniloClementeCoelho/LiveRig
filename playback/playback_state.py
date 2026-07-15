from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from models import Song


@dataclass
class PlaybackState:
    """
    Estado global do show.

    Esta classe será a única fonte de verdade do estado de reprodução
    do LiveRig.

    Nesta primeira fase ela é apenas um objeto de dados.
    """

    current_song: Optional[Song] = None

    position: float = 0.0

    playing: bool = False

    current_region: Optional[str] = None

    current_marker: Optional[str] = None