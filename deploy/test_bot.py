#!/usr/bin/env python3
"""
Simple test bot for python-telegram-bot v13.15
"""
import os
import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('TestBot')

class TestBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_API_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_API_TOKEN environment variable not set")
        
        # Create updater and dispatcher
        self.updater = Updater(self.bot_token)
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self.register_handlers()
    
    def register_handlers(self):
        """Register command and message handlers"""
        # Command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("photo", self.photo_command))
        
        # Message handlers - including photo handler
        self.dispatcher.add_handler(MessageHandler(filters.PHOTO, self.photo_handler))
        self.dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler))

    def start_command(self, update: Update, context: CallbackContext):
        """Handle /start command"""
        update.message.reply_text(
            "🤖 *Test Bot* is online!\n\n"
            "This is a simple test bot to verify functionality.\n"
            "Type /help for available commands.",
            parse_mode=ParseMode.MARKDOWN
        )

    def help_command(self, update: Update, context: CallbackContext):
        """Handle /help command"""
        help_text = """
🤖 *Test Bot - Help*

*Available Commands:*
• /start - Start the bot
• /help - Show this help message
• /photo - Test photo handling

You can also send a photo to test the photo handler.
"""
        update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    def photo_command(self, update: Update, context: CallbackContext):
        """Handle /photo command"""
        update.message.reply_text(
            "Please send me a photo to test the photo handler.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def photo_handler(self, update: Update, context: CallbackContext):
        """Handle photo messages"""
        # Log that we received a photo
        logger.info("Received photo from user %s", update.effective_user.id)
        
        # Get the photo file_id (largest size)
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Reply with confirmation and file_id
        update.message.reply_text(
            f"✅ Photo received!\n\nFile ID: `{file_id}`\n\nThis confirms the photo handler is working correctly.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def text_handler(self, update: Update, context: CallbackContext):
        """Handle text messages"""
        update.message.reply_text(
            f"You said: {update.message.text}\n\nSend a photo to test the photo handler.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def run(self):
        """Run the bot"""
        logger.info("Starting bot")
        # Start the Bot
        self.updater.start_polling()
        logger.info("Bot is running!")
        
        # Run the bot until you press Ctrl-C
        self.updater.idle()

def main():
    """Main function"""
    bot = TestBot()
    bot.run()

if __name__ == "__main__":
    main()