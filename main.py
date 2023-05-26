# This is a sample Python script.
import string
import sys
import csv
from bs4 import BeautifulSoup
from typing import List
from urllib.request import urlopen, Request
from urllib.error import HTTPError
import utils.google_drive as drive
from utils.backup_output import backup_file

# todos:
# 1) make a CSV with rules -
#  - May need to make the format into numbers (instead of '150B', '2.7%' etc as the Excel is
#       having a hard time processing it
# 2) - reordering? of the columns

# WATCHLIST = ['c', 'bac', 'stwd', 'hpe']
WATCHLIST = [ 'MRK', 'khc', 'BMY', 'ko', 'pru', 'viac', 'cvs', 'ups', 'NLY', 'MBT', 'PG',
             'shlx', 'iep', 'sun', 'cim', 'AM', 'PSXP', 'MPLX', 'ET', 'LUMN', 'AIZ', 'BWA', 'CMA', 'COG', 'DXC', 'FANG', 'FRT', 'FTI', 'HBI', 'HII',
              'IPG', 'IRM', 'IVZ', 'JNPR', 'KIM', 'LEG', 'LNC', 'NI', 'LSN', 'PBCT', 'PNW', 'PRGO', 'RE', 'REG', 'SEE', 'SLG',
             'SNA', 'TPR', 'UNM', 'VNO', 'VNT', 'VTRS', 'WU', 'XRX', 'ZION']
WATCHLIST_MINING = ['SBSW', 'AMR', 'PLL', 'SLCA', 'DNN', 'NXE', 'SILV']

WATCHLIST_OLD = ['AMZN', 'GM', 'AXP', 'HON', 'ISRG', 'FSLY', 'XOM']
FINVIZ_TABLE_CONTENTS_ALL = ['Index', 'P/E', 'EPS (ttm)', 'Insider Own', 'Shs Outstand', 'Perf Week',
                             'Market Cap', 'Forward P/E', 'EPS next Y', 'Insider Trans', 'Shs Float', 'Perf Month',
                             'Income', 'PEG', 'EPS next Q', 'Inst Own', 'Short Float', 'Perf Quarter',
                             'Sales', 'P/S', 'EPS this Y', 'Inst Trans', 'Short Ratio', 'Perf Half Y',
                             'Book/sh', 'P/B', 'EPS next Y', 'ROA', 'Target Price', 'Perf Year',
                             'Cash/sh', 'P/C', 'EPS next 5Y', 'ROE', '52W Range', 'Perf YTD',
                             'Dividend', 'P/FCF', 'EPS past 5Y', 'ROI', '52W High', 'Beta',
                             'Dividend %', 'Quick Ratio', 'Sales past 5Y', 'Gross Margin', '52W Low', 'ATR',
                             'Employees', 'Current Ratio', 'Sales Q/Q', 'Oper. Margin', 'RSI (14)', 'Volatility',
                             'Optionable', 'Debt/Eq', 'EPS Q/Q', 'Profit Margin', 'Rel Volume', 'Prev Close',
                             'Shortable', 'LT Debt/Eq', 'Earnings', 'Payout', 'Avg Volume', 'Price',
                             'Recom', 'SMA20', 'SMA50', 'SMA200', 'Volume', 'Change']
FINVIZ_TABLE_CONTENTS_REQ_EXTENDED = ['Index', 'P/E', 'EPS (ttm)', 'Insider Own', 'Perf Week',
                             'Market Cap', 'Forward P/E', 'EPS next Y', 'Shs Float', 'Perf Month',
                             'Income', 'PEG', 'EPS next Q', 'Short Float', 'Perf Quarter',
                             'Sales', 'P/S', 'EPS this Y', 'Inst Trans', 'Short Ratio', 'Perf Half Y',
                             'Book/sh', 'P/B', 'ROA', 'Target Price', 'Perf Year',
                             'Cash/sh', 'P/C', 'ROE', 'Perf YTD',
                             'Dividend', 'P/FCF', 'EPS past 5Y', 'ROI', 'Beta',
                             'Dividend %', 'Quick Ratio', 'Sales past 5Y', 'Gross Margin', '52W Low', 'ATR',
                             'Employees', 'Current Ratio', 'Sales Q/Q', 'Oper. Margin', 'RSI (14)', 'Volatility',
                             'Debt/Eq', 'EPS Q/Q', 'Profit Margin',
                             'LT Debt/Eq', 'Earnings', 'Payout', 'Avg Volume', 'Price',
                             'Volume', 'Change']

FINVIZ_TABLE_CONTENTS_REQ_MAIN = ['Stock', 'Market Cap', 'Index', 'P/E', 'Forward P/E', 'Dividend %',
                             'Income', 'EPS (ttm)', 'PEG',
                             'Sales', 'P/S', 'EPS Q/Q', 'EPS this Y', 'Inst Trans',
                             'Book/sh', 'P/B', 'ROA', 'Perf Year',
                             'Cash/sh', 'P/C', 'ROE',
                             'P/FCF', 'EPS past 5Y', 'ROI',
                             'Current Ratio', 'Quick Ratio', 'Debt/Eq', 'LT Debt/Eq', 'Sales past 5Y', 'Gross Margin', 'ATR',
                             'Profit Margin', 'Oper. Margin', 'Volatility',

                             'Avg Volume', 'Price',
                             'Change']

CSV_COLUMNS = ['Stock']
CSV_COLUMNS.extend(FINVIZ_TABLE_CONTENTS_REQ_MAIN)

# Beta - For example, if a stock's beta value is 1.3, it means, theoretically this stock is 30% more volatile than the market.
# so if the market is expected to go up by 10% the stock is expected to go up 13%

FINVIZ_URL = 'https://finviz.com/quote.ashx?t=' # + <stock ticker>

FINVIZ_URL_CITI = 'https://finviz.com/quote.ashx?t=c'
FINVIZ_URL_BAC = 'https://finviz.com/quote.ashx?t=bac'

PRINT_FREQ_HIGH = False
PRINT_FREQ_MED = True
PRINT_FREQ_LOW = True


def printfrq(msg: string, frq: bool):
    if frq:
        print(msg)


def get_webpage_soup(wp_url: string):
    req = Request(wp_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        page = urlopen(req)
    except HTTPError as e:
        printfrq('caught HTTPError exception:' + str(e.code), PRINT_FREQ_LOW)
        return None

    return BeautifulSoup(page, 'html.parser')


csv_file_name = 'test_scraper.csv'


def write_to_csv(data: dict, write_header: bool = False):
    printfrq(f'Writing to .csv file..', PRINT_FREQ_LOW)
    csv_columns = CSV_COLUMNS

    try:
        with open(csv_file_name, 'a+', newline='') as csvfile:
        # with open(csv_file_name, 'a+', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FINVIZ_TABLE_CONTENTS_REQ_MAIN)
            if write_header:
                writer.writeheader()
            # for data in dict_data:
            writer.writerow(data)
    except IOError as e:
        print(f'I/O error !!! {e}')


def fetch_stock_data(stocks: List[str]):
    for s in stocks:
        url_to_fetch = FINVIZ_URL + s
        printfrq('getting info for stock:' + s.upper() + ' url - ' + url_to_fetch, PRINT_FREQ_LOW)

        webpage = get_webpage_soup(url_to_fetch)
        if webpage is None:
            continue

        printfrq(webpage, PRINT_FREQ_HIGH)

        element_titles = webpage.findAll("td", {"class": "snapshot-td2-cp"})
        element_values = webpage.findAll("td", {"class": "snapshot-td2"})
        title_list = []
        dict_1 = dict()
        dict_1['Stock'] = s
        enumerate(FINVIZ_TABLE_CONTENTS_REQ_MAIN)
        # todo:
        #  can swap the condition and order the Excel file columns with more important stats first
        index_map = {v: i for i, v in enumerate(FINVIZ_TABLE_CONTENTS_REQ_MAIN)}
        # data_dict = dict(zip(element_titles, element_values))
        for t, v in zip(element_titles, element_values):
            if t.text in FINVIZ_TABLE_CONTENTS_REQ_MAIN:
                dict_1[t.text] = v.text
                title_list.append(t.text)

        # sort items by their order in FINVIZ_TABLE_CONTENTS_REQ_MAIN
        # dict_2 = sorted(dict_1.items(), key=lambda pair: index_map[pair[0]])
        # printfrq(dict_2, PRINT_FREQ_LOW)

        write_to_csv(dict_1, s == stocks[0])


output_file = "test_scraper"
output_file_ext = "csv"

if __name__ == '__main__':
    printfrq('Starting py scraper..', PRINT_FREQ_LOW)

    backup_file(output_file, output_file_ext)
    if True:
        url_to_fetch = FINVIZ_URL_CITI
        if len(sys.argv) > 1:
            fetch_stock_data(sys.argv[1:])
        else:
            fetch_stock_data(WATCHLIST)

    printfrq('Scraper Finished Successfully !', PRINT_FREQ_LOW)

    # upload to drive
    dc = drive.init()
    drive.upload_to_drive(dc, ".".join([output_file, output_file_ext]))

