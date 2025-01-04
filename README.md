# telegram-bot

A telegram bot that scans for messages and automatically buys meme coins

# Requirements
- Python and venv installed
- A redis server
- Telegram API credentials

# Functionality

The bot authenticates a user and accepts inputs to define which channels and other users to listen to. After this it creates a thread that listens to the configured messages and replies with predefined messaged to other channels.

After a specified timeout the connection is killed and needs to be restarted.

# Running the bot
```
./start.sh
```

# Technical debt
- Tests. This application has no tests, a huge flaw, but it worked mostly as a proof of concept.
- Some lingering connections. Once the process starts the connection to the Redis server is not gracefully shutdown, which could cause leaks or problems when trying to exit gracefully.
  - In addition, the redis connection is not password protected as of now.
- Encryption: Telegram authentication tokens are not encrypted when stored on the Redis server, and that is not safe.
- Running on a serverless environment. Currently the program does not gracefully handle existing connections to be restarted in case the server restarts, which could lead to interruptions of service.

# Some limitations
- In order for the impersonation of users to work, the user needs to provide their own OTP, which is also not ideal, but as of now I could not find a way of authentication. Ideally in a full product there would be another way of authentication.
- Due to restrictions on whar users can do in a group, there is some limitation on the functionality a product like this could provide, specially regarding listing users and seeing who is on a chat.
