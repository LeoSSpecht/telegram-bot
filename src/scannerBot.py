import os
import asyncio
from pyromod import Client, Message, Chat
from pyrogram import filters, idle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, User
from dotenv import load_dotenv
from scanner import Scanner
from userSession import UserSession
from typing import Dict


# Load environment variables
load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_key = os.getenv('TELEGRAM_API_KEY')
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')

app = Client("apollo_scanner_bot", api_id=api_id, api_hash=api_key, bot_token=bot_token)

class ScannerBot:
    def __init__(self, bot_client : Client, task_group: asyncio.TaskGroup):
        self.bot_client = bot_client
        self.user_sessions : Dict[str, UserSession] = {}
        self.task_group = task_group
        
    async def handle_start(self, message: Message):
        await self.bot_client.send_message(message.chat.id, "Welcome to the Scanner Bot! Use /auth to authenticate.")
    
    async def clear_menu(self, message: Message):
        await self.bot_client.send_message(message.chat.id, "Choose an option:", reply_markup=None)

    async def display_menu(self, message: Message):
        """Displays the menu options using InlineKeyboardMarkup."""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Select Chat", callback_data="select_chat")],
            [InlineKeyboardButton("Select Destination Chat", callback_data="select_destination_chat")],
            [InlineKeyboardButton("Start Scanner", callback_data="start_scanner")],
            [InlineKeyboardButton("Exit", callback_data="exit")]
        ])
        await self.bot_client.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)

    async def handle_menu_callback(self, client: Client, callback_query: CallbackQuery):
        """Handles button clicks from InlineKeyboardMarkup."""
        data = callback_query.data
        user = callback_query.from_user
        message = callback_query.message

        if data == "select_chat":
            await self.select_chat(user, message)
        elif data == "select_destination_chat":
            await self.select_destination_chat(message)
        elif data == "start_scanner":
            await self.start_scanner(message)
        elif data == "exit":
            await self.bot_client.send_message(message.chat.id, "Exiting setup.")
            await self.bot_client.answer_callback_query(callback_query.id, text="Exited.")
            return
        
        # After each action, display the menu again (unless exit)
        await self.display_menu(message)

    async def handle_setup(self, message: Message):
        await self.display_menu(message)

    async def handle_auth(self, message: Message):
        user = message.from_user
        print(user.id)
        self.user_sessions[user.id] = UserSession(user.id, self.bot_client, self.task_group)
        await self.user_sessions[user.id].start_auth(message)
    
    # Select chat
    async def select_chat(self, user: User, message: Message):
        scanner = self.get_user_scanner(user.id)
        dialogs = await scanner.getAvailableGroups()
        chat_choices = [{'name': dialog.chat.title or dialog.chat.first_name, 'value': str(dialog.chat.id)} for dialog in dialogs]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(chat["name"], callback_data=chat["value"])] for chat in chat_choices
        ])
        await self.bot_client.send_message(message.chat.id, "Choose a chat to listen to:", reply_markup=keyboard)

    def get_user_scanner(self, user_id) -> Scanner:
        return self.user_sessions[user_id].scanner

# Initialize the scanner and bot logic
async def main():
    # Initialize bot client
    async with asyncio.TaskGroup() as taskGroup:
        async with app:
            bot = ScannerBot(app, taskGroup)

            # Register bot command handlers
            @app.on_message(filters.command("start"))
            async def start_command_handler(client: Client, message: Message):
                await bot.handle_start(message)

            @app.on_message(filters.command("auth"))
            async def auth_command_handler(client: Client, message: Message):
                await bot.handle_auth(message)

            @app.on_message(filters.command("setup"))
            async def setup_command_handler(client: Client, message: Message):
                await bot.handle_setup(message)

            @app.on_callback_query()
            async def callback_query_handler(client: Client, callback_query):
                await bot.handle_menu_callback(client, callback_query)
            await idle()

if __name__ == "__main__":
    app.run(main())
