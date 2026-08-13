from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.messages import MENSAJE_AYUDA


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(MENSAJE_AYUDA)