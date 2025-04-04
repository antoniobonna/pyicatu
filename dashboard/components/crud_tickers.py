import streamlit as st
from api.client import (
    get_ticker_types, 
    get_tickers, 
    create_ticker, 
    update_ticker, 
    delete_ticker, 
    create_ticker_type
)
from config import success_message, warning_message, error_message, info_message, card_container
from utils.formatting import get_synthetic_tickers

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
                new_ticker_name = st.text_input("Nome do Ativo (Ex. CDI +5)", 
                                               placeholder="Digite o nome do ativo",
                                               key="create_name")
                
                # Check if we need to create a new type
                create_new_type = st.checkbox("Criar novo indexador")
                
                if create_new_type:
                    new_type_name = st.text_input("Nome do Novo Indexador", 
                                                 placeholder="Digite o nome do novo indexador")
                    
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
                    help="Taxa anual representa o rendimento do ativo em relação ao indexador"
                )
                
                st.markdown("""
                <div style="background-color: #f8fafc; padding: 12px; border-radius: 6px; margin-top: 10px;">
                    <p style="margin: 0; color: #64748b; font-size: 0.9rem;">
                        <b>📝 Dica:</b> A taxa anual representa o rendimento anual do ativo em relação ao indexador selecionado.
                        Por exemplo, <b>CDI +2</b> significa que o ativo rende 2% acima do CDI ao ano.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
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
                        "Selecione o Ativo para Editar", 
                        options=ticker_names,
                        key="edit_select"
                    )
                    
                    # Create a simplified ticker object for UI
                    selected_ticker = {
                        "ticker_nm": selected_ticker_name,
                        "annual_tax": 0.01,  # Default value
                        "ticker_type": {"ticker_type_nm": ticker_types[0] if ticker_types else "CDI"}
                    }
                else:
                    # Handle complex object list response
                    ticker_options = {t["ticker_nm"]: t for t in synthetic_tickers}
                    selected_ticker_name = st.selectbox(
                        "Selecione o Ativo para Editar", 
                        options=list(ticker_options.keys()),
                        key="edit_select"
                    )
                    selected_ticker = ticker_options[selected_ticker_name]
                
                if selected_ticker_name:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input(
                            "Nome do Ativo", 
                            value=selected_ticker["ticker_nm"],
                            key="edit_name"
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
                            key="edit_type"
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
                            key="edit_tax"
                        )
                    
                    if st.button("💾 Atualizar Ativo"):
                        # Chama a função update_ticker diretamente com os valores atuais
                        success, message = update_ticker(
                            ticker_nm=selected_ticker_name,
                            ticker_type_nm=new_type,
                            annual_tax=new_tax,
                            new_ticker_nm=new_name
                        )
                        if success:
                            success_message(message)
                            # Refresh the page by rerunning the app
                            # st.experimental_rerun()
                        else:
                            error_message(message)
    
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
                    "Selecione o Ativo para Excluir", 
                    options=ticker_names,
                    key="delete_select"
                )
                
                if selected_ticker:
                    st.markdown("""
                    <div style="background-color: #fee2e2; padding: 12px; border-radius: 6px; margin: 12px 0;">
                        <p style="margin: 0; color: #b91c1c; font-weight: 500;">
                            ⚠️ Tem certeza que deseja excluir o ativo '{0}'? Esta ação não pode ser desfeita.
                        </p>
                    </div>
                    """.format(selected_ticker), unsafe_allow_html=True)
                    
                    if st.button("🗑️ Confirmar Exclusão"):
                        success, message = delete_ticker(selected_ticker)
                        if success:
                            success_message(message)
                            # Refresh the page by rerunning the app
                            # st.experimental_rerun()
                        else:
                            error_message(message)