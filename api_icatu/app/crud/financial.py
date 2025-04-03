"""
CRUD operations for financial database tables.
"""
import hashlib
from typing import Optional

from models.financial.dim_ticker import Ticker
from models.financial.dim_ticker_type import TickerType
from sqlalchemy.orm import Session


def generate_ticker_id(ticker_nm):
    """Generate a unique ID for new ticker records."""
    return hashlib.md5(ticker_nm.encode("utf-8")).hexdigest()

class TickerService:
    """Service for ticker-related operations."""
    
    @staticmethod
    def get_ticker_type_by_name(db: Session, ticker_type_nm: str) -> Optional[TickerType]:
        """
        Get ticker type by name.
        
        Args:
            db: Database session
            ticker_type_nm: Ticker type name
            
        Returns:
            TickerType object or None if not found
        """
        return db.query(TickerType)\
                .join(Ticker, TickerType.ticker_type_id == Ticker.ticker_type_id)\
                .filter(Ticker.ticker_nm == ticker_type_nm)\
                .first()
    
    @staticmethod
    def get_ticker_by_name(db: Session, ticker_nm: str) -> Optional[Ticker]:
        """
        Get ticker by name.
        
        Args:
            db: Database session
            ticker_nm: Ticker name
            
        Returns:
            Ticker object or None if not found
        """
        return db.query(Ticker).filter(Ticker.ticker_nm == ticker_nm).first()
    
    @staticmethod
    def get_all_tickers(db: Session) -> list[str]:
        """
        Get all tickers with pagination.
        
        Args:
            db: Database session
            
        Returns:
            List of ticker names (strings)
        """
        return [ticker.ticker_nm for ticker in db.query(Ticker).all()]
    
    @staticmethod
    def get_all_ticker_types(db: Session) -> list[str]:
        """
        Get all tickers with pagination.
        
        Args:
            db: Database session
            
        Returns:
            List of ticker type names (strings)
        """
        return [ticker.ticker_type_nm for ticker in db.query(TickerType).all()]
    
    @staticmethod
    def create_ticker(
        db: Session,
        ticker_nm: str,
        ticker_type_nm: str,
        annual_tax: float
    ) -> Ticker:
        """
        Create a new ticker.
        
        Args:
            db: Database session
            ticker_nm: Ticker name
            ticker_type_nm: Ticker type name
            annual_tax: Annual tax rate
            
        Returns:
            Created Ticker object
            
        Raises:
            ValueError: If ticker type not found
        """
        # Get ticker type
        ticker_type = TickerService.get_ticker_type_by_name(db, ticker_type_nm)
        if not ticker_type:
            raise ValueError(f"Ticker type '{ticker_type_nm}' not found")
        
        # Create ticker object
        ticker = Ticker(
            ticker_id=generate_ticker_id(ticker_nm),
            ticker_nm=ticker_nm,
            ticker_type_id=ticker_type.ticker_type_id,
            annual_tax=annual_tax
        )
        
        # Add to database and commit
        db.add(ticker)
        db.commit()
        db.refresh(ticker)
        
        return ticker
    
    @staticmethod
    def update_ticker(
        db: Session, 
        ticker_nm: str,
        ticker_type_nm: Optional[str] = None,
        annual_tax: Optional[float] = None,
        new_ticker_nm: Optional[float] = None
    ) -> Optional[Ticker]:
        """
        Update an existing ticker.
        
        Args:
            db: Database session
            ticker_nm: New ticker name (optional)
            ticker_type_nm: New ticker type name (optional)
            annual_tax: New annual tax rate (optional)
            new_ticker_nm: New ticker name (optional)
            
        Returns:
            Updated Ticker object or None if not found
            
        Raises:
            ValueError: If ticker type not found
        """
        # Get ticker by ID
        ticker = TickerService.get_ticker_by_name(db, ticker_nm)
        if not ticker:
            return None
        
        # Update ticker type if provided
        if ticker_type_nm:
            ticker_type = TickerService.get_ticker_type_by_name(db, ticker_type_nm)
            ticker.ticker_type_id = ticker_type.ticker_type_id
        
        # Update annual tax if provided
        if annual_tax is not None:
            ticker.annual_tax = annual_tax
        
        # Update ticker name if provided
        if new_ticker_nm is not None:
            ticker.ticker_nm = new_ticker_nm
        
        # Commit changes
        db.commit()
        db.refresh(ticker)
        
        return ticker
    
    @staticmethod
    def delete_ticker(db: Session, ticker_nm: str) -> bool:
        """
        Delete a ticker by name.
        
        Args:
            db: Database session
            ticker_nm: Ticker to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Get ticker by ID
        ticker = TickerService.get_ticker_by_name(db, ticker_nm)
        if not ticker:
            return False
        
        # Delete and commit
        db.delete(ticker)
        db.commit()
        
        return True
