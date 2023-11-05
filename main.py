from telegram_poll import poll_telegram
from scrape import *
import time
import threading
import schedule

def daily_scrape():
    ''' Helper function which calls scrape function for daily schedule function'''
    scrape(scrape_interval=5, scrape_duration=1, timezone=india)

def daily_schedule():
    '''Creates a schedule which runs Mon to Fri @9.47 AM, 10.02 AM & 11.02 AM IST'''

    schedule.every().monday.at("09:47").do(daily_scrape)
    schedule.every().tuesday.at("09:47").do(daily_scrape)
    schedule.every().wednesday.at("09:47").do(daily_scrape)
    schedule.every().thursday.at("09:47").do(daily_scrape)
    schedule.every().friday.at("09:47").do(daily_scrape)

    schedule.every().monday.at("10:02").do(daily_scrape)
    schedule.every().tuesday.at("10:02").do(daily_scrape)
    schedule.every().wednesday.at("10:02").do(daily_scrape)
    schedule.every().thursday.at("10:02").do(daily_scrape)
    schedule.every().friday.at("10:02").do(daily_scrape)

    schedule.every().monday.at("11:02").do(daily_scrape)
    schedule.every().tuesday.at("11:02").do(daily_scrape)
    schedule.every().wednesday.at("11:02").do(daily_scrape)
    schedule.every().thursday.at("11:02").do(daily_scrape)
    schedule.every().friday.at("11:02").do(daily_scrape)

    while True:
        schedule.run_pending()
        time.sleep(1)

periodic_thread = threading.Thread(target=daily_schedule)
periodic_thread.daemon = True
periodic_thread.start()

while True:
    poll_telegram()
    time.sleep(2)
