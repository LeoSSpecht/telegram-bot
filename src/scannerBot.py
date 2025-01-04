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
            [InlineKeyboardButton("Select Chat", callback_data="menu_input-select_chat")],
            [InlineKeyboardButton("Select Destination Chat", callback_data="menu_input-select_destination_chat")],
            [InlineKeyboardButton("Start Scanner", callback_data="menu_input-start_scanner")],
        ])
        await self.bot_client.send_message(message.chat.id, "Choose an option:", reply_markup=keyboard)

    async def handle_menu_callback(self, client: Client, callback_query: CallbackQuery):
        """Handles button clicks from InlineKeyboardMarkup."""
        data = callback_query.data

        data_key, data_value = data.split("-", maxsplit=1)
        user = callback_query.from_user
        message = callback_query.message

        if data_key == "menu_input":
            if data_value == "select_chat":
                await self.show_select_chat_options(user, message)
            elif data_value == "select_destination_chat":
                await self.show_destination_chat_options(user, message)
            elif data_value == "start_scanner":
                await self.run_user(user)
        if data_key == "select_chat_answer":
            await self.select_chat(user, data_value)
            await self.show_select_admin_options(user, message)

        if data_key == "select_destination_answer":
            await self.select_destination_chat(user, data_value)


    async def handle_setup(self, message: Message):
        await self.display_menu(message)

    async def handle_auth(self, message: Message):
        user = message.from_user
        self.user_sessions[user.id] = UserSession(user.id, self.bot_client, self.task_group)
        await self.user_sessions[user.id].start_auth(message)

    async def run_user(self, user: User):
        scanner = self.get_user_scanner(user.id)
        scanner.startListening()

    # Destination chat
    async def show_destination_chat_options(self, user: User, message: Message):
        scanner = self.get_user_scanner(user.id)
        dialogs = await scanner.getAvailableGroups()
        chat_choices = [{'name': dialog.chat.title or dialog.chat.first_name, 'value': str(dialog.chat.id)} for dialog in dialogs]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(chat["name"], callback_data='select_destination_answer-' + chat["value"])] for chat in chat_choices
        ])
        await self.bot_client.send_message(message.chat.id, "Choose a chat to send to:", reply_markup=keyboard)

    async def select_destination_chat(self, user, chat_id):
        scanner = self.get_user_scanner(user.id)
        await scanner.setDestinationChat(chat_id) 

    # Select chat
    async def show_select_chat_options(self, user: User, message: Message):
        scanner = self.get_user_scanner(user.id)
        dialogs = await scanner.getAvailableGroups()
        chat_choices = [{'name': dialog.chat.title or dialog.chat.first_name, 'value': str(dialog.chat.id)} for dialog in dialogs]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(chat["name"], callback_data='select_chat_answer-' + chat["value"])] for chat in chat_choices
        ])
        await self.bot_client.send_message(message.chat.id, "Choose a chat to listen to:", reply_markup=keyboard)

    async def select_chat(self, user, chat_id):
        scanner = self.get_user_scanner(user.id)
        await scanner.setSelectedChat(chat_id)

    async def show_select_admin_options(self, user: User, message: Message):
        scanner = self.get_user_scanner(user.id)
        chat = message.chat
        admin_username = await chat.ask("Please enter the telegram username of the user you want to follow")
        admin_user = await scanner.getUserByUsername(admin_username.text)
        scanner.setSelectedAdmin(admin_user)
        await self.display_menu(message)

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
