from datetime import datetime

from backtrader.feeds import PandasData


class PandasDataFeedDaily(PandasData):
    lines: tuple = ()

    params: tuple = (
        # Possible values for datetime (must always be present)
        #  None : datetime is the "index" in the Pandas Dataframe
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ("fromdate", datetime(2010, 1, 1)),
        ("dtformat", "%Y-%m-%d"),
        ("datetime", None),
        # Possible values below:
        #  None : column not present
        #  -1 : autodetect position or case-wise equal name
        #  >= 0 : numeric index to the colum in the pandas dataframe
        #  string : column name (as index) in the pandas dataframe
        ("open", "open"),
        ("high", "high"),
        ("low", "low"),
        ("close", "close"),
        ("volume", "volume"),
    )
