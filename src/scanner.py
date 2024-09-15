from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler
import asyncio 
from messageListener import Listener

# Once set to start, then launch a new process? Or maybe just return the request?
#   - Set listener -> Maybe use filters?
#   - Find a way to check if it ever logged out?
#   - Set a limit time to when the socket should stop (initially 1h)

class Scanner():
    def __init__(self, app: Client, tg: asyncio.TaskGroup):
        # The telegram user client
        self.client = app

        # Selected chat to be listened
        self.selectedChat : types.Chat = None
        # Admins to listen to
        self.selectedAdmins : types.ChatMember = []


        self.taskGroup = tg
        self.runningListener = None
        self.runningTask = None
    
    def run(self):
        self.client.run()

    async def taskFinishedHandler(self,):
        print("Called this")
        self.runningTask = None
        self.runningListener = None
        await self.client.stop()

    async def printAdminMessage(self, client: Client, message: types.Message):
        await self.client.send_message('me', message.text)

    def getSocketDuration(self):
        """
        Returns duration in seconds
        """
        return 10
    
    def startListening(self):
        if self.runningListener or self.runningTask:
            raise Exception("Can't initiate more than one lister")
        
        self.runningListener = Listener(
            self.client,
            self.selectedAdmins,
            self.printAdminMessage,
            self.taskFinishedHandler,
            self.getSocketDuration()
        )
        self.runningTask = self.taskGroup.create_task(self.runningListener.run())

    async def getAvailableChatNames(self) -> types.Dialog:
        """
        Gets the names of the chat names a user can listen to
        """
        dialogs = []
        async for dialog in self.client.get_dialogs():
            dialogs.append(dialog)
        return dialogs
    
    async def setSelectedChat(self, selectedChatId):
        """
        Sets a specific chat to be listened
        """
        self.selectedChat = await self.client.get_chat(selectedChatId)

    async def getAvailableAdmins(self):
        """
        Gets the users from a specific chat
        """
        members = []
        async for member in self.selectedChat.get_members():
            members.append(member)
        return members

    async def setSelectedAdmin(self, selectedAdminId):
        """
        Sets users who the listener should listen to 
        """
        # Makes sure user exists
        admin_user : types.ChatMember = await self.selectedChat.get_member(selectedAdminId)
        self.selectedAdmins.append(admin_user)



    