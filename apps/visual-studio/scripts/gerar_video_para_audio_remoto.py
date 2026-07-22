from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.workflow_loader import build_lowvram_ksampler_workflow, build_sdxl_turbo_workflow


DEFAULT_AUDIO_PATH = Path(
    r"D:\Projetos AI\LiveRig VSs\COMFORTABLY NUMB - PINK FLOYD (FIREBIRD).wav"
)
DEFAULT_COMFYUI_URL = "http://192.168.15.9:8188"
DEFAULT_HOST = "danilocoelho@192.168.15.9"
REMOTE_GENERATOR_PATH = "/tmp/gerar_video_aleatorio.py"
IMAGE_COUNT = 15
AUDIO_EXTENSIONS = {".wav", ".mp3"}
HTTP_TIMEOUT_SECONDS = 120
HTTP_RETRIES = 3
DEFAULT_IMAGE_WIDTH = 512
DEFAULT_IMAGE_HEIGHT = 512
DEFAULT_WORKFLOW = "lowvram-ksampler"
DEFAULT_CHECKPOINT = "v1-5-pruned-emaonly.safetensors"
DEFAULT_RESTART_COMFYUI_COMMAND = "cd ~/homelab/compose/comfyui && docker compose restart"


PROMPT_PREFIXES = [
    "psychedelic progressive rock stage visual",
    "dreamlike guitar solo atmosphere",
    "surreal hospital light and smoke",
    "cinematic classic rock concert projection",
    "slow emotional neon haze",
    "abstract pulse synchronized with music",
]

PROMPT_SCENES = [
    "floating lights over a dark stage",
    "blue lasers through fog and silhouettes",
    "melancholic face dissolving into clouds",
    "vintage analog film texture, soft glow",
    "cosmic tunnel, stars, prism refraction",
    "large screen visual for a live band",
    "deep red and cyan liquid light patterns",
    "slow moving geometric wall of light",
]

PROMPT_SUFFIXES = [
    "high detail, cinematic, no text",
    "wide projection background, dramatic contrast",
    "stage-ready visuals, atmospheric, sharp",
    "music video frame, emotional, immersive",
]


