import argparse
import logging
from typing import Optional

from pandas import DataFrame

from backtest_result import BacktestResult
from backtester import Backtester
from binance_data_provider import BinanceDataProvider
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from data_provider import BINANCE_DATA_PROVIDER, DataProvider
from utils import logging_setup


def gather_data(
    token_tickers: list[str],
    data_provider_name: Optional[str],
) -> tuple[dict[str, DataFrame], DataProvider]:
    """
    Gather OHLCV data.

    :param token_tickers: List of token tickers for which gather OHLCV data.
    :param data_provider_name: Data provider name.
    :return: Tuple of dictionary with token ticker as name and OHLCV data DataFrame as value and DataProvider object.
    """
    if not data_provider_name:
        data_provider_name: str = BINANCE_DATA_PROVIDER
        logging.warning(
            f"No data provider was entered. Setting it to: '{data_provider_name}' data provider."
        )
    else:
        data_provider_name: str = data_provider_name.lower()

    # Set data provider.
    if data_provider_name == BINANCE_DATA_PROVIDER:
        dp: BinanceDataProvider = BinanceDataProvider(
            api_key=str(BINANCE_API_KEY), api_secret=str(BINANCE_API_SECRET)
        )
    else:
        logging.error(f"Unknown data provider: {data_provider_name}")
        raise Exception(f"Unknown data provider: {data_provider_name}")

    logging.info(f"Using '{dp.data_provider_name}' data provider.")

    ohlcv_data: dict[str, DataFrame] = {}
    for token_ticker in token_tickers:
        logging.info(f"Gathering OHLCV data for: {token_ticker.upper()}")
        ohlcv_data[token_ticker] = dp.get_historical_ohlcv_data(
            token_ticker=token_ticker
        )

    return ohlcv_data, dp


def log_aggregated_results(backtesting_results: list[BacktestResult]) -> None:
    """
    Log aggregated results for all pairs.

    :param backtesting_results: List of BacktestResult objects.
    :return: None.
    """
    # TODO: Use pprint.
    logging.info(
        "Strategy name |   Pair   | Sharpe | Max DD |         Total returns          | Cash"
    )
    for r in backtesting_results:
        logging.info(
            f"Strategy {r.strategy_name.upper()}  | {r.token_ticker}/{r.denomination_ticker} | "
            f"{r.sharpe_ratio:.2f} | {-1.0 * r.max_draw_down:.2f}% | "
            f"{[f'{i * 100.0:.2f}%' for i in r.total_returns]} | ${r.cash:.2f}"
        )


def backtest(
    token_tickers: list[str],
    strategy_names: list[str],
    data_provider_name: Optional[str] = None,
    with_graphs: bool = False,
) -> None:
    """
    Entrypoint for backtesting.

    :param token_tickers: List of token tickers, e.g.: uni, 1inch, etc.
    :param strategy_names: List of strategy names.
    :param data_provider_name: Data provider for OHLCV prices.
    :param with_graphs: Flag for enabling or disabling plotting.
    :return: None.
    """
    logging.info("Sanity check of input parameters ...")

    # Token tickers.
    if token_tickers:
        token_tickers: list[str] = [
            token_ticker.lower() for token_ticker in token_tickers
        ]
    else:
        token_tickers: list[str] = [
            "uni",
            "aave",
            "snx",
            "crv",
            "comp",
            "1inch",
            "yfi",
            "zen",
        ]
        logging.warning(
            f"No token ticker was provided. Using default token tickers: {token_tickers}"
        )

    # Strategies.
    if strategy_names:
        strategy_names: list[str] = [
            strategy_name.lower() for strategy_name in strategy_names
        ]
    else:
        logging.error("No strategy name was provided.")
        raise Exception("No strategy name was provided.")

    # Gather data.
    logging.info("Starting gathering OHLCV data ...")
    token_ohlcv_data, data_provider = gather_data(
        token_tickers=token_tickers,
        data_provider_name=data_provider_name,
    )

    # Perform backtests.
    logging.info("Starting backtesting ...")
    backtester: Backtester = Backtester(with_graphs=with_graphs)
    backtesting_results: list[BacktestResult] = []
    for token_ticker, price_data in token_ohlcv_data.items():
        for strategy_name in strategy_names:
            logging.info(
                f"Backtesting {token_ticker.upper()} with {strategy_name} strategy."
            )
            backtesting_results.append(
                backtester.backtest(
                    token_ticker=token_ticker,
                    denomination_ticker=data_provider.denomination_ticker,
                    strategy_name=strategy_name,
                    price_data=price_data,
                )
            )

    # Log aggregated results.
    log_aggregated_results(backtesting_results=backtesting_results)


if __name__ == "__main__":
    """
    Main entry point.
    """
    # Logging setup.
    logging_setup()

    logging.info(f"Starting Vinter tech challenge (by Lukas Bures).")

    logging.debug("Parsing input parameters ...")
    parser = argparse.ArgumentParser(description="Main parser")
    parser.add_argument(
        "-tt",
        "--token-tickers",
        nargs="+",
        dest="token_tickers",
        help="List of token tickers.",
    )
    parser.add_argument(
        "-us",
        "--use-strategies",
        nargs="+",
        dest="strategy_names",
        required=True,
        help="List of strategy names for backtesting.",
    )
    parser.add_argument(
        "-dp",
        "--data-provider",
        dest="data_provider_name",
        help="Data provider name.",
    )
    parser.add_argument(
        "-wg",
        "--with-graphs",
        dest="with_graphs",
        action="store_true",
        help="Plot graphs.",
    )
    parser.set_defaults(with_graphs=False)

    args = parser.parse_args()
    logging.info(f"Input parameters: {vars(args)}")
    backtest(**vars(args))
