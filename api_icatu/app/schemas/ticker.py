"""
Pydantic schemas for request and response validation.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


# Ticker Type Schemas
class TickerTypeBase(BaseModel):
    """Base schema for ticker type data."""

    ticker_type_nm: str
    is_src: bool = False


class TickerTypeCreate(BaseModel):
    """Schema for creating a new ticker type."""

    ticker_type_nm: str = Field(..., description="Ticker type name")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class TickerTypeResponse(TickerTypeBase):
    """Schema for ticker type in responses."""

    ticker_type_id: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Ticker Schemas
class TickerBase(BaseModel):
    """Base schema for ticker data."""

    ticker_nm: str
    annual_tax: Optional[Decimal] = Field(None, description="Annual tax rate")


class TickerCreate(TickerBase):
    """Schema for creating a new ticker."""

    ticker_type_nm: str


class TickerUpdate(BaseModel):
    """Schema for updating an existing ticker."""

    ticker_nm: Optional[str] = None
    ticker_type_nm: Optional[str] = None
    annual_tax: Optional[Decimal] = None
    new_ticker_nm: Optional[str] = None


class TickerResponse(TickerBase):
    """Schema for ticker in responses."""

    ticker_id: str
    ticker_type: TickerTypeResponse

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Profitability Schemas
class ProfitabilityRequest(BaseModel):
    """Schema for profitability calculation requests."""

    ticker_nm: str
    init_date: date
    end_date: date


class MonthlyProfitability(BaseModel):
    """Schema for monthly profitability data."""

    year: int
    month: int
    cumulative_return: float


class CumulativeProfitabilityResponse(BaseModel):
    """Schema for cumulative profitability response."""

    ticker_date: date
    cumulative_return: float


class MonthlyProfitabilityResponse(BaseModel):
    """Schema for monthly profitability response."""

    ticker_nm: str
    init_date: date
    end_date: date
    monthly_returns: List[MonthlyProfitability]


class TickerTypeResponse(BaseModel):
    """Schema for ticker type in responses."""

    ticker_type_id: str
    ticker_type_nm: str
    is_src: bool

    class Config:
        """Pydantic configuration."""

        from_attributes = True
