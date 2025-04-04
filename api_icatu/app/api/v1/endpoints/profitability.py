from typing import Any

from crud.financial import TickerService
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.ticker import (
    CumulativeProfitabilityResponse,
    MonthlyProfitabilityResponse,
    ProfitabilityRequest,
)
from sqlalchemy.orm import Session

from pyicatu.financial_metrics import FinancialMetrics

router = APIRouter(tags=["Rentabilidade"])


@router.post("/profitability/cumulative", response_model=list[CumulativeProfitabilityResponse])
def calculate_cumulative_profitability(
    request: ProfitabilityRequest, db: Session = Depends(get_db)
) -> Any:
    """
    Calcula rentabilidade cumulativa para um ticker.
    """
    # Check if ticker exists
    ticker = TickerService.get_ticker_by_name(db, request.ticker_nm)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{request.ticker_nm}' not found"
        )

    # Create FinancialMetrics instance directly
    metrics_obj = FinancialMetrics()

    # Calculate profitability
    cumulative_return = metrics_obj.get_cumulative_profitability(
        request.ticker_nm, request.init_date, request.end_date
    )

    return cumulative_return


@router.post("/profitability/monthly", response_model=MonthlyProfitabilityResponse)
def calculate_monthly_profitability(
    request: ProfitabilityRequest, db: Session = Depends(get_db)
) -> Any:
    """
    Calcula rentabilidade mês a mês para um ticker.
    """
    # Check if ticker exists
    ticker = TickerService.get_ticker_by_name(db, request.ticker_nm)
    if not ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{request.ticker_nm}' not found"
        )

    # Create FinancialMetrics instance directly
    metrics_obj = FinancialMetrics()

    # Calculate monthly profitability and convert to list of dictionaries
    monthly_returns = metrics_obj.get_monthly_cumulative_profitability(
        request.ticker_nm, request.init_date, request.end_date
    )

    return {
        "ticker_nm": request.ticker_nm,
        "init_date": request.init_date,
        "end_date": request.end_date,
        "monthly_returns": monthly_returns,
    }
