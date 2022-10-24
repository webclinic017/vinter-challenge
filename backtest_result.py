from typing import Optional


class BacktestResult:
    def __init__(
        self,
        token_ticker: Optional[str] = None,
        denomination_ticker: Optional[str] = None,
        strategy_name: Optional[str] = None,
        total_returns: Optional[list[float]] = None,
        sharpe_ratio: Optional[float] = None,
        max_draw_down: Optional[float] = None,
        with_graphs: Optional[bool] = None,
        cash: Optional[float] = None,
        bokeh_report_path: Optional[str] = None,
        quantstats_report_path: Optional[str] = None,
    ) -> None:
        self.token_ticker: Optional[str] = token_ticker
        self.denomination_ticker: Optional[str] = denomination_ticker
        self.strategy_name: Optional[str] = strategy_name
        self.total_returns: Optional[list[float]] = total_returns
        self.sharpe_ratio: Optional[float] = sharpe_ratio
        self.max_draw_down: Optional[float] = max_draw_down
        self.with_graphs: Optional[bool] = with_graphs
        self.cash: Optional[float] = cash
        self.bokeh_report_path: Optional[str] = bokeh_report_path
        self.quantstats_report_path: Optional[str] = quantstats_report_path
