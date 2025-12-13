# 🤖 Telegram Group Parser Bot

A Telegram bot for parsing members of Telegram groups using a user account via **Telethon**, with control through a Telegram bot interface.

The bot allows you to select a group, parse its members, and save the collected data to a file.

⚠️ This project is intended for educational and research purposes only.

## 🧠 Architecture
The project consists of two components:
- **Telethon Client** — operates on behalf of a Telegram user account
- **Telegram Bot (pyTelegramBotAPI)** — provides the control interface

> Group member data is retrieved exclusively via Telethon.  
> The Telegram Bot API is **not** used for parsing.

## 🚀 Features
- List available megagroups
- Parse members of a selected group
- Collect user data:
  - ID
  - username
  - full name
  - group name
  - phone number (if available)
- Save data to a CSV file
- Automatically send the file to the user via Telegram

## 📄 Data Format
Data is stored in `members.txt` (CSV format):

