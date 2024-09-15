from pyrogram import Client, types, filters
from pyrogram.handlers import MessageHandler
import asyncio 
from messageListener import Listener
from stringExtractor import Extractor

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

        # Who the message will be sent to
        self.selectedDestinationChat : types.Chat = None
        # How will the message be sent
        self.destinationFormat : str = "{token}"
        # Message format that will be used to filter and selecte messages
        # Must use regex format to extract token
        self.stringExtractor : Extractor = Extractor()

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

    async def redirectMessage(self, client: Client, message: types.Message):
        # Checks if token exists
        token = self.stringExtractor.extractToken(message.text)
        if not token:
            print("Message did not match correct pattern")
            return

        await self.client.send_message(self.selectedDestinationChat.id, self.destinationFormat.format(**{"token": token}))

    def getSocketDuration(self):
        """
        Returns duration in seconds
        """
        return 60
    
    def startListening(self):
        if self.runningListener or self.runningTask:
            raise Exception("Can't initiate more than one lister")
        
        self.runningListener = Listener(
            self.client,
            self.selectedAdmins,
            self.redirectMessage,
            self.taskFinishedHandler,
            self.getSocketDuration()
        )
        self.runningTask = self.taskGroup.create_task(self.runningListener.run())

    async def getAvailableContacts(self):  
        """
        Gets the names of contacts with chats
        """
        contacts = []
        async for contact in self.client.get_contacts():
            contacts.append(contact)
        return contacts
    async def getAvailableGroups(self) -> types.Dialog:
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

    async def setDestinationChat(self, selectedChatId):
        """
        Sets a specific chat to send messages to
        """
        if selectedChatId == self.selectedChat.id:
            raise Exception("Destination chat can't be the same as origin chat")
        
        self.selectedDestinationChat = await self.client.get_chat(selectedChatId)

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



    