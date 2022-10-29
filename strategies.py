import logging
from typing import Final

import backtrader as bt
from backtrader import Indicator, Strategy
from backtrader.indicators import ExponentialMovingAverage, Highest, Lowest

# Implemented strategies.
KDJ: Final[str] = "kdj"
KNOWN_STRATEGIES: Final[list[str]] = [KDJ]


class KDJStrategy(Strategy):
    """
    KDJStrategy class.
    """

    params = dict(h_period=14, l_period=14, ema_period=3)

    def __init__(self) -> None:
        """
        Constructor.
        """
        self.log("Initializing KDJStrategy.")

        self.data_id: int = 0
        self.data_close = self.datas[self.data_id].close
        self.volume = self.datas[self.data_id].volume
        self.order = None
        self.buy_price = None
        self.buy_comm = None
        self.bar_executed_close = None
        self.bar_executed = None

        # Highest price in X trading days.
        self.high = Highest(self.data.high, period=self.p.h_period, plot=False)
        # Lowest price in X trading days.
        self.low = Lowest(self.data.low, period=self.p.l_period, plot=False)
        # Calculate RSV value.

        self.rsv = 100.0 * bt.DivByZero(
            self.data.close - self.low, self.high - self.low, zero=0.0
        )
        self.rsv.plot = False

        # Calculate the 3-period weighted average of rsv, the K value.
        self.K = ExponentialMovingAverage(
            self.rsv, period=self.p.ema_period, plot=False
        )
        # D value is 3-period weighted average of K values.
        self.D = ExponentialMovingAverage(self.K, period=self.p.ema_period, plot=False)
        # J=3*K-2*D
        self.J: Indicator = 3 * self.K - 2 * self.D
        self.J.plot = False

    def log(self, txt: str, dt=None) -> None:
        """
        Logging method.

        :param txt: Text.
        :param dt: Date time.
        :return: None.
        """
        dt = dt or self.datas[0].datetime.date(0)
        logging.info(f"{dt.isoformat()}: {txt}")

    def notify_order(self, order):
        """
        Order notification.

        :param order: Order object.
        :return: None.
        """
        if order.status is order.Submitted:
            self.log("Order Submitted.")
            return
        elif order.status is order.Accepted:
            self.log("Order Accepted.")
            self.order = order
            return
        elif order.status is order.Expired:
            self.log("Order Expired.")
        elif order.status is order.Completed:
            if order.isbuy():
                self.log(
                    f"BUY EXECUTED, "
                    f"Price: ${order.executed.price:.2f}, "
                    f"Cost: ${order.executed.value:.2f}, "
                    f"Commission: ${order.executed.comm:.2f}."
                )

                self.buy_price = order.executed.price
                self.buy_comm = order.executed.comm
                self.bar_executed_close = self.data_close[0]
            else:
                self.log(
                    f"SELL EXECUTED, "
                    f"Price: ${order.executed.price:.2f}, "
                    f"Cost: ${order.executed.value:.2f}, "
                    f"Commission: ${order.executed.comm:.2f}."
                )
            self.bar_executed = len(self)
        elif order.status is order.Canceled:
            self.log("Order Canceled.")
        elif order.status is order.Margin:
            self.log("Order Margin.")
        elif order.status is order.Rejected:
            self.log("Order Rejected.")

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(
            f"OPERATION PROFIT, GROSS: ${trade.pnl:.2f}, NET: ${trade.pnlcomm:.2f}"
        )

    def next(self):
        if self.order:
            return

        condition_yesterday = self.J[-1] - self.D[-1]
        condition_today = self.J[0] - self.D[0]
        if not self.position:
            # J - D value
            # D is crossing J, from bellow up
            # KDJ is indicating golden and dead crosses
            if condition_yesterday < 0 < condition_today:
                self.log(f"BUY CREATE, {self.data.close[0]:.2f}")
                self.order = self.buy()

        else:
            if condition_yesterday > 0 or condition_today < 0:
                self.log(f"SELL CREATE, {self.data.close[0]:.2f}")
                self.order = self.sell()

        # Log some values for the reference.
        self.log(
            f"Close: ${self.data.close[0]:.2f}, "
            f"DrawDown: {self.stats.drawdown.drawdown[0]:.2f}, "
            f"MaxDrawDown: {self.stats.drawdown.maxdrawdown[0]:.2f}, "
            f"Cash: ${self.broker.get_cash():.2f}"
        )
