from stocks.datalayer import LiveStock

TOP_100_STOCKS_SYMBOLS = [
    "ATVI", "ADBE", "AMD", "ALXN", "ALGN", "GOOG", "GOOGL", "AMZN", "AMGN", "ADI", "ANSS", "AAPL",
    "AMAT", "ASML", "ADSK", "ADP", "BIDU", "BIIB", "BMRN", "BKNG", "AVGO", "CDNS", "CDW", "CERN",
    "CHTR", "CHKP", "CTAS", "CSCO", "CTXS", "CTSH", "CMCSA", "CPRT", "CSGP", "COST", "CSX",
    "DXCM", "DOCU", "DLTR", "EBAY", "EA", "EXC", "EXPE", "FB", "FAST", "FISV", "FOX", "FOXA",
    "GILD", "IDXX", "ILMN", "INCY", "INTC", "INTU", "ISRG", "JD", "KLAC", "LRCX", "LBTYA",
    "LBTYK", "LULU", "MAR", "MXIM", "MELI", "MCHP", "MU", "MSFT", "MDLZ", "MNST", "NTAP", "NTES",
    "NFLX", "NVDA", "NXPI", "ORLY", "PCAR", "PAYX", "PYPL", "PEP", "QCOM", "REGN", "ROST", "SGEN",
    "SIRI", "SWKS", "SPLK", "SBUX", "SNPS", "TMUS", "TTWO", "TSLA", "TXN", "KHC", "TCOM", "ULTA",
    "VRSN", "VRSK", "VRTX", "WBA", "WDC", "WDAY", "XEL", "XLNX", "ZM"
]

TOP_100_STOCKS = [LiveStock.from_stock_name(x) for x in TOP_100_STOCKS_SYMBOLS]
