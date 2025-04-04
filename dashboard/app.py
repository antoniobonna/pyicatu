import base64
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Calculadora de Rentabilidade Financeira",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom CSS for professional look (without table styling)
st.markdown(
    """
<style>
    /* General styling */
    .main {
        background-color: #f5f7fa;
        padding: 1.5rem;
    }
    
    /* Headers */
    h1, h2, h3, h4 {
        color: #1e3a8a;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1 {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        padding-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
        margin-bottom: 2rem !important;
    }
    
    h2 {
        font-size: 1.8rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h3 {
        font-size: 1.4rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
    }
    
    /* Form fields */
    div.stTextInput > div > div > input {
        border-radius: 6px;
    }
    
    div.stNumberInput > div > div > input {
        border-radius: 6px;
    }
    
    div.stDateInput > div > div > input {
        border-radius: 6px;
    }
    
    /* Select boxes */
    div.stSelectbox > div > div {
        border-radius: 6px;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #1e3a8a;
        color: white;
        font-weight: 500;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #2563eb;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f3f4f6;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 16px;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #e0e7ff !important;
        color: #1e3a8a !important;
    }
    
    /* Cards for sections */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1e3a8a !important;
    }
    
    /* Success messages */
    .success-message {
        background-color: #d1fae5;
        color: #065f46;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    
    /* Warning messages */
    .warning-message {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    
    /* Error messages */
    .error-message {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #ef4444;
        margin: 1rem 0;
    }
    
    /* Info messages */
    .info-message {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 0.75rem;
        border-radius: 6px;
        border-left: 4px solid #0ea5e9;
        margin: 1rem 0;
    }
    
    /* Custom headers and captions */
    .st-emotion-cache-16idsys p {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 1rem !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Constants
API_URL = "http://localhost:8001/api/v1"


# Custom styled messages
def success_message(text):
    st.markdown(f'<div class="success-message">{text}</div>', unsafe_allow_html=True)


def warning_message(text):
    st.markdown(f'<div class="warning-message">{text}</div>', unsafe_allow_html=True)


def error_message(text):
    st.markdown(f'<div class="error-message">{text}</div>', unsafe_allow_html=True)


def info_message(text):
    st.markdown(f'<div class="info-message">{text}</div>', unsafe_allow_html=True)


# Card container
def card_container():
    return st.container()


# Helper functions
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


def update_ticker(ticker_id, ticker_nm=None, ticker_type_nm=None, annual_tax=None):
    """Update an existing ticker"""
    data = {}
    if ticker_nm:
        data["ticker_nm"] = ticker_nm
    if ticker_type_nm:
        data["ticker_type_nm"] = ticker_type_nm
    if annual_tax is not None:
        data["annual_tax"] = annual_tax

    try:
        response = requests.put(f"{API_URL}/tickers/{ticker_id}", json=data)
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


def get_month_name(month_number):
    """Convert month number to month name in Portuguese"""
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
        12: "Dezembro",
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


# Function to create styled dataframe - KEEP SIMPLE WITHOUT CSS STYLING
def create_styled_dataframe(df, hide_index=True):
    # Simply return the dataframe without styling
    if hide_index:
        return df.style.hide(axis="index")
    else:
        return df.style


# UI Components
def render_ticker_crud():
    """Render the ticker CRUD interface"""
    st.header("Gerenciamento de Ativos Sintéticos")

    # Get data
    ticker_types = get_ticker_types()
    all_tickers = get_tickers()

    # Create tabs for CRUD operations
    crud_tabs = st.tabs(["✨ Criar", "✏️ Editar", "🗑️ Excluir"])

    # Create tab
    with crud_tabs[0]:
        with card_container():
            st.subheader("Criar Novo Ativo Sintético")

            col1, col2 = st.columns(2)

            with col1:
                new_ticker_name = st.text_input(
                    "Nome do Ativo (Ex. CDI +5)",
                    placeholder="Digite o nome do ativo",
                    key="create_name",
                )

                # Check if we need to create a new type
                create_new_type = st.checkbox("Criar novo indexador")

                if create_new_type:
                    new_type_name = st.text_input(
                        "Nome do Novo Indexador", placeholder="Digite o nome do novo indexador"
                    )

                    if st.button("➕ Criar Indexador"):
                        if new_type_name:
                            success, message = create_ticker_type(new_type_name)
                            if success:
                                success_message(message)
                                # Update ticker types
                                ticker_types = get_ticker_types()
                            else:
                                error_message(message)
                        else:
                            warning_message("Nome do indexador não pode ser vazio")

                # Create a default list if ticker_types is empty
                type_options = ticker_types if ticker_types else ["CDI", "Ibovespa"]
                selected_type = st.selectbox("Indexador", options=type_options, key="create_type")

            with col2:
                annual_tax = st.number_input(
                    "Taxa Anual (% a.a.)",
                    min_value=0.01,
                    max_value=100.0,
                    value=1.0,
                    step=0.01,
                    key="create_tax",
                    help="Taxa anual representa o rendimento do ativo em relação ao indexador",
                )

                st.markdown(
                    """
                <div style="background-color: #f8fafc; padding: 12px; border-radius: 6px; margin-top: 10px;">
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                        <b>📝 Dica:</b> A taxa anual representa o rendimento anual do ativo em relação ao indexador selecionado.
                        Por exemplo, <b>CDI +2</b> significa que o ativo rende 2% acima do CDI ao ano.
                    </p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

            if st.button("💾 Criar Ativo"):
                if new_ticker_name and selected_type and annual_tax > 0:
                    success, message = create_ticker(new_ticker_name, selected_type, annual_tax)
                    if success:
                        success_message(message)
                    else:
                        error_message(message)
                else:
                    warning_message("Nome do ativo, indexador e taxa anual são obrigatórios.")

    # Edit tab
    with crud_tabs[1]:
        with card_container():
            st.subheader("Editar Ativo Existente")

            # Get synthetic tickers only
            synthetic_tickers = get_synthetic_tickers(all_tickers, ticker_types)

            if not synthetic_tickers:
                info_message("Não há ativos sintéticos para editar. Crie um ativo primeiro.")
            else:
                # Handle simple string list response
                if all(isinstance(t, str) for t in synthetic_tickers):
                    ticker_names = synthetic_tickers

                    selected_ticker_name = st.selectbox(
                        "Selecione o Ativo para Editar", options=ticker_names, key="edit_select"
                    )

                    # Create a simplified ticker object for UI
                    selected_ticker = {
                        "ticker_id": selected_ticker_name,  # Use name as ID
                        "ticker_nm": selected_ticker_name,
                        "annual_tax": 0.01,  # Default value
                        "ticker_type": {
                            "ticker_type_nm": ticker_types[0] if ticker_types else "CDI"
                        },
                    }
                else:
                    # Handle complex object list response
                    ticker_options = {t["ticker_nm"]: t for t in synthetic_tickers}
                    selected_ticker_name = st.selectbox(
                        "Selecione o Ativo para Editar",
                        options=list(ticker_options.keys()),
                        key="edit_select",
                    )
                    selected_ticker = ticker_options[selected_ticker_name]

                if selected_ticker_name:
                    col1, col2 = st.columns(2)

                    with col1:
                        new_name = st.text_input(
                            "Nome do Ativo", value=selected_ticker["ticker_nm"], key="edit_name"
                        )

                        # Create a default list if ticker_types is empty
                        type_options = ticker_types if ticker_types else ["CDI", "Ibovespa"]
                        current_type = selected_ticker.get("ticker_type", {}).get("ticker_type_nm")

                        # If current_type is None or not in options, select the first one
                        if not current_type or current_type not in type_options:
                            current_type = type_options[0]

                        new_type = st.selectbox(
                            "Indexador",
                            options=type_options,
                            index=type_options.index(current_type),
                            key="edit_type",
                        )

                    with col2:
                        current_tax = selected_ticker.get("annual_tax", 0.01)
                        if current_tax:
                            # Convert from decimal to percentage for display
                            current_tax = float(current_tax) * 100

                        new_tax = st.number_input(
                            "Taxa Anual (% a.a.)",
                            min_value=0.01,
                            max_value=100.0,
                            value=max(1.0, current_tax),
                            step=0.01,
                            key="edit_tax",
                        )

                    if st.button("💾 Atualizar Ativo"):
                        # Only update fields that have changed
                        update_name = new_name if new_name != selected_ticker["ticker_nm"] else None
                        update_type = new_type if new_type != current_type else None

                        # Check if tax has changed and convert to decimal for storage
                        update_tax = None
                        if new_tax > 0:
                            tax_decimal = new_tax / 100
                            if (
                                abs(tax_decimal - current_tax / 100) > 0.0001
                            ):  # Allow for small floating point differences
                                update_tax = tax_decimal

                        if update_name or update_type or update_tax is not None:
                            success, message = update_ticker(
                                selected_ticker["ticker_id"], update_name, update_type, update_tax
                            )
                            if success:
                                success_message(message)
                                # Refresh the page by rerunning the app
                                st.experimental_rerun()
                            else:
                                error_message(message)
                        else:
                            info_message("Nenhuma alteração detectada")

    # Delete tab
    with crud_tabs[2]:
        with card_container():
            st.subheader("Excluir Ativo")

            # Get synthetic tickers only
            synthetic_tickers = get_synthetic_tickers(all_tickers, ticker_types)

            if not synthetic_tickers:
                info_message("Não há ativos sintéticos para excluir. Crie um ativo primeiro.")
            else:
                # Handle simple string list
                if all(isinstance(t, str) for t in synthetic_tickers):
                    ticker_names = synthetic_tickers
                else:
                    # Handle complex object list
                    ticker_names = [t["ticker_nm"] for t in synthetic_tickers]

                selected_ticker = st.selectbox(
                    "Selecione o Ativo para Excluir", options=ticker_names, key="delete_select"
                )

                if selected_ticker:
                    st.markdown(
                        """
                    <div style="background-color: #fee2e2; padding: 12px; border-radius: 6px; margin: 12px 0;">
                        <p style="margin: 0; color: #b91c1c; font-weight: 500;">
                            ⚠️ Tem certeza que deseja excluir o ativo '{0}'? Esta ação não pode ser desfeita.
                        </p>
                    </div>
                    """.format(selected_ticker),
                        unsafe_allow_html=True,
                    )

                    if st.button("🗑️ Confirmar Exclusão"):
                        success, message = delete_ticker(selected_ticker)
                        if success:
                            success_message(message)
                            # Refresh the page by rerunning the app
                            st.experimental_rerun()
                        else:
                            error_message(message)


def render_profitability_calculator():
    """Render the profitability calculator interface"""
    st.header("Calculadora de Rentabilidade")

    with card_container():
        # Get tickers for dropdown
        tickers = get_tickers()

        # Initialize ticker options with default values
        ticker_options = ["CDI", "Ibovespa"]

        # Add tickers from API if available
        if tickers:
            if all(isinstance(t, str) for t in tickers):
                # Simple string list - add any new items not already in defaults
                for ticker in tickers:
                    if ticker not in ticker_options:
                        ticker_options.append(ticker)
            else:
                # Complex object list - extract ticker names
                for ticker in tickers:
                    if isinstance(ticker, dict) and "ticker_nm" in ticker:
                        ticker_name = ticker["ticker_nm"]
                        if ticker_name not in ticker_options:
                            ticker_options.append(ticker_name)

        # Create input form
        with st.form("profitability_form"):
            st.markdown(
                """
            <p style="font-size: 1.1rem; font-weight: 500; margin-bottom: 1rem; color: #1f2937;">
                ⚙️ Parâmetros da Simulação
            </p>
            """,
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                selected_ticker = st.selectbox("Selecione o Ativo/Índice", options=ticker_options)

            with col2:
                # Default to 1 year ago
                default_start = datetime.now() - timedelta(days=365)
                start_date = st.date_input(
                    "Data Inicial", value=default_start, max_value=datetime.now()
                )

            with col3:
                end_date = st.date_input(
                    "Data Final",
                    value=datetime.now(),
                    min_value=start_date,
                    max_value=datetime.now(),
                )

            calculate_button = st.form_submit_button("📊 Calcular Rentabilidade")

        # Process form submission
        if calculate_button:
            with st.spinner("Calculando rentabilidade..."):
                # Format dates for API
                start_str_api = start_date.strftime("%Y-%m-%d")
                end_str_api = end_date.strftime("%Y-%m-%d")

                # Get daily and monthly profitability data from API
                cumulative_data = get_cumulative_profitability(
                    selected_ticker, start_str_api, end_str_api
                )
                monthly_data = get_monthly_profitability(
                    selected_ticker, start_str_api, end_str_api
                )

                # Format dates for Display
                start_str = start_date.strftime("%d/%m/%Y")
                end_str = end_date.strftime("%d/%m/%Y")

                if cumulative_data and monthly_data:
                    display_profitability_results(
                        cumulative_data, monthly_data, selected_ticker, start_str, end_str
                    )
                else:
                    error_message(
                        "Não foi possível obter os dados de rentabilidade. Verifique os parâmetros e tente novamente."
                    )


def display_profitability_results(cumulative_data, monthly_data, ticker_nm, start_date, end_date):
    """Display profitability results"""
    st.markdown(
        """
    <div style="margin-top: 2rem;">
        <h2>Resultados da Rentabilidade</h2>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Process cumulative (daily) data
    df_daily = pd.DataFrame(cumulative_data)

    if df_daily.empty:
        info_message("Não há dados de rentabilidade diária disponíveis para o período selecionado.")
        return

    # Create summary card
    with card_container():
        # Display total cumulative return (last value)
        total_return = df_daily["cumulative_return"].iloc[-1] * 100

        cols = st.columns([2, 1])
        with cols[0]:
            st.metric(
                "Rentabilidade Acumulada Total",
                f"{total_return:.2f}%",
                delta=f"{total_return:.2f}%",
                delta_color="normal",
            )

        with cols[1]:
            # Get start and end dates from dataframe
            first_date = pd.to_datetime(df_daily["ticker_date"].iloc[0]).strftime("%d/%m/%Y")
            last_date = pd.to_datetime(df_daily["ticker_date"].iloc[-1]).strftime("%d/%m/%Y")

            st.markdown(
                f"""
            <div style="padding: 10px 0;">
                <p style="font-size: 0.9rem; color: #6b7280; margin: 0;">Período de Análise:</p>
                <p style="font-size: 1.1rem; font-weight: 500; margin: 0; color: #1e3a8a;">{first_date} a {last_date}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Format daily data for the chart
    df_daily["Date"] = pd.to_datetime(df_daily["ticker_date"])
    df_daily["Rentabilidade Acumulada (%)"] = df_daily["cumulative_return"] * 100

    # Create chart with better styling
    with card_container():
        st.subheader("Gráfico de Rentabilidade Acumulada")

        # Create line chart using plotly.graph_objects
        fig = go.Figure()

        # Add line trace with formatting for 2 decimal places
        fig.add_trace(
            go.Scatter(
                x=df_daily["Date"],
                y=df_daily["Rentabilidade Acumulada (%)"],
                mode="lines",
                name="Rentabilidade Acumulada",
                line=dict(color="#1e40af", width=3),
                hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Rentabilidade:</b> %{y:.2f}%<extra></extra>",
            )
        )

        # Add baseline at 0%
        fig.add_shape(
            type="line",
            x0=df_daily["Date"].min(),
            y0=0,
            x1=df_daily["Date"].max(),
            y1=0,
            line=dict(color="gray", width=1, dash="dash"),
        )

        # Customize layout
        fig.update_layout(
            title=f"Rentabilidade Acumulada de {ticker_nm} ({start_date} a {end_date})",
            xaxis_title="Data",
            yaxis_title="Rentabilidade Acumulada (%)",
            yaxis_ticksuffix="%",
            yaxis_tickformat=".2f",  # Format y-axis ticks to 2 decimal places
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            width=800,
            height=500,
            margin=dict(l=40, r=40, t=60, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            font=dict(family="Segoe UI, Arial, sans-serif", size=12),
        )

        # Add grid, improve visual appearance
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor="rgba(211,211,211,0.3)",
            zeroline=False,
            tickformat="%d/%m/%Y",
        )

        fig.update_yaxes(
            showgrid=True, gridwidth=1, gridcolor="rgba(211,211,211,0.3)", zeroline=False
        )

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

    # Process monthly data
    if "monthly_returns" in monthly_data and monthly_data["monthly_returns"]:
        monthly_returns = monthly_data["monthly_returns"]
        df_monthly = pd.DataFrame(monthly_returns)

        with card_container():
            # Prepare data for display
            # If data contains 'monthly_return', use it directly
            # Otherwise calculate it from cumulative_return values
            if "monthly_return" in df_monthly.columns:
                df_monthly["Rentabilidade Mensal (%)"] = df_monthly["monthly_return"] * 100
            else:
                # Calculate monthly returns from the provided data
                # Converting type to numeric if needed
                df_monthly["cumulative_return"] = pd.to_numeric(df_monthly["cumulative_return"])

                # Sort by year and month to ensure correct calculation
                df_monthly = df_monthly.sort_values(by=["year", "month"])

                # Calculate monthly returns (this assumes cumulative_return is properly calculated)
                df_monthly["prev_cumulative"] = df_monthly["cumulative_return"].shift(1).fillna(0)

                # Calculate monthly return
                def calculate_monthly_return(row):
                    if row["prev_cumulative"] == 0:
                        return row["cumulative_return"]
                    else:
                        return (1 + row["cumulative_return"]) / (1 + row["prev_cumulative"]) - 1

                df_monthly["monthly_return"] = df_monthly.apply(calculate_monthly_return, axis=1)
                df_monthly["Rentabilidade Mensal (%)"] = df_monthly["monthly_return"] * 100

            # Create display dataframe with proper formatting
            display_monthly = df_monthly.copy()
            display_monthly["Ano"] = display_monthly["year"].astype(int)
            display_monthly["Mês"] = display_monthly["month"].apply(
                lambda x: get_month_name(int(x))
            )
            display_monthly["Rentabilidade Mensal"] = display_monthly["monthly_return"].apply(
                lambda x: f"{x * 100:.2f}%"
            )
            display_monthly["Rentabilidade Acumulada"] = display_monthly["cumulative_return"].apply(
                lambda x: f"{x * 100:.2f}%"
            )

            # Select and order columns
            display_cols = ["Ano", "Mês", "Rentabilidade Mensal", "Rentabilidade Acumulada"]

            # Display table after chart
            st.subheader("Rentabilidade Mensal")

            # Use simplified table approach - no complex styling
            display_df = pd.DataFrame(display_monthly[display_cols])

            # Display the dataframe without complex styling
            st.dataframe(
                display_df,
                use_container_width=True,
                column_config={
                    "Ano": st.column_config.NumberColumn(format="%d"),
                    "Mês": st.column_config.TextColumn(width="medium"),
                    "Rentabilidade Mensal": st.column_config.TextColumn(width="medium"),
                    "Rentabilidade Acumulada": st.column_config.TextColumn(width="medium"),
                },
            )

            # Add download button for CSV export
            csv = display_monthly[display_cols].to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()

            st.download_button(
                label="📥 Baixar dados em CSV",
                data=csv,
                file_name=f"rentabilidade_{ticker_nm}_{start_date.replace('/', '-')}_{end_date.replace('/', '-')}.csv",
                mime="text/csv",
            )
    else:
        info_message("Não há dados de rentabilidade mensal disponíveis para o período selecionado.")


def render_help_section():
    """Render help and information section"""
    st.header("Ajuda e Informações")

    with card_container():
        st.markdown(
            """
        <h3>💡 Como usar esta aplicação</h3>
        <p>Esta aplicação permite gerenciar ativos sintéticos e calcular sua rentabilidade ao longo do tempo.</p>
        
        <h4>Gestão de Ativos Sintéticos</h4>
        <ol>
            <li><strong>Criar Ativos</strong>: Defina um nome, selecione um indexador base e especifique a taxa anual.</li>
            <li><strong>Editar Ativos</strong>: Modifique propriedades de ativos existentes.</li>
            <li><strong>Excluir Ativos</strong>: Remova ativos que não são mais necessários.</li>
        </ol>
        
        <h4>Calculadora de Rentabilidade</h4>
        <ol>
            <li>Selecione um ativo ou índice.</li>
            <li>Defina o período de análise (data inicial e final).</li>
            <li>Clique em "Calcular Rentabilidade" para visualizar os resultados.</li>
        </ol>
        
        <p>Os resultados incluem um gráfico de rentabilidade acumulada e uma tabela detalhada de rentabilidade mensal.</p>
        """,
            unsafe_allow_html=True,
        )


# Main application
def main():
    # Add application logo and title
    st.markdown(
        """
    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
        <h1 style="margin: 0; flex-grow: 1;">📈 Calculadora de Rentabilidade Financeira</h1>
    </div>
    <p style="color: #6b7280; margin-top: -0.5rem; margin-bottom: 2rem;">
        Gerencie ativos sintéticos e calcule rentabilidade de investimentos
    </p>
    """,
        unsafe_allow_html=True,
    )

    # Create tabs for different sections with icons
    tab1, tab2, tab3 = st.tabs(
        ["🏦 Ativos Sintéticos", "📊 Calculadora de Rentabilidade", "❓ Ajuda"]
    )

    with tab1:
        render_ticker_crud()

    with tab2:
        render_profitability_calculator()

    with tab3:
        render_help_section()

    # Footer
    st.markdown(
        """
    <div style="margin-top: 3rem; border-top: 1px solid #e5e7eb; padding-top: 1rem; text-align: center;">
        <p style="color: #6b7280; font-size: 0.9rem;">
            Calculadora de Rentabilidade Financeira © 2025 | Desenvolvido com Streamlit
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
