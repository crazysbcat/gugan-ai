import yfinance as yf
import pandas_ta as ta
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from dateutil.relativedelta import relativedelta

def init_stock_data():
    stockId = input("股票代碼？ex.2330.tw (台積電) ")
    sel =  int(input("資料區間: 1)1個月 2)3個月 3)6個月 4)1年 5)2年")) -1
    periods = [1,3,6,12,24]
    period = periods[sel]
    now = datetime.now()
    from_time = now - relativedelta(months=period)
    stock_data = yf.download(stockId, start=from_time.strftime('%Y-%m-%d'), end=now.strftime('%Y-%m-%d'))
    # 改掉 multi-column header, 原本為Price Ticker
    stock_data.columns = stock_data.columns.droplevel(1)
    return stockId, stock_data
    #print(stock_data.head())

def calIndicator(stock_data):
    # 14天平均移動線 SMA
    stock_data['SMA_14'] = ta.sma(stock_data['Close'], 14)
    # 14天相對強弱指標 RSI
    stock_data['RSI_14'] = ta.rsi(stock_data['Close'], 14)
    # 計算MACD
    macd_df = ta.macd(stock_data['Close']) #回傳data frame
    # 合併MACD 回原本的資料
    stock_data = pd.concat([stock_data, macd_df], axis=1, ignore_index=False)
    #Bollinger Bands 布林通道
    bb_df = ta.bbands(stock_data['Close'], length=20, std=2)
    stock_data = pd.concat([stock_data, bb_df], axis=1, ignore_index=False)
    print(stock_data.tail())
    print(stock_data[['Close', 'SMA_14', 'RSI_14']].head(20))
    return stock_data

def plot_stock_indicators(stock_data):
    plt.style.use('seaborn-darkgrid')
    
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # --- 圖 1：收盤價 + 布林通道 + SMA ---
    ax1.plot(stock_data.index, stock_data['Close'], label='Close Price', color='blue')
    ax1.plot(stock_data.index, stock_data['SMA_14'], label='SMA 14', color='purple')
    ax1.plot(stock_data.index, stock_data['BBL_20_2.0'], label='Lower Band', linestyle='--', color='green')
    ax1.plot(stock_data.index, stock_data['BBM_20_2.0'], label='Middle Band', linestyle='-', color='orange')
    ax1.plot(stock_data.index, stock_data['BBU_20_2.0'], label='Upper Band', linestyle='--', color='red')
    ax1.set_title('Stock Price + Bollinger Bands + SMA')
    ax1.set_ylabel('Price')
    ax1.legend()
        
    # --- 圖 2：MACD ---
    ax2.plot(stock_data.index, stock_data['MACD_12_26_9'], label='MACD', color='purple')
    ax2.plot(stock_data.index, stock_data['MACDs_12_26_9'], label='Signal', color='orange')
    ax2.bar(stock_data.index, stock_data['MACDh_12_26_9'], label='Histogram', color='gray')
    ax2.set_title('MACD')
    ax2.set_ylabel('MACD')
    ax2.legend()
        
    # --- 圖 3：RSI + 超買/超賣區間線 ---
    ax3.plot(stock_data.index, stock_data['RSI_14'], label='RSI 14', color='green')
    ax3.axhline(70, linestyle='--', color='red', label='Overbought (70)')
    ax3.axhline(30, linestyle='--', color='blue', label='Oversold (30)')
    ax3.set_title('RSI')
    ax3.set_ylabel('RSI')  
    ax3.set_ylim(0, 100)
    ax3.legend()
        
    plt.xlabel('Date')
    plt.tight_layout()
    plt.show()

stock_Id, stock_data = init_stock_data()
print("data types:\n", stock_data.dtypes)
analyzed_data = calIndicator(stock_data)
plot_stock_indicators(analyzed_data)
analyzed_data.to_csv(stock_Id+'.data_with_indicators.csv')