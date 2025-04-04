def get_month_name(month_number):
    """
    Convert month number to month name in Portuguese
    
    Args:
        month_number (int): Número do mês (1-12)
        
    Returns:
        str: Nome do mês em português
    """
    month_names = {
        1: "Janeiro",
        2: "Fevereiro",
        3: "Março",
        4: "Abril",
        5: "Maio",
        6: "Junho",
        7: "Julho",
        8: "Agosto",
        9: "Setembro",
        10: "Outubro",
        11: "Novembro",
        12: "Dezembro"
    }
    return month_names.get(month_number, str(month_number))

def get_synthetic_tickers(all_tickers, ticker_types):
    """
    Get only synthetic tickers (tickers that are not in ticker_types)
    
    Args:
        all_tickers: List of all tickers
        ticker_types: List of ticker types/base tickers
        
    Returns:
        List of synthetic tickers
    """
    if all(isinstance(t, str) for t in all_tickers):
        # If all_tickers is just a list of strings
        ticker_names = set(all_tickers)
        type_names = set(ticker_types)
        return list(ticker_names - type_names)
    else:
        # If all_tickers is a list of objects
        ticker_names = {t["ticker_nm"] for t in all_tickers}
        type_names = set(ticker_types)
        synthetic_names = list(ticker_names - type_names)
        return [t for t in all_tickers if t["ticker_nm"] in synthetic_names]