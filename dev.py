# -*- coding: utf-8 -*-
import json
import csv
import requests
import pickle
from datetime import date
from bs4 import BeautifulSoup


def get_cookies():
    with open('FT.pkl', 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
    cookie = ""
    for i in cookies:
        if cookie == "":
            cookie = cookie+i['name']+"="+i['value']+";"
        else:
            cookie = cookie+" "+i['name']+"="+i['value']+";"
    return cookie


if __name__ == '__main__':
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '^\\^Google',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '^\\^Windows^\\^',
        'Upgrade-Insecure-Requests': '1',
        'Cookie': get_cookies(),
        # 'Cookie': "GZIP=1; spoor-id=bd01ebed-a1df-4a89-8495-cc618cb12167; _csrf=utfaYH-lYS84W0jVWVvgbZf_; FTSession=02B7GvQR-Ukg07Mi3hXKVEC20wAAAX74cAjJw8I.MEQCIFE2Rx9WuDZNtiBn21yKIMpGkL43OwC21xrNxnnlyw5KAiBpQf7_XJbVNP7WvpYmKN-_pNIKlnOUD3Tk7KCkFZCDqg; FTSession_s=02B7GvQR-Ukg07Mi3hXKVEC20wAAAX74cAjJw8I.MEUCIQDdY0iCsQcFgNlogLMdVrlfRy8d8l5D00g95pm4kY39GAIgCEpHb5iq186u1wAV228U_MkVbgcwA-BDxoNiLSrhiKY; FTLogin=beta; FTAllocation=607b1af4-11f9-4920-b322-de15ca5440b6; FTCookieConsentGDPR=true; __RequestVerificationToken_L2RhdGE1=4zqIvWTJkYIrSJ4OjW9FFdI1DzZsc-c4bnZFlozNoyjQ6WgnqBnctk_uxH7aU0TvmucByr0jRdgW1Ep5FiPnvUS6yxqnJNfIZiMrMUtxw501; FTConsent=behaviouraladsOnsite:on,cookiesOnsite:on,cookiesUseraccept:on,demographicadsOnsite:on,enhancementByemail:on,enhancementByfax:off,enhancementByphonecall:on,enhancementBypost:on,enhancementBysms:off,marketingByemail:on,marketingByfax:off,marketingByphonecall:on,marketingBypost:on,marketingBysms:off,membergetmemberByemail:off,programmaticadsOnsite:on,recommendedcontentOnsite:on; 1751_0=BFA1FFB42ACF36477C552016B779C7853EA97DB5AA77A11610AD6345E9607241",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-User': '?1',
        'Sec-Fetch-Dest': 'document',
        'Referer': f'https://markets.ft.com/data/portfolio/watchlist?c={id}',
        'Accept-Language': 'en-US,en;q=0.9',
    }
    req = requests.get(
        "https://markets.ft.com/data/portfolio/dashboard", headers=headers).text
    soup = BeautifulSoup(req, "lxml")

    print('--> Parsed soup...')

    watchlists = {}
    for watchlist in soup.find_all('td', {"class": "mod-watchlist-name"}):
        watchlists[watchlist.find("a")['href']] = watchlist.find("a").text
    # print(watchlists)
    print('--> Got watchlist...')

    funds = {}
    for index, watchlist in enumerate(watchlists):
        # if index == 5:  # delete
        #     break  # delete
        print('                     ', end='')
        print(f'--- {round((index+1)/len(watchlists) * 100, 2)} % ---', end='\r')
        reqw = requests.get("https://markets.ft.com" +
                            watchlist, headers=headers).text
        soup = BeautifulSoup(reqw, "lxml")
        for fund in soup.find_all("tr", {"class": "mod-ui-table-action-menu-row mod-ui-table-action-menu-row--with-button"}):
            data = json.loads(fund['data-mod-symbol-args'])
            try:
                if data['group'] != "Equity" and fund.find("a")['href'] not in funds:
                    funds[data['lotName']+"/"+watchlists[watchlist]
                          ] = fund.find("a")['href']
            except:
                pass

    print('--> Created fund dictionary...')

    # Getting Summary.csv
    f = open('Summary.csv', 'w', newline='', encoding='utf-8')
    writer = csv.writer(f)
    writer.writerow(['Asset Name', 'FT URL', 'Market Cap', 'Investment Style',
                    'Launch date', 'Price currency', 'Manager & start date', 'Fund size', 'Ongoing charge', 'UK ISA', 'Avail In'])

    # Getting summary
    for index, fund in enumerate(funds):
        # if index == 5:  # delete
        #     break  # delete
        print(fund, '- summary',
              f'{round((index+1)/len(funds)*100,2)} % of {len(funds)}')

        # r+=1
        # if r == 11:
        #     break
        url = "https://markets.ft.com" + \
            funds[fund].replace("summary", 'summary')
        reqf = requests.get(url, headers=headers).text
        soup = BeautifulSoup(reqf, "lxml")
        row = [fund, url, '', '', '', '', '', '', '', '','']
        trs = soup.find_all('tr')

        for tr in trs:
            if 'market cap' in str(tr).lower():
                td = tr.find('td')
                row[2] = td.text.split(':')[1].replace(
                    'Investment Style', '').strip()  # Market Cap
                # Investment Style
                row[3] = td.text.split(':')[2].strip()

            if 'launch date' in str(tr).lower():
                td = tr.find('td')
                row[4] = td.text.strip()
            if 'price currency' in str(tr).lower():
                td = tr.find('td')
                row[5] = td.text.strip()
            if 'Manager &amp; start date' in str(tr):
                td = tr.find('td')
                row[6] = td.text.strip()
            if 'fund size' in str(tr).lower():
                td = tr.find('td')
                if td.text:
                    val = td.text.replace('GBP', '').strip()
                row[7] = val
            if 'Ongoing charge' in str(tr):
                td = tr.find('td')
                row[8] = td.text
            if 'UK ISA' in str(tr):
                td = tr.find('td')
                row[9] = td.text
            if 'Available for sale' in str(tr):
                td = tr.find('td')
                row[10] = td.text

        writer.writerow(row)
        f.flush()
    f.close()
    # print('quit()')  # delete
    # quit()  # delete

    # Getting Risk.csv
    f = open('Risk.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['Asset Name', 'Fund ID', 'FT URL', 'Watchlist', 'Benchmark', '1 Yr Alpha Fund', '1 Yr Alpha Cat. Av', '1 Yr Beta Fund ', '1 Yr Beta Cat. Av', '1 Yr IR Fund ', '1 Yr IR Cat. Av', '1 Yr R2 Fund', '1 Yr R2 Cat. Av', '1 Yr Sharpe Fund', '1 Yr Sharpe Cat. Av', '1 Yr SD Fund', '1 Yr SD Cat. Av', '3 Yr Alpha Fund', '3 Yr Alpha Cat. Av', '3 Yr Beta Fund ', '3 Yr Beta Cat. Av',
                    '3 Yr IR Fund ', '3 Yr IR Cat. Av', '3 Yr R2 Fund', '3 Yr R2 Cat. Av', '3 Yr Sharpe Fund', '3 Yr Sharpe Cat. Av', '3 Yr SD Fund', '3 Yr SD Cat. Av', '5 Yr Alpha Fund', '5 Yr Alpha Cat. Av', '5 Yr Beta Fund ', '5 Yr Beta Cat. Av', '5 Yr IR Fund ', '5 Yr IR Cat. Av', '5 Yr R2 Fund', '5 Yr R2 Cat. Av', '5 Yr Sharpe Fund', '5 Yr Sharpe Cat. Av', '5 Yr SD Fund', '5 Yr SD Cat. Av'])
    # r = 0
    for fund in funds:
        print(fund, '- risk')
        # r+=1
        # if r == 10:
        #     break
        reqf = requests.get("https://markets.ft.com" +
                            funds[fund].replace("summary", 'risk'), headers=headers).text
        soup = BeautifulSoup(reqf, "lxml")
        row = []
        for nr, tables in enumerate(soup.find_all('table', {"class": "mod-ui-table"})):
            for tr in tables.find_all('tr'):
                try:
                    row.append(tr.find_all('td')[1].text.strip())
                    row.append(tr.find_all('td')[2].text.strip())
                except:
                    pass
        try:
            Benchmark = soup.find(
                "span", {"class": "mod-risk-measures__benchmark--dark"}).text
        except:
            Benchmark = "--"
        writer.writerow(["/".join(fund.split("/")[:-1]), funds[fund].split('s=')[-1], "https://markets.ft.com" +
                        funds[fund].replace("summary", 'risk'), fund.split("/")[-1], Benchmark]+row)
        f.flush()
    f.close()

    f = open('Ratings.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['Asset Name', 'Fund ID', 'FT URL', 'Watchlist', 'Category', 'Morningstar Overal', 'Lipper Overal Total', 'Lipper Overall Consistent', 'Lipper Overal Preservation ', 'Lipper Overall Expense', 'Lipper 3 Yr Total', 'Lipper 3 Yr Consistent',
                    'Lipper 3 Yr Preservation ', 'Lipper 3 Yr Expense', 'Lipper 5 Yr Total', 'Lipper 5 Yr Consistent', 'Lipper 5 Yr Preservation ', 'Lipper 5 Yr Expense', 'Lipper 10 Yr Total', 'Lipper 10 Yr Consistent', 'Lipper 10 Yr Preservation ', 'Lipper 10 Yr Expense'])
    # r = 0
    for fund in funds:
        print(fund, '- ratings')

        # r+=1
        # if r == 10:
        #     break
        reqf = requests.get("https://markets.ft.com" +
                            funds[fund].replace("summary", 'ratings'), headers=headers).text
        soup = BeautifulSoup(reqf, "lxml")

        row = []
        for nr, tables in enumerate(soup.find_all('table', {"class": "mod-ui-table mod-ui-table--freeze-pane"})):
            for tr in tables.find_all('tr'):
                try:
                    row.append(tr.find_all('td')[1].find(
                        "i")['class'][-1].split("-")[-1])
                    row.append(tr.find_all('td')[2].find(
                        "i")['class'][-1].split("-")[-1])
                    row.append(tr.find_all('td')[3].find(
                        "i")['class'][-1].split("-")[-1])
                    row.append(tr.find_all('td')[4].find(
                        "i")['class'][-1].split("-")[-1])
                except:
                    pass
        try:
            MSrating = len(
                soup.find("span", {"data-mod-stars-highlighted": "true"}).find_all("i"))
        except:
            MSrating = "--"
        try:
            category = soup.find(
                "div", {"class": "mod-morningstar-rating-app__category"}).find_all("span")[1].text
        except:
            category = "--"
        writer.writerow(["/".join(fund.split("/")[:-1]), funds[fund].split('s=')[-1], "https://markets.ft.com" +
                        funds[fund].replace("summary", 'ratings'), fund.split("/")[-1], category, MSrating]+row)
        f.flush()
    f.close()

    # fundi = {}
    # n = 7
    # for i in funds:
    #     n-=1
    #     if n == 0:
    #         break
    #     fundi[i] = funds[i]
    # funds = fundi
    # funds['FidelityÂ® Select Medical Technology and Devices/Roy'] = '/data/funds/tearsheet/performance?s=FSMEX'
    f = open('Performance.csv', 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(['Asset Name', 'Fund ID', 'FT URL', 'Watchlist', '5 Yr Fund %', '3 Yr Fund %', '1 Yr Fund %', '6 Mnth Fund %', '3 Mnth Fund %', '1 Mnth Fund %', 'Category', '5 Yr Cat %', '3 Yr Cat %', '1 Yr Cat %', '6 Mnth Cat %', '3 Mnth Cat %', '1 Mnth Cat %', 'Benchmark', '5 Yr Bench%', '3 Yr Bench %', '1 Yr Bench %', '6 Mnth Bench %', '3 Mnth Bench %', '1 Mnth Bench %', '5 YR Q', '3 YR Q', '1 YR Q', '6 Mnth Q', '3 Mnth Q', '1 Mnth Q',
                    '5 Yr Prior Fund %', '4 Yr Prior Fund %', '3 Yr Prior Fund %', '2 Yr Prior Fund %', '1 Yr Prior Fund %', 'YTD Fund %', '5 Yr Prior Cat %', '4 Year Prior Cat %', '3 Yr Prior Cat %', '2 Yr Prior Cat %', '1 Yr Prior Cat %', 'YTD Cat %', '5 Yr Prior Bench%', '4 Year Prior Bench%', '3 Yr Prior Bench%', '2 Yr Prior Bench%', '1 Yr Prior Bench%', 'YTD Bench%', '5 Yr Prior Q%', '4 Year Prior Q%', '3 Yr Prior Q%', '2 Yr Prior Q%', '1 Yr Prior Q%', 'YTD Q%'])

    for fund in funds:
        print(fund, '- performance')

        reqf = requests.get("https://markets.ft.com" +
                            funds[fund].replace("summary", 'performance'), headers=headers).text
        soup = BeautifulSoup(reqf, "lxml")

        row = []
        for i in range(0, 29):
            row.append("")
        for nr, tables in enumerate(soup.find_all('table', {"class": "mod-ui-table mod-ui-table--freeze-pane"})):
            for tr in tables.find_all('tr'):
                if "Funds in category" in tr.text:
                    continue
                try:
                    if "Fund quartile" in tr.text:
                        row[20] = tr.find_all('td')[1].text.strip()
                        row[21] = tr.find_all('td')[2].text.strip()
                        row[22] = tr.find_all('td')[3].text.strip()
                        row[23] = tr.find_all('td')[4].text.strip()
                        row[24] = tr.find_all('td')[5].text.strip()
                        row[25] = tr.find_all('td')[6].text.strip()
                    if "#EEA45F" in tr.find("span")['style']:
                        row[13] = tr.find_all('td')[0].text.strip()
                        row[14] = tr.find_all('td')[1].text.strip()
                        row[15] = tr.find_all('td')[2].text.strip()
                        row[16] = tr.find_all('td')[3].text.strip()
                        row[17] = tr.find_all('td')[4].text.strip()
                        row[18] = tr.find_all('td')[5].text.strip()
                        row[19] = tr.find_all('td')[6].text.strip()
                    if "#27757B" in tr.find("span")['style']:
                        row[6] = tr.find_all('td')[0].text.strip()
                        row[7] = tr.find_all('td')[1].text.strip()
                        row[8] = tr.find_all('td')[2].text.strip()
                        row[9] = tr.find_all('td')[3].text.strip()
                        row[10] = tr.find_all('td')[4].text.strip()
                        row[11] = tr.find_all('td')[5].text.strip()
                        row[12] = tr.find_all('td')[6].text.strip()
                    if "#ff7f8a" in tr.find("span")['style']:
                        row[0] = tr.find_all('td')[1].text.strip()
                        row[1] = tr.find_all('td')[2].text.strip()
                        row[2] = tr.find_all('td')[3].text.strip()
                        row[3] = tr.find_all('td')[4].text.strip()
                        row[4] = tr.find_all('td')[5].text.strip()
                        row[5] = tr.find_all('td')[6].text.strip()
                except:
                    pass

        params = {
            'chartType': 'annual',
            'symbol': funds[fund].split('=')[-1],
        }
        response = requests.get(
            'https://markets.ft.com/data/funds/ajax/trailing-total-returns', headers=headers, params=params)
        dicti = response.json()
        soup = BeautifulSoup(dicti['html'], "lxml")

        for i in range(0, 29):
            row.append("")
        for nr, tables in enumerate(soup.find_all('table', {"class": "mod-ui-table mod-ui-table--freeze-pane"})):
            for tr in tables.find_all('tr'):
                if "Funds in category" in tr.text:
                    continue
                try:
                    if "Fund quartile" in tr.text:
                        row[44] = tr.find_all('td')[1].text.strip()
                        row[45] = tr.find_all('td')[2].text.strip()
                        row[46] = tr.find_all('td')[3].text.strip()
                        row[47] = tr.find_all('td')[4].text.strip()
                        row[48] = tr.find_all('td')[5].text.strip()
                        row[49] = tr.find_all('td')[6].text.strip()
                    if "#EEA45F" in tr.find("span")['style']:
                        row[38] = tr.find_all('td')[1].text.strip()
                        row[39] = tr.find_all('td')[2].text.strip()
                        row[40] = tr.find_all('td')[3].text.strip()
                        row[41] = tr.find_all('td')[4].text.strip()
                        row[42] = tr.find_all('td')[5].text.strip()
                        row[43] = tr.find_all('td')[6].text.strip()
                    if "#27757B" in tr.find("span")['style']:
                        row[32] = tr.find_all('td')[1].text.strip()
                        row[33] = tr.find_all('td')[2].text.strip()
                        row[34] = tr.find_all('td')[3].text.strip()
                        row[35] = tr.find_all('td')[4].text.strip()
                        row[36] = tr.find_all('td')[5].text.strip()
                        row[37] = tr.find_all('td')[6].text.strip()
                    if "#ff7f8a" in tr.find("span")['style']:
                        row[26] = tr.find_all('td')[1].text.strip()
                        row[27] = tr.find_all('td')[2].text.strip()
                        row[28] = tr.find_all('td')[3].text.strip()
                        row[29] = tr.find_all('td')[4].text.strip()
                        row[30] = tr.find_all('td')[5].text.strip()
                        row[31] = tr.find_all('td')[6].text.strip()
                except:
                    pass
        writer.writerow(["/".join(fund.split("/")[:-1]), funds[fund].split('s=')[-1],
                        "https://markets.ft.com" + funds[fund].replace("summary", 'performance'), fund.split("/")[-1]]+row)
        f.flush()
    f.close()