from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler
import asyncio
class Scanner():
    def __init__(self, app: Client):
        self.client = app
        self.selectedChatName : str = None
        self.selectedChat : types.Chat = None
        self.selectedAdmins : types.User = []
    def run(self):
        self.client.run()

    async def printAdminMessage(self, client: Client, message: types.Message):
        await self.client.send_message('me', message.text)

    async def getAvailableChatNames(self) -> types.Dialog:
        dialogs = []
        async for dialog in self.client.get_dialogs():
            dialogs.append(dialog)
        return dialogs
    
    async def setSelectedChat(self, selectedChatId):
        self.selectedChat = await self.client.get_chat(selectedChatId)

    async def getAvailableAdmins(self):
        members = []
        async for member in self.selectedChat.get_members():
            members.append(member)
        return members

    async def setSelectedAdmin(self, selectedAdminId):
        # Makes sure user exists
        admin_user : types.ChatMember = await self.selectedChat.get_member(selectedAdminId)
        self.selectedAdmins.append(admin_user)
        my_handler = MessageHandler(self.printAdminMessage, filters.group & filters.user(selectedAdminId) & ~filters.bot)
        self.client.add_handler(my_handler)



    