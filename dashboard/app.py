import streamlit as st
from components.crud_tickers import render_ticker_crud
from components.profitability_calculator import render_profitability_calculator
from config import setup_page_config


def render_help_section():
    """Render help and information section"""
    st.header("Ajuda e Informações")

    with st.container():
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
    # Configuração da página
    setup_page_config()

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
