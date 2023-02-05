from telegram_bot import poll_telegram
import time

while True:
    poll_telegram()
    time.sleep(2)