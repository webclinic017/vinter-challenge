from abc import ABC, abstractmethod
from typing import Final, Optional

from pandas import DataFrame

# Implemented data providers.
BINANCE_DATA_PROVIDER: Final[str] = "binance"
KNOWN_DATA_PROVIDERS: Final[list[str]] = [BINANCE_DATA_PROVIDER]


class DataProvider(ABC):
    """
    DataProvider abstract class.
    """

    @abstractmethod
    def __init__(
        self,
        data_provider_name: str,
        denomination_ticker: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
    ) -> None:
        """
        Abstract constructor of DataProvider class.

        :param data_provider_name: Data provider name.
        :param denomination_ticker: Denomination ticker.
        :param api_key: Binance API key.
        :param api_secret: Binance API secret.
        """
        self.data_provider_name: str = data_provider_name
        self.denomination_ticker: str = denomination_ticker
        self._api_key: Optional[str] = api_key
        self._api_secret: Optional[str] = api_secret

    @abstractmethod
    def get_historical_ohlcv_data(
        self,
        token_ticker: str,
        past_days: Optional[int] = None,
        tick_interval: Optional[str] = None,
    ) -> DataFrame:
        """
        Returns historical candlestick/bar data from past for given symbol and tick interval.

        :param token_ticker: Token/Coin ticker.
        :param past_days: How many days back one wants to download the data.
        :param tick_interval: Tick interval for bars.
        :return: OHLCV data in DataFrame format with date as index.
        """
        raise NotImplementedError
