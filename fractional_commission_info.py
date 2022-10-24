from backtrader import CommissionInfo


class FractionalCommissionInfo(CommissionInfo):
    """
    This class allows to trade fractional parts of assets, e.g. 0.1 BTC instead of 1 BTC.
    """

    def getsize(self, price, cash):
        """
        Returns fractional size for cash operation at price.

        :param price: Price.
        :param cash: Cash.
        :return:
        """
        return self.p.leverage * (cash / price)
