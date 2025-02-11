from pyromod import Client, Message
from pyrogram import types, filters
from pyrogram.handlers import MessageHandler
import asyncio 
from messageListener import Listener
from stringExtractor import Extractor

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

    async def taskFinishedHandler(self,):
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
        ONLY AVAILABLE WHEN ADMIN
        """
        members = []
        async for member in self.selectedChat.get_members():
            members.append(member)
        return members

    async def getUserByUsername(self, username):
        if not self.selectedChat:
            raise Exception("Need to have a chat to select admin")
        member = await self.client.get_chat_member(self.selectedChat.id, username)
        return member

    def setSelectedAdmin(self, selectedUser: types.ChatMember):
        """
        Sets users who the listener should listen to 
        """
        # Makes sure user exists
        self.selectedAdmins.append(selectedUser)

    