import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
import time
import os
import sys
import csv

# 외부 모듈 불러오기
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from components.get_current_status import get_cs

# 환경 변수 로드
load_dotenv()

# Upbit API 키 로드
access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

# 로그 파일 경로
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'LSTM_training_log.csv')

# 로그 저장 함수
def log_prediction(timestamp, current_price, predicted_price, smoothed_predicted, decision):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, current_price, predicted_price, smoothed_predicted, decision])

# 시퀀스 생성 함수
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length])
    return np.array(X), np.array(y)

# LSTM 모델 학습 함수 (루프 밖에서 1회만 실행)
def create_trained_model():
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1000)
    close_prices = df['close'].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(close_prices)

    seq_length = 10
    X, y = create_sequences(scaled_data, seq_length)
    X = X.reshape(X.shape[0], seq_length, 1)

    model = Sequential()
    model.add(LSTM(64, return_sequences=True, input_shape=(seq_length, 1)))
    model.add(LSTM(32))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=100, batch_size=32, verbose=0)

    return model, scaler, seq_length

# 예측 함수
def predict_price(model, scaler, seq_length):
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=seq_length + 1)
    close_prices = df['close'].values.reshape(-1, 1)
    scaled_data = scaler.transform(close_prices)

    last_sequence = scaled_data[-seq_length:]
    last_sequence = last_sequence.reshape(1, seq_length, 1)
    predicted = model.predict(last_sequence, verbose=0)
    return scaler.inverse_transform(predicted)[0][0]

# 스무딩 함수
def smooth_predictions(predicted_price, history=[], window_size=3):
    history.append(predicted_price)
    if len(history) > window_size:
        history.pop(0)
    return np.mean(history), history

# 매매 판단 함수
def decide_action(current_price, predicted_price):
    threshold = 0.005  # 0.5%
    if predicted_price > current_price * (1 + threshold):
        return "buy"
    elif predicted_price < current_price * (1 - threshold):
        return "sell"
    else:
        return "hold"

# 거래 실행 함수
prediction_history = []

def execute_trade(model, scaler, seq_length):
    predicted_price = predict_price(model, scaler, seq_length)
    current_price = pyupbit.get_current_price("KRW-BTC")
    smoothed_predicted, updated_history = smooth_predictions(predicted_price, prediction_history)
    decision = decide_action(current_price, smoothed_predicted)

    print(f"[{datetime.now()}] 현재가: {current_price:,.0f} | 예측가: {predicted_price:,.0f} | 스무딩: {smoothed_predicted:,.0f} | 판단: {decision.upper()}")
    log_prediction(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), current_price, predicted_price, smoothed_predicted, decision)

    krw_balance = upbit.get_balance("KRW")
    btc_balance = upbit.get_balance("KRW-BTC")

    if decision == "buy" and krw_balance > 5000:
        print("🟢 시장가 매수 진행")
        upbit.buy_market_order("KRW-BTC", krw_balance * 0.9995)

    elif decision == "sell" and float(btc_balance) > 0.0001:
        print("🔴 시장가 매도 진행")
        upbit.sell_market_order("KRW-BTC", btc_balance)

    else:
        print("🟡 매수/매도 조건 미충족")

# 로그 파일이 없으면 헤더 작성
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'current_price', 'predicted_price', 'smoothed_predicted', 'decision'])

# 메인 루프
print("📈 LSTM 기반 비트코인 자동매매 봇 시작")
print("⏳ 모델 학습 중...")

model, scaler, seq_length = create_trained_model()

print("✅ 학습 완료! 3분마다 자동매매 시작")

while True:
    try:
        get_cs("KRW-BTC")
        execute_trade(model, scaler, seq_length)
    except KeyboardInterrupt:
        print("\n🛑 사용자 중지: 자동매매 종료")
        break
    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")
    print("⏱ 3분 대기 중...\n")
    time.sleep(180)
