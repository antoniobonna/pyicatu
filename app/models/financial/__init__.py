"""
SQLAlchemy models package.
"""

from models.financial.dim_ticker import Ticker
from models.financial.dim_ticker_type import TickerType
from sqlalchemy.orm import relationship

Ticker.ticker_type = relationship("TickerType", back_populates="tickers")
TickerType.tickers = relationship("Ticker", back_populates="ticker_type")
