import os
import logging
import json

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from cli.chatbot import initialize_agent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableBinding

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

ENVIRONMENT = "TEST"
TELEGRAM_TOKEN_KEY = f"TELEGRAM_{ENVIRONMENT}_BOT_TOKEN"
# Your Telegram bot token
TOKEN = os.environ.get(TELEGRAM_TOKEN_KEY)
if not TOKEN:
    raise ValueError(f"{TELEGRAM_BOT_TOKEN} environment variable not set.")

user_sessions = {}
user_storage = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""

    storage = dict()
    user_storage[update.effective_user.id] = storage
    agent_ctx = {
        "user_id": update.effective_user.id,
        "storage": storage
    }
    user_sessions[update.effective_user.id] = initialize_agent(agent_ctx)
    text = "Hello! I'm your friendly AI assistant. What can I help you with?"

    await update.message.reply_text(text)


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /status is issued."""

    user_id = update.effective_user.id
    if user_id not in user_sessions:
        await update.message.reply_text("No status for this user")
        return

    await update.message.reply_text(json.dumps(user_storage[user_id]))


async def handle_message(update: Update,
                         context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process incoming messages."""

    if update.effective_user.id not in user_sessions:
        await update.message.reply_text("Please type /start to begin.")
        return

    agent_executor, config = user_sessions.get(update.effective_user.id)
    user_input = update.message.text

    message = await update.message.reply_text("Thinking...")
    response_text = ""

    # Run agent with the user's input in chat mode
    for chunk in agent_executor.stream(
        {"messages": [HumanMessage(content=user_input)]}, config):

        content = None
        if "agent" in chunk:
            content = chunk["agent"]["messages"][0].content
        elif "tools" in chunk:
            content = None
            logging.info(f"tool: {chunk["tools"]["messages"][0].content}")

        if content:
            response_text += content
            await message.edit_text(response_text)


def main() -> None:
    """Start the Telegram bot."""
    application = ApplicationBuilder().token(TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()
