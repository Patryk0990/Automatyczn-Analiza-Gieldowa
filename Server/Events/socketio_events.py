from flask_socketio import join_room, leave_room, emit, rooms
from flask import request, session
from Stock.stock_manager import StockManager
from Stock.stock_chart import StockChart
from User.user_manager import UserManager
from time import sleep
from threading import Thread
from datetime import datetime
thread = None
stream = None
watched_stocks = []
active_rooms_changed = False
latest_bars_changed = False


class SocketIOEvents:

    @staticmethod
    async def collect_bar(bar):
        global latest_bars_changed
        for watched_stock in watched_stocks:
            if watched_stock['symbol'] == bar['S']:
                for room in watched_stock['rooms']:
                    room['latest_bar'] = {
                        'stock': {
                            'charts': {
                                'Timestamp': datetime.fromtimestamp(bar['t'].seconds).isoformat(),
                                'Candles': {
                                    'Open': bar['o'],
                                    'High': bar['h'],
                                    'Low': bar['l'],
                                    'Close': bar['c']
                                },
                                'Volume': bar['v'],
                                'Vwap': bar['vw']
                            }
                        },
                        'interval_value': room['name'].split('_')[1],
                        'interval_unit': room['name'].split('_')[2],
                    }
        latest_bars_changed = True

    @staticmethod
    def collect_bar_thread():
        global stream
        stream = StockManager.get_stream_connection()
        stream.subscribe_bars(
            SocketIOEvents.collect_bar,
            ', '.join(watched_stock['symbol'] for watched_stock in watched_stocks)
        )
        stream.run()

    @staticmethod
    def rooms_live_data_manager(socketio):
        global active_rooms_changed
        global latest_bars_changed
        global watched_stocks
        global thread
        global stream
        last_subscriptions = None
        # Get Alpaca Stream connection
        while True:
            if latest_bars_changed:
                for watched_stock in watched_stocks:
                    for room in watched_stock['rooms']:
                        if 'latest_bar' in room:
                            socketio.emit(
                                'latest_bar',
                                room.pop('latest_bar'),
                                room=room['name'],
                                namespace='/trade/stocks/'
                            )
                print("Latest bars sent")
                latest_bars_changed = False
            if active_rooms_changed:
                if StockManager.get_market_opening_time()['is_open']:
                    if thread is None:
                        thread = Thread(target=SocketIOEvents.collect_bar_thread)
                        thread.start()
                    else:
                        if last_subscriptions is not None:
                            subscriptions = [watched_stock['symbol'] for watched_stock in watched_stocks]
                            subscriptions_to_add = ', '.join(set(subscriptions).difference(last_subscriptions))
                            subscriptions_to_remove = ', '.join(set(last_subscriptions).difference(subscriptions))
                            if len(subscriptions_to_remove) > 0:
                                stream.unsubscribe_bars(subscriptions_to_remove)
                            if len(subscriptions_to_add) > 0:
                                stream.subscribe_bars(
                                    SocketIOEvents.collect_bar,
                                    subscriptions_to_add
                                )
                elif thread is not None:
                    stream.stop()
                last_subscriptions = [watched_stock['symbol'] for watched_stock in watched_stocks]
                active_rooms_changed = False
                print(watched_stocks)
            sleep(5)

    @staticmethod
    def calculate_latest_interval_with_indicators(data):
        symbol = None
        for room in rooms(namespace='/trade/stocks/'):
            if room != request.sid:
                symbol = room.split('_')[0]

        stock_data = StockChart(
            StockManager.get_stock_by_symbol(symbol),
            data['charts']['Timestamp'],
            data['charts']['Candles'],
            data['charts']['Volume'],
            data['charts']['Vwap']
        )
        # Send status for error (default)
        predictions = None
        status = 'Error occurred while reading data. Error while connecting with external server or no data to retrive.'
        # Check if historical stock bars data has anything inside
        if stock_data is not None:
            # Load price prediction for priviliged clients
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                predictions = stock_data.get_predictions()
            # Get string dictionary representation of StockChart Class and change status
            stock_data = stock_data.__dict__()['charts']
            stock_data = {
                "Timestamp": stock_data['Timestamp'][-1],
                "Candles": stock_data['Candles'][-1],
                "Volume": stock_data['Volume'][-1],
                "Vwap": stock_data['Vwap'][-1],
                "RSI": stock_data['RSI'][-1],
                "MACD": stock_data['RSI'][-1],
                "MFI": stock_data['MFI'][-1],
                "EMA": stock_data['EMA'][-1]
            }
            status = "OK"
        emit('stocks_bar_update', {'stocks_bar': stock_data, 'predictions': predictions, 'status': status})

    @staticmethod
    def connect_trade_stocks():
        # Send data to connected user about market opening time
        emit('market_info', StockManager.get_market_opening_time())
        print("User connected - ", request.sid)

    @staticmethod
    def join_trade_stocks(data):
        global watched_stocks
        # Go through every room that user is connected to
        for room in rooms(namespace='/trade/stocks/'):
            # Check if room is not user-specific
            if room != request.sid:
                # Call a function to handle leaving room
                SocketIOEvents.leave_trade_stocks({"room": room})
        # Join room
        join_room(data['room'])
        print("User joined %s" % data['room'])
        # Split room into symbol, interval_value, interval_unit
        data['room'] = data['room'].split('_')

        # Check if symbol of a room that user wants to connect is already created
        if any(data['room'][0] in watched_stock['symbol'] for watched_stock in watched_stocks):
            for watched_stock in watched_stocks:
                # Check if watched_stock is specified for given symbol
                if watched_stock['symbol'] == data['room'][0]:
                    # Check if room has specific interval value and unit
                    if any('_'.join(data['room']) in room['name'] for room in watched_stock['rooms']):
                        # Add user to existing room
                        for room in watched_stock['rooms']:
                            if room['name'] == '_'.join(data['room']):
                                room['users'].append(request.sid)
                                break
                    else:
                        # Add new room
                        watched_stock['rooms'].append({
                            'name': '_'.join(data['room']),
                            'users': [request.sid]
                        })
                    break
            print("Modified active room - new user")
        else:
            # Add new watched_stock for specified symbol and interval value and unit
            global active_rooms_changed
            watched_stocks.append({
                'symbol': data['room'][0],
                'rooms': [
                    {
                        'name': '_'.join(data['room']),
                        'users': [request.sid]
                    }
                ]
            })
            active_rooms_changed = True
            print("Added new active room")
        # Check if start_date is specified
        if len(data['start_date']) == 0:
            data['start_date'] = None
        # Get historical stock bars data
        stock_data = StockManager.get_stock_bars(
            data['room'][0],
            interval_value=int(data['room'][1]),
            interval_unit=data['room'][2],
            start_date=data['start_date']
        )
        # Send status for error (default)
        predictions = None
        status = 'Error occurred while reading data. Error while connecting with external server or no data to retrive.'
        # Check if historical stock bars data has anything inside
        if stock_data is not None:
            # Load price prediction for priviliged clients
            user = UserManager.load_user(
                session.get('user').get('id'),
                session.get('user').get('username'),
                session.get('user').get('permission_level'),
                session.get('user').get('authenticated'),
                session.get('user').get('active')
            )
            if user.is_privileged():
                predictions = stock_data.get_predictions()
            # Get string dictionary representation of StockChart Class and change status
            stock_data = stock_data.__dict__()
            status = "OK"
        # Get latest bar data for buy/sell information
        latest_bar = StockManager.get_latest_stock_bar(data['room'][0])
        # Send data to user that sent request
        emit('stock_bars', {'stock': stock_data, 'latest_bar': latest_bar, 'predictions': predictions, 'status': status})

    @staticmethod
    def leave_trade_stocks(data):
        global watched_stocks
        # Leave room
        leave_room(data['room'])
        print("User left %s" % data['room'])
        # Split room into symbol, interval_value, interval_unit
        data['room'] = data['room'].split('_')
        # Look for every room that user was connected to
        for watched_stock in watched_stocks:
            # Check if watched_stock has symbol of a room that user was connected to
            # and if it has only 1 active room with 1 user
            if watched_stock['symbol'] == data['room'][0] and len(watched_stock['rooms']) == 1 and len(watched_stock['rooms'][0]['users']) == 1:
                # Remove watched stock
                global active_rooms_changed
                active_rooms_changed = True
                watched_stocks.remove(watched_stock)
                break
            # Check if watched_stock has symbol of a room that user was connected to
            elif watched_stock['symbol'] == data['room'][0]:
                for room in watched_stock['rooms']:
                    # Check if user disconnects from room and if it has only 1 user
                    if room['name'] == '_'.join(data['room']) and len(room['users']) == 1:
                        # Remove room
                        watched_stock['rooms'].remove(room)
                        break
                    # Check if user disconnects from room
                    elif room['name'] == '_'.join(data['room']):
                        # Remove user from room
                        room['users'].remove(request.sid)
                        break
                break

    @staticmethod
    def disconnect_trade_stocks():
        # Go through every room that user is connected to
        for room in rooms(namespace='/trade/stocks/'):
            # Call a function to handle leaving room
            SocketIOEvents.leave_trade_stocks({"room": room})
        print("User disconnected - ", request.sid)
