import os
import asyncio
from pyrogram import Client, enums, idle
from dotenv import load_dotenv
from InquirerPy import prompt_async, separator
from scanner import Scanner

# Load environment variables from .env file
load_dotenv()

api_id = os.getenv('TELEGRAM_API_ID')
api_key = os.getenv('TELEGRAM_API_KEY')

class ScannerCLI:
    def __init__(self, scanner: Scanner):
        self.scanner = scanner


    async def list_chats(self):
        dialogs = await self.scanner.getAvailableGroups()
        chat_choices = [{'name': dialog.chat.title or dialog.chat.first_name, 'value': dialog.chat.id} for dialog in dialogs if dialog.chat.type == enums.ChatType.GROUP]
        if not chat_choices:
            await prompt_async("No groups found")
            return
        
        questions = [
            {
                'type': 'list',
                'name': 'chat',
                'message': 'Select a chat:',
                'choices': chat_choices
            }
        ]
        answers = await prompt_async(questions)
        chat_id = answers['chat']
        return chat_id
    
    async def select_chat(self):
        selected_chat = await self.list_chats()
        await self.scanner.setSelectedChat(selected_chat)
        return selected_chat
    
    async def list_destination_chats(self):
        dialogs = await self.scanner.getAvailableGroups()
        chat_choices = [{'name': dialog.chat.title or dialog.chat.first_name, 'value': dialog.chat.id} for dialog in dialogs]
        if not chat_choices:
            await prompt_async("No groups found")
            return
        
        questions = [
            {
                'type': 'list',
                'name': 'chat',
                'message': 'Select a chat:',
                'choices': chat_choices
            }
        ]
        answers = await prompt_async(questions)
        chat_id = answers['chat']
        return chat_id

    async def select_destination_chat(self):
        selected_chat = await self.list_destination_chats()
        await self.scanner.setDestinationChat(selected_chat)
        return selected_chat

    async def list_admins(self):
        admins = await self.scanner.getAvailableAdmins()
        admin_choices = [{'name': admin.user.first_name, 'value': admin.user.id} for admin in admins]
        questions = [
            {
                'type': 'list',
                'name': 'admin',
                'message': 'Select an admin:',
                'choices': admin_choices
            }
        ]
        answers = await prompt_async(questions)
        return answers['admin']

    async def select_admin(self):
        selected_admin = await self.list_admins()
        await self.scanner.setSelectedAdmin(selected_admin)

    async def run(self):
        while True:
            try:
                questions = [
                    {
                        'type': 'list',
                        'name': 'option',
                        'message': 'Choose an option:',
                        'choices': [
                            'Select Chat',
                            'Select Destination Chat',
                            'Start Running',
                            separator.Separator(),
                            'Exit'
                        ]
                    }
                ]
                answer = await prompt_async(questions)
                option = answer['option']

                if option == 'Select Chat':
                    await self.select_chat()
                    await self.select_admin()
                if option == 'Select Destination Chat':
                    await self.select_destination_chat()
                elif option == "Start Running":
                    self.scanner.startListening()
                elif option == 'Exit':
                    print("Exiting...")
                    break
            except Exception as e:
                print("ERROR: ", e)

async def main():
    async with Client("my_account", api_id, api_key) as app:
        async with asyncio.TaskGroup() as taskGroup:
            scanner = Scanner(app, taskGroup)
            cli = ScannerCLI(scanner)
            await cli.run()  # Run the CLI
        

if __name__ == "__main__":
    asyncio.run(main())