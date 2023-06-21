from telegram_poll import poll_telegram
import time

while True:
    poll_telegram()
    time.sleep(2)