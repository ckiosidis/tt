"""
 talky Utils
"""
__version__ = "4.4.0"


import asyncio

from apprise import Apprise, NotifyFormat
from iamlistening import Listener

from tt.config import logger, settings
from tt.plugins.plugin_manager import PluginManager


async def send_notification(msg):
    """
    💬 Notification via Apprise 
    """
    aobj = Apprise()
    if settings.apprise_api_endpoint:
        aobj.add(settings.apprise_api_endpoint)
    elif settings.apprise_config:
        aobj.add(settings.apprise_config)
    elif settings.apprise_url:
        aobj.add(settings.apprise_url)
    msg_format = settings.apprise_format or NotifyFormat.MARKDOWN
    await aobj.async_notify(
        body=msg,
        body_format=msg_format)


async def start_plugins(plugin_manager):
    """
    Start all plugins.
    """
    if settings.plugin_enabled:
        plugin_manager.load_plugins()
        loop = asyncio.get_running_loop()
        loop.create_task(plugin_manager.start_all_plugins())

 
async def start_bot(listener, plugin_manager):
    """
    Listen to the message in the bot channel
    and dispatch to plugins
    """
    await listener.start()
    await start_plugins(plugin_manager)
    while True:
        try:
            msg = await listener.handler.get_latest_message()
            if msg and settings.plugin_enabled:
                logger.debug("👂 listener: {}", msg)
                await plugin_manager.process_message(msg)
        except Exception as error:
            logger.error("👂 listener: {}", error)

        await asyncio.sleep(1)
 

async def run_bot(max_iterations=None):
    """
    Run the chat bot & the plugins.
    """
    listener = Listener()
    plugin_manager = PluginManager()
    await asyncio.gather(start_bot(listener, plugin_manager))