"""
SQLAlchemy model for dim_ticker_tb table.
"""

from db.session import Base
from models.financial.dim_ticker_type import TickerType
from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.orm import relationship


class Ticker(Base):
    """
    SQLAlchemy model for dim_ticker_tb table.

    Attributes:
        ticker_id: Primary key
        ticker_nm: Name of the ticker
        ticker_type_id: Foreign key to TickerType
        annual_tax: Annual tax rate
        ticker_type: Relationship to TickerType model
    """

    __tablename__ = "dim_ticker_tb"
    __table_args__ = {"schema": "financial_s"}

    ticker_id = Column(String, primary_key=True, index=True)
    ticker_nm = Column(String, index=True)
    ticker_type_id = Column(String, ForeignKey("financial_s.dim_ticker_type_tb.ticker_type_id"))
    annual_tax = Column(Numeric)

    # Relationship with TickerType model
    ticker_type = relationship("TickerType", back_populates="tickers")
