from __future__ import annotations

from pathlib import Path
import json
import re
import shutil

try:
    from .models import Song
    from .parser import ensure_start_marker, export_lyrics_markdown
except ImportError:
    from models import Song
    from parser import ensure_start_marker, export_lyrics_markdown


def import_song(song: Song, output_root: Path, overwrite: bool = False) -> Path:
    folder = _unique_folder(output_root / _safe_folder_name(song.title), overwrite)
    folder.mkdir(parents=True, exist_ok=True)

    project_name = "project.rpp"
    project_path = folder / project_name
    if song.source_file.resolve() != project_path.resolve():
        shutil.copy2(song.source_file, project_path)

    _copy_media_files(song, folder)
    ensure_start_marker(project_path, song)
    lyrics_name = _write_text(folder / "lyrics.md", export_lyrics_markdown(song))
    notes_name = _write_text(folder / "notes.md", song.notes)
    config = _build_config(song, project_name, lyrics_name, notes_name)

    with (folder / "config.json").open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=4, ensure_ascii=False)
        file.write("\n")

    return folder


def update_song(song: Song, folder: Path) -> None:
    """Compatibility wrapper for the first importer script."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "project.rpp"
    if song.source_file.resolve() != target.resolve():
        shutil.copy2(song.source_file, target)
    _copy_media_files(song, folder)
    ensure_start_marker(target, song)

    data = _build_config(
        song,
        "project.rpp",
        _write_text(folder / "lyrics.md", export_lyrics_markdown(song)),
        _write_text(folder / "notes.md", song.notes),
    )

    with (folder / "config.json").open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")

    print(f"OK {song.title}")


def _build_config(
    song: Song,
    project_name: str,
    lyrics_name: str | None,
    notes_name: str | None,
) -> dict[str, object]:
    data: dict[str, object] = {
        "title": song.title,
        "artist": song.artist,
        "project": project_name,
        "duration": song.duration,
        "bpm": song.bpm,
        "patch": 32,
        "tuning": "Eb",
    }
    if lyrics_name is not None:
        data["lyrics"] = lyrics_name
    if notes_name is not None:
        data["notes"] = notes_name
    return data


def _write_text(path: Path, text: str) -> str | None:
    if not text.strip():
        return None
    path.write_text(text, encoding="utf-8")
    return path.name


def _copy_media_files(song: Song, folder: Path) -> None:
    for media_file in song.media_files:
        source = _resolve_media_source(song.source_file.parent, media_file)
        if source is None:
            song.warnings.append(f"Arquivo de audio nao encontrado: {media_file}")
            continue

        destination = _media_destination(folder, media_file, source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            shutil.copy2(source, destination)


def _resolve_media_source(project_folder: Path, media_file: str) -> Path | None:
    raw_path = Path(media_file)
    candidates = []
    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.append(project_folder / raw_path)
        candidates.append(project_folder / raw_path.name)
        candidates.append(project_folder / "Media" / raw_path.name)

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    return None


def _media_destination(folder: Path, media_file: str, source: Path) -> Path:
    raw_path = Path(media_file)
    if raw_path.is_absolute():
        return folder / "Media" / source.name
    return folder / raw_path


def _safe_folder_name(name: str) -> str:
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', " ", name).strip()
    safe = re.sub(r"\s+", " ", safe)
    return safe or "Musica"


def _unique_folder(folder: Path, overwrite: bool) -> Path:
    if overwrite or not folder.exists():
        return folder

    index = 2
    while True:
        candidate = folder.with_name(f"{folder.name} {index}")
        if not candidate.exists():
            return candidate
        index += 1
