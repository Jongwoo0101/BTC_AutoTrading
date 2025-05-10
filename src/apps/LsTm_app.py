import streamlit as st
import time
from datetime import datetime
import pyupbit
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
import os

load_dotenv()
access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

st.set_page_config(page_title="비트코인 자동매매봇", layout="wide")

st.title("📈 LSTM 기반 비트코인 자동매매봇")
log = st.empty()

def get_current_status(ticker="KRW-BTC"):
    krw = float(upbit.get_balance("KRW"))
    coin = float(upbit.get_balance(ticker))
    price = pyupbit.get_current_price(ticker)
    avg_price = float(upbit.get_avg_buy_price(ticker))
    return krw, coin, price, avg_price

def train_model():
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=200)
    data = df['close'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    X, y = [], []
    for i in range(len(scaled) - 10):
        X.append(scaled[i:i+10])
        y.append(scaled[i+10])
    X = np.array(X).reshape(-1, 10, 1)
    y = np.array(y)

    model = Sequential()
    model.add(LSTM(50, input_shape=(10, 1)))
    model.add(Dense(1))
    model.compile(optimizer="adam", loss="mse")
    model.fit(X, y, epochs=30, batch_size=16, verbose=0)

    last_seq = scaled[-10:].reshape(1, 10, 1)
    pred = model.predict(last_seq)
    return scaler.inverse_transform(pred)[0][0]

def decide_action(current, predicted):
    if predicted > current * 1.01:
        return "BUY"
    elif predicted < current * 0.99:
        return "SELL"
    return "HOLD"

st.sidebar.header("설정")
run = st.sidebar.checkbox("자동매매 시작", value=False)

status_area = st.empty()
log_area = st.empty()

if run:
    while True:
        try:
            krw, coin, current_price, avg_price = get_current_status()
            predicted_price = train_model()
            decision = decide_action(current_price, predicted_price)

            # 상태 표시
            status_area.markdown(f"""
            ### 📊 현재 상태
            - **현재가**: {current_price:,.0f} KRW  
            - **예측가**: {predicted_price:,.0f} KRW  
            - **판단**: `{decision}`  
            - **보유 원화**: {krw:,.0f} KRW  
            - **보유 BTC**: {coin:.6f}  
            - **평균 매수가**: {avg_price:,.0f} KRW  
            - **미실현 손익**: {(coin * current_price - coin * avg_price):,.0f} KRW
            """)

            # 판단 및 매매
            if decision == "BUY" and krw > 5000:
                upbit.buy_market_order("KRW-BTC", krw * 0.9995)
                log_area.info(f"🟢 [{datetime.now()}] 매수 실행: {current_price:,.0f} KRW")
            elif decision == "SELL" and coin > 0.0001:
                upbit.sell_market_order("KRW-BTC", coin)
                log_area.info(f"🔴 [{datetime.now()}] 매도 실행: {current_price:,.0f} KRW")
            else:
                log_area.info(f"⏸️ [{datetime.now()}] 매매 없음 | 판단: {decision}")

            time.sleep(60)  # 1분 대기

        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
            break
