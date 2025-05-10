import pyupbit
from dotenv import load_dotenv
import os

load_dotenv()

access = os.getenv('UPBIT_ACCEES_KEY')
secret = os.getenv('UPBIT_SECRET_KEY')

upbit = pyupbit.Upbit(access, secret)

def get_cs(ticker):
        """현재 투자 상태 조회"""
        try:
            krw_balance = float(upbit.get_balance("KRW"))
            crypto_balance = float(upbit.get_balance(ticker))
            avg_buy_price = float(upbit.get_avg_buy_price(ticker))
            current_price = float(pyupbit.get_current_price(ticker))
           
            print("\n=== Current Investment Status ===")
            print(f"보유 현금: {krw_balance:,.0f} KRW")
            print(f"보유 코인: {crypto_balance:.8f} {ticker}")
            print(f"평균 매수가: {avg_buy_price:,.0f} KRW")
            print(f"현재가: {current_price:,.0f} KRW")
           
            total_value = krw_balance + (crypto_balance * current_price)
            unrealized_profit = ((current_price - avg_buy_price) * crypto_balance) if crypto_balance else 0
            profit_percentage = ((current_price / avg_buy_price) - 1) * 100 if crypto_balance else 0
           
            print(f"미실현 손익: {unrealized_profit:,.0f} KRW ({profit_percentage:.2f}%)")
           
            return {
                "krw_balance": krw_balance,
                "crypto_balance": crypto_balance,
                "avg_buy_price": avg_buy_price,
                "current_price": current_price,
                "total_value": total_value,
                "unrealized_profit": unrealized_profit,
                "profit_percentage": profit_percentage
            }
        except Exception as e:
            print(f"Error in get_current_status: {e}")
            return None