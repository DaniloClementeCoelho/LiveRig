from __future__ import annotations

from pathlib import Path
import re

try:
    from .catalog import MusicCatalog
    from .models import RppItem, Song
except ImportError:
    from catalog import MusicCatalog
    from models import RppItem, Song


catalog = MusicCatalog()

TEMPO_RE = re.compile(r"^\s*TEMPO\s+([0-9.]+)", re.MULTILINE)
MARKER_RE = re.compile(r'^\s*MARKER\s+(\d+)\s+([0-9.]+)\s+"([^"]*)"(.*)$')
CURSOR_RE = re.compile(r"^\s*CURSOR\s+[-0-9.]+")
NAME_RE = re.compile(r'^\s*NAME\s+(?:"([^"]*)"|(.+))\s*$')
LYRICS_TRACK_INDEX = 2
LYRICS_TRACK_NAME = "Lyrics"
POSITION_RE = re.compile(r"^\s*POSITION\s+([0-9.]+)")
LENGTH_RE = re.compile(r"^\s*LENGTH\s+([0-9.]+)")
FILE_RE = re.compile(r'^\s*FILE\s+"?([^"\n]+)"?')


def parse_rpp(path: Path) -> Song:
    text = path.read_text(encoding="utf-8", errors="ignore")
    tracks = _parse_tracks(text)
    lyric_track = _find_track(tracks, ("lyrics", "letras", "letra"))
    audio_track = _find_audio_track(tracks, lyric_track)
    audio_items = audio_track["items"] if audio_track is not None else []
    all_items = [item for track in tracks for item in track["items"]]
    media_files = _media_files(all_items)

    start_position = min((item.position for item in audio_items), default=0.0)
    duration_end = max((item.end for item in all_items), default=start_position)
    duration = max(0, round(duration_end - start_position))
    bpm = _extract_bpm(text)
    source_name = _source_name(path, media_files)
    title = _extract_marker_title(text, start_position) or source_name
    metadata = catalog.get(source_name)
    warnings = _build_warnings(tracks, audio_track, lyric_track)

    return Song(
        title=metadata.get("title") or title,
        artist=metadata.get("artist") or "Unknown",
        duration=duration,
        bpm=bpm,
        source_file=path,
        start_position=start_position,
        lyrics=lyric_track["items"] if lyric_track is not None else [],
        media_files=media_files,
        warnings=warnings,
    )


def ensure_start_marker(path: Path, song: Song) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines(keepends=True)
    newline = _detect_newline(text)
    marker_line = _start_marker_line(song, newline)
    cursor_line = _cursor_line(song, newline)
    output: list[str] = []
    replaced = False
    cursor_replaced = False

    for line in lines:
        if CURSOR_RE.match(line.rstrip("\r\n")):
            if not cursor_replaced:
                output.append(cursor_line)
                cursor_replaced = True
            continue

        marker_match = MARKER_RE.match(line.rstrip("\r\n"))
        if marker_match and marker_match.group(1) == "1":
            if not replaced:
                output.append(marker_line)
                replaced = True
            continue
        output.append(line)

    if not replaced:
        insert_at = _marker_insert_index(output)
        output.insert(insert_at, marker_line)

    if not cursor_replaced:
        insert_at = _project_setting_insert_index(output)
        output.insert(insert_at, cursor_line)

    path.write_text("".join(output), encoding="utf-8")
    ensure_lyrics_track_name(path)


