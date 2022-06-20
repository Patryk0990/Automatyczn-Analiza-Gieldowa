class Stock:

    def __init__(self, stock_id, symbol, name, exchange):
        self.__id = stock_id
        self.__symbol = symbol
        self.__name = name
        self.__exchange = exchange

    def get_id(self):
        return self.__id

    def get_symbol(self):
        return self.__symbol

    def get_name(self):
        return self.__name

    def get_exchange(self):
        return self.__exchange
