from Backtest.backtest import Backtest


class StockChart:

    def __init__(self, stock, timestamp, candles, volume, vwap):
        self.__stock = stock
        self.__charts = {
            "Timestamp": timestamp,
            "Candles": candles,
            "Volume": volume,
            "Vwap": vwap,
            "RSI": Backtest.generate_rsi(candles),
            "MACD": Backtest.generate_macd(candles),
            "MFI": Backtest.generate_mfi(candles, volume),
            "EMA": Backtest.generate_ema(candles, 9)
        }

    def get_stock_id(self):
        return self.__stock.get_id()

    def get_stock_symbol(self):
        return self.__stock.get_symbol()

    def get_stock_name(self):
        return self.__stock.get_name()

    def get_stock_exchange(self):
        return self.__stock.get_exchange()

    def get_predictions(self):
        return Backtest.generate_price_prediction(self.__charts)

    def __dict__(self):
        return {
            'symbol': self.__stock.get_symbol(),
            'charts': self.__charts
        }
