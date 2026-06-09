import httpx
import os

IA_API_URL = os.getenv("IA_API_URL", "http://ia:8001")

async def analisar_texto(text: str, use_sabia: bool = False, mode: str = "completa") -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{IA_API_URL}/api/analyze",
            json={
                "text": text,
                "use_sabia": use_sabia,
                "mode": mode,
            }
        )
        response.raise_for_status()
        return response.json()

async def analisar_url(url: str, use_sabia: bool = False) -> dict:
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{IA_API_URL}/api/analyze/url",
            json={
                "url": url,
                "use_sabia": use_sabia,
            }
        )
        response.raise_for_status()
        return response.json()