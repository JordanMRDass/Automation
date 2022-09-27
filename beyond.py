from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import re
import json
import pandas as pd
from send2trash import send2trash
from itertools import combinations
from itertools import product
from collections import defaultdict
import unicodedata
from datetime import datetime 

try:
    from webdriver_manager.chrome import ChromeDriverManager
except:
    import pip
    pip.main(['install', 'webdriver-manager'])
    from webdriver_manager.chrome import ChromeDriverManager

import os
from selenium.webdriver.support.ui import WebDriverWait       
from selenium.webdriver.common.by import By       
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import numpy as np
import time

try:
    import lxml
except:
    import pip
    pip.main(['install', 'lxml'])
    import lxml

def filtering(url1, url2):
    # URL for finviz page with filters
    url = url1

    # Creating header to attain requests
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    # Created html for scraping
    html = soup(webpage, "html.parser")

    overview_df = pd.read_html(str(html), attrs = {'class': 'table-light'})[0]

    # Processing finviz overview table
    overview_df.columns = overview_df.iloc[0]

    overview_df = overview_df.iloc[1:, :]

    overview_df = overview_df.drop(columns = ["No."])

    overview_df = overview_df.set_index("Ticker")



    url = url2

    # Creating header to attain requests
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()

    # Created html for scraping
    html = soup(webpage, "html.parser")

    financial_df = pd.read_html(str(html), attrs = {'class': 'table-light'})[0]

    # Processing finviz financial table
    financial_df.columns = financial_df.iloc[0]

    financial_df = financial_df.iloc[1:, :]

    financial_df = financial_df.drop(columns = ["No."])

    financial_df = financial_df.set_index("Ticker")

    df = pd.concat([overview_df, financial_df], axis = "columns", join = "inner")

    try:
        df_compare = pd.read_csv("filter_company_2.0.csv")
        ticker_list = set(list(df["Ticker"]))

        ticker_compare_list = set(list(df_compare["Ticker"]))

        print("Difference :", ticker_list - ticker_compare_list)
    except:
        pass

    df.to_csv("/Users/Jordandass/Automation/filter_company_2.0.csv")

import re
import json
import pandas as pd
def clean_ads_df(df):
    header = list(df.columns)
    
    array = []
    for num in range(len(df)):
        row = list(df.iloc[num, :].values)
        
        if not re.findall("[a-zA-Z]", row[0]):
            array.append(row)
            
    df_clean = pd.DataFrame(array, columns = header)
    df_clean["Date"] = pd.to_datetime(df_clean["Date"], format = '%m/%d/%Y')
    return df_clean

import numpy as np
def extract_price_target(df):
    price_clean_list = []
    
    price_list = list(df["Price Target"])
    for price_raw in price_list:
        if type(price_raw) == str:
            if re.findall("➝", str(price_raw)):
                price_split = price_raw.split()
                price_dollar = price_split[-1]

                price_dollar = re.sub(",", "", price_dollar)
                price = float(price_dollar[1:])
                price_clean_list.append(price)
            else:
                price_raw = re.sub(",", "", price_raw)
                price = float(price_raw[1:])
                price_clean_list.append(price)
     
    median_price = np.median(price_clean_list)
    mean_price = np.mean(price_clean_list)
    
    return median_price, mean_price


def median_mean_price_creator(html_earnings, html_price):
    try:
        earnings_df = pd.read_html(str(html_earnings), attrs = {'id': 'earnings-history'})[0]

        earnings_date_list = list(earnings_df.Date)

        last_report_date_raw = earnings_date_list[1]
        last_report_date = pd.to_datetime(pd.to_datetime(last_report_date_raw).strftime('%m/%d/%Y'))

        price_df = pd.read_html(str(html_price), attrs = {'id': 'history-table'})[0]

        price_df = clean_ads_df(price_df)

        price_df_after_report = price_df[price_df["Date"] >= last_report_date]
    
        if len(price_df_after_report) > 0:
            median_target_price, mean_target_price = extract_price_target(price_df_after_report)
        else:
            median_target_price, mean_target_price = f"No analyst ratings after last report date: {last_report_date}", f"No analyst ratings after last report date: {last_report_date}"
    except:
        median_target_price, mean_target_price = f"No tables found"
        
    return median_target_price, mean_target_price

