import pandas
import matplotlib.pyplot as plot
import time

class Portfolio:
    def __init__(self, starting_balance, filepath):
        self.filepath = filepath
        self.starting_balance = starting_balance
        self.trades = pandas.DataFrame([], columns = ['order_time', 'symbol', 'order_type', 'quantity', 'price'])
        self.trades = self.trades.set_index('order_time')

    def save_trades(self):
        self.trades.to_csv(self.filepath)

    def load_trades(self):
        self.trades = pandas.read_csv(self.filepath)
        self.trades = self.trades.set_index('order_time')

    def trade(self, symbol: str, order_type: bool, quantity: int, price: float, order_time: int = None):
        if order_time is None:
            order_time = time.time()

        order_time = round(order_time)

        new_trade = pandas.DataFrame(
            [[order_time, symbol, order_type, quantity, price]],
            columns = ['order_time', 'symbol', 'order_type', 'quantity', 'price']
        )
        new_trade = new_trade.set_index('order_time')

        if self.trades.empty:
            self.trades = new_trade

        else:
            self.trades = pandas.concat([self.trades, new_trade])
            self.trades = self.trades.sort_index()

    def get_balance_over_time(self):
        balances = [self.starting_balance]
        for i in range(len(self.trades.index)):
            trade = self.trades.iloc[i]
            balances.append(balances[i] + (trade['quantity'] * trade['price'] * (-1 if trade['order_type'] else 1)))

        return balances

    def get_balance(self):
        balance = self.starting_balance
        for i in range(len(self.trades.index)):
            trade = self.trades.iloc[i]
            balance += trade['quantity'] * trade['price'] * (-1 if trade['order_type'] else 1)

        return balance

    def get_equity_over_time(self):
        balance = self.starting_balance
        positions = {}
        prices = {}
        equities = [balance]

        for _, trade in self.trades.iterrows():
            symbol = trade['symbol']
            qty = trade['quantity']
            price = trade['price']

            balance += qty * price * (-1 if trade['order_type'] else 1)

            positions[symbol] = positions.get(symbol, 0) + (qty if trade['order_type'] else -qty)
            prices[symbol] = trade['price']

            total_equity = balance
            for symbol, qty in positions.items():
                if qty != 0:
                    last_price = prices.get(symbol, 0.0)
                    total_equity += qty * last_price

            equities.append(total_equity)

        return equities

    def get_equity(self, custom_prices = {}):
        balance = self.starting_balance
        positions = {}
        prices = {}

        for _, trade in self.trades.iterrows():
            symbol = trade['symbol']
            qty = trade['quantity']
            price = trade['price']

            balance += qty * price * (-1 if trade['order_type'] else 1)

            positions[symbol] = positions.get(symbol, 0) + (qty if trade['order_type'] else -qty)
            prices[symbol] = trade['price']

        total_equity = balance
        for symbol, qty in positions.items():
            if qty != 0:
                last_price = custom_prices.get(symbol, prices.get(symbol, 0.0))
                total_equity += qty * last_price

        return total_equity

    def get_all_assets(self):
        positions = {}

        for _, trade in self.trades.iterrows():
            symbol = trade['symbol']
            qty = trade['quantity']

            positions[symbol] = positions.get(symbol, 0) + (qty if trade['order_type'] else -qty)

        return positions

    def get_latest_asset_prices(self):
        return self.trades.groupby('symbol')['price'].last().to_dict()

    def get_asset_values(self, custom_prices = {}):
        positions = self.get_all_assets()
        latest_prices = self.get_latest_asset_prices()

        asset_values = {}
        for symbol, qty in positions.items():
            if qty != 0:
                price = custom_prices.get(symbol, latest_prices.get(symbol, 0.0))
                asset_values[symbol] = qty * price

        return asset_values

    def get_total_asset_equity(self):
        asset_values = self.get_asset_values()
        return sum(list(asset_values.values()))

    def plot_equity_over_time(self):
        equity = self.get_equity_over_time()
        index = pandas.to_datetime(self.trades.index, unit = 's')
        adj_index = [index[0]] + list(index) # because of the starting balance

        plot.plot(adj_index, equity)

    def plot_growth_over_time(self):
        equity = self.get_equity_over_time()
        equity = [(e / equity[0]) - 1 for e in equity]
        index = pandas.to_datetime(self.trades.index, unit = 's')
        adj_index = [index[0]] + list(index) # because of the starting balance

        plot.plot(adj_index, equity)