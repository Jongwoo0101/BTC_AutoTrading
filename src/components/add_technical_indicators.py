import ta

def add_technical_indicators(df):
        """기술적 분석 지표 추가"""
        # 볼린저 밴드
        indicator_bb = ta.volatility.BollingerBands(close=df['close'])
        df['bb_high'] = indicator_bb.bollinger_hband()
        df['bb_mid'] = indicator_bb.bollinger_mavg()
        df['bb_low'] = indicator_bb.bollinger_lband()
        df['bb_pband'] = indicator_bb.bollinger_pband()
       
        # RSI
        df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi()
       
        # MACD
        macd = ta.trend.MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
       
        # 이동평균선
        df['ma5'] = ta.trend.SMAIndicator(close=df['close'], window=5).sma_indicator()
        df['ma20'] = ta.trend.SMAIndicator(close=df['close'], window=20).sma_indicator()
        df['ma60'] = ta.trend.SMAIndicator(close=df['close'], window=60).sma_indicator()
        df['ma120'] = ta.trend.SMAIndicator(close=df['close'], window=120).sma_indicator()
       
        # ATR
        df['atr'] = ta.volatility.AverageTrueRange(
            high=df['high'], low=df['low'], close=df['close']
        ).average_true_range()
       
        return df