def ensure_lyrics_track_name(path: Path) -> None:
    """Garante que a terceira track do projeto se chame 'Lyrics' (exigido pelo LiveRig)."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines(keepends=True)
    newline = _detect_newline(text)
    indent = _name_line_indent(lines)
    output: list[str] = []
    track_index = -1
    track_depth = 0
    in_track = False
    name_set = False

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("<TRACK"):
            track_index += 1
            in_track = True
            track_depth = 1
            name_set = False
            output.append(line)
            continue

        if not in_track:
            output.append(line)
            continue

        if track_index == LYRICS_TRACK_INDEX and not name_set and NAME_RE.match(line.rstrip("\r\n")):
            output.append(f"{indent}NAME {LYRICS_TRACK_NAME}{newline}")
            name_set = True
            continue

        if stripped.startswith("<"):
            track_depth += 1
        elif stripped == ">":
            track_depth -= 1
            if track_depth == 0:
                if track_index == LYRICS_TRACK_INDEX and not name_set:
                    output.append(f"{indent}NAME {LYRICS_TRACK_NAME}{newline}")
                    name_set = True
                in_track = False

        output.append(line)

    path.write_text("".join(output), encoding="utf-8")


def start_marker_position(song: Song) -> str:
    return _format_float(song.start_position)


def export_lyrics_markdown(song: Song) -> str:
    if not song.lyrics:
        return ""

    blocks = []
    for item in song.lyrics:
        timestamp = _format_timestamp(item.position - song.start_position)
        text = item.notes.strip()
        if text:
            blocks.append(f"[{timestamp}] {text}")

    return "\n\n".join(blocks).strip() + ("\n" if blocks else "")


def _parse_tracks(text: str) -> list[dict[str, object]]:
    lines = text.splitlines()
    tracks: list[dict[str, object]] = []
    current_track: dict[str, object] | None = None
    track_depth = 0
    in_item = False
    item_depth = 0
    item_lines: list[str] = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("<TRACK"):
            current_track = {"name": "", "items": []}
            track_depth = 1
            continue

        if current_track is None:
            continue

        if in_item:
            item_lines.append(line)
            if stripped.startswith("<"):
                item_depth += 1
            elif stripped == ">":
                item_depth -= 1
                if item_depth == 0:
                    item = _parse_item(item_lines, str(current_track["name"]))
                    if item is not None:
                        current_track["items"].append(item)
                    in_item = False
                    item_lines = []
            continue

        if stripped.startswith("<ITEM"):
            in_item = True
            item_depth = 1
            item_lines = [line]
            continue

        name = _parse_name(line)
        if name is not None:
            current_track["name"] = name

        if stripped.startswith("<"):
            track_depth += 1
        elif stripped == ">":
            track_depth -= 1
            if track_depth == 0:
                tracks.append(current_track)
                current_track = None

    return tracks


def _source_name(path: Path, media_files: list[str]) -> str:
    if path.stem.casefold() in {"project", "projeto"} and media_files:
        return Path(media_files[0]).stem
    if path.stem.casefold() in {"project", "projeto"} and path.parent.name:
        return path.parent.name
    return path.stem


def _parse_item(lines: list[str], track_name: str) -> RppItem | None:
    position = None
    length = None
    notes: list[str] = []
    source = ""
    in_notes = False

    for line in lines:
        stripped = line.strip()

        position_match = POSITION_RE.match(stripped)
        if position_match:
            position = float(position_match.group(1))
            continue

        length_match = LENGTH_RE.match(stripped)
        if length_match:
            length = float(length_match.group(1))
            continue

        file_match = FILE_RE.match(stripped)
        if file_match:
            source = file_match.group(1)
            continue

        if stripped.startswith("<NOTES"):
            in_notes = True
            continue

        if in_notes:
            if stripped == ">":
                in_notes = False
                continue
            notes.append(stripped.removeprefix("|"))

    if position is None or length is None:
        return None

    return RppItem(
        track_name=track_name,
        position=position,
        length=length,
        notes="\n".join(notes).strip(),
        source=source,
    )


def _parse_name(line: str) -> str | None:
    match = NAME_RE.match(line)
    if not match:
        return None
    return (match.group(1) or match.group(2) or "").strip()


def _name_line_indent(lines: list[str]) -> str:
    for line in lines:
        if NAME_RE.match(line.rstrip("\r\n")):
            return line[: len(line) - len(line.lstrip("\r\n"))]
    return "    "


def _find_track(tracks: list[dict[str, object]], aliases: tuple[str, ...]) -> dict[str, object] | None:
    normalized_aliases = {alias.casefold() for alias in aliases}
    for track in tracks:
        name = str(track["name"]).strip().casefold()
        if name in normalized_aliases:
            return track
    return None


def _find_audio_track(
    tracks: list[dict[str, object]],
    lyric_track: dict[str, object] | None,
) -> dict[str, object] | None:
    for track in tracks:
        if track is lyric_track:
            continue
        items = track["items"]
        if any(_looks_like_audio(item) for item in items):
            return track
    for track in tracks:
        if track is not lyric_track and track["items"]:
            return track
    return None


def _looks_like_audio(item: RppItem) -> bool:
    return Path(item.source).suffix.casefold() in {".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif"}


def _media_files(items: list[RppItem]) -> list[str]:
    media = []
    seen = set()
    for item in items:
        if not item.source or not _looks_like_audio(item):
            continue
        key = item.source.casefold()
        if key in seen:
            continue
        seen.add(key)
        media.append(item.source)
    return media


def _extract_bpm(text: str) -> int:
    tempo_match = TEMPO_RE.search(text)
    return round(float(tempo_match.group(1))) if tempo_match else 120


def _extract_marker_title(text: str, start_position: float) -> str | None:
    fallback = None
    for line in text.splitlines():
        marker_match = MARKER_RE.match(line)
        if not marker_match:
            continue
        name = marker_match.group(3).strip()
        if not name:
            continue
        position = float(marker_match.group(2))
        if abs(position - start_position) < 0.001:
            return name
        fallback = fallback or name
    return fallback


def _build_warnings(
    tracks: list[dict[str, object]],
    audio_track: dict[str, object] | None,
    lyric_track: dict[str, object] | None,
) -> list[str]:
    warnings = []
    if len(tracks) != 3:
        warnings.append(f"Esperava 3 tracks, encontrei {len(tracks)}.")
    if audio_track is None:
        warnings.append("Nao encontrei uma track de audio com item WAV/MP3/FLAC/OGG.")
    if lyric_track is None:
        warnings.append('Nao encontrei track "Lyrics" ou "Letras".')
    elif not lyric_track["items"]:
        warnings.append("A track de letras nao tem items com POSITION/LENGTH.")
    return warnings


def _marker_insert_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        if line.lstrip().startswith("<TRACK"):
            return index
    return len(lines)


def _project_setting_insert_index(lines: list[str]) -> int:
    for index, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("MARKER") or stripped.startswith("<TRACK"):
            return index
    return len(lines)


def _start_marker_line(song: Song, newline: str) -> str:
    return f'  MARKER 1 {_format_float(song.start_position)} "Start" 0 0 1{newline}'


def _cursor_line(song: Song, newline: str) -> str:
    return f"  CURSOR {_format_float(song.start_position)}{newline}"


def _escape_marker_name(name: str) -> str:
    return name.replace('"', "'")


def _detect_newline(text: str) -> str:
    return "\r\n" if "\r\n" in text else "\n"


def _format_float(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"


def _format_timestamp(seconds: float) -> str:
    seconds = max(0, seconds)
    minutes = int(seconds // 60)
    remaining = seconds - minutes * 60
    return f"{minutes:02d}:{remaining:06.3f}"
