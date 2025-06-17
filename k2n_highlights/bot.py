import logging
import uuid
import shutil
import requests
import os
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from .notion.notion_client import Client, process_html_file, continue_processing_after_confirmation
from .notion.user_state import AwaitingField, user_states, user_data_overrides
from .utils.imgur import upload_to_imgur
from dotenv import load_dotenv

TEMP_DIR = Path("./temp")

def prepare_temp_dir():
    """Ensure temp directory exists and is clean."""
    TEMP_DIR.mkdir(exist_ok=True)
    for item in TEMP_DIR.iterdir():
        if item.name == ".gitkeep":
            continue
        try:
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        except Exception as e:
            logging.warning(f"⚠️ Failed to delete {item}: {e}")

prepare_temp_dir()

logging.basicConfig(level=logging.INFO)

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        await update.message.reply_text("Please send an HTML file.")
        return

    file = await context.bot.get_file(update.message.document.file_id)
    filename = TEMP_DIR / f"{uuid.uuid4()}.html"
    await file.download_to_drive(filename)

    await update.message.reply_text("Processing file...")

    try:
        from .parser.html_parser import parse_html
        parsed = parse_html(str(filename))
        author = parsed["author"]
        title = parsed["title"]
        user_id = update.effective_chat.id

        user_data_overrides[user_id] = {
            "parsed": parsed,
            "file_path": filename
        }
        user_states[user_id] = AwaitingField.AUTHOR_CONFIRMATION

        keyboard = [
            [InlineKeyboardButton("✅ OK", callback_data="author_ok"),
             InlineKeyboardButton("✏️ Edit", callback_data="edit_author")]
        ]
        await update.message.reply_text(
            f"The book will be added with the author: {author}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logging.exception("❌ Error while processing the file")
        await update.message.reply_text("❌ Error while processing the file.")

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_chat.id
    state = user_states.get(user_id, AwaitingField.NONE)
    data = user_data_overrides.get(user_id)

    if not data:
        await query.edit_message_text("❌ No data found. Please send the file again.")
        return

    if query.data == "author_ok":
        user_states[user_id] = AwaitingField.TITLE_CONFIRMATION
        title = data["parsed"]["title"]
        keyboard = [
            [InlineKeyboardButton("✅ OK", callback_data="title_ok"),
             InlineKeyboardButton("✏️ Edit", callback_data="edit_title")]
        ]
        await query.edit_message_text(
            f"The book will be added with the title: {title}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == "edit_author":
        user_states[user_id] = AwaitingField.AUTHOR_CONFIRMATION
        current_author = data["parsed"]["author"]
        await query.edit_message_text(
            f"✏️ Enter the correct author:\n\nCurrent value: <code>{current_author}</code>",
            parse_mode="HTML"
        )
    elif query.data == "edit_title":
        user_states[user_id] = AwaitingField.TITLE_CONFIRMATION
        current_title = data["parsed"]["title"]
        await query.edit_message_text(
            f"✏️ Enter the correct book title:\n\nCurrent value: <code>{current_title}</code>",
            parse_mode="HTML"
        )
    elif query.data == "title_ok":
        await query.edit_message_text("🔄 Adding the book to Notion...")
        await continue_processing_after_confirmation(user_id, update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    state = user_states.get(user_id, AwaitingField.NONE)

    if state == AwaitingField.AUTHOR_CONFIRMATION:
        user_data_overrides[user_id]["parsed"]["author"] = update.message.text
        user_states[user_id] = AwaitingField.TITLE_CONFIRMATION
        title = user_data_overrides[user_id]["parsed"]["title"]
        keyboard = [
            [InlineKeyboardButton("✅ OK", callback_data="title_ok"),
             InlineKeyboardButton("✏️ Edit", callback_data="edit_title")]
        ]
        await update.message.reply_text(
            f"The book will be added with the title: {title}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif state == AwaitingField.TITLE_CONFIRMATION:
        user_data_overrides[user_id]["parsed"]["title"] = update.message.text
        user_states[user_id] = AwaitingField.NONE
        await update.message.reply_text("🔄 Adding the book to Notion...")
        await continue_processing_after_confirmation(user_id, update, context)
    else:
        await update.message.reply_text("🤖 Please send a Kindle HTML file or a cover image.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = context.user_data.get("pending_cover")
    if not pending:
        await update.message.reply_text("No book pending for cover. Please send the file first.")
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    byte_data = await file.download_as_bytearray()

    local_path = TEMP_DIR / f"cover_{uuid.uuid4().hex}.jpg"
    local_path.write_bytes(byte_data)

    try:
        photo_url = upload_to_imgur(str(local_path))
        notion = Client(auth=os.getenv("NOTION_API_KEY"))
        notion.pages.update(pending["page_id"], cover={
            "type": "external",
            "external": {"url": photo_url}
        })
        await update.message.reply_text("📸 Cover added to the book")
    except Exception as e:
        logging.exception("❌ Could not add an image to Notion")
        await update.message.reply_text("❌ An error occurred while adding an image.")
    finally:
        try:
            local_path.unlink()
        except Exception as e:
            logging.warning(f"⚠️ Could not delete temporary cover file: {e}")
        context.user_data["pending_cover"] = None

def main():
    load_dotenv()

    required_vars = ["TELEGRAM_BOT_TOKEN", "NOTION_API_KEY", "NOTION_DATABASE_ID"]
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        raise ValueError(f"Missing environment variables: {', '.join(missing)}. Please create and configure your .env file.")

    logging.info("Starting k2n-highlights bot...")

    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    app.run_polling()

if __name__ == "__main__":
    main()
