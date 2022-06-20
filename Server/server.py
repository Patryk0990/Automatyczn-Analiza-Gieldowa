from Server.flaskappwrapper import FlaskAppWrapper
from Server.Routes.routes import Routes
from Server.socketiowrapper import SocketIOWrapper
from Server.Events.socketio_events import SocketIOEvents
from Database.databasewrapper import DatabaseWrapper


class Server:

    def __init__(self, config):
        DatabaseWrapper().create_database_schema()
        self.__flask_app = FlaskAppWrapper(config)
        self.__set_routes()
        self.__socketio = SocketIOWrapper(self.__flask_app.get_app_object())
        self.__set_socketio_events()
        self.__socketio.get_socketio_object().start_background_task(
            SocketIOEvents.rooms_live_data_manager,
            self.__socketio.get_socketio_object()
        )

    def __set_routes(self):
        self.__flask_app.add_endpoint(
            '/',
            'index',
            Routes.render_index_view,
            ['GET', 'POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/',
            'dashboard',
            Routes.render_dashboard_view
        )
        self.__flask_app.add_endpoint(
            '/dashboard/user/settings/interface/update/',
            'update_user_interface_settings',
            Routes.render_update_user_interface_settings
        )
        self.__flask_app.add_endpoint(
            '/dashboard/user/settings/api/change/',
            'change_user_api_settings',
            Routes.render_change_user_api_settings,
            ['GET', 'POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/admin/user/manage/',
            'manage_users',
            Routes.render_manage_users_view
        )
        self.__flask_app.add_endpoint(
            '/dashboard/admin/user/modify/',
            'modify_user',
            Routes.render_modify_user_view,
            ['GET', 'POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/admin/user/delete',
            'delete_user',
            Routes.render_delete_user_view,
            ['GET', 'POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/user/password/change/',
            'change_user_password',
            Routes.render_change_user_password_view,
            ['GET', 'POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/positions/get/',
            'get_positions',
            Routes.render_get_positions,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/account/budget/',
            'get_account_budget',
            Routes.render_get_account_budget,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/buy/',
            'buy_stocks',
            Routes.render_buy_stocks,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/sell/',
            'sell_stocks',
            Routes.render_sell_stocks,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/view/',
            'view_stocks',
            Routes.render_stocks_view,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/search/',
            'search_stocks',
            Routes.render_stocks_search,
            ['POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/graph/',
            'get_stocks_candles',
            Routes.render_stocks_graph,
            ['POST']
        )
        self.__flask_app.add_endpoint(
            '/dashboard/trade/stocks/update/',
            'update_stocks',
            Routes.render_update_stocks,
            ['GET']
        )
        self.__flask_app.add_endpoint(
            '/logout/',
            'logout',
            Routes.render_logout_user
        )

    def __set_socketio_events(self):

        self.__socketio.add_event(
            'connect',
            SocketIOEvents.connect_trade_stocks,
            '/trade/stocks/'
        )
        self.__socketio.add_event(
            'disconnect',
            SocketIOEvents.disconnect_trade_stocks,
            '/trade/stocks/'
        )
        self.__socketio.add_event(
            'join',
            SocketIOEvents.join_trade_stocks,
            '/trade/stocks/'
        )
        self.__socketio.add_event(
            'leave',
            SocketIOEvents.leave_trade_stocks,
            '/trade/stocks/'
        )
        self.__socketio.add_event(
            'calculate_latest_interval_with_indicators',
            SocketIOEvents.calculate_latest_interval_with_indicators,
            '/trade/stocks/'
        )

    def run(self, **kwargs):
        self.__socketio.get_socketio_object().run(self.__flask_app.get_app_object(), **kwargs)
