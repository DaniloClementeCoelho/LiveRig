import asyncio

import httpx


class ComfyUIClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def system_stats(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/system_stats")
            response.raise_for_status()
            return response.json()

    async def queue_prompt(self, workflow: dict) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/prompt",
                json={"prompt": workflow},
            )
            response.raise_for_status()
            return response.json()

    async def history(self, prompt_id: str) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/history/{prompt_id}")
            response.raise_for_status()
            return response.json()

    async def view_image(
        self,
        filename: str,
        file_type: str = "output",
        subfolder: str = "",
    ) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(
                f"{self.base_url}/view",
                params={
                    "filename": filename,
                    "type": file_type,
                    "subfolder": subfolder,
                },
            )
            response.raise_for_status()
            return {
                "content": response.content,
                "content_type": response.headers.get("content-type", "image/png"),
            }

    async def wait_for_history(
        self,
        prompt_id: str,
        timeout_seconds: int = 120,
        poll_interval_seconds: float = 1.0,
    ) -> dict:
        deadline = asyncio.get_running_loop().time() + timeout_seconds

        while asyncio.get_running_loop().time() < deadline:
            history = await self.history(prompt_id)
            prompt_history = history.get(prompt_id)

            if isinstance(prompt_history, dict):
                status = prompt_history.get("status")
                if isinstance(status, dict) and status.get("completed") is True:
                    return history

            await asyncio.sleep(poll_interval_seconds)

        raise TimeoutError(f"ComfyUI nao concluiu o prompt {prompt_id} em {timeout_seconds}s.")
