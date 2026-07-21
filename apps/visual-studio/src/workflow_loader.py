import copy
import json
from pathlib import Path


WORKFLOWS_ROOT = Path(__file__).resolve().parent.parent / "workflows"
WORKFLOW_PATH = WORKFLOWS_ROOT / "sdxlturbo_api.json"
LOWVRAM_KSAMPLER_WORKFLOW_PATH = WORKFLOWS_ROOT / "lowvram_ksampler_api.json"


def build_sdxl_turbo_workflow(
    prompt: str,
    negative_prompt: str,
    seed: int,
    filename_prefix: str,
    width: int | None = None,
    height: int | None = None,
    checkpoint: str | None = None,
) -> dict:
    workflow = _load_workflow()

    if width is not None:
        workflow["5"]["inputs"]["width"] = width
    if height is not None:
        workflow["5"]["inputs"]["height"] = height
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt
    workflow["13"]["inputs"]["noise_seed"] = seed
    if checkpoint:
        workflow["20"]["inputs"]["ckpt_name"] = checkpoint
    workflow["27"]["inputs"]["filename_prefix"] = filename_prefix

    return workflow


def build_lowvram_ksampler_workflow(
    prompt: str,
    negative_prompt: str,
    seed: int,
    filename_prefix: str,
    width: int | None = None,
    height: int | None = None,
    checkpoint: str | None = None,
    steps: int | None = None,
    cfg: float | None = None,
) -> dict:
    workflow = _load_workflow(LOWVRAM_KSAMPLER_WORKFLOW_PATH)

    if width is not None:
        workflow["5"]["inputs"]["width"] = width
    if height is not None:
        workflow["5"]["inputs"]["height"] = height
    workflow["6"]["inputs"]["text"] = prompt
    workflow["7"]["inputs"]["text"] = negative_prompt
    workflow["13"]["inputs"]["seed"] = seed
    if checkpoint:
        workflow["20"]["inputs"]["ckpt_name"] = checkpoint
    if steps is not None:
        workflow["13"]["inputs"]["steps"] = steps
    if cfg is not None:
        workflow["13"]["inputs"]["cfg"] = cfg
    workflow["27"]["inputs"]["filename_prefix"] = filename_prefix

    return workflow


def _load_workflow(path: Path = WORKFLOW_PATH) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return copy.deepcopy(json.load(file))
