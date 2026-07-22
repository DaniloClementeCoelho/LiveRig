import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import re
from pathlib import Path

from src.comfyui_client import ComfyUIClient
from src.config import settings
from src.project_assets import save_generated_image_asset, save_remote_generated_image_asset
from src.workflow_loader import build_sdxl_turbo_workflow

app = FastAPI(title="LiveRig Visual Studio")


class GenerateImageRequest(BaseModel):
    prompt: str = Field(min_length=1)
    negative_prompt: str = "blurry, low quality, text, watermark"
    seed: int = 0
    filename_prefix: str = "LiveRigVisualStudio"


class GenerateProjectImageAssetRequest(BaseModel):
    prompt: str = Field(min_length=1)
    negative_prompt: str = "blurry, low quality, text, watermark"
    seed: int = 0


class GenerateStudioImageRequest(BaseModel):
    song_name: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    negative_prompt: str = "blurry, low quality, text, watermark"
    seed: int = 0


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "LiveRig Visual Studio",
    }


@app.get("/comfyui/status")
async def comfyui_status() -> dict:
    client = ComfyUIClient(settings.comfyui_url)

    try:
        system_stats = await client.system_stats()
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel conectar ao ComfyUI: {error}",
        ) from error

    return {
        "ok": True,
        "comfyui_url": settings.comfyui_url,
        "system_stats": system_stats,
    }


@app.post("/comfyui/generate-image")
async def comfyui_generate_image(request: GenerateImageRequest) -> dict:
    client = ComfyUIClient(settings.comfyui_url)
    workflow = build_sdxl_turbo_workflow(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        seed=request.seed,
        filename_prefix=request.filename_prefix,
    )

    try:
        result = await client.queue_prompt(workflow)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel enviar workflow ao ComfyUI: {error}",
        ) from error

    return {
        "ok": True,
        "comfyui_url": settings.comfyui_url,
        **result,
    }


@app.post("/comfyui/generate-image-and-wait")
async def comfyui_generate_image_and_wait(request: GenerateImageRequest) -> dict:
    client = ComfyUIClient(settings.comfyui_url)
    workflow = build_sdxl_turbo_workflow(
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        seed=request.seed,
        filename_prefix=request.filename_prefix,
    )

    try:
        result = await client.queue_prompt(workflow)
        prompt_id = result["prompt_id"]
        history = await client.wait_for_history(prompt_id)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel gerar imagem no ComfyUI: {error}",
        ) from error
    except TimeoutError as error:
        raise HTTPException(status_code=504, detail=str(error)) from error

    image = _first_history_image(history, prompt_id)
    if image is None:
        raise HTTPException(
            status_code=502,
            detail="ComfyUI concluiu o prompt, mas nao retornou imagem.",
        )

    filename = image["filename"]
    image_type = image.get("type", "output")
    subfolder = image.get("subfolder", "")
    url = _image_url(filename, image_type, subfolder)

    return {
        "ok": True,
        "comfyui_url": settings.comfyui_url,
        "prompt_id": prompt_id,
        "image": {
            "filename": filename,
            "subfolder": subfolder,
            "type": image_type,
            "url": url,
        },
    }


@app.get("/comfyui/history/{prompt_id}")
async def comfyui_history(prompt_id: str) -> dict:
    client = ComfyUIClient(settings.comfyui_url)

    try:
        history = await client.history(prompt_id)
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel consultar historico do ComfyUI: {error}",
        ) from error

    return {
        "ok": True,
        "comfyui_url": settings.comfyui_url,
        "prompt_id": prompt_id,
        "history": history,
    }


@app.get("/comfyui/image")
async def comfyui_image(
    filename: str,
    type: str = "output",
    subfolder: str = "",
) -> Response:
    client = ComfyUIClient(settings.comfyui_url)

    try:
        image = await client.view_image(
            filename=filename,
            file_type=type,
            subfolder=subfolder,
        )
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel buscar imagem no ComfyUI: {error}",
        ) from error

    return Response(
        content=image["content"],
        media_type=image["content_type"],
    )


@app.post("/projects/{project_id}/generate-image-asset")
async def generate_project_image_asset(
    project_id: str,
    request: GenerateProjectImageAssetRequest,
) -> dict:
    filename_prefix = f"LiveRig_{project_id.replace('-', '_')}"
    generation = await comfyui_generate_image_and_wait(
        GenerateImageRequest(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            filename_prefix=filename_prefix,
        )
    )

    image = generation["image"]
    client = ComfyUIClient(settings.comfyui_url)

    try:
        image_content = await client.view_image(
            filename=image["filename"],
            file_type=image["type"],
            subfolder=image["subfolder"],
        )
    except httpx.HTTPError as error:
        raise HTTPException(
            status_code=502,
            detail=f"Nao foi possivel baixar imagem gerada: {error}",
        ) from error

    try:
        asset = save_generated_image_asset(
            project_id=project_id,
            image_filename=image["filename"],
            image_content=image_content["content"],
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            prompt_id=generation["prompt_id"],
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "project_id": project_id,
        "asset": asset,
    }


@app.post("/projects/{project_id}/generate-remote-image-asset")
async def generate_remote_project_image_asset(
    project_id: str,
    request: GenerateProjectImageAssetRequest,
) -> dict:
    filename_prefix = f"LiveRig_{project_id.replace('-', '_')}"
    generation = await comfyui_generate_image_and_wait(
        GenerateImageRequest(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            filename_prefix=filename_prefix,
        )
    )

    image = generation["image"]

    try:
        asset = save_remote_generated_image_asset(
            project_id=project_id,
            image_filename=image["filename"],
            image_type=image["type"],
            image_subfolder=image["subfolder"],
            preview_url=image["url"],
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            prompt_id=generation["prompt_id"],
        )
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return {
        "ok": True,
        "project_id": project_id,
        "asset": asset,
    }


@app.post("/api/studio/generate-image")
async def studio_generate_image(request: GenerateStudioImageRequest) -> dict:
    song_folder = _safe_folder_name(request.song_name)
    filename_prefix = f"{song_folder}/LiveRig_{song_folder}"
    generation = await comfyui_generate_image_and_wait(
        GenerateImageRequest(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            seed=request.seed,
            filename_prefix=filename_prefix,
        )
    )

    image = generation["image"]

    return {
        "ok": True,
        "song_name": request.song_name,
        "server_output_folder": f"~/homelab/compose/comfyui/output/{song_folder}",
        "comfyui_url": generation["comfyui_url"],
        "prompt_id": generation["prompt_id"],
        "image": image,
    }


def _first_history_image(history: dict, prompt_id: str) -> dict | None:
    prompt_history = history.get(prompt_id)
    if not isinstance(prompt_history, dict):
        return None

    outputs = prompt_history.get("outputs")
    if not isinstance(outputs, dict):
        return None

    for output in outputs.values():
        if not isinstance(output, dict):
            continue

        images = output.get("images")
        if isinstance(images, list) and images:
            first_image = images[0]
            if isinstance(first_image, dict):
                return first_image

    return None


def _image_url(filename: str, image_type: str, subfolder: str) -> str:
    url = f"/comfyui/image?filename={filename}&type={image_type}"
    if subfolder:
        url += f"&subfolder={subfolder}"
    return url


def _safe_folder_name(value: str) -> str:
    normalized = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    if not normalized:
        return "sem-nome"
    return normalized


STUDIO_DIR = Path(__file__).resolve().parent.parent / "studio"
app.mount("/studio", StaticFiles(directory=STUDIO_DIR, html=True), name="studio")
