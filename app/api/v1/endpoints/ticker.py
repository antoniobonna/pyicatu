"""
API endpoints for ticker operations.
"""

from typing import Any

from crud.financial import TickerService
from db.session import get_db
from fastapi import APIRouter, Depends, HTTPException, Path, status
from schemas.ticker import (
    TickerCreate,
    TickerResponse,
    TickerTypeCreate,
    TickerTypeResponse,
    TickerUpdate,
)
from sqlalchemy.orm import Session

router = APIRouter(tags=["Tickers"])


@router.get("/", response_model=list[str])
def read_tickers(db: Session = Depends(get_db)) -> Any:
    """
    Retorna lista com todos os tickers.
    """
    tickers = TickerService.get_all_tickers(db)
    return tickers


@router.post("/", response_model=TickerResponse, status_code=status.HTTP_201_CREATED)
def create_ticker(ticker_in: TickerCreate, db: Session = Depends(get_db)) -> Any:
    """
    Adiciona novo ticker.
    """
    # Check if ticker already exists
    existing_ticker = TickerService.get_ticker_by_name(db, ticker_in.ticker_nm)
    if existing_ticker:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker with name '{ticker_in.ticker_nm}' already exists",
        )

    try:
        # Create new ticker
        ticker = TickerService.create_ticker(
            db=db,
            ticker_nm=ticker_in.ticker_nm,
            ticker_type_nm=ticker_in.ticker_type_nm,
            annual_tax=ticker_in.annual_tax,
        )
        return ticker
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put("/", response_model=TickerResponse)
def update_ticker(ticker_in: TickerUpdate, db: Session = Depends(get_db)) -> Any:
    """
    Update ticker.
    """
    try:
        ticker = TickerService.update_ticker(
            db=db,
            ticker_nm=ticker_in.ticker_nm,
            ticker_type_nm=ticker_in.ticker_type_nm,
            annual_tax=ticker_in.annual_tax,
            new_ticker_nm=ticker_in.new_ticker_nm,
        )
        if not ticker:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticker not found")
        return ticker
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{ticker_nm}", response_model=dict, status_code=status.HTTP_200_OK)
def delete_ticker(
    ticker_nm: str = Path(..., description="Nome do ticker a ser excluído"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Remove um ticker.
    """
    deleted = TickerService.delete_ticker(db, ticker_nm)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticker not found")
    return {"success": True, "message": f"Ticker '{ticker_nm}' deleted successfully"}


@router.post("/types", response_model=TickerTypeResponse, status_code=status.HTTP_201_CREATED)
def create_ticker_type(ticker_type_in: TickerTypeCreate, db: Session = Depends(get_db)) -> Any:
    """
    Cria um novo tipo de ticker.
    """
    # Check if a ticker type with this name already exists
    existing_ticker_type = TickerService.get_ticker_type_by_name(db, ticker_type_in.ticker_type_nm)
    if existing_ticker_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ticker type '{ticker_type_in.ticker_type_nm}' already exists",
        )

    # Create new ticker type
    ticker_type = TickerService.create_ticker_type(db, ticker_type_in.ticker_type_nm)
    return ticker_type
