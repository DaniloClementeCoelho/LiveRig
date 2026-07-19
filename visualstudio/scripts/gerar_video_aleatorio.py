from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


DEFAULT_INPUT_DIR = Path("~/homelab/compose/comfyui/output/a-lot-of-respect")
DEFAULT_DURATION_SECONDS = 60
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720
DEFAULT_FPS = 25
IMAGE_EXTENSIONS = {".png"}
VIDEO_EXTENSIONS = {".mp4"}


def main() -> None:
    args = parse_args()
    input_dir = args.input_dir.expanduser().resolve()
    output_dir = input_dir / "videos"
    temp_dir = output_dir / "_tmp_random_video"

    ensure_tool("ffmpeg")
    ensure_tool("ffprobe")

    files = find_media_files(input_dir)
    if not files:
        raise SystemExit(f"Nenhum PNG ou MP4 encontrado em {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    reset_temp_dir(temp_dir)

    try:
        segments = build_segments(
            files=files,
            temp_dir=temp_dir,
            duration_seconds=args.duration_seconds,
            width=args.width,
            height=args.height,
            fps=args.fps,
            sync_items=load_sync_plan(args.sync_plan),
            input_dir=input_dir,
        )
        output_path = output_dir / output_filename()
        concat_segments(segments, output_path)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"Video gerado: {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um video aleatorio de 1 minuto com PNGs e MP4s do ComfyUI."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Diretorio com PNGs/MP4s gerados para a musica.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=DEFAULT_DURATION_SECONDS,
        help="Duracao final aproximada do video.",
    )
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH)
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT)
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS)
    parser.add_argument(
        "--sync-plan",
        type=Path,
        default=None,
        help="JSON opcional com trechos fixos e texto sincronizado.",
    )
    return parser.parse_args()


def ensure_tool(tool_name: str) -> None:
    if shutil.which(tool_name) is None:
        raise SystemExit(f"{tool_name} nao encontrado no PATH.")


def find_media_files(input_dir: Path) -> list[Path]:
    output_videos_dir = input_dir / "videos"
    files = []

    for path in input_dir.rglob("*"):
        if not path.is_file():
            continue
        if output_videos_dir in path.parents:
            continue
        if path.suffix.lower() in IMAGE_EXTENSIONS | VIDEO_EXTENSIONS:
            files.append(path)

    return sorted(files)


def reset_temp_dir(temp_dir: Path) -> None:
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(parents=True, exist_ok=True)


def build_segments(
    files: list[Path],
    temp_dir: Path,
    duration_seconds: int,
    width: int,
    height: int,
    fps: int,
    sync_items: list[dict],
    input_dir: Path,
) -> list[Path]:
    segments = []
    elapsed = 0.0
    index = 1

    for item in sync_items:
        start = float(item.get("start", 0))
        end = float(item.get("end", start))
        if end <= start:
            continue

        while elapsed < min(start, duration_seconds):
            segment_duration = min(
                random.uniform(3.5, 7.0),
                min(start, duration_seconds) - elapsed,
            )
            segment_path = temp_dir / f"segment-{index:03d}.mp4"
            render_media_segment(
                random.choice(files),
                segment_path,
                segment_duration,
                width,
                height,
                fps,
            )
            segments.append(segment_path)
            elapsed += segment_duration
            index += 1

        if elapsed >= duration_seconds:
            break

        segment_duration = min(end, duration_seconds) - elapsed
        if segment_duration <= 0:
            continue

        segment_path = temp_dir / f"segment-{index:03d}.mp4"
        render_media_segment(
            choose_sync_source(item, files, input_dir),
            segment_path,
            segment_duration,
            width,
            height,
            fps,
            text=item.get("text"),
        )
        segments.append(segment_path)
        elapsed += segment_duration
        index += 1

    while elapsed < duration_seconds:
        source = random.choice(files)
        segment_duration = min(random.uniform(3.5, 7.0), duration_seconds - elapsed)
        segment_path = temp_dir / f"segment-{index:03d}.mp4"

        render_media_segment(source, segment_path, segment_duration, width, height, fps)

        segments.append(segment_path)
        elapsed += segment_duration
        index += 1

    return segments


