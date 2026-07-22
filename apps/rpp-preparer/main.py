from __future__ import annotations

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import sys

try:
    from .importer import import_song
    from .parser import parse_rpp, start_marker_position
    from .rpp_builder import create_project_from_audio, is_audio_file
except ImportError:
    from importer import import_song
    from parser import parse_rpp, start_marker_position
    from rpp_builder import create_project_from_audio, is_audio_file


DEFAULT_CONFIG = Path(__file__).resolve().parent / "config.local.json"
OUTPUT_ENV_VAR = "LIVERIG_IMPORTER_OUTPUT_DIR"


def main() -> int:
    parser = ArgumentParser(
        description="Importa projetos .rpp ou audio para o formato de pacote do LiveRig."
    )
    parser.add_argument(
        "source",
        nargs="?",
        default=Path.cwd() / "input",
        type=Path,
        help="Arquivo .rpp, arquivo de audio ou pasta contendo arquivos .rpp. Padrao: ./input",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Pasta onde os pacotes do LiveRig serao criados.",
    )
    parser.add_argument(
        "--config",
        default=DEFAULT_CONFIG,
        type=Path,
        help="Arquivo JSON de configuracao. Padrao: apps/rpp-preparer/config.local.json",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Usa a pasta da musica existente em vez de criar 'Nome 2'.",
    )
    args = parser.parse_args()
    args.source = _clean_path_argument(args.source)
    args.output = _clean_path_argument(args.output)
    args.config = _clean_path_argument(args.config)

    sources = _find_sources(args.source)
    if not sources:
        print(f"Nenhum .rpp ou audio suportado encontrado em: {args.source}")
        return 1

    output = _resolve_output(args.output, args.config)
    if output is None:
        print("Pasta de saida nao configurada.")
        print("Use uma destas opcoes:")
        print("  python apps\\rpp-preparer\\main.py entrada.rpp --output caminho\\da\\saida")
        print(f"  $env:{OUTPUT_ENV_VAR} = 'caminho\\da\\saida'")
        print(f'  crie {args.config} com: {{"output_dir": "caminho/da/saida"}}')
        return 1

    output.mkdir(parents=True, exist_ok=True)

    for source in sources:
        song = parse_rpp(source)
        folder = import_song(song, output, overwrite=args.overwrite)
        print(f"OK {song.title} -> {folder}")
        print(f"   marker: {start_marker_position(song)}s")
        for warning in song.warnings:
            print(f"   aviso: {warning}")

    return 0


def _find_sources(source: Path) -> list[Path]:
    if source.is_file() and source.suffix.casefold() == ".rpp":
        return [source]

    if is_audio_file(source):
        return [create_project_from_audio(source)]

    if source.is_dir():
        return sorted(
            [path for path in source.rglob("*") if path.is_file() and path.suffix.casefold() == ".rpp"],
            key=lambda path: str(path).casefold(),
        )

    return []


def _resolve_output(argument: Path | None, config_path: Path) -> Path | None:
    if argument is not None:
        return _clean_path_argument(argument)

    env_value = os.environ.get(OUTPUT_ENV_VAR)
    if env_value:
        return _clean_path_argument(Path(env_value))

    config = _read_config(config_path)
    output_dir = config.get("output_dir")
    if isinstance(output_dir, str) and output_dir.strip():
        return _clean_path_argument(Path(output_dir))

    return None


def _clean_path_argument(path: Path | None) -> Path | None:
    if path is None:
        return None
    return Path(str(path).strip().rstrip("\"'"))


def _read_config(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (OSError, json.JSONDecodeError):
        return {}

    return data if isinstance(data, dict) else {}


if __name__ == "__main__":
    sys.exit(main())
