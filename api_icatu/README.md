# API Financeira Pyicatu

Uma aplicação FastAPI para gerenciamento de dados financeiros e cálculo de métricas.

## Funcionalidades

- Operações CRUD para tickers financeiros
- Cálculo de métricas financeiras incluindo:
  - Rentabilidade acumulada
  - Rentabilidade acumulada mensal

## Estrutura do Projeto

```
api_icatu/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Ponto de entrada da aplicação FastAPI
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py              # Dependências de injeção
│   │   ├── metadata.py          # Metadados da API para documentação
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── ticker.py    # Endpoints para tickers
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py            # Configurações da aplicação
│   ├── crud/
│   │   ├── __init__.py
│   │   └── financial.py         # Operações de banco de dados
│   ├── db/
│   │   ├── __init__.py
│   │   └── session.py           # Sessão do banco de dados
│   ├── models/
│   │   ├── __init__.py
│   │   └── financial/
│   │       ├── __init__.py
│   │       ├── dim_ticker.py    # Modelo SQLAlchemy para ticker
│   │       └── dim_ticker_type.py # Modelo SQLAlchemy para tipo de ticker
│   └── schemas/
│       ├── __init__.py
│       └── ticker.py            # Schemas Pydantic
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

## Executando a Aplicação

```bash
uvicorn app.main:app --reload
```

A API estará disponível em http://localhost:8000.

A documentação da API está disponível em:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints da API

### Tickers
- `GET /api/v1/tickers/` - Listar todos os tickers
- `POST /api/v1/tickers/` - Criar um novo ticker
- `GET /api/v1/tickers/{ticker_id}` - Obter um ticker específico
- `PUT /api/v1/tickers/{ticker_id}` - Atualizar um ticker
- `DELETE /api/v1/tickers/{ticker_id}` - Excluir um ticker

### Métricas Financeiras
- `POST /api/v1/tickers/profitability/cumulative` - Calcular rentabilidade acumulada
- `POST /api/v1/tickers/profitability/monthly` - Calcular rentabilidade acumulada mensal

## Implantação com Docker

O projeto inclui configurações Docker para facilitar a implantação:

```bash
# Construir e iniciar os contêineres
docker-compose up --build

# Executar em segundo plano
docker-compose up -d
```

## Estrutura do Banco de Dados

A aplicação utiliza duas tabelas principais:

1. `financial_s.dim_ticker_type_tb` - Armazena os tipos de ticker
   - `ticker_type_id`: Identificador único do tipo
   - `ticker_type_nm`: Nome do tipo de ticker
   - `is_src`: Indica se é uma fonte de dados

2. `financial_s.dim_ticker_tb` - Armazena os tickers
   - `ticker_id`: Identificador único do ticker
   - `ticker_nm`: Nome do ticker
   - `ticker_type_id`: Referência ao tipo de ticker
   - `annual_tax`: Taxa anual (quando aplicável)

## Contribuição

1. Faça um fork do projeto
2. Crie sua branch de funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## Licença

MIT