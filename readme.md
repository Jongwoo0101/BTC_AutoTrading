# 📈 BTC_AutoTrading

An automated Bitcoin trading program utilizing a variety of trading strategies including machine learning, deep learning, technical indicators, market sentiment, and news analysis.

---

## ❓ About the Project

This project aims to automate Bitcoin trading decisions using multiple models and tools:

- **Time-series forecasting models** (LSTM, Prophet)
- **News and sentiment-based trading**
- **Technical indicator-based strategies**
- **Backtesting and optimization support**

---

## 📂 Project Structure

### 📚 `docs`
- `prophet.md`: Official documentation summary for Prophet
- `pyupbit.md`: Guide to using the PyUpbit API

### ⚙️ `src`

#### 🧠 `src/models`
- `LsTmAutoTrade.py`: LSTM-based model that predicts future prices and makes trading decisions
- `proPhetAutoTrade.py`: Combines Prophet forecasting with Volatility Breakout Strategy
- `newsBasedTrade.py`: Integrated AI model using real-time news, sentiment index, and indicators
- `selfKtrading.py`: Optimized Volatility Breakout Strategy using the best `k` value

#### 🖥️ `src/apps`
- `LsTm_app.py`: Streamlit app to monitor LSTM trading model
- `proPhet_app.py`: Streamlit app for Prophet-based model monitoring

#### 🧩 `src/components`
- `add_technical_indicators.py`: Adds indicators like RSI, MACD
- `get_crypto_news.py`: Collects latest Bitcoin-related news
- `get_current_status.py`: Retrieves user's current investment and holdings
- `get_fear_greed_index.py`: Fetches Fear & Greed Index data

#### 📈 `src/logs`
- `backTestResult.xlsx`: Backtesting result file
- `LSTM_training_log.csv`: Training log for LSTM model

#### 🧪 `src/test`
- `back_test.py`: Basic backtesting script using Volatility Breakout Strategy
- `bestk_test.py`: Finds optimal `k` value by simulating strategy performance
- `module_test.py`: PyUpbit API test script

##### 📓 `src/test/jupyter`
> ⚠️ **Not intended for actual investment use.**
- `CNN.ipynb`: CNN-based prediction experiment
- `LsTm.ipynb`: LSTM model test notebook
- `prophet_test.ipynb`: Prophet model testing
- `pyupbit_test.ipynb`: PyUpbit feature test

---

## ▶️ How to Run

1. Create a `.env` file and insert the following:
    ```ini
    UPBIT_ACCESS_KEY=your_access_key
    UPBIT_SECRET_KEY=your_secret_key
    OPENAI_API_KEY=your_openai_key
    SERPAPI_KEY=your_serpapi_key
    GEMINI_API_KEY=your_gemini_key
    ```

2. Navigate to `src/models/` and run your preferred auto-trading model.

---

## 🛠️ Technologies Used

- Python (pandas, numpy, tensorflow, prophet, streamlit, etc.)
- APIs: Upbit, OpenAI, SERP API
- ML/DL Models: LSTM, CNN, Prophet
- Backtesting and visualization tools

---

## ⚠️ Disclaimer

This project is for **educational and research purposes only**.  
It is **not** intended for live trading or financial advice.  
Use APIs and trading bots at your own risk.

---

## 📬 Contact

Feel free to open an [issue](https://github.com/your-repo/issues) or submit a pull request if you’d like to contribute or report a bug.