import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import numpy as np
import time

def scrape_html_earnings(ticker):
    # URL for each tickers market index page
    try:
        html_list = []
        for url in [f"https://www.marketbeat.com/stocks/NASDAQ/{ticker.upper()}/Earnings/",
                   f"https://www.marketbeat.com/stocks/NASDAQ/{ticker.upper()}/price-target/"]:
            # Creating header to attain requests
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()

            # Created html for scraping
            html = soup(webpage, "html.parser")

            html_list.append(html)

        median_target_price, mean_target_price = median_mean_price_creator(html_list[0], html_list[1])
    except:
        html_list = []
        for url in [f"https://www.marketbeat.com/stocks/NYSE/{ticker.upper()}/Earnings/",
                   f"https://www.marketbeat.com/stocks/NYSE/{ticker.upper()}/price-target/"]:
            # Creating header to attain requests
            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            webpage = urlopen(req).read()

            # Created html for scraping
            html = soup(webpage, "html.parser")

            html_list.append(html)

        median_target_price, mean_target_price = median_mean_price_creator(html_list[0], html_list[1])
    
    return median_target_price, mean_target_price

def median_mean_multiple_tickers(ticker_list):
    filter_company = pd.read_csv("filter_company_2.0.csv")
    filter_company_list_name = []
    for ticker in ticker_list:
        company_name = filter_company[filter_company["Ticker"] == ticker]["Company"].values[0]
        filter_company_list_name.append(company_name)
    
    
    median_list, mean_list = [], []
    for ticker in ticker_list:
        median_target_price, mean_target_price = scrape_html_earnings(ticker)
        
        mean_list.append(mean_target_price)
        median_list.append(median_target_price)
    
    df = pd.DataFrame({"Ticker":ticker_list, "Company":filter_company_list_name, "Mean":mean_list, "Median":median_list})
    df.to_csv("/Users/Jordandass/Automation/Analyst_rating_median.csv")
    return df

try:
    import hvplot.pandas
except:
    import pip
    pip.main(['install', 'hvplot'])
    
    pip.main(['install', 'lxml'])
    import hvplot.pandas
    
import panel as pn

def clean_up_df(df):
    df = df.reset_index()
    column_list = list(df.columns)
    
    clean_values_dict = {}
    for column in column_list:
        column_values = list(df[column])
        
        clean_values = []
        for value in column_values:
            if type(value) != str:
                clean_values.append(value)
                
            # Negative number identifying
            elif re.findall("\(|\)", value):
                remove_para = re.sub("\(|\)|%|,", "", str(value))
                clean_value = float(f"-{remove_para}")
                
                clean_values.append(clean_value)
                
            else:
                remove_para = re.sub("\(|\)|%|,", "", str(value))
                clean_value = float(f"{remove_para}")
                
                clean_values.append(clean_value)
                
        clean_values_dict[column] = clean_values
    
    return pd.DataFrame(clean_values_dict).set_index('year')
    
