import streamlit as st
import pyupbit
import datetime
from prophet import Prophet
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv


# 로그인
load_dotenv()


access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

st.set_page_config(page_title="Auto Trading Monitor", layout="wide")
st.title("📈 비트코인 자동매매 모니터링")
st.markdown("---")

# 현재 시세 및 잔고 정보
def get_current_data(ticker):
    now = datetime.datetime.now()
    price = pyupbit.get_current_price(ticker)
    balances = upbit.get_balances()
    krw = next((float(b['balance']) for b in balances if b['currency'] == 'KRW'), 0)
    btc = next((float(b['balance']) for b in balances if b['currency'] == 'BTC'), 0)
    return {
        "현재 시간": now.strftime('%Y-%m-%d %H:%M:%S'),
        "현재가": price,
        "보유 KRW": round(krw, 2),
        "보유 BTC": round(btc, 6)
    }

# 종가 예측 (1시간 캐시)
@st.cache_data(ttl=3600)
def predict_price(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute60")
    df = df.reset_index()
    df['ds'] = df['index']
    df['y'] = df['close']
    model = Prophet()
    model.fit(df[['ds', 'y']])
    future = model.make_future_dataframe(periods=24, freq='H')
    forecast = model.predict(future)
    close_df = forecast[forecast['ds'] == forecast.iloc[-1]['ds'].replace(hour=9)]
    if len(close_df) == 0:
        close_df = forecast[forecast['ds'] == df.iloc[-1]['ds'].replace(hour=9)]
    predicted_price = close_df['yhat'].values[0]
    return predicted_price, forecast

# 거래 내역 조회
def get_recent_orders(ticker):
    try:
        df = pyupbit.get_order(ticker, state="done")
        if df:
            return pd.DataFrame(df)
        else:
            return pd.DataFrame(columns=["uuid", "side", "price", "volume", "created_at"])
    except:
        return pd.DataFrame(columns=["uuid", "side", "price", "volume", "created_at"])

# 실시간 차트 데이터
def get_ohlcv_chart(ticker):
    df = pyupbit.get_ohlcv(ticker, interval="minute1", count=60)
    return df[['close']]

# 메인 실행
ticker = "KRW-BTC"
data = get_current_data(ticker)
predicted_price, forecast_df = predict_price(ticker)
ohlcv_df = get_ohlcv_chart(ticker)

# 실시간 정보 표시
st.subheader("🔍 현재 시세 및 잔고")
col1, col2, col3, col4 = st.columns(4)
col1.metric("현재 시간", data["현재 시간"])
col2.metric("현재가", f"{data['현재가']:,} KRW")
col3.metric("보유 KRW", f"{data['보유 KRW']:,}")
col4.metric("보유 BTC", data['보유 BTC'])

# 예측 종가
st.subheader("🔮 예측 종가 (내일 09:00)")
st.metric("예측 종가", f"{int(predicted_price):,} KRW")

# 예측 시각화
st.subheader("📊 Prophet 예측 그래프")
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(forecast_df['ds'], forecast_df['yhat'], label='예측')
ax1.fill_between(forecast_df['ds'], forecast_df['yhat_lower'], forecast_df['yhat_upper'], color='gray', alpha=0.2)
ax1.set_xlabel("시간")
ax1.set_ylabel("가격")
ax1.set_title("Prophet 예측 시세")
st.pyplot(fig1)

# 실시간 가격 그래프
st.subheader("📉 실시간 가격 그래프 (1분봉 기준)")
fig2, ax2 = plt.subplots(figsize=(10, 3))
ax2.plot(ohlcv_df.index, ohlcv_df['close'], label="1분봉 종가", color="orange")
ax2.set_ylabel("가격")
st.pyplot(fig2)

# 거래내역 표시
st.subheader("📜 최근 거래내역")
orders_df = get_recent_orders(ticker)
if not orders_df.empty:
    st.dataframe(orders_df[["uuid", "side", "price", "volume", "created_at"]].sort_values("created_at", ascending=False).head(10))
else:
    st.info("최근 체결된 거래내역이 없습니다.")

# 수동 매수/매도 섹션
st.subheader("🛒 수동 거래 실행")

col_buy, col_sell = st.columns(2)

with col_buy:
    if st.button("🔼 수동 매수 실행"):
        krw_balance = get_current_data(ticker)["보유 KRW"]
        if krw_balance > 5000:
            upbit.buy_market_order(ticker, krw_balance * 0.9995)
            st.success(f"{int(krw_balance * 0.9995):,} KRW 만큼 비트코인 수동 매수 실행됨")
        else:
            st.warning("보유 KRW가 부족합니다 (최소 5,000원 필요)")

with col_sell:
    if st.button("🔽 수동 매도 실행"):
        btc_balance = get_current_data(ticker)["보유 BTC"]
        if btc_balance > 0.00008:
            upbit.sell_market_order(ticker, btc_balance * 0.9995)
            st.success(f"{btc_balance * 0.9995:.6f} BTC 수동 매도 실행됨")
        else:
            st.warning("보유 BTC가 부족합니다 (최소 0.00008 BTC 필요)")