def render_media_segment(
    source: Path,
    output_path: Path,
    duration_seconds: float,
    width: int,
    height: int,
    fps: int,
    text: str | None = None,
) -> None:
    if source.suffix.lower() in IMAGE_EXTENSIONS:
        render_image_segment(source, output_path, duration_seconds, width, height, fps, text)
    else:
        render_video_segment(source, output_path, duration_seconds, width, height, fps, text)


def render_image_segment(
    source: Path,
    output_path: Path,
    duration_seconds: float,
    width: int,
    height: int,
    fps: int,
    text: str | None = None,
) -> None:
    frames = max(1, round(duration_seconds * fps))
    video_filter = add_text_filter(
        random_image_filter(width, height, fps, frames, duration_seconds),
        text,
    )

    run(
        [
            "ffmpeg",
            "-y",
            "-loop",
            "1",
            "-i",
            str(source),
            "-t",
            f"{duration_seconds:.3f}",
            "-vf",
            video_filter,
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )


def render_video_segment(
    source: Path,
    output_path: Path,
    duration_seconds: float,
    width: int,
    height: int,
    fps: int,
    text: str | None = None,
) -> None:
    source_duration = probe_duration(source)
    start_at = 0.0
    if source_duration > duration_seconds + 1:
        start_at = random.uniform(0, source_duration - duration_seconds)

    video_filter = add_text_filter(random_video_filter(width, height, fps), text)

    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{start_at:.3f}",
            "-i",
            str(source),
            "-t",
            f"{duration_seconds:.3f}",
            "-vf",
            video_filter,
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ]
    )


