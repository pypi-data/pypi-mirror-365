"""
Template para flowbuilder.py - Orquestração do pipeline
"""

FLOWBUILDER_TEMPLATE = '''"""
FlowBuilder para {project_name}
"""
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Optional
from .config import pipeline_config
from .steps import DataCleaningStep, DataTransformStep, DataValidationStep
from .base import StepResult, ProcessStep


class {project_class_name}FlowBuilder:
    """Construtor de fluxo para {project_name}"""
    
    def __init__(self):
        self.pipeline_config = pipeline_config
        self.data: pd.DataFrame = pd.DataFrame()
        self.step_results: List[StepResult] = []
        self.date_reference: Optional[datetime] = None
    
    def set_date_reference(self, date_ref: datetime):
        """Define a data de referência para o pipeline"""
        self.date_reference = date_ref
        return self
    
    def collect(self) -> '{project_class_name}FlowBuilder':
        """Coleta dados das fontes configuradas"""
        try:
            for source_name in self.pipeline_config.list_data_sources():
                data_source = self.pipeline_config.get_data_source(source_name)
                storage_client = self.pipeline_config.get_storage_client(source_name)
                source_data = data_source.read_data_by_date(storage_client)
                # Recomenda-se criar um atributo para cada fonte:
                setattr(self, f"data_{source_name}", source_data)
        except Exception as e:
            step_result = StepResult(
                success=False,
                message=f"Erro na coleta de dados: {str(e)}",
                metadata={"error": str(e), "step": "collect"}
            )
            self.step_results.append(step_result)
        return self
    
    def process(self, process_step: ProcessStep) -> '{project_class_name}FlowBuilder':
        """Processa os dados com um step específico"""
        try:
            result = process_step.execute(self.data)
            if result.success and result.data is not None:
                self.data = result.data
            self.step_results.append(result)
        except Exception as e:
            step_result = StepResult(
                success=False,
                message=f"Erro no step {process_step.name}: {str(e)}",
                metadata={"error": str(e), "step": process_step.name}
            )
            self.step_results.append(step_result)
        return self
    
    def save(self) -> '{project_class_name}FlowBuilder':
        """Salva os dados no target configurado"""
        try:
            target_name = self.pipeline_config.list_data_targets()[0]
            data_target = self.pipeline_config.get_data_target(target_name)
            data_target.write_data_by_date(self.data, self.date_reference)
            # Recomenda-se criar um atributo para indicar que o target foi salvo:
            setattr(self, f"saved_{target_name}", True)
        except Exception as e:
            step_result = StepResult(
                success=False,
                message=f"Erro no salvamento: {str(e)}",
                metadata={"error": str(e), "step": "save"}
            )
            self.step_results.append(step_result)
        return self
    
    def get_results(self) -> List[StepResult]:
        """Retorna todos os resultados dos steps"""
        return self.step_results
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo da execução"""
        successful_steps = [r for r in self.step_results if r.success]
        failed_steps = [r for r in self.step_results if not r.success]
        
        return {{
            "total_steps": len(self.step_results),
            "successful_steps": len(successful_steps),
            "failed_steps": len(failed_steps),
            "final_data_rows": len(self.data) if self.data is not None else 0,
            "pipeline_config": self.pipeline_config.get_pipeline_summary(),
            "execution_summary": [
                {{
                    "step": i + 1,
                    "success": result.success,
                    "message": result.message,
                    "timestamp": result.timestamp.isoformat()
                }}
                for i, result in enumerate(self.step_results)
            ]
        }}
    
    def reset(self):
        """Reseta o estado do builder"""
        self.data = pd.DataFrame()
        self.step_results = []
        self.date_reference = None
'''