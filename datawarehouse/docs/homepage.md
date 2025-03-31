
{% docs __overview__ %}

# Data Warehouse Financeiro

Este projeto DBT implementa um **data warehouse dimensional** para séries temporais financeiras, com suporte a carga incremental, documentação automatizada e integridade referencial entre dimensões e fatos.

---

## 🧾 Visão Geral

Este projeto transforma dados financeiros brutos em um modelo dimensional, com:

- Tabelas de dimensão para: tickers, tipos de ticker e datas
- Tabela fato com métricas de rentabilidade (profitability)
- Suporte à carga incremental de dados
- Constraints no banco de dados: `PRIMARY KEY`, `FOREIGN KEY`, `UNIQUE`
- Testes automatizados com `dbt test`
- Documentação interativa com `dbt docs`

---

## 📁 Estrutura de Diretórios

```
.
datawarehouse/
├── analyses/          # Análises SQL ad-hoc
├── dbt_packages/      # Dependências instaladas
├── docs/              # Documentação gerada
├── logs/              # Logs de execução
├── macros/            # Macros reutilizáveis
├── models/            → Coração do projeto
│   ├── marts/
│   │   └── financial/  # Modelos finais (camada business)
│   │       ├── dimensions/  # Dimensões
│   │       │   ├── dim_date_tb.sql
│   │       │   ├── dim_ticker_tb.sql
│   │       │   └── dim_ticker_type_tb.sql
│   │       ├── facts/       # Fatos
│   │       │   └── fct_serie_tb.sql
│   │       └── financial.yml  # Esquema YAML
│   └── staging/       # Camada de staging
│       └── financial/
│           ├── stg_financial.yml
│           ├── vw_stg_raw_market_data.sql
│           └── _sources.yml  # Definição de fontes
├── seeds/            # Dados estáticos/referência
├── target/           # Artefatos compilados
├── tests/            # Testes personalizados
├── .gitignore        # Arquivos ignorados pelo Git
├── .user.yml         # Configurações de usuário (local)
├── dbt_project.yml   → Configuração principal
├── package-lock.yml  # Versões exatas de pacotes
├── packages.yml      # Dependências do projeto
└── profiles.yml      → Conexões com banco de dados
```

---

## 🚀 Primeiros Passos

### Pré-requisitos

- Python com `dbt-core` e `dbt-postgres` instalados
- PostgreSQL operacional com acesso
- Dependência: pacote `dbt-utils`

---

## ⚙️ Instalação

```bash
# 1. Clone o repositório
git clone https://seu-repo.git

# 2. Atualize o profiles.yml com suas credenciais

# 3. Instale dependências
dbt deps

# 4. Execute o projeto
dbt run
```

---

## 🔄 Modos de Execução

### Carga completa

```bash
dbt run --full-refresh
```

### Carga incremental (padrão)

```bash
dbt run
```

---

## ✅ Testes de Qualidade

Execute os testes definidos no arquivo `financial.yml` com:

```bash
dbt test
```

---

## 📚 Documentação

Gere e visualize a documentação interativa com:

```bash
dbt docs generate
dbt docs serve --port 8081
```

---

## 🤝 Contribuindo

1. Crie uma branch de feature
2. Faça alterações locais
3. Execute os testes e o `dbt run`
4. Submeta um Pull Request com a descrição da mudança

---

{% enddocs %}
