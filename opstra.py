import requests, json
from prettytable import PrettyTable
import datetime, sys
from time import sleep
 
count_500 = 0

def return_table(rows, columns):
    tb = PrettyTable()
    tb.field_names = columns
    tb.add_rows(rows=rows)
    return tb

def pnl():
    portfolio = ['real', 'paper']
    columns = ['Portfolio', 'PNL', 'Time']
    rows = []
    for portfolio in portfolio:
        response = requests.get('https://opstra.definedge.com/api/strategybuilder/portfolio/{}&2c5eeef3-8dd0-4010-acad-081f80ed3309'.format(portfolio), cookies=cookies, headers=headers)
        if response.status_code==200:
            data  = json.loads(response.text)
            rows.append(
                    [
                        portfolio,
                        "{:.2f}".format(data['portfolioPNL']),
                        datetime.datetime.now().strftime("%H:%M:%S")
                    ]
                )
        else:
            return response
    return return_table(rows=rows, columns=columns)

def pcr(expiry):    #index - NIFTY, BANKNIFTY     expiry - DDMONYYYY e.g. 15SEP2022
    index = ['NIFTY', 'BANKNIFTY']
    columns = ['Index', 'Spot', 'Futures', 'Strike', 'Strike PCR', 'Total PCR', 'Time']
    rows = []
    for index in index:
        response = requests.get('https://opstra.definedge.com/api/openinterest/{}&{}'.format(index, expiry), cookies=cookies, headers=headers)
        if response.status_code==200:
            data  = json.loads(response.text)
            rows.append(
                    [
                        index, 
                        data['spotprice'], 
                        data['futuresprice'], 
                        data['spotstrike'], 
                        data['data'][data['spotstrikepos']]['PCR'], 
                        data['totalpcr'],
                        datetime.datetime.now().strftime("%H:%M:%S")
                    ]
                )
        else:
            return response
    return return_table(rows=rows, columns=columns)

def backtest(expiry, index, buy_time, sell_time):
    expiry_datetime = datetime.datetime.strptime(expiry + ' ' + buy_time, '%d%b%Y %I:%M%p')
    expiry_2 = expiry_datetime.strftime("%Y-%m-%d")  # format -> yyyy-mm-dd
    start_timestamp = int(expiry_datetime.timestamp())
    end_timestamp = int(datetime.datetime.strptime(expiry + ' ' + sell_time, '%d%b%Y %I:%M%p').timestamp())
    if index=='NIFTY':
        multiplier = 50
    else:
        multiplier = 100


    columns = ['Option', 'Entry Price', 'Entry Time', 'Exit Price', 'Exit Time', 'P&L']
    rows = []
    
    option_chain_url = 'https://opstra.definedge.com/api/optionsimulator/optionchain/{}&{}&{}'.format(start_timestamp, index, expiry)
    response = requests.get(option_chain_url, cookies=cookies, headers=headers)
    
    if response.status_code==200:
        data  = json.loads(response.text)
        spot = data['spotPrice']
        put_strike = (multiplier * round(spot/multiplier)) + (multiplier * 1)
        call_strike = (multiplier * round(spot/multiplier)) - (multiplier * 1)
        flag = 0
        global count_500

        for i in data['optionchaindata']:
            if flag==2:
                break
            if i['Strikes'] == put_strike:
                pe_buy = i['PutLTP']
                PutIV  = i['PutIV']
                flag += 1
            if i['Strikes'] == call_strike:
                ce_buy = i['CallLTP']
                CallIV  = i['CallIV']
                flag += 1
        if pe_buy + ce_buy > 260:
            count_500 += 1
            print("skipped : ", pe_buy + ce_buy, count_500)
            return []
    else:
        count_500 += 1
        print(response, count_500)
        return response
    
    
    #buy_put -- https://opstra.definedge.com/api/optionsimulator/payoff/NIFTY$+50x14000PEx25AUG2022x1.4x0x55.43$2022-08-25$0$0$0$1660621800 
    #buy_ce  -- https://opstra.definedge.com/api/optionsimulator/payoff/NIFTY$+50x14000PEx25AUG2022x1.4x0x55.43&+50x15500CEx25AUG2022x2291.8x0x0$2022-08-25$0$0$0$1660621800
    #           https://opstra.definedge.com/api/optionsimulator/payoff/NIFTY$+100x14400CEx25AUG2022x3390x0x0$2022-08-25$0$0$0$1660621800
    #           https://opstra.definedge.com/api/optionsimulator/payoff/NIFTY$+50x17750PEx25AUG2022x151.85x0x15.28&+50x17800CEx25AUG2022x167.55x0x15.12$2022-08-25$0$0$0$1660621800
    #           https://opstra.definedge.com/api/optionsimulator/payoff/NIFTY$+50x17750PEx25AUG2022x151.85x0x15.28&+50x17800CEx25AUG2022x167.55x0x15.12$2022-08-25$0$0$0$1660622700 
    simulator_url = 'https://opstra.definedge.com/api/optionsimulator/payoff/{}$+50x{}PEx{}x{}x0x{}&+50x{}CEx{}x{}x0x{}${}$0$0$0${}'.format(index, put_strike, expiry, pe_buy, PutIV, call_strike, expiry, ce_buy, CallIV, expiry_2, end_timestamp)
    response = requests.get(
                            simulator_url,
                            cookies=cookies, 
                            headers=headers
                            )
    
    if response.status_code==200:
        data  = json.loads(response.text)      # dict_keys(['maxloss', 'maxprofit', 'pnl', 'spotPrice', 'totalPNL'])
        for option in data['pnl'][:-1]:
            rows.append(
                [
                    option['Position'],
                    option['EntryPrice'],
                    datetime.datetime.fromtimestamp(start_timestamp).strftime('%Y-%m-%d %H:%M'),
                    option['CurrentPrice'],
                    datetime.datetime.fromtimestamp(end_timestamp).strftime('%Y-%m-%d %H:%M'),
                    option['P&L'],
                ]
            )
        rows.append(["",spot,"",data['spotPrice'],"Total PNL",data['totalPNL']])
    
    else:
        print(response)
    
    return rows

