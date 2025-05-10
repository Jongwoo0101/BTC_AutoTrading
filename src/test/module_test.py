import pyupbit

import os
from dotenv import load_dotenv


# 로그인
load_dotenv()

access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')
upbit = pyupbit.Upbit(access, secret)

print(upbit.get_balance("KRW-BTC"))     # KRW-BTC 조회
print(upbit.get_balance("KRW"))         # 보유 현금 조회