from typing import Final
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

TOKEN: Final = "7556108080:AAFKS-enq33gcWIUPVzD3Wd418Ro8jKOxbI"
BOT_USERNAME: Final = '@PT_1ST_bot'

# Load lectures data from JSON file
with open("lectures.json", "r") as file:
    lectures_data = json.load(file)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Use /search to find lectures.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /search to find lectures.")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # List subjects
    keyboard = [[InlineKeyboardButton(subject, callback_data=subject) for subject in lectures_data.keys()]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a subject:", reply_markup=reply_markup)

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data

    # Check if it's a subject or lecture
    if callback_data in lectures_data:
        # List lectures for the selected subject
        keyboard = [[InlineKeyboardButton(f"Lecture {num}", callback_data=f"{callback_data}_{num}") for num in lectures_data[callback_data].keys()]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Select a lecture for {callback_data}:", reply_markup=reply_markup)

    # Check if it's a lecture selection
    elif "_" in callback_data:
        selected_subject, lecture_num = callback_data.split("_")
        
        if selected_subject in lectures_data and lecture_num in lectures_data[selected_subject]:
            lecture_path = lectures_data[selected_subject][lecture_num]
            await query.message.reply_document(document=open(lecture_path, 'rb'))
        else:
            await query.edit_message_text(text="Lecture not found.")

async def handle_lecture_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Extract subject and lecture number from callback data
    selected_data = query.data.split("_")
    selected_subject = selected_data[0]
    selected_lecture_num = selected_data[1]

    # Get the file path for the selected lecture
    lecture_file_path = lectures_data[selected_subject].get(selected_lecture_num)

    if lecture_file_path:
        # Send the lecture file as a PDF
        with open(lecture_file_path, "rb") as file:
            await query.message.reply_document(document=file, filename=f"{selected_subject}_Lecture_{selected_lecture_num}.pdf")
    else:
        await query.edit_message_text(text="Lecture not found.")

def main():
    application = Application.builder().token(TOKEN).build()

    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", search_command))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Handle lecture selection
    application.add_handler(CallbackQueryHandler(handle_lecture_selection, pattern=r'^[A-Z]+\_\d+$'))

    application.run_polling()

if __name__ == "__main__":
    main()
