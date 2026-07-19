import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


PROJECTS_ROOT = Path(__file__).resolve().parent.parent / "projects"
ASSETS_SCHEMA_VERSION = "0.1"


def save_generated_image_asset(
    project_id: str,
    image_filename: str,
    image_content: bytes,
    prompt: str,
    negative_prompt: str,
    seed: int,
    prompt_id: str,
) -> dict:
    project_dir = _project_dir(project_id)
    images_dir = project_dir / "assets" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(image_filename).name
    asset_id = f"img-{uuid4().hex[:12]}"
    output_filename = f"{asset_id}-{safe_filename}"
    output_path = images_dir / output_filename
    output_path.write_bytes(image_content)

    relative_file = output_path.relative_to(project_dir).as_posix()
    asset = {
        "id": asset_id,
        "type": "image",
        "origin": "generated",
        "status": "draft",
        "file": relative_file,
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "seed": seed,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "engine": "comfyui",
            "workflow": "workflows/sdxlturbo_api.json",
            "prompt_id": prompt_id,
            "original_filename": image_filename,
        },
    }

    assets_data = _load_assets(project_dir)
    assets_data["assets"].append(asset)
    _save_assets(project_dir, assets_data)

    return asset


def _project_dir(project_id: str) -> Path:
    project_dir = (PROJECTS_ROOT / project_id).resolve()
    projects_root = PROJECTS_ROOT.resolve()

    if not project_dir.is_relative_to(projects_root):
        raise FileNotFoundError("Projeto invalido.")

    if not project_dir.exists() or not project_dir.is_dir():
        raise FileNotFoundError(f"Projeto nao encontrado: {project_id}")

    return project_dir


def _load_assets(project_dir: Path) -> dict:
    assets_path = project_dir / "assets.json"
    if not assets_path.exists():
        return {
            "schema_version": ASSETS_SCHEMA_VERSION,
            "assets": [],
        }

    with assets_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return {
            "schema_version": ASSETS_SCHEMA_VERSION,
            "assets": [],
        }

    assets = data.get("assets")
    if not isinstance(assets, list):
        data["assets"] = []

    data.setdefault("schema_version", ASSETS_SCHEMA_VERSION)
    return data


def _save_assets(project_dir: Path, assets_data: dict) -> None:
    assets_path = project_dir / "assets.json"
    temp_path = project_dir / "assets.tmp.json"

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(assets_data, file, ensure_ascii=False, indent=2)
        file.write("\n")

    shutil.move(temp_path, assets_path)
