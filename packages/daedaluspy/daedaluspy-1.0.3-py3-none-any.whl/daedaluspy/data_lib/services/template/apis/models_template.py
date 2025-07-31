MODEL_TEMPLATE = """
from dataclasses import dataclass
from typing import Optional

@dataclass
class {data_name}:
    {columns}
    
    def to_dict(self) -> dict:
        \"\"\"
        Converte o modelo para um dicionário.
        \"\"\"
        return self.__dict__
"""