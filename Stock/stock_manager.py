from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
from alpaca_trade_api.stream import Stream
from Stock.config import APCA_API_BASE_URL, APCA_API_DATA_URL, APCA_API_KEY_ID, APCA_API_SECRET_KEY
from Database.databasewrapper import DatabaseWrapper
from Stock.stock import Stock
from Stock.stock_chart import StockChart
from datetime import date


class StockManager:

    @staticmethod
    def buy_stocks(symbol, quantity, key_id, secret_key, feed='iex'):
        rest_api = StockManager.get_rest_api_connection(key_id, secret_key, APCA_API_BASE_URL)
        rest_api.submit_order(symbol, quantity, 'buy')

    @staticmethod
    def sell_stocks(symbol, quantity, key_id, secret_key, feed='iex'):
        rest_api = StockManager.get_rest_api_connection(key_id, secret_key, APCA_API_BASE_URL)
        rest_api.submit_order(symbol, quantity, 'sell')

    @staticmethod
    def get_market_opening_time():
        return StockManager.get_rest_api_connection().get_clock()

    @staticmethod
    def get_stream_connection(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY, data_base_url=APCA_API_DATA_URL, feed='iex'):
        return Stream(
            key_id,
            secret_key,
            data_base_url,
            raw_data=True,
            data_feed=feed
        )

    @staticmethod
    def get_rest_api_connection(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY, base_url=APCA_API_BASE_URL):
        return REST(
            key_id,
            secret_key,
            base_url,
            api_version='v2',
            raw_data=True
        )

    @staticmethod
    def get_stock_bars(symbol, start_date=date.today().strftime("%Y-%m-%d"), interval_value=1, interval_unit='Minute'):
        if interval_unit == 'Month':
            interval_unit = TimeFrameUnit.Month
        elif interval_unit == 'Week':
            interval_unit = TimeFrameUnit.Week
        elif interval_unit == 'Day':
            interval_unit = TimeFrameUnit.Day
        elif interval_unit == 'Hour':
            interval_unit = TimeFrameUnit.Hour
        else:
            interval_unit = TimeFrameUnit.Minute

        api = StockManager.get_rest_api_connection()
        bars = api.get_bars(symbol, TimeFrame(interval_value, interval_unit), start=start_date).df
        if bars.size == 0:
            return None
        bars.pop('trade_count')

        candles = []
        timestamp = []
        for index, row in bars.iterrows():
            timestamp.append(
                index.isoformat()
            )
            candles.append(
                {
                    'Open': row['open'],
                    'High': row['high'],
                    'Low': row['low'],
                    'Close': row['close']
                }
            )

        stock_chart = StockChart(
            StockManager.get_stock_by_symbol(symbol),
            timestamp,
            candles,
            bars['volume'].tolist(),
            bars['vwap'].tolist(),
        )
        return stock_chart

    @staticmethod
    def get_latest_stock_bar(symbol):
        api = StockManager.get_rest_api_connection()
        bar = api.get_latest_bar(symbol)
        stock_bar = {
            'Timestamp': bar['t'],
            'Candles': {
                'Open': bar['o'],
                'High': bar['h'],
                'Low': bar['l'],
                'Close': bar['c'],
            },
            'Volume': bar['v'],
            'Vwap': bar['vw']
        }

        return stock_bar

    @staticmethod
    def get_stock_by_symbol(symbol):
        db = DatabaseWrapper()
        result = db.read("stocks", symbol=symbol)
        if result is not None and result:
            result = result[0]
            return Stock(result[0], result[1], result[2], result[3])
        return None

    @staticmethod
    def search_stocks_by_name(name):
        db = DatabaseWrapper()
        result = db.read("stocks", name=('%' + name + '%'), order_by='name', limit=10)
        response = {"body": {"symbols": [], "names": []}, "status": "Error while collecting data."}
        if result is not None and result:
            response['status'] = "OK"
            for row in result:
                response['body']['symbols'].append(row[1])
                response['body']['names'].append(row[2])

        return response

    @staticmethod
    def update_stocks():
        api = StockManager.get_rest_api_connection()
        # Get list of companies
        assets = api.list_assets(status='active')
        stocks = {
            "symbol": [],
            "name": [],
            "exchange": []
        }
        # Bulk insert companies specific data
        db = DatabaseWrapper()
        db.truncate("stocks")
        for asset in assets:
            if asset["tradable"]:
                stocks["symbol"].append(asset.get("symbol", ""))
                stocks["name"].append(asset.get("name", ""))
                stocks["exchange"].append(asset.get("exchange", ""))
        if not db.bulk_create("stocks", stocks):
            return None
        return True
