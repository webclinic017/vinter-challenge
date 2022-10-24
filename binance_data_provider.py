import datetime as dt
import logging
from typing import Optional

import pandas as pd
from binance.client import Client
from pandas import DataFrame, Timestamp

from data_provider import DataProvider


class BinanceDataProvider(DataProvider):
    """
    BinanceDataProvider class.
    """

    def __init__(
        self, api_key: str, api_secret: str, denomination_ticker: str = "usdt"
    ) -> None:
        """
        Constructor.

        :param api_key: Binance API key.
        :param api_secret: Binance API secret.
        """
        super().__init__(
            data_provider_name="binance",
            denomination_ticker=denomination_ticker,
            api_key=api_key,
            api_secret=api_secret,
        )
        self._client: Client = Client(api_key=api_key, api_secret=api_secret)
        logging.info(
            f"Providing OHLCV data in {self.denomination_ticker.upper()} denomination."
        )

    def get_historical_ohlcv_data(
        self,
        token_ticker: str,
        past_days: Optional[int] = None,
        tick_interval: Optional[str] = None,
    ) -> Optional[DataFrame]:
        """
        Returns historical K-lines (candlestick data) from past for given symbol and tick interval.

        :param token_ticker: Token/Coin ticker e.g. uni, 1inch, etc.
        :param past_days: How many days back one wants to download the data.
        :param tick_interval: Tick interval for bars, e.g. 1d.
        :return: OHLCV data in DataFrame format with date as index.
        """

        if not tick_interval:
            # Default interval 1 day.
            tick_interval: str = "1d"
            logging.warning(
                f"Tick interval was not set - setting default value: '{tick_interval}'."
            )
        if not past_days:
            # Default number of past days: 10_000 days.
            past_days: int = 10_000
            logging.warning(
                f"Number of past days was not set - setting default value: '{past_days}' days."
            )

        # Create token in denomination ticker for Binance, e.g. UNI + USDT = UNIUSDT ticker.
        token_denomination_ticker: str = (
            f"{token_ticker}{self.denomination_ticker}".upper()
        )

        # Start date string in UTC format.
        start_date_str: str = str(
            (pd.to_datetime("today") - pd.Timedelta(str(past_days) + " days")).date()
        )

        try:
            data: DataFrame = DataFrame(
                self._client.get_historical_klines(
                    symbol=token_denomination_ticker,
                    start_str=start_date_str,
                    interval=tick_interval,
                )
            )
        except Exception as error:
            logging.warning(
                f"Skipping: Binance does not have OHLCV data for: {token_denomination_ticker}"
            )
            logging.debug(f"Error: {error}")
            return None

        data.columns = [
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "qav",
            "num_trades",
            "taker_base_vol",
            "taker_quote_vol",
            "is_best_match",
        ]
        data.index = [
            Timestamp(dt.datetime.fromtimestamp(x / 1000).date())
            for x in data.open_time
        ]
        data: DataFrame = data[["open", "high", "low", "close", "volume"]]

        # Convert data to floats.
        data: DataFrame = data.astype(
            {
                "open": "float",
                "high": "float",
                "low": "float",
                "close": "float",
                "volume": "float",
            }
        )

        # Drop last 1 day - which means "toda" (incomplete data).
        data: DataFrame = data[:-1]
        return data
