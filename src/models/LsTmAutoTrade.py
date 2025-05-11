import pyupbit
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
import time
import os
import sys
import csv

# 외부 모듈 경로 설정
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from components.get_current_status import get_cs

# 환경 변수 로드
load_dotenv()

# api key load
access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

# 로그 경로 설정
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'LSTM_training_log.csv')

# 로그 저장
def log_prediction(timestamp, current_price, predicted_price, smoothed_predicted, decision):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, current_price, predicted_price, smoothed_predicted, decision])

# 시퀀스 생성
def create_sequences(data, seq_length, target_index=3):  # target_index=3 -> 'close'
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i + seq_length])
        y.append(data[i + seq_length][target_index])
    return np.array(X), np.array(y)

# 모델 생성 및 학습
def create_trained_model():
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=1000)
    features = df[['open', 'high', 'low', 'close', 'volume']].values

    scaler = MinMaxScaler()
    scaled_data = scaler.fit_transform(features)

    seq_length = 10
    X, y = create_sequences(scaled_data, seq_length)
    X = X.reshape(X.shape[0], seq_length, X.shape[2])

    model = Sequential()
    model.add(LSTM(128, return_sequences=True, input_shape=(seq_length, X.shape[2])))
    model.add(Dropout(0.2))
    model.add(LSTM(64))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=100, batch_size=32, verbose=0)

    return model, scaler, seq_length

# 가격 예측
def predict_price(model, scaler, seq_length):
    df = pyupbit.get_ohlcv("KRW-BTC", interval="day", count=seq_length + 1)
    features = df[['open', 'high', 'low', 'close', 'volume']].values
    scaled_data = scaler.transform(features)

    last_sequence = scaled_data[-seq_length:]
    last_sequence = last_sequence.reshape(1, seq_length, features.shape[1])
    predicted = model.predict(last_sequence, verbose=0)
    # 'close' 값 역변환
    dummy = np.zeros((1, features.shape[1]))
    dummy[0][3] = predicted[0][0]
    return scaler.inverse_transform(dummy)[0][3]

# 스무딩
def smooth_predictions(predicted_price, history=[], window_size=3):
    history.append(predicted_price)
    if len(history) > window_size:
        history.pop(0)
    return np.mean(history), history

# 매매 판단
def decide_action(current_price, predicted_price):
    threshold = 0.005
    if predicted_price > current_price * (1 + threshold):
        return "buy"
    elif predicted_price < current_price * (1 - threshold):
        return "sell"
    else:
        return "hold"

# 매매 실행
prediction_history = []

def execute_trade(model, scaler, seq_length):
    predicted_price = predict_price(model, scaler, seq_length)
    current_price = pyupbit.get_current_price("KRW-BTC")
    smoothed_predicted, _ = smooth_predictions(predicted_price, prediction_history)

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

# 로그 파일 없을 경우 헤더 생성
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['timestamp', 'current_price', 'predicted_price', 'smoothed_predicted', 'decision'])

# 메인 루프
print("📈 LSTM 기반 비트코인 자동매매 봇 시작")
print("⏳ 모델 학습 중...")

model, scaler, seq_length = create_trained_model()
last_retrain_time = datetime.now()

print("✅ 학습 완료! 3분마다 자동매매 시작")

while True:
    try:
        get_cs("KRW-BTC")
        execute_trade(model, scaler, seq_length)

        # 1시간마다 재학습
        if datetime.now() - last_retrain_time > timedelta(hours=1):
            print("🔁 모델 재학습 중...")
            model, scaler, seq_length = create_trained_model()
            last_retrain_time = datetime.now()
            print("✅ 재학습 완료")

    except KeyboardInterrupt:
        print("\n🛑 사용자 중지: 자동매매 종료")
        break
    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")
    print("⏱ 3분 대기 중...\n")
    time.sleep(180)
