# Calculadora de Rentabilidade Financeira

Uma aplicação Streamlit para gerenciamento de ativos financeiros sintéticos e cálculo de rentabilidade baseada em indexadores de mercado.

## 📋 Descrição

Esta aplicação permite que usuários criem, editem e gerenciem ativos financeiros sintéticos, como "CDI +2%" ou "Ibovespa -1%", e calculem sua rentabilidade ao longo do tempo. Os usuários podem visualizar a rentabilidade acumulada e mensal através de gráficos interativos e tabelas.

## 🔧 Funcionalidades

- **Gerenciamento de Ativos Sintéticos**
  - Criar novos ativos sintéticos baseados em indexadores (CDI, Ibovespa, etc.)
  - Editar ativos existentes
  - Excluir ativos

- **Calculadora de Rentabilidade**
  - Selecionar entre ativos e indexadores disponíveis
  - Definir período de análise personalizado
  - Visualizar rentabilidade acumulada em gráfico interativo
  - Ver dados mensais detalhados em tabela
  - Exportar resultados para CSV

## 🏗️ Estrutura do Projeto

```
streamlit_app/
│
├── app.py                  # Ponto de entrada da aplicação
├── config.py               # Configurações globais
├── requirements.txt        # Dependências do projeto
│
├── api/                    # Interação com a API de dados
│   └── client.py           # Cliente REST para comunicação com backend
│
├── components/             # Componentes da UI
│   ├── crud_tickers.py     # Interface de gerenciamento de ativos
│   ├── profitability_calculator.py  # Calculadora de rentabilidade
│   └── table_utils.py      # Utilitários para tabelas
│
└── utils/                  # Utilitários gerais
    └── formatting.py       # Funções de formatação e conversão
```

## 🚀 Como Executar

### Pré-requisitos

- Python 3.10 ou superior

1. Execute a aplicação:
```bash
streamlit run app.py
```

2. Abra o navegador e acesse:
```
http://localhost:8501
```

## 🔌 Configuração da API

A aplicação espera uma API REST de backend em execução na URL definida em `config.py`. Por padrão, a URL é:

```
http://localhost:8001/api/v1
```

Para alterar a URL da API, modifique a constante `API_URL` no arquivo `config.py`.

### Endpoints da API

- `/tickers/` - GET: Listar todos os tickers, POST: Criar um ticker
- `/tickers/{ticker_id}` - PUT: Atualizar ticker, DELETE: Excluir ticker
- `/tickers/types` - GET: Listar indexadores, POST: Criar indexador
- `/tickers/profitability/cumulative` - POST: Calcular rentabilidade acumulada
- `/tickers/profitability/monthly` - POST: Calcular rentabilidade mensal