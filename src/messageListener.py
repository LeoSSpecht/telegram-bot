from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler
import asyncio
import time


class Listener():
    def __init__(self, client: Client, messageSenders: list[types.ChatMember], messageHandler, finishedHandler, timeout):
        self.client = client
        self.messageSenders = messageSenders
        self.messageHandler = messageHandler
        self.finishedHandler = finishedHandler
        self.timeout = timeout

        self.messageHandlers = []
    
    async def run(self):
        print("Starting to listen to messages")
        await self.setupListeners()

    def getSocketExpiration(self):
        return int(time.time()) + self.timeout
    
    async def setupListeners(self):
        for user in self.messageSenders:
            messageHandler = MessageHandler(self.messageHandler, filters.group & filters.user(user.user.id) & ~filters.bot)
            self.client.add_handler(messageHandler)
            self.messageHandlers.append(messageHandler)
        
        await self.waitToTimeout()

    def removeAllHandlers(self):
        for messageHandler in self.messageHandlers:
            self.client.remove_handler(messageHandler)

    async def waitToTimeout(self):
        # Run the event loop for the specified timeout
        await asyncio.sleep(self.timeout)
        print("Expired listener, finishing task")
        self.removeAllHandlers()
        await self.finishedHandler()

