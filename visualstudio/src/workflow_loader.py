import copy
import json
from pathlib import Path


WORKFLOW_PATH = Path(__file__).resolve().parent.parent / "workflows" / "sdxlturbo_api.json"


def build_sdxl_turbo_workflow(
    prompt: str,
    negative_prompt: str,
    seed: int,
    filename_prefix: str,
) -> dict:
    workflow = _load_workflow()

    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt
    workflow["13"]["inputs"]["noise_seed"] = seed
    workflow["27"]["inputs"]["filename_prefix"] = filename_prefix

    return workflow


def _load_workflow() -> dict:
    with WORKFLOW_PATH.open("r", encoding="utf-8") as file:
        return copy.deepcopy(json.load(file))
