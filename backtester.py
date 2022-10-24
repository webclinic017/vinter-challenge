import logging
from datetime import datetime

import backtrader as bt
import quantstats as qs
from backtrader import Cerebro
from backtrader_plotting import Bokeh
from pandas import DataFrame

from backtest_result import BacktestResult
from daily_data_feed import PandasDataFeedDaily
from fractional_commission_info import FractionalCommissionInfo
from strategies import KDJ, KDJStrategy


class Backtester:
    """
    Backtester class.
    """

    def __init__(
        self,
        with_graphs: bool = True,
        starting_cash: float = 100_000.0,
        commission: float = 0.0,
    ) -> None:
        """
        Constructor.

        :param with_graphs: Flag for plotting graphs.
        :param starting_cash: Starting cash for backtesting strategy.
        :param commission: Commission.
        """
        self._with_graphs: bool = with_graphs
        self._starting_cash: float = starting_cash
        self._commission: float = commission

    def backtest(
        self,
        token_ticker: str,
        denomination_ticker: str,
        strategy_name: str,
        price_data: DataFrame,
    ) -> BacktestResult:

        token_ticker: str = token_ticker.lower()
        denomination_ticker: str = denomination_ticker.lower()
        strategy_name: str = strategy_name.lower()
        # backtest_name: str = f"Backtest of {token_ticker} in {denomination_ticker} with {strategy_name} strategy"

        # Init Cerebro engine.
        cerebro: Cerebro = bt.Cerebro()

        # Add the trading strategy.
        if strategy_name == KDJ:
            logging.info(f"Selecting {strategy_name} strategy.")
            cerebro.addstrategy(KDJStrategy)

        else:
            logging.error(f"Unknown strategy: '{strategy_name}' strategy.")
            raise Exception(f"Unknown strategy: '{strategy_name}' strategy.")

        # Add data.
        feed: bt.feeds.PandasData = PandasDataFeedDaily(dataname=price_data)
        cerebro.adddata(feed, name=f"{token_ticker} in {denomination_ticker}")

        # Set cash.
        cerebro.broker.setcash(cash=self._starting_cash)
        cerebro.broker.addcommissioninfo(FractionalCommissionInfo())

        # Set sizer, invest 100% per trade, only one active trade.
        cerebro.addsizer(bt.sizers.PercentSizer, percents=100.0)

        # Set commission.
        cerebro.broker.setcommission(commission=self._commission)

        # Add observers that are used in plots.
        cerebro.addobserver(bt.observers.DrawDown)

        # Add preferred analyzers for generating performance metrics for the strategy.
        cerebro.addanalyzer(
            bt.analyzers.SharpeRatio,
            _name="SharpeRatio",
            riskfreerate=0,
            timeframe=bt.TimeFrame.Days,
            compression=1,
            factor=365,
            annualize=True,
        )
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DrawDown")
        cerebro.addanalyzer(bt.analyzers.PyFolio, _name="PyFolio")
        cerebro.addanalyzer(bt.analyzers.AnnualReturn, _name="AnnualReturn")

        # Backtest!
        logging.info(f"Starting portfolio value: {cerebro.broker.getvalue()}")
        results = cerebro.run()
        strat = results[0]
        returns, positions, transactions, gross_lev = strat.analyzers.getbyname(
            "PyFolio"
        ).get_pf_items()
        returns.index = returns.index.tz_convert(None)
        logging.info(
            f"Final portfolio value: ${cerebro.broker.getvalue():.2f} "
            f"(starting value: ${self._starting_cash:.2f})"
        )

        # Build result.
        br: BacktestResult = BacktestResult()
        br.token_ticker = token_ticker
        br.denomination_ticker = denomination_ticker
        br.strategy_name = strategy_name
        br.total_returns = strat.analyzers.getbyname("AnnualReturn").rets
        br.sharpe_ratio = strat.analyzers.getbyname("SharpeRatio").rets["sharperatio"]
        br.max_draw_down = strat.analyzers.getbyname("DrawDown").rets["max"]["drawdown"]
        br.with_graphs = self._with_graphs
        br.cash = strat.broker.get_cash()

        # Plot the result.
        if self._with_graphs:
            report_path: str = (
                f"./reports/{str(datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))}_"
                f"{strategy_name}_strategy_"
                f"{token_ticker}_in_{denomination_ticker}_"
            )
            bokeh_report_path: str = f"{report_path}bokeh_report.html"
            quantstats_report_path: str = f"{report_path}quantstat_report.html"
            br.bokeh_report_path = bokeh_report_path
            br.quantstats_report_path = quantstats_report_path

            # Quantstat report.
            qs.reports.html(
                returns,
                output=quantstats_report_path,
                download_filename=quantstats_report_path,
                title=strategy_name,
                periods_per_year=365,
            )

            # Backtrader Bokeh report.
            try:
                bpl: Bokeh = Bokeh(
                    style="bar",
                    plot_mode="single",
                    filename=bokeh_report_path,
                    show=False,
                )
                cerebro.plot(bpl)
            except Exception as error:
                logging.warning(
                    f"Can not create interactive Bokeh HTML reports. Error: {error}"
                )
                # raise error

        return br