cookies = {
    'JSESSIONID': 'your-session-id',
    }

headers = {'<headers-here>'}

while True:
    f = open('pcr','a')
    #f.write(str(pnl()))
    f.write(str(pcr(expiry='13JUL2023')))
    f.close()
    sleep(300)
    
#expiry = sys.argv[1]
# weeks = 52*3
# response = requests.get(
#             'https://opstra.definedge.com/api/optionsimulator/simulatorexpiries',
#             cookies=cookies, 
#             headers=headers
#         )
# if response.status_code == 200:
#     bnf_profit = 0
#     nifty_profit = 0
#     expiries = response.text[1:-1].split(",")
#     for i in expiries[:weeks]:
#         result = backtest(expiry=i[1:-1], index='BANKNIFTY', buy_time='2:15PM', sell_time='3:15PM')
#         try:
#             bnf_profit += result[-1][-1]
#         except:
#             print(result)
#         print(i)
#         f = open('output','a')
#         f.write(str(return_table(rows=result, columns = ['Option', 'Entry Price', 'Entry Time', 'Exit Price', 'Exit Time', 'P&L'])))
#         f.close()
#         sleep(1)
#         # print(backtest(expiry=i[1:-1], index='BANKNIFTY', buy_time='9:30AM', sell_time='3:30PM'))
#         # x = backtest(expiry=i[1:-1], index='NIFTY', buy_time='9:20AM', sell_time='10:00AM')[-1][-1]
#         # y = backtest(expiry=i[1:-1], index='BANKNIFTY', buy_time='9:20AM', sell_time='10:00AM')[-1][-1]
#         # print(i, x, y)
#         # nifty_profit = nifty_profit + x
#         # bnf_profit   = bnf_profit + y
#         # print('----------------------------------------------------------------------',nifty_profit, bnf_profit)
#     f = open('output','a')
#     f.write("Total: " + str(bnf_profit))
#     f.write("Avg: " + str(bnf_profit/(weeks - count_500)))
#     f.close()
#     print(bnf_profit, bnf_profit/(weeks - count_500))
# else:
#     print(response)