def main() -> None:
    args = parse_args()
    audio_path = resolve_audio_path(args.audio_path)

    audio_name = audio_path.stem
    folder_name = safe_folder_name(audio_name)
    remote_input_dir = f"~/homelab/compose/comfyui/output/{folder_name}"
    duration_seconds = args.duration_seconds
    if duration_seconds is None:
        duration_seconds = round(wav_duration_seconds(audio_path))

    print(f"Audio: {audio_path}")
    print(f"Duracao: {duration_seconds}s")
    print(f"Pasta remota: {remote_input_dir}")
    print(f"Workflow: {args.workflow}")
    print(f"Checkpoint: {args.checkpoint}")
    print(f"Resolucao das imagens: {args.image_width}x{args.image_height}")

    if args.restart_comfyui_before:
        restart_comfyui(args.host, args.restart_comfyui_command)

    existing_images = count_remote_images(args.host, remote_input_dir)
    images_to_generate = max(0, args.image_count - existing_images)
    print(f"Imagens existentes no servidor: {existing_images}")
    print(f"Imagens novas a gerar: {images_to_generate}")

    for index in range(existing_images + 1, existing_images + images_to_generate + 1):
        prompt = random_prompt(audio_name)
        filename_prefix = f"{folder_name}/LiveRig_{folder_name}_{index:02d}"
        print(f"Gerando imagem {index:02d}: {prompt}")
        prompt_id = queue_image(
            comfyui_url=args.comfyui_url,
            prompt=prompt,
            negative_prompt=args.negative_prompt,
            seed=random.randint(1, 999999999),
            filename_prefix=filename_prefix,
            image_width=args.image_width,
            image_height=args.image_height,
            workflow_name=args.workflow,
            checkpoint=args.checkpoint,
            steps=args.steps,
            cfg=args.cfg,
        )
        if not wait_for_image(args.comfyui_url, prompt_id, args.image_timeout_seconds):
            print(f"Aviso: imagem {index:02d} nao concluiu. Continuando.")
        if args.free_memory_after_image:
            free_comfyui_memory(args.comfyui_url)
        generated_in_this_run = index - existing_images
        if (
            args.restart_comfyui_every > 0
            and generated_in_this_run < images_to_generate
            and generated_in_this_run % args.restart_comfyui_every == 0
        ):
            restart_comfyui(args.host, args.restart_comfyui_command)

    run(["scp", str(local_generator_script()), f"{args.host}:{REMOTE_GENERATOR_PATH}"])

    remote_sync_plan = None
    if args.sync_plan is not None:
        remote_sync_plan = "/tmp/liverig_audio_sync_plan.json"
        run(["scp", str(args.sync_plan), f"{args.host}:{remote_sync_plan}"])

    remote_command = [
        "python3",
        REMOTE_GENERATOR_PATH,
        "--input-dir",
        remote_input_dir,
        "--duration-seconds",
        str(duration_seconds),
        "--width",
        str(args.width),
        "--height",
        str(args.height),
        "--fps",
        str(args.fps),
    ]
    if remote_sync_plan is not None:
        remote_command.extend(["--sync-plan", remote_sync_plan])

    run(["ssh", args.host, " ".join(remote_command)])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera imagens no ComfyUI e monta um video no HomeLab com duracao do audio."
    )
    parser.add_argument("--audio-path", type=Path, default=DEFAULT_AUDIO_PATH)
    parser.add_argument("--comfyui-url", default=DEFAULT_COMFYUI_URL)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--image-count", type=int, default=IMAGE_COUNT)
    parser.add_argument(
        "--image-timeout-seconds",
        type=int,
        default=600,
        help="Tempo maximo de espera por imagem no ComfyUI.",
    )
    parser.add_argument(
        "--duration-seconds",
        type=int,
        default=None,
        help="Duracao manual do video. Se informado, o script nao abre o arquivo de audio.",
    )
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=720)
    parser.add_argument("--fps", type=int, default=25)
    parser.add_argument("--image-width", type=int, default=DEFAULT_IMAGE_WIDTH)
    parser.add_argument("--image-height", type=int, default=DEFAULT_IMAGE_HEIGHT)
    parser.add_argument(
        "--workflow",
        choices=["lowvram-ksampler", "sdxlturbo"],
        default=DEFAULT_WORKFLOW,
    )
    parser.add_argument(
        "--checkpoint",
        default=DEFAULT_CHECKPOINT,
        help="Nome do checkpoint instalado no ComfyUI.",
    )
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--cfg", type=float, default=None)
    parser.add_argument(
        "--negative-prompt",
        default="blurry, low quality, text, watermark, logo, distorted faces",
    )
    parser.add_argument(
        "--sync-plan",
        type=Path,
        default=None,
        help="JSON opcional com trechos sincronizados, textos e arquivos fixos.",
    )
    parser.add_argument(
        "--free-memory-after-image",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Chama /free no ComfyUI depois de cada imagem.",
    )
    parser.add_argument(
        "--restart-comfyui-before",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Reinicia o container ComfyUI antes do lote.",
    )
    parser.add_argument(
        "--restart-comfyui-every",
        type=int,
        default=3,
        help="Reinicia o ComfyUI a cada N imagens geradas. Use 0 para desativar.",
    )
    parser.add_argument(
        "--restart-comfyui-command",
        default=DEFAULT_RESTART_COMFYUI_COMMAND,
        help="Comando remoto usado para reiniciar o ComfyUI.",
    )
    return parser.parse_args()


def wav_duration_seconds(path: Path) -> float:
    if path.suffix.lower() != ".wav":
        raise SystemExit("Por enquanto este script le duracao automaticamente apenas de WAV.")

    with wave.open(str(path), "rb") as audio:
        return audio.getnframes() / audio.getframerate()


def resolve_audio_path(path: Path) -> Path:
    resolved = path.resolve()
    if not resolved.exists():
        raise SystemExit(f"Caminho de audio nao encontrado: {resolved}")

    if resolved.is_file():
        if resolved.suffix.lower() not in AUDIO_EXTENSIONS:
            raise SystemExit(f"Arquivo nao e WAV nem MP3: {resolved}")
        return resolved

    if not resolved.is_dir():
        raise SystemExit(f"Caminho de audio invalido: {resolved}")

    candidates = [
        file
        for file in resolved.rglob("*")
        if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS
    ]
    if not candidates:
        raise SystemExit(f"Nenhum WAV ou MP3 encontrado dentro de: {resolved}")

    candidates.sort(key=lambda file: (file.suffix.lower() != ".wav", str(file).lower()))
    selected = candidates[0]
    print(f"Audio encontrado na pasta: {selected}")
    return selected


