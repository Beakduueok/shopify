import telebot
import threading
import time

BOT_TOKEN = "8594926943:AAHjRBMFmcFKwHfpYVurO2h19DnWtafJrwE"
bot = telebot.TeleBot(BOT_TOKEN)

def delayed_delete(chat_id, message_id):
    time.sleep(10)
    try:
        bot.delete_message(chat_id, message_id)
        print(f"Deleted forwarded post {message_id}")
    except Exception as e:
        print("Delete failed:", e)

@bot.channel_post_handler(func=lambda message: True)
def handle_channel_post(message):
    try:
        # STRICT forward check (sirf forwarded hi)
        is_forwarded = (
            message.forward_from is not None or
            message.forward_from_chat is not None or
            message.forward_sender_name is not None
        )

        if is_forwarded:
            # Non-blocking delete
            t = threading.Thread(
                target=delayed_delete,
                args=(message.chat.id, message.message_id)
            )
            t.start()

    except Exception as e:
        print("Handler error:", e)

print("Bot running with advanced delayed delete...")
bot.infinity_polling()