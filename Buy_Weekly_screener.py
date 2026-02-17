import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Weekly Pattern Screener", layout="wide")

st.title("📈 Weekly Candlestick Pattern Screener")
st.write("Scanning for **Doji** and **Railroad Tracks** on a Weekly Timeframe.")

# 1. Input: List of Tickers
ticker_input = st.text_input("Enter Tickers (separated by commas)", "RELIANCE.NS, PGHH.NS, MAZDOCK.NS, NATIONALUM.NS, TRENT.NS, DIXON.NS, KPITTECH.NS")
tickers = [t.strip() for t in ticker_input.split(",")]

def identify_patterns(df,symbol):
    if len(df) < 2:
        return None
    
    # Get last two weekly candles
    current_w = df.iloc[-1]
    prev_w = df.iloc[-2]
    results = [ ]
    
    # Doji Logic (Body < 10% of total range)
    body = abs(current_w['Open'] - current_w['Close'])
    total_range = current_w['High'] - current_w['Low']
    if total_range[symbol] > 0 and body[symbol] <= (total_range[symbol] * 0.1):
        results.append("Doji ⚖️")
    
    # Railroad Tracks Logic
    # 1. Opposite colors 2. Similar body sizes 3. Significxant size
    prev_body = abs(prev_w['Open'] - prev_w['Close'])
    curr_body = abs(current_w['Open'] - current_w['Close'])
    
    # Tolerance for "similar size" (within 10%)
    size_similarity = abs(curr_body[symbol] - prev_body[symbol]) < (prev_body[symbol] * 0.1)
    
    if size_similarity and prev_body[symbol] > 0:
        if prev_w['Close'] < prev_w['Open'] and current_w['Close'] > current_w['Open']:
            results.append("Bullish Railtrack 🚆⬆️")
        elif prev_w['Close'] > prev_w['Open'] and current_w['Close'] < current_w['Open']:
            results.append("Bearish Railtrack 🚆⬇️")
            
    return ", ".join(results) if results else "No Pattern"

# 2. Execution Button
if st.button("Run Screener"):
    data_list = [ ]
    
    with st.spinner('Fetching weekly data...'):
        for symbol in tickers:
            try:
                # Fetching 6 months of weekly data
                ticker_data = yf.download(symbol, period="6mo", interval="1wk", progress=False)
                
                if not ticker_data.empty:
                    pattern = identify_patterns(ticker_data,symbol)
                    last_price = round(ticker_data['Close'].iloc[-1], 2)
                    data_list.append({"Ticker": symbol, "Price": last_price[symbol], "Weekly Pattern": pattern})
                   
            except Exception as e:
                st.error(f"Error loading {symbol}: {e}")

    # 3. Display Results
    df_results = pd.DataFrame(data_list)
    if not df_results.empty:
        st.table(df_results)
    else:
        st.write("No data found.")

st.info("Note: Patterns are calculated based on the last completed weekly candle.")
