"""
TalkyTrader 🪙🗿
"""

import http
import asyncio
import uvicorn
from fastapi import FastAPI, Request

from tt.config import settings, logger
from tt.utils import listener, notify, load_exchange, init_message, PluginManager


# ⛓️🤖🙊BOT
app = FastAPI(title="TALKYTRADER",)

@app.on_event("startup")
async def startup_event():
    """Starts the bot"""
    loop = asyncio.get_event_loop()
    try:
        plugin_manager = PluginManager()
        loop.create_task(listener())
        await load_exchange()
        plugin_manager.load_plugins("tt.plugins")
        await plugin_manager.start_all_plugins()

        logger.info("bot started successfully")
    except Exception as error:
        logger.error("bot startup failed: %s",error)


@app.on_event('shutdown')
async def shutdown_event():
    """fastapi shutdown"""
    logger.info("shutting down")
    uvicorn.keep_running = False


@app.get("/")
async def root():
    """fastapi root"""
    return await init_message()


@app.get("/health")
async def health_check():
    """fastapi health"""
    return await init_message()


@app.post("/webhook", status_code=http.HTTPStatus.ACCEPTED)
async def webhook(request: Request):
    payload = await request.body()
    print(payload)
    # if payload["key"] == settings.webhook_secret:
    return await notify(payload)

if __name__ == '__main__':
    """Launch TalkyTrader"""
    uvicorn.run(app, host=settings.host, port=int(settings.port))