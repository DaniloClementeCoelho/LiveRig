from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


DEFAULT_HOST = "danilocoelho@192.168.15.9"
DEFAULT_REMOTE_SCRIPT = "/tmp/gerar_video_aleatorio.py"
DEFAULT_REMOTE_INPUT_DIR = "~/homelab/compose/comfyui/output/a-lot-of-respect"


def main() -> None:
    args = parse_args()
    local_script = Path(__file__).resolve().parent / "gerar_video_aleatorio.py"

    if not local_script.exists():
        raise SystemExit(f"Script local nao encontrado: {local_script}")

    run(["scp", str(local_script), f"{args.host}:{args.remote_script}"])

    remote_sync_plan = ""
    if args.sync_plan is not None:
        remote_sync_plan = "/tmp/liverig_sync_plan.json"
        run(["scp", str(args.sync_plan), f"{args.host}:{remote_sync_plan}"])

    remote_command = [
        "python3",
        args.remote_script,
        "--input-dir",
        args.input_dir,
        "--duration-seconds",
        str(args.duration_seconds),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--fps",
        str(args.fps),
    ]
    if remote_sync_plan:
        remote_command.extend(["--sync-plan", remote_sync_plan])

    run(["ssh", args.host, " ".join(remote_command)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa no HomeLab a geracao aleatoria de video."
    )
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--remote-script", default=DEFAULT_REMOTE_SCRIPT)
    parser.add_argument("--input-dir", default=DEFAULT_REMOTE_INPUT_DIR)
    parser.add_argument("--duration-seconds", type=int, default=60)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument(
        "--sync-plan",
        type=Path,
        default=None,
        help="JSON local opcional com trechos sincronizados.",
    )
    return parser.parse_args()


def run(command: list[str]) -> None:
    print("Executando:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
