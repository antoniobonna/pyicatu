"""
API metadata for documentation.

This module contains metadata for OpenAPI documentation,
including tag descriptions and other documentation enhancements.
"""

# API Tags metadata
tags_metadata = [
    {
        "name": "Tickers",
        "description": """<h3>Gerenciar tickers financeiros</h3>
                <p>Estes endpoints permitem criar, ler, atualizar e excluir tickers financeiros.</p>
                <ul><li>Criar novos tickers com seus tipos associados</li><li>
                Recuperar informações de tickers</li><li>
                Atualizar propriedades dos tickers</li>
                <li>Remover tickers do banco de dados</li></ul>""",
    },
    {
        "name": "Rentabilidade",
        "description": """<h3>Calcular métricas de rentabilidade financeira</h3><p>Estes endpoints calculam várias métricas de rentabilidade para instrumentos financeiros.</p><ul><li>Calcular rentabilidade acumulada em intervalos de datas específicos</li><li>Calcular rentabilidade acumulada mensal</li></ul><p><strong>Nota:</strong> Todos os cálculos usam dias úteis (252 dias por ano).</p>""",
    },
]
