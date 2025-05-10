import pyupbit
import numpy as np
import os

# 로그 디렉토리 경로 설정
log_dir = os.path.join(os.path.dirname(__file__), "../logs")
os.makedirs(log_dir, exist_ok=True)  # logs 폴더 없으면 생성
result_path = os.path.join(log_dir, "backTestResult.xlsx")

df = pyupbit.get_ohlcv("KRW-BTC", count=7)
df['range'] = (df['high'] - df['low']) * 0.5
df['target'] = df['open'] + df['range'].shift(1)

df['ror'] = np.where(df['high'] > df['target'],
                     df['close'] / df['target'],
                     1)

df['hpr'] = df['ror'].cumprod()
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

# 콘솔에 MDD 출력
print("MDD(%): ", df['dd'].max())

# 엑셀 파일 저장
df.to_excel(result_path)
