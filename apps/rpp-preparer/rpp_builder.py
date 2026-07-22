from __future__ import annotations

from pathlib import Path
import wave


AUDIO_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif"}
DEFAULT_AUDIO_LENGTH = 300.0


def is_audio_file(path: Path) -> bool:
    return path.is_file() and path.suffix.casefold() in AUDIO_EXTENSIONS


def create_project_from_audio(audio_file: Path, project_path: Path | None = None) -> Path:
    audio_file = audio_file.resolve()
    project_path = project_path or audio_file.with_name("project.rpp")
    track_name = audio_file.stem
    source_type = _source_type(audio_file)
    media_path = f"Media/{audio_file.name}"
    audio_length = _audio_length(audio_file)

    project_path.write_text(
        "\n".join(
            [
                '<REAPER_PROJECT 0.1 "7.0" 1700000000',
                "  RIPPLE 0",
                "  GROUPOVERRIDE 0 0 0",
                "  AUTOXFADE 1",
                "  ENVATTACH 1",
                "  POOLEDENVATTACH 0",
                "  MIXERUIFLAGS 11 48",
                "  PEAKGAIN 1",
                "  FEEDBACK 0",
                "  PANLAW 1",
                "  PROJOFFS 0 0 0",
                "  MAXPROJLEN 0 600",
                "  GRID 3199 8 1 8 1 0 0 0",
                "  TIMEMODE 1 5 -1 30 0 0 -1",
                "  VIDEO_CONFIG 0 0 256",
                "  PANMODE 3",
                "  CURSOR 0",
                "  ZOOM 100 0 0",
                "  VZOOMEX 6 0",
                "  USE_REC_CFG 0",
                "  RECMODE 1",
                "  SMPTESYNC 0 30 100 40 1000 300 0 0 1 0 0",
                "  LOOP 0",
                "  LOOPGRAN 0 4",
                "  RECORD_PATH \"\" \"\"",
                "  TEMPO 120 4 4",
                '  MARKER 1 0 "Start" 0 0 1',
                "  <TRACK",
                f'    NAME "{_escape(track_name)}"',
                "    PEAKCOL 16576",
                "    BEAT -1",
                "    AUTOMODE 0",
                "    VOLPAN 1 0 -1 -1 1",
                "    MUTESOLO 0 0 0",
                "    IPHASE 0",
                "    PLAYOFFS 0 1",
                "    ISBUS 0 0",
                "    BUSCOMP 0 0 0 0 0",
                "    SHOWINMIX 1 0.6667 0.5 1 0.5 0 0 0",
                "    FREEMODE 0",
                "    SEL 0",
                "    REC 0 0 1 0 0 0 0 0",
                "    VU 2",
                "    TRACKHEIGHT 0 0 0 0 0 0",
                "    INQ 0 0 0 0.5 100 0 0 100",
                "    NCHAN 2",
                "    FX 1",
                "    TRACKID {00000000-0000-0000-0000-000000000001}",
                "    PERF 0",
                "    MIDIOUT -1",
                "    MAINSEND 1 0",
                "    <ITEM",
                "      POSITION 0",
                f"      LENGTH {_format_float(audio_length)}",
                "      LOOP 0",
                "      ALLTAKES 0",
                "      FADEIN 1 0 0 1 0 0 0",
                "      FADEOUT 1 0 0 1 0 0 0",
                "      MUTE 0 0",
                "      SEL 0",
                f'      NAME "{_escape(audio_file.name)}"',
                "      IGUID {00000000-0000-0000-0000-000000000101}",
                "      IID 1",
                "      VOLPAN 1 0 1 -1",
                "      SOFFS 0",
                "      PLAYRATE 1 1 0 -1 0 0.0025",
                "      CHANMODE 0",
                "      GUID {00000000-0000-0000-0000-000000000201}",
                f"      <SOURCE {source_type}",
                f'        FILE "{_escape(media_path)}"',
                "      >",
                "    >",
                "  >",
                '  <TRACK',
                '    NAME "guitarra"',
                "  >",
                '  <TRACK',
                '    NAME "Lyrics"',
                "  >",
                ">",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return project_path


def _source_type(path: Path) -> str:
    if path.suffix.casefold() == ".mp3":
        return "MP3"
    return "WAVE"


def _audio_length(path: Path) -> float:
    suffix = path.suffix.casefold()
    if suffix == ".wav":
        return _wav_length(path) or DEFAULT_AUDIO_LENGTH
    if suffix == ".mp3":
        return _mp3_length(path) or DEFAULT_AUDIO_LENGTH
    return DEFAULT_AUDIO_LENGTH


def _wav_length(path: Path) -> float | None:
    try:
        with wave.open(str(path), "rb") as file:
            frames = file.getnframes()
            rate = file.getframerate()
            if rate > 0:
                return frames / rate
    except (OSError, wave.Error):
        return None
    return None


def _mp3_length(path: Path) -> float | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None

    offset = _skip_id3v2(data)
    duration = 0.0
    while offset + 4 <= len(data):
        header = int.from_bytes(data[offset : offset + 4], "big")
        frame = _mp3_frame_info(header)
        if frame is None:
            offset += 1
            continue
        frame_size, samples, sample_rate = frame
        duration += samples / sample_rate
        offset += frame_size

    return duration if duration > 0 else None


def _skip_id3v2(data: bytes) -> int:
    if len(data) < 10 or data[:3] != b"ID3":
        return 0
    size = 0
    for byte in data[6:10]:
        size = (size << 7) | (byte & 0x7F)
    return 10 + size


def _mp3_frame_info(header: int) -> tuple[int, int, int] | None:
    if (header >> 21) & 0x7FF != 0x7FF:
        return None

    version_id = (header >> 19) & 0x3
    layer_id = (header >> 17) & 0x3
    bitrate_index = (header >> 12) & 0xF
    sample_rate_index = (header >> 10) & 0x3
    padding = (header >> 9) & 0x1

    if version_id == 1 or layer_id != 1 or bitrate_index in {0, 15} or sample_rate_index == 3:
        return None

    bitrates = {
        3: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
        0: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160],
    }
    sample_rates = {
        3: [44100, 48000, 32000],
        2: [22050, 24000, 16000],
        0: [11025, 12000, 8000],
    }

    bitrate = bitrates[version_id][bitrate_index] * 1000
    sample_rate = sample_rates[version_id][sample_rate_index]
    samples = 1152 if version_id == 3 else 576
    factor = 144 if version_id == 3 else 72
    frame_size = int((factor * bitrate) / sample_rate) + padding
    if frame_size <= 4:
        return None
    return frame_size, samples, sample_rate


def _escape(text: str) -> str:
    return text.replace('"', "'")


def _format_float(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text or "0"