def probe_duration(source: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(source),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def load_sync_plan(sync_plan: Path | None) -> list[dict]:
    if sync_plan is None:
        return []

    path = sync_plan.expanduser().resolve()
    if not path.exists():
        raise SystemExit(f"Plano de sincronizacao nao encontrado: {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    items = data.get("segments", data)
    if not isinstance(items, list):
        raise SystemExit("Plano de sincronizacao deve ser uma lista ou conter 'segments'.")

    return sorted(
        [item for item in items if isinstance(item, dict)],
        key=lambda item: float(item.get("start", 0)),
    )


def choose_sync_source(item: dict, files: list[Path], input_dir: Path) -> Path:
    file_value = item.get("file")
    if not isinstance(file_value, str) or not file_value.strip():
        return random.choice(files)

    requested = Path(file_value)
    candidates = []
    if requested.is_absolute():
        candidates.append(requested)
    else:
        candidates.append((input_dir / requested).resolve())
        candidates.extend(path for path in files if path.name == file_value)

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate

    print(f"Aviso: arquivo sincronizado nao encontrado, usando aleatorio: {file_value}")
    return random.choice(files)


def add_text_filter(video_filter: str, text: str | None) -> str:
    if not isinstance(text, str) or not text.strip():
        return video_filter

    safe_text = escape_drawtext(text.strip())
    drawtext = (
        "drawtext="
        f"text='{safe_text}':"
        "fontcolor=white:"
        "fontsize=54:"
        "box=1:"
        "boxcolor=black@0.58:"
        "boxborderw=24:"
        "x=(w-text_w)/2:"
        "y=h-(text_h*2.4)"
    )
    return f"{video_filter},{drawtext}"


def escape_drawtext(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "\\'")
        .replace("\n", "\\n")
    )


def random_image_filter(
    width: int,
    height: int,
    fps: int,
    frames: int,
    duration_seconds: float,
) -> str:
    effect = random.choice(
        [
            "zoom_in",
            "zoom_out",
            "pan_left",
            "pan_right",
            "pan_down",
            "rotate_left",
            "rotate_right",
            "pulse_color",
            "blink",
        ]
    )
    base = f"scale={width * 2}:{height * 2}:force_original_aspect_ratio=increase"
    saturation = random.uniform(1.0, 1.55)
    contrast = random.uniform(1.0, 1.25)
    brightness = random.uniform(-0.04, 0.05)

    if effect == "zoom_in":
        zoompan = (
            f"zoompan=z='min(zoom+{random.choice(['0.0012', '0.0018', '0.0024'])},1.18)':"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={width}x{height}:fps={fps}"
        )
        filters = [base, zoompan]
    elif effect == "zoom_out":
        zoompan = (
            "zoompan=z='max(1.18-on/250,1.0)':"
            "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
            f"d={frames}:s={width}x{height}:fps={fps}"
        )
        filters = [base, zoompan]
    elif effect == "pan_left":
        filters = [
            base,
            f"crop={width}:{height}:x='(n/{frames})*(iw-{width})':y='(ih-{height})/2'",
            f"fps={fps}",
        ]
    elif effect == "pan_right":
        filters = [
            base,
            f"crop={width}:{height}:x='(1-n/{frames})*(iw-{width})':y='(ih-{height})/2'",
            f"fps={fps}",
        ]
    elif effect == "pan_down":
        filters = [
            base,
            f"crop={width}:{height}:x='(iw-{width})/2':y='(n/{frames})*(ih-{height})'",
            f"fps={fps}",
        ]
    elif effect in {"rotate_left", "rotate_right"}:
        direction = "-" if effect == "rotate_left" else ""
        filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            f"rotate={direction}0.035*sin(2*PI*t/{duration_seconds:.3f}):fillcolor=black",
            f"scale={width}:{height}",
            f"fps={fps}",
        ]
    elif effect == "pulse_color":
        filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            f"eq=saturation='1.1+0.55*sin(2*PI*t/{max(duration_seconds / 2, 1):.3f})':"
            f"contrast='1.05+0.18*sin(2*PI*t/{max(duration_seconds, 1):.3f})'",
            f"fps={fps}",
        ]
    else:
        filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            "tblend=all_mode=screen:all_opacity=0.22",
            "eq=brightness='if(gt(mod(t,1.2),1.05),0.30,0)':saturation=1.45",
            f"fps={fps}",
        ]

    filters.extend(
        [
            f"eq=saturation={saturation:.2f}:contrast={contrast:.2f}:brightness={brightness:.2f}",
            "fade=t=in:st=0:d=0.35",
            f"fade=t=out:st={max(duration_seconds - 0.35, 0):.3f}:d=0.35",
            "format=yuv420p",
        ]
    )
    return ",".join(filters)


def random_video_filter(width: int, height: int, fps: int) -> str:
    speed = random.choice([0.80, 0.90, 1.0, 1.12, 1.25])
    saturation = random.uniform(0.85, 1.45)
    hue = random.uniform(-12, 12)
    filters = [
        f"scale={width}:{height}:force_original_aspect_ratio=increase",
        f"crop={width}:{height}",
        f"setpts={1 / speed:.4f}*PTS",
        f"fps={fps}",
        f"hue=h={hue:.2f}",
        f"eq=saturation={saturation:.2f}:contrast={random.uniform(1.0, 1.18):.2f}",
    ]

    extra_effect = random.choice(["none", "hflip", "blink", "pulse"])
    if extra_effect == "hflip":
        filters.append("hflip")
    elif extra_effect == "blink":
        filters.append("eq=brightness='if(gt(mod(t,1.6),1.48),0.22,0)'")
    elif extra_effect == "pulse":
        filters.append("eq=brightness='0.08*sin(2*PI*t/2)'")

    filters.extend(["fade=t=in:st=0:d=0.25", "format=yuv420p"])
    return ",".join(filters)


def concat_segments(segments: list[Path], output_path: Path) -> None:
    concat_file = output_path.parent / "_concat_random_video.txt"
    concat_file.write_text(
        "".join(f"file '{segment.as_posix()}'\n" for segment in segments),
        encoding="utf-8",
    )

    try:
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                str(output_path),
            ]
        )
    finally:
        concat_file.unlink(missing_ok=True)


def output_filename() -> str:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"video-aleatorio-{stamp}.mp4"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
