import os
import asyncio
from pyromod import Client, Message, Chat
from pyrogram import filters, enums
from dotenv import load_dotenv
from scanner import Scanner
from cache import r

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
        self.is_authenticated = False
    
    def set_auth_token(self, auth_token):
        user_sessions[self.user_id] = auth_token
        r.set("auth-" + str(self.user_id), auth_token)

    async def set_auth_status(self, auth_token: str, message: Message):
        if not self.telegram_client:
            # TODO: Handle case where auth token is expired/wrong
            self.telegram_client = Client(self.user_id, api_id, api_key, in_memory=True, session_string=auth_token)
        if not self.telegram_client.is_connected:
            await self.telegram_client.connect()
        if not self.telegram_client.is_initialized:
            await self.telegram_client.initialize()
        
        self.set_auth_token(auth_token)
        self.scanner = Scanner(self.telegram_client, self.taskGroup)
        self.is_authenticated = True
        await message.reply(f"Authenticated successfully, use /setup to start")

    async def start_auth(self, message: Message):
        """
        Takes a received /start message a checks if user is authenticated
        """
        chat : Chat = message.chat
        if self.user_id in user_sessions:
            await self.set_auth_status(user_sessions[self.user_id], message)
            return

        cached_token = r.get('auth-'+str(self.user_id))
        if cached_token:
            token = str(cached_token, encoding='utf-8')
            await self.set_auth_status(token, message)
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
            await self.telegram_client.sign_in(self.phone_number, phone_hash, code)
            auth_token = await self.telegram_client.export_session_string()
            await self.set_auth_status(auth_token, message)
            return
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