# FINPLUS/stock.py

from typing import Union, List

class Stock:
    def __init__(self, stock_id: Union[str, List[str]]):
        """
        Initializes the Stock object with one or multiple stock IDs.

        Args:
            stock_id (Union[str, List[str]]): A single stock ID or a list of stock IDs.
        """
        if isinstance(stock_id, str):
            self.stock_ids = [stock_id]
        else:
            self.stock_ids = stock_id

    def __repr__(self):
        return f"<Stock(stock_ids={self.stock_ids})>"

    def get_all_stock_ids(self) -> List[str]:
        """
        Returns the list of stock IDs associated with this Stock object.

        Returns:
            List[str]: The list of stock IDs.
        """
        return self.stock_ids

class Portfolio:
    def __init__(self, stocks: Union[Stock, List[Stock]] = None):
        """
        Initializes the Portfolio object with one or multiple Stock objects.

        Args:
            stocks (Union[Stock, List[Stock]], optional): A single Stock object or a list of Stock objects.
                                                         Defaults to None.
        """
        self.stocks = []
        if stocks:
            if isinstance(stocks, Stock):
                self.stocks.append(stocks)
            elif isinstance(stocks, list):
                self.add_stocks(stocks)

    def add_stock(self, stock: Stock):
        """
        Adds a Stock object to the portfolio.

        Args:
            stock (Stock): A Stock object to be added to the portfolio.
        """
        self.stocks.append(stock)

    def add_stocks(self, stocks: List[Stock]):
        """
        Adds multiple Stock objects to the portfolio.

        Args:
            stocks (List[Stock]): A list of Stock objects to be added to the portfolio.
        """
        self.stocks.extend(stocks)

    def remove_stock(self, stock: Stock):
        """
        Removes a Stock object from the portfolio.

        Args:
            stock (Stock): A Stock object to be removed from the portfolio.
        """
        self.stocks.remove(stock)

    def get_all_stock_ids(self) -> List[str]:
        """
        Returns a list of all stock IDs in the portfolio.

        Returns:
            List[str]: A list of stock IDs from all Stock objects in the portfolio.
        """
        stock_ids = []
        for stock in self.stocks:
            stock_ids.extend(stock.get_all_stock_ids())
        return stock_ids

    def __repr__(self):
        return f"<Portfolio({len(self.stocks)} stocks)>"
