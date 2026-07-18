from pathlib import Path

from lyrics import LyricItem, LyricsTimeline


def load_lyrics(project_path: Path) -> LyricsTimeline:
    with project_path.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    items = []

    in_lyrics = False
    in_item = False
    in_notes = False

    position = None
    length = None
    notes = []

    for line in lines:
        line = line.strip()

        # Encontrou a track
        if line == "NAME Lyrics":
            in_lyrics = True
            continue

        if not in_lyrics:
            continue

        # Novo ITEM
        if line.startswith("<ITEM"):
            in_item = True
            position = None
            length = None
            notes = []
            continue

        if not in_item:
            continue

        if line.startswith("POSITION "):
            position = float(line.split()[1])
            continue

        if line.startswith("LENGTH "):
            length = float(line.split()[1])
            continue

        if line.startswith("<NOTES"):
            in_notes = True
            continue

        if in_notes:

            if line == ">":
                in_notes = False
                continue

            notes.append(line.removeprefix("|"))
            continue

        # fim do ITEM
        if line == ">":

            if position is not None and length is not None:

                items.append(
                    LyricItem(
                        index=len(items),
                        start=position,
                        end=position + length,
                        text="\n".join(notes).strip(),
                    )
                )

            in_item = False

    return LyricsTimeline(items)
