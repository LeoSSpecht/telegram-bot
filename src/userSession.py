import os
import asyncio
from pyromod import Client, Message, Chat
from pyrogram import filters, enums
from dotenv import load_dotenv
from scanner import Scanner

# Load environment variables
load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_key = os.getenv('TELEGRAM_API_KEY')

user_sessions = {}

class UserSession:
    def __init__(self, user_id, bot_client: Client, taskGroup: asyncio.TaskGroup):
        self.user_id = user_id
        self.taskGroup = taskGroup
        self.bot_client = bot_client
        self.phone_number = None
        self.telegram_client = None
        self.scanner = None
    
    async def start_auth(self, message: Message):
        """
        Takes a received /start message a checks if user is authenticated
        """
        chat : Chat = message.chat
        if self.user_id in user_sessions:
            self.telegram_client = Client(self.user_id, api_id, api_key, in_memory=True, session_string=user_sessions[self.user_id])
            if await self.telegram_client.connect():
                await message.reply("Authenticated successfully!")
                return

        
        # Start the Pyrogram client for the user session
        self.telegram_client = Client(self.user_id, api_id, api_key, in_memory=True)
        await self.telegram_client.connect()

        # Ask for phone number
        response = await chat.ask("Please provide your phone number (with country code, e.g., +1XXXXXXXXXX):")
        self.phone_number = response.text

        # Send authentication code request
        try:
            phone_hash = (await self.telegram_client.send_code(self.phone_number)).phone_code_hash
            code_response = await chat.ask("A Telegram code has been sent to your phone. Please enter the code:")
            code = code_response.text[1:]
        except Exception as e:
            self.telegram_client = None
            await message.reply(f"Error sending code: {e}")
            return        
        
        # Complete authentication
        try:
            auth = await self.telegram_client.sign_in(self.phone_number, phone_hash, code)
            auth_token = await self.telegram_client.export_session_string()
            await self.telegram_client.initialize()
            user_sessions[self.user_id] = auth_token
            self.scanner = Scanner(self.telegram_client, self.taskGroup)
            await message.reply("Authenticated successfully!")
        except Exception as e:
            self.telegram_client = None
            await message.reply(f"Error authenticating: {e}")
            return

    async def send_message_as_user(self, message, chat_id, text):
        if self.telegram_client:
            try:
                await self.telegram_client.send_message(chat_id, text)
                await message.reply(f"Message sent to chat {chat_id}: {text}")
            except Exception as e:
                await message.reply(f"Error sending message: {e}")
        else:
            await message.reply("You need to authenticate first using /auth")