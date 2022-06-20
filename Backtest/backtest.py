class Backtest:

    @staticmethod
    def generate_rsi(candles):
        if len(candles) > 14:
            rsi = [None] * 14
            gain = 0
            loss = 0
            for index in range(1, 14):
                value = candles[index]['Close'] - candles[index - 1]['Close']
                if value > 0:
                    gain += value
                else:
                    loss -= value
            gain /= 14
            loss /= 14

            for index in range(14, len(candles)):
                value = candles[index]['Close'] - candles[index - 1]['Close']
                if value > 0:
                    gain = ((gain * 13) + value) / 14
                    loss = loss * 13 / 14
                else:
                    gain = gain * 13 / 14
                    loss = ((loss * 13) - value) / 14
                rs = gain / loss
                rsi.append(100 - (100 / (1 + rs)))
            return rsi
        return [None] * len(candles)

    @staticmethod
    def generate_macd(candles):
        if len(candles) > 26:
            ema12 = Backtest.generate_ema(candles, 12)
            ema26 = Backtest.generate_ema(candles, 26)
            macd = [None] * 25
            for index in range(26, len(candles)):
                macd.append(ema12[index] - ema26[index])
            return macd
        return [None] * len(candles)

    @staticmethod
    def generate_mfi(candles, volume):
        if len(candles) > 16:
            mfi = [None] * 15
            positive_flow = []
            negative_flow = []

            for index in range(1, len(candles)):
                typical_price_prev = (candles[index - 1]['High'] + candles[index - 1]['Low'] + candles[index - 1]['Close']) / 3
                typical_price = (candles[index]['High'] + candles[index]['Low'] + candles[index]['Close']) / 3
                if len(positive_flow) == 14:
                    mfr = sum(positive_flow) / (sum(negative_flow) if sum(negative_flow) > 0 else 1)
                    mfi.append(100 - (100 / (1 + mfr)))
                    positive_flow.pop(0)
                    negative_flow.pop(0)
                if typical_price > typical_price_prev:
                    positive_flow.append(typical_price_prev * volume[index - 1])
                    negative_flow.append(0)
                elif typical_price < typical_price_prev:
                    positive_flow.append(0)
                    negative_flow.append(typical_price_prev * volume[index - 1])
                else:
                    positive_flow.append(0)
                    negative_flow.append(0)
            return mfi
        return [None] * len(candles)

    @staticmethod
    def generate_ema(candles, interval, smoothing=2):
        if len(candles) > (interval - 1):
            ema = [None] * (interval - 1)
            sum = 0
            for index in range(interval):
                sum += candles[index]['Close']
            ema.append(sum / interval)
            for index in range(interval, len(candles)):
                ema.append((candles[index]['Close'] * (smoothing / (interval + 1))) + (ema[index - 1] * (1 - (smoothing / (interval + 1)))))
            return ema
        return [None] * len(candles)

    @staticmethod
    def generate_price_prediction(charts):
        predictions = {
            'trend_direction': None,
            'action': None
        }
        size = len(charts['RSI'])
        if len(charts['RSI']) < 2:
            return predictions
        if len(charts['RSI']) > 5:
            size = 5
        if (charts['RSI'][-1] > 70 and charts['RSI'][-1] > (sum(charts['RSI'][-size:]) / size)) or (
                charts['MACD'][-1] > 5):
            predictions['trend_direction'] = 'Up'
            predictions['action'] = 'Hold'
        elif charts['RSI'][-1] > 70 or charts['MACD'][-1] < -5 or charts['MFI'][-1] > 80:
            predictions['trend_direction'] = 'Down'
            predictions['action'] = 'Sell'
        elif charts['RSI'][-1] < 30 and charts['RSI'][-1] > (sum(charts['RSI'][-size:]) / 5) or (
                charts['MACD'][-1] > 5) or charts['MFI'][-1] < 20:
            predictions['trend_direction'] = 'Up'
            predictions['action'] = 'Buy'
        elif charts['RSI'][-1] < 30 or charts['MACD'][-1] < -5:
            predictions['trend_direction'] = 'Down'
            predictions['action'] = 'Hold'
        elif charts['RSI'][-1] > charts['RSI'][-2] and charts['RSI'][-1] > (
                sum(charts['RSI'][-size:]) / 5):
            predictions['trend_direction'] = 'Up'
            predictions['action'] = 'Hold'
        elif charts['RSI'][-1] < charts['RSI'][-2] and charts['RSI'][-1] < (
                sum(charts['RSI'][-size:]) / 5):
            predictions['trend_direction'] = 'Down'
            predictions['action'] = 'Hold'
        else:
            predictions['trend_direction'] = 'Steady'
            predictions['action'] = 'Hold'
        return predictions
