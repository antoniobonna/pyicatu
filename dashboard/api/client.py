import requests
from config import API_URL, error_message


def get_ticker_types():
    """Fetch all ticker types from API"""
    try:
        response = requests.get(f"{API_URL}/tickers/types")
        if response.status_code == 200:
            return response.json()
        else:
            error_message(f"Erro ao buscar tipos de ticker: {response.status_code}")
            return []
    except Exception as e:
        error_message(f"Erro de conexão: {e}")
        return []


def get_tickers():
    """Fetch all tickers from API"""
    try:
        response = requests.get(f"{API_URL}/tickers/")
        if response.status_code == 200:
            return response.json()
        else:
            error_message(f"Erro ao buscar tickers: {response.status_code}")
            return []
    except Exception as e:
        error_message(f"Erro de conexão: {e}")
        return []


def create_ticker(ticker_nm, ticker_type_nm, annual_tax):
    """Create a new ticker"""
    # Convert annual_tax from percentage to decimal
    annual_tax_decimal = annual_tax / 100

    data = {
        "ticker_nm": ticker_nm,
        "ticker_type_nm": ticker_type_nm,
        "annual_tax": annual_tax_decimal,  # Always include annual_tax (required)
    }

    try:
        response = requests.post(f"{API_URL}/tickers/", json=data)
        if response.status_code == 201:
            return True, "Ticker criado com sucesso!"
        else:
            return False, f"Erro ao criar ticker: {response.json()}"
    except Exception as e:
        return False, f"Erro de conexão: {e}"


def update_ticker(ticker_nm, ticker_type_nm=None, annual_tax=None, new_ticker_nm=None):
    """Update an existing ticker"""
    data = {
        "ticker_nm": ticker_nm  # Always include the current ticker name
    }

    # Somente adicione os campos que foram fornecidos
    if ticker_type_nm:
        data["ticker_type_nm"] = ticker_type_nm
    if annual_tax is not None:
        # Converta de porcentagem para decimal
        data["annual_tax"] = annual_tax / 100
    if new_ticker_nm:
        data["new_ticker_nm"] = new_ticker_nm

    try:
        # Baseado no curl, a URL não tem o nome do ticker
        response = requests.put(f"{API_URL}/tickers/", json=data)
        if response.status_code == 200:
            return True, "Ticker atualizado com sucesso!"
        else:
            return False, f"Erro ao atualizar ticker: {response.json()}"
    except Exception as e:
        return False, f"Erro de conexão: {e}"


def delete_ticker(ticker_nm):
    """Delete a ticker"""
    try:
        response = requests.delete(f"{API_URL}/tickers/{ticker_nm}")
        if response.status_code == 200:
            return True, "Ticker excluído com sucesso!"
        else:
            return False, f"Erro ao excluir ticker: {response.json()}"
    except Exception as e:
        return False, f"Erro de conexão: {e}"


def create_ticker_type(ticker_type_nm):
    """Create a new ticker type"""
    try:
        response = requests.post(
            f"{API_URL}/tickers/types", json={"ticker_type_nm": ticker_type_nm}
        )
        if response.status_code == 201:
            return True, "Indexador criado com sucesso!"
        else:
            return False, f"Erro ao criar indexador: {response.json()}"
    except Exception as e:
        return False, f"Erro de conexão: {e}"


def get_cumulative_profitability(ticker_nm, init_date, end_date):
    """Get cumulative profitability for a ticker"""
    try:
        response = requests.post(
            f"{API_URL}/tickers/profitability/cumulative",
            json={"ticker_nm": ticker_nm, "init_date": init_date, "end_date": end_date},
        )
        if response.status_code == 200:
            return response.json()
        else:
            error_message(f"Erro ao calcular rentabilidade acumulada: {response.status_code}")
            return None
    except Exception as e:
        error_message(f"Erro de conexão: {e}")
        return None


def get_monthly_profitability(ticker_nm, init_date, end_date):
    """Get monthly profitability for a ticker"""
    try:
        response = requests.post(
            f"{API_URL}/tickers/profitability/monthly",
            json={"ticker_nm": ticker_nm, "init_date": init_date, "end_date": end_date},
        )
        if response.status_code == 200:
            return response.json()
        else:
            error_message(f"Erro ao calcular rentabilidade mensal: {response.status_code}")
            return None
    except Exception as e:
        error_message(f"Erro de conexão: {e}")
        return None
