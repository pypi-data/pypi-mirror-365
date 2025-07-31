"""
DaedalusPy - Framework para Engenharia de Dados Multi-Cloud

Este módulo fornece ferramentas para automatizar e padronizar o desenvolvimento
de soluções de engenharia de dados em múltiplas plataformas cloud.

Módulos principais:
- data: Biblioteca para templates e estruturas de dados
- generator: Biblioteca para geração de entidades e integrações  
- services: Biblioteca para templates de serviços

Exemplo de uso:
    from data_lib.generator.data_entity import generate_entity_file
    
    generate_entity_file(
        cloud_provider="azure",
        classname="MinhaEntidade",
        file_extension="parquet",
        columns=['col1', 'col2'],
        imports="import pandas as pd",
        read_code="return pd.read_parquet(buffer)",
        write_code="data.to_parquet(buffer, index=False)",
        output_path="./output"
    )

Autor: Golden Valley Consulting LTDA
Licença: MIT
"""

__version__ = "1.0.0"
__author__ = "Golden Valley Consulting LTDA"

# Importações principais
from . import data
from . import generator
from . import services

__all__ = ['data', 'generator', 'services']