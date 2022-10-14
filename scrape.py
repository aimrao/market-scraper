import requests
import json
import time
import math
import datetime
import os
from pytz import timezone
from prettytable import PrettyTable
from telegram_bot import send_to_telegram

def roundTime(dt=None, dateDelta=datetime.timedelta(minutes=1)):
    ''' Rounds down time to nearest 5 mins '''
    return dt.replace(hour=0, minute=0, second=0) + (math.ceil((dt - dt.replace(hour=0, minute=0, second=0)) / dateDelta) * dateDelta) - dateDelta

def parse_data(data, current_time, legend, trend):
    ''' Filters stocks which has high=open or low=open '''
    current_time = roundTime(current_time, datetime.timedelta(minutes=5)).strftime("%H:%M")
    flag = 1
    message = ''
    match legend:
        case 'NIFTY':
            message += "Top {} of Nifty @{}\n".format(trend, current_time)
        case 'BANKNIFTY':
            message += "Top {} of BNF @{}\n".format(trend, current_time)
        case 'FOSec':
            message += "Top {} of FnO @{}\n".format(trend, current_time)
    message += "----------------------------\n"    
    for i in data.rows:
        if i[-1] == 'Yes':
            flag = 0
            message += "Stock                {}\n".format(i[0])
            message += "LTP                   {}\n".format(i[4])
            message += "Open                {}\n".format(i[1])
            message += "Low                  {}\n".format(i[3])
            message += "High                 {}\n".format(i[2])
            message += "PrevClose       {}\n".format(i[5])
            message += "% Change       {}\n".format(i[6])
            message += "----------------------------\n"
    if flag:
        return
    return message

def process_data(trend, data, timezone):
    ''' Extracts data from the response and processes  it into the required format, also outputs the result to respective files '''
    if trend == 'gainers':
        check = 'low_price'
    else:
        check = 'high_price'

    for legend in ['NIFTY', 'FOSec', 'BANKNIFTY']:
        tb = PrettyTable()
        tb.field_names = ['Stock', 'Open Price', 'High Price', 'Low Price', 'LTP', 'Prev Close', '% Change', 'Traded Quantity (in lacs)', 'open_price = {}'.format(check)]
        rows = []

        for stock in data[legend]['data']:    #stock.keys --> ['legends', 'NIFTY', 'BANKNIFTY', 'NIFTYNEXT50', 'SecGtr20', 'SecLwr20', 'FOSec', 'allSec']
            rows.append(
                            [
                                stock['symbol'], 
                                stock['open_price'],
                                stock['high_price'],
                                stock['low_price'],
                                stock['ltp'],
                                stock['prev_price'],
                                stock['perChange'],
                                "{:.2f}".format(stock['trade_quantity']/100000),
                                ('Yes' if stock['open_price'] == stock[check] else "No")
                            ]
                        )
        tb.add_rows(rows=rows)
        f = open('{}/data/{}/{}_{}'.format(os.getcwd(), legend, datetime.datetime.now(timezone).strftime("%d-%m-%Y"), trend), 'a')
        current_time = datetime.datetime.now(timezone)
        f.write("Scrape time: {}\n".format(current_time.strftime("%H:%M")))
        send_to_telegram(parse_data(tb, current_time, legend, trend))
        f.write(str(tb) + '\n')
        f.close()
    
    return current_time


def scrape(scrape_interval, scrape_duration, timezone):
    ''' Scrapes top gainers/losers data from NSE Official Website '''

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'
    }

    url = "https://www.nseindia.com/api/live-analysis-variations?index="
    
    current_time = datetime.datetime.now(timezone)
    end_time = current_time.timestamp() + scrape_duration*60

    print("Scraping started at: {}".format(current_time.strftime("%H:%M")))

    while current_time.timestamp() < end_time:
        for trend in ['gainers', 'loosers']:
            count = 0 
            while True:
                response = requests.get(url+trend, headers=headers)
                if response.status_code != 200:
                    count += 1
                    if count < 6:
                        time.sleep(5)
                    else:
                        time.sleep(20)
                        count += 3
                    print("I am stuck in loop for {} seconds.".format(5*count))
                    continue
                else:
                    break
            
            data = json.loads(response.text)
            print("Scraping {}...".format(trend))
            current_time = process_data(data=data, trend=trend, timezone=timezone)
            time.sleep(5)
        
        print("Sleeping for {} minutes".format(scrape_interval))
        time.sleep(scrape_interval*60)
        

    print("Scraping finished at: {}".format(current_time.strftime("%H:%M")))
    
    return 0

# setting timezone to IST or GMT+5.30
india = timezone("Asia/Kolkata")

# scrape_interval and scrape_duration ( in minutes ) e.g. scrape_interval=5, scrape_duration=60 means "scrape every 5 mins for 60 minutes" 
scrape(scrape_interval=5, scrape_duration=90, timezone=india)       
