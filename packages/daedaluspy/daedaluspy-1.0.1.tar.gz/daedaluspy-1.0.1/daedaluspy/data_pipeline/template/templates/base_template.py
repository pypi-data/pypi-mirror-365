"""
Template para base.py - Classes base para pipeline
"""

BASE_TEMPLATE = '''"""
Classes base para {project_name}
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional
import pandas as pd


class StepResult:
    """Resultado de um step do pipeline"""
    
    def __init__(self, success: bool, data: Optional[pd.DataFrame] = None, 
                 message: str = "", metadata: Optional[Dict[str, Any]] = None):
        self.success = success
        self.data = data
        self.message = message
        self.metadata = metadata or {{}}
        self.timestamp = datetime.now()
    
    def __repr__(self):
        return f"StepResult(success={{{{self.success}}}}, message='{{{{self.message}}}}')"


class ProcessStep(ABC):
    """Classe base para steps do pipeline"""
    
    def __init__(self, name: str):
        self.name = name
        self.execution_time = None
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    def execute(self, data: pd.DataFrame) -> StepResult:
        """Executa o step com os dados fornecidos"""
        pass
    
    def _start_execution(self):
        """Marca o início da execução"""
        self.start_time = datetime.now()
    
    def _end_execution(self):
        """Marca o fim da execução"""
        self.end_time = datetime.now()
        if self.start_time:
            self.execution_time = (self.end_time - self.start_time).total_seconds()
    
    def run(self, data: pd.DataFrame) -> StepResult:
        """Executa o step com controle de tempo"""
        self._start_execution()
        try:
            result = self.execute(data)
            self._end_execution()
            return result
        except Exception as e:
            self._end_execution()
            return StepResult(
                success=False,
                message=f"Erro no step {{{{self.name}}}}: {{{{str(e)}}}}",
                metadata={{"error": str(e), "step": self.name}}
            )
'''
