# config.py
import streamlit as st

# Constants
API_URL = "http://fastapi:8001/api/v1"

def setup_page_config():
    """Configure a página do Streamlit e aplica estilos CSS"""
    # Set page config
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