# Valuating companies
def past_growth(ticker, driver, time_to_sleep):
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')

    driver.get('https://stockrow.com/'+ str(ticker) +'/financials/income/annual')
    time.sleep(time_to_sleep)

    ticker_dict = {}
    # STR NAMES REV
    ticker_rev = 'rev'
    ticker_rev_per = 'rev(%)'

    # STR NAMES OPE
    ticker_ope = 'ope'
    ticker_ope_per = 'ope(%)'

    # STR NAMES EPS
    ticker_eps = 'eps'
    ticker_eps_per = 'eps(%)'

    row_label_num = list(range(10, 200, 9)) # num of data which are labels
    # BI important signals of a healthy company
    num_label_list = ['Revenue', 'Revenue Growth', 'Operating Income', 'EPS (Diluted)']
    num_label_growth_list = ['Operating Income Growth', 'EPS Growth (diluted)']
    #num_label_dict = {'Revenue': ticker_rev, 'Revenue Growth': ticker_rev_per, 'Operating Income': ticker_ope, 'EPS (Diluted)': ticker_eps, 'Operating Income Growth': ticker_ope_per, 'EPS Growth (diluted)': ticker_eps_per}

    years_list = []
    for num in range(3, 8):
        dat = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[4]/div/div[3]/div/div/div[4]/div/div/div['+str(num)+']')
        years_list.append(dat.text)
    
    array_dat = [] # contains lists of data
    for num in row_label_num:
        try:
            dat = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[4]/div/div[3]/div/div/div[4]/div/div/div['+str(num)+']').text
            if dat in num_label_list:
                lists_dat = []
                for num_dat in range(num + 2, num + 7):
                    dat = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[4]/div/div[3]/div/div/div[4]/div/div/div['+str(num_dat)+']').text
                    lists_dat.append(dat)
                array_dat.append(lists_dat)
        except:
            break

    driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[3]/div/div[1]/a[5]').click()
    time.sleep(7)

    for num in row_label_num:
        try:
            dat = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[4]/div/div[3]/div/div/div[4]/div/div/div['+str(num)+']').text
            if dat in num_label_growth_list:
                lists_dat = []
                for num_dat in range(num + 2, num + 7):
                    dat = driver.find_element(By.XPATH, '//*[@id="root"]/div/div/section/div/div[2]/div[1]/section[4]/div/div[3]/div/div/div[4]/div/div/div['+str(num_dat)+']').text
                    lists_dat.append(dat)
                array_dat.append(lists_dat)
        except:
            break


    labels = [ticker_rev, ticker_rev_per, ticker_ope, ticker_eps, ticker_ope_per, ticker_eps_per]

    for dat_list, label in zip(array_dat, labels):
        ticker_dict[label] = dat_list
    ticker_dict['year'] = years_list
        
    return ticker_dict

          
        
def ticker_evaluation(df_dict, rev_growth, ope_growth, eps_growth):
    tabs = pn.Tabs(dynamic=True, tabs_location='left')
    
    good_companies = []
    for ticker in df_dict:
        df = df_dict[ticker]
        
        table = df.hvplot.table()
        
        clean_df = clean_up_df(df)
        string = ""
        check = 0
        if min(clean_df["rev(%)"]) < rev_growth:
            string += (f"{ticker} does not meet revenue growth of {rev_growth}<br>")
            check += 1
        else:
            string += (f"{ticker} meets revenue growth of {rev_growth}<br>")
            
        if min(clean_df["ope(%)"]) < ope_growth:
            string += (f"{ticker} does not meet operating income growth of {ope_growth}<br>")
            check += 1
        else:
            string += (f"{ticker} meets operating income growth of {ope_growth}<br>")
            
        if min(clean_df["eps(%)"]) < eps_growth:
            string += (f"{ticker} does not meet earnings per share growth of {eps_growth}<br>")
            check += 1
        else:
            string += (f"{ticker} meets earnings per share growth of {eps_growth}<br>")
            
        if check == 0:
            string += (f"{ticker} meets all conditions")
            good_companies.append(ticker)
            
        viz = clean_df['rev'].hvplot.bar(title = f"{ticker} Revenue", shared_axes = False) + clean_df['ope'].hvplot.bar(title = f"{ticker} Operating Income", shared_axes = False) + clean_df['eps'].hvplot.bar(title = f"{ticker} Earnings per Share", shared_axes = False)
        
        ticker_column = pn.Column(f"##{ticker}", table, string, viz)
        tabs.append((ticker, ticker_column))
        
    return good_companies, tabs


# End of functions, beginning of commands

## Filtering with Finviz
filtering("https://finviz.com/screener.ashx?v=111&f=an_recom_buybetter,fa_epsyoy_o10,fa_epsyoy1_o10,fa_estltgrowth_o5,fa_roa_o10,fa_roe_o15,geo_usa,idx_sp500,sh_avgvol_o1000,sh_instown_o60",
         "https://finviz.com/screener.ashx?v=161&f=an_recom_buybetter,fa_epsyoy_o10,fa_epsyoy1_o10,fa_estltgrowth_o5,fa_roa_o10,fa_roe_o15,geo_usa,idx_sp500,sh_avgvol_o1000,sh_instown_o60")

filter_company = pd.read_csv("filter_company_2.0.csv") 
filter_ticker = list(filter_company["Ticker"])

print("Finish filtering")
## Target price analysis
target_price_df = median_mean_multiple_tickers(filter_ticker)
print("Finish Target Price")