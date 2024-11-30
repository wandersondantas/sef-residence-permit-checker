# SEF Visa Renewal Checker

## Overview
Automated tool to check SEF visa renewal status and send Telegram notifications.

## Prerequisites
- GitHub Account
- Telegram Bot Token
- SEF Credentials

## Setup Instructions
1. Fork this repository
2. Go to repository Settings → Secrets and Variables → Actions
3. Add the following secrets:
   - `SEF_USERNAME`: Your SEF username
   - `SEF_PASSWORD`: Your SEF password
   - `SEF_RESIDENCY_NUMBER`: Your residency document number
   - `TELEGRAM_BOT_TOKEN`: Telegram bot token
   - `TELEGRAM_CHAT_ID`: Telegram chat ID to receive notifications

## How to Create Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow prompts to create bot
4. Copy bot token
5. Start a chat with your bot
6. Visit `https://api.telegram.org/bot<YourBOTToken>/getUpdates` to find your chat ID

## Workflow
- Runs once a day
- Checks SEF renewal page
- Sends Telegram alerts for errors