def random_prompt(audio_name: str) -> str:
    parts = [
        random.choice(PROMPT_PREFIXES),
        random.choice(PROMPT_SCENES),
        random.choice(PROMPT_SUFFIXES),
        f"inspired by {audio_name}",
    ]
    return ", ".join(parts)


def queue_image(
    comfyui_url: str,
    prompt: str,
    negative_prompt: str,
    seed: int,
    filename_prefix: str,
    image_width: int,
    image_height: int,
    workflow_name: str,
    checkpoint: str,
    steps: int | None,
    cfg: float | None,
) -> str:
    if workflow_name == "sdxlturbo":
        workflow = build_sdxl_turbo_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            filename_prefix=filename_prefix,
            width=image_width,
            height=image_height,
            checkpoint=checkpoint,
        )
    else:
        workflow = build_lowvram_ksampler_workflow(
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
            filename_prefix=filename_prefix,
            width=image_width,
            height=image_height,
            checkpoint=checkpoint,
            steps=steps,
            cfg=cfg,
        )
    payload = json.dumps({"prompt": workflow}).encode("utf-8")
    request = urllib.request.Request(
        f"{comfyui_url.rstrip('/')}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    response = request_json(request)
    return str(response["prompt_id"])


def wait_for_image(comfyui_url: str, prompt_id: str, timeout_seconds: int) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        request = urllib.request.Request(f"{comfyui_url.rstrip('/')}/history/{prompt_id}")
        history = request_json(request)
        item = history.get(prompt_id)
        if isinstance(item, dict):
            status = item.get("status")
            if isinstance(status, dict):
                if status.get("completed") is True:
                    return True
                status_str = str(status.get("status_str", "")).lower()
                if status_str in {"error", "failed"}:
                    print(f"Aviso: ComfyUI retornou erro no prompt {prompt_id}: {status}")
                    return False
        time.sleep(1)

    print(f"Aviso: ComfyUI nao concluiu o prompt {prompt_id} em {timeout_seconds}s.")
    return False


def free_comfyui_memory(comfyui_url: str) -> None:
    payload = json.dumps(
        {
            "unload_models": True,
            "free_memory": True,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{comfyui_url.rstrip('/')}/free",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        request_text(request)
        print("Memoria do ComfyUI liberada.")
    except SystemExit as error:
        print(f"Aviso: nao foi possivel liberar memoria do ComfyUI: {error}")


def request_json(request: urllib.request.Request) -> dict:
    text = request_text(request)
    if not text.strip():
        return {}

    return json.loads(text)


def request_text(request: urllib.request.Request) -> str:
    last_error: Exception | None = None

    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                return response.read().decode("utf-8")
        except urllib.error.URLError as error:
            last_error = error
            if attempt < HTTP_RETRIES:
                wait_seconds = attempt * 5
                print(
                    f"ComfyUI nao respondeu na tentativa {attempt}/{HTTP_RETRIES}. "
                    f"Tentando de novo em {wait_seconds}s..."
                )
                time.sleep(wait_seconds)

    raise SystemExit(f"Erro ao chamar ComfyUI: {last_error}")


def safe_folder_name(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "audio"


def local_generator_script() -> Path:
    return Path(__file__).resolve().parent / "gerar_video_aleatorio.py"


def count_remote_images(host: str, remote_input_dir: str) -> int:
    command = (
        f"find {remote_input_dir} -maxdepth 1 -type f "
        "\\( -iname '*.png' -o -iname '*.mp4' \\) | wc -l"
    )
    result = subprocess.run(
        ["ssh", host, command],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 0

    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0


def restart_comfyui(host: str, command: str) -> None:
    print("Reiniciando ComfyUI no HomeLab...")
    run(["ssh", host, command])
    print("Aguardando ComfyUI subir...")
    time.sleep(20)


def run(command: list[str]) -> None:
    print("Executando:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
