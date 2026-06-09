import asyncio
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from scraper import executar_scraping

load_dotenv()

async def job_scraping():

    print("[Scheduler] Executando job de scraping...")
    try:
        await executar_scraping()
    except Exception as e:
        print(f"[Scheduler] Erro no job: {e}")

async def main():
    scheduler = AsyncIOScheduler()

    await job_scraping()

    scheduler.add_job(
        job_scraping,
        "interval",
        hours=1,
        id="scraping_telegram",
    )

    scheduler.start()
    print("[Scheduler] Agendador iniciado - rodando a cada hora")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("[Scheduler] Agendador encerrado")

if __name__ == "__main__":
    asyncio.run(main())