"""
SQLAlchemy model for dim_ticker_type_tb table.
"""
from db.session import Base
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship


class TickerType(Base):
    """
    SQLAlchemy model for dim_ticker_type_tb table.
    
    Attributes:
        ticker_type_id: Primary key
        ticker_type_nm: Name of the ticker type
        is_src: Boolean indicating if this is a source ticker
        tickers: Relationship to Ticker model
    """
    __tablename__ = "dim_ticker_type_tb"
    __table_args__ = {"schema": "financial_s"}

    ticker_type_id = Column(String, primary_key=True, index=True)
    ticker_type_nm = Column(String, index=True)
    is_src = Column(Boolean)
    
    # Relationship with Ticker model
    tickers = relationship("Ticker", back_populates="ticker_type")
