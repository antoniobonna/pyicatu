import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64

from api.client import get_tickers, get_cumulative_profitability, get_monthly_profitability
from config import error_message, info_message, card_container, success_message
from utils.formatting import get_month_name

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
            st.markdown("""
            <p style="font-size: 1.1rem; font-weight: 500; margin-bottom: 1rem; color: #1f2937;">
                ⚙️ Parâmetros da Simulação
            </p>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_ticker = st.selectbox(
                    "Selecione o Ativo/Índice",
                    options=ticker_options
                )
            
            with col2:
                # Default to 1 year ago
                default_start = datetime.now() - timedelta(days=365)
                start_date = st.date_input(
                    "Data Inicial",
                    value=default_start,
                    max_value=datetime.now()
                )
            
            with col3:
                end_date = st.date_input(
                    "Data Final",
                    value=datetime.now(),
                    min_value=start_date,
                    max_value=datetime.now()
                )
            
            calculate_button = st.form_submit_button("📊 Calcular Rentabilidade")
        
        # Process form submission
        if calculate_button:
            with st.spinner("Calculando rentabilidade..."):
                # Format dates for API
                start_str_api = start_date.strftime("%Y-%m-%d")
                end_str_api = end_date.strftime("%Y-%m-%d")
                
                # Get daily and monthly profitability data from API
                cumulative_data = get_cumulative_profitability(selected_ticker, start_str_api, end_str_api)
                monthly_data = get_monthly_profitability(selected_ticker, start_str_api, end_str_api)

                # Format dates for Display
                start_str = start_date.strftime("%d/%m/%Y")
                end_str = end_date.strftime("%d/%m/%Y")
                
                if cumulative_data and monthly_data:
                    display_profitability_results(cumulative_data, monthly_data, selected_ticker, start_str, end_str)
                else:
                    error_message("Não foi possível obter os dados de rentabilidade. Verifique os parâmetros e tente novamente.")

def display_profitability_results(cumulative_data, monthly_data, ticker_nm, start_date, end_date):
    """Display profitability results"""
    st.markdown("""
    <div style="margin-top: 2rem;">
        <h2>Resultados da Rentabilidade</h2>
    </div>
    """, unsafe_allow_html=True)
    
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
                delta_color="normal"
            )
        
        with cols[1]:
            # Get start and end dates from dataframe
            first_date = pd.to_datetime(df_daily["ticker_date"].iloc[0]).strftime("%d/%m/%Y")
            last_date = pd.to_datetime(df_daily["ticker_date"].iloc[-1]).strftime("%d/%m/%Y")
            
            st.markdown(f"""
            <div style="padding: 10px 0;">
                <p style="font-size: 0.9rem; color: #6b7280; margin: 0;">Período de Análise:</p>
                <p style="font-size: 1.1rem; font-weight: 500; margin: 0; color: #1e3a8a;">{first_date} a {last_date}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Format daily data for the chart
    df_daily["Date"] = pd.to_datetime(df_daily["ticker_date"])
    df_daily["Rentabilidade Acumulada (%)"] = df_daily["cumulative_return"] * 100
    
    # Create chart with better styling
    with card_container():
        st.subheader("Gráfico de Rentabilidade Acumulada")
        
        # Create line chart using plotly.graph_objects
        fig = go.Figure()
        
        # Add line trace with formatting for 2 decimal places
        fig.add_trace(go.Scatter(
            x=df_daily["Date"],
            y=df_daily["Rentabilidade Acumulada (%)"],
            mode="lines",
            name="Rentabilidade Acumulada",
            line=dict(color="#1e40af", width=3),
            hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Rentabilidade:</b> %{y:.2f}%<extra></extra>"
        ))
        
        # Add baseline at 0%
        fig.add_shape(
            type="line",
            x0=df_daily["Date"].min(),
            y0=0,
            x1=df_daily["Date"].max(),
            y1=0,
            line=dict(color="gray", width=1, dash="dash")
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
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            font=dict(
                family="Segoe UI, Arial, sans-serif",
                size=12
            )
        )
        
        # Add grid, improve visual appearance
        fig.update_xaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.3)',
            zeroline=False,
            tickformat="%d/%m/%Y"
        )
        
        fig.update_yaxes(
            showgrid=True,
            gridwidth=1,
            gridcolor='rgba(211,211,211,0.3)',
            zeroline=False
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
            display_monthly["Mês"] = display_monthly["month"].apply(lambda x: get_month_name(int(x)))
            display_monthly["Rentabilidade Mensal"] = display_monthly["monthly_return"].apply(lambda x: f"{x*100:.2f}%")
            display_monthly["Rentabilidade Acumulada"] = display_monthly["cumulative_return"].apply(lambda x: f"{x*100:.2f}%")
            
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
                    "Rentabilidade Acumulada": st.column_config.TextColumn(width="medium")
                }
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
