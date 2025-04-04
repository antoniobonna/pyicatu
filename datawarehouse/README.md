# Armazém de Dados Financeiros

Este projeto dbt implementa um data warehouse multidimensional para séries temporais de dados financeiros.

## Visão Geral do Projeto

Este projeto transforma dados financeiros brutos em um modelo dimensional com:
- Tabelas de dimensão para tickers, tipos de ticker e datas
- Uma tabela fato para dados de séries financeiras com métricas de rentabilidade
- Suporte para carregamento incremental
- Particionamento temporal por ano e mês

## Primeiros Passos

### Pré-requisitos

- dbt 1.3.0 ou superior
- Banco de dados PostgreSQL
- Pacote dbt-utils

### Instalação

1. Clone este repositório
2. Atualize o arquivo `profiles.yml` com os dados de conexão do seu banco de dados
3. Execute `dbt deps` para instalar as dependências
4. Execute `dbt run` para construir os modelos

## Estrutura do Projeto

Este projeto segue as [melhores práticas do dbt](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview) para estruturação:

- **staging**: Limpeza e padronização dos dados brutos
- **marts/dimensions**: Tabelas de dimensão (ticker, tipo de ticker, data)
- **marts/facts**: Tabelas fato (dados de séries financeiras)
- **macros**: Funcionalidades customizadas para particionamento

## Uso

### Reconstrução Completa

Para executar uma reconstrução completa de todos os modelos:
```bash
dbt run --full-refresh
```

### Carregamento Incremental

Para executar um carregamento incremental (processando apenas novos dados):
```bash
dbt run
```

## Testes

Execute a suíte de testes com:
```bash
dbt test
```

## Documentação

Gere e visualize a documentação com:
```bash
dbt docs generate
dbt docs serve --port 8081
```

## Contribuindo

1. Crie uma branch de funcionalidade
2. Faça suas alterações
3. Execute os testes
4. Envie um pull request