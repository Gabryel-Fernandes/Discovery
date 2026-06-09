import os
import httpx
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")


GRUPOS_MONITORADOS = [
    "golpesnainternet",
    "provas_das_fraudes",
]

client = TelegramClient("discovery_session", API_ID, API_HASH)


async def buscar_mensagens(grupo: str, limite: int = 20) -> list:
    try:
        entity = await client.get_entity(grupo)
        result = await client(GetHistoryRequest(
            peer=entity,
            limit=limite,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0,
        ))
        mensagens = []
        for msg in result.messages:
            if msg.message:
                mensagens.append({
                    "texto": msg.message,
                    "data": msg.date.isoformat(),
                    "grupo": grupo,
                })
        return mensagens
    except Exception as e:
        print(f"[Scraper] Erro ao buscar mensagens de {grupo}: {e}")
        return []


async def enviar_para_ia(texto: str, fonte: str) -> dict:
    async with httpx.AsyncClient(timeout=30.0) as http:
        response = await http.post(
            f"{BACKEND_URL}/analise-manual/texto",
            json={
                "text": texto,
                "use_sabia": True,
                "fonte": fonte,
            }
        )
        return response.json()


async def executar_scraping():
    print("[Scraper] Iniciando scraping do Telegram...")

    async with client:
        await client.start(phone=PHONE)

        for grupo in GRUPOS_MONITORADOS:
            print(f"[Scraper] Buscando mensagens de: {grupo}")
            mensagens = await buscar_mensagens(grupo)

            for msg in mensagens:
                print(f"[Scraper] Analisando mensagem de {msg['grupo']}...")
                resultado = await enviar_para_ia(msg["texto"], "telegram")

                if resultado:
                    print(f"[Scraper] Resultado: {resultado.get('data', {}).get('risk_level', 'N/A')}")

    print("[Scraper] Scraping concluído!")