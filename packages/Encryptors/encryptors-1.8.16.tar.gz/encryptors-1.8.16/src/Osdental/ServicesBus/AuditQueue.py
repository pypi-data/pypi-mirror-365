import os
import asyncio
from typing import Dict
from dotenv import load_dotenv
from Osdental.ServicesBus.ServicesBus import ServicesBus
from Osdental.Shared.Logger import logger

load_dotenv(dotenv_path='.env', override=True)

class AuditFlowQueue:
    
    def __init__(self):
        self.queue = asyncio.Queue()
        self.service_bus = ServicesBus(os.getenv('CONNECTION_STRING'), os.getenv('QUEUE'))
        self.task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            msg = await self.queue.get()
            try:
                await self.service_bus.send_message(msg)
            except Exception as e:
                logger.error(f'Error sending audit message: {e}')
            finally:
                self.queue.task_done()

    async def enqueue(self, message: Dict[str, str]):
        await self.queue.put(message)

    async def close(self):
        """Ensure all messages are processed before closing"""
        await self.queue.join()
