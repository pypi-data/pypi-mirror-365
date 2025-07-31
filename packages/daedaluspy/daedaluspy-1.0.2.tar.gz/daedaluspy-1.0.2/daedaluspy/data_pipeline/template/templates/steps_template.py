"""
Template para steps.py - Steps específicos do pipeline
"""

STEPS_TEMPLATE = '''"""
Steps específicos para {project_name}
"""
import pandas as pd
from typing import Dict, List
from .base import ProcessStep, StepResult


class DataCleaningStep(ProcessStep):
    """Step para limpeza de dados"""
    
    def __init__(self):
        super().__init__("DataCleaning")
    
    def execute(self, data: pd.DataFrame) -> StepResult:
        """Executa limpeza dos dados"""
        try:
            # Remover linhas completamente vazias
            cleaned_data = data.dropna(how='all')
            
            # Remover duplicatas
            cleaned_data = cleaned_data.drop_duplicates()
            
            # Limpar espaços em branco em colunas de texto
            string_columns = cleaned_data.select_dtypes(include=['object']).columns
            for col in string_columns:
                cleaned_data[col] = cleaned_data[col].astype(str).str.strip()
            
            # Substituir valores vazios por None
            cleaned_data = cleaned_data.replace(['', 'NULL', 'null'], None)
            
            rows_removed = len(data) - len(cleaned_data)
            
            return StepResult(
                success=True,
                data=cleaned_data,
                message=f"Limpeza concluída. {{rows_removed}} linhas removidas.",
                metadata={{
                    "original_rows": len(data),
                    "cleaned_rows": len(cleaned_data),
                    "rows_removed": rows_removed
                }}
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message=f"Erro na limpeza: {{str(e)}}",
                metadata={{"error": str(e)}}
            )


class DataTransformStep(ProcessStep):
    """Step para transformação de dados"""
    
    def __init__(self):
        super().__init__("DataTransform")
    
    def execute(self, data: pd.DataFrame) -> StepResult:
        """Executa transformações nos dados"""
        try:
            transformed_data = data.copy()
            
            # Converter datas se necessário
            date_columns = ['created_at', 'updated_at', 'date_field']
            for col in date_columns:
                if col in transformed_data.columns:
                    transformed_data[col] = pd.to_datetime(transformed_data[col], errors='coerce')
            
            # Converter valores numéricos
            numeric_columns = ['value', 'amount', 'quantity']
            for col in numeric_columns:
                if col in transformed_data.columns:
                    transformed_data[col] = pd.to_numeric(transformed_data[col], errors='coerce')
            
            # Adicionar colunas calculadas
            if 'created_at' in transformed_data.columns:
                transformed_data['year'] = transformed_data['created_at'].dt.year
                transformed_data['month'] = transformed_data['created_at'].dt.month
            
            # Normalizar texto
            text_columns = ['name', 'description', 'title']
            for col in text_columns:
                if col in transformed_data.columns:
                    transformed_data[col] = transformed_data[col].str.lower().str.strip()
            
            return StepResult(
                success=True,
                data=transformed_data,
                message="Transformação concluída com sucesso.",
                metadata={{
                    "columns_transformed": len(transformed_data.columns),
                    "rows_processed": len(transformed_data)
                }}
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message=f"Erro na transformação: {{str(e)}}",
                metadata={{"error": str(e)}}
            )


class DataValidationStep(ProcessStep):
    """Step para validação de dados"""
    
    def __init__(self):
        super().__init__("DataValidation")
    
    def validate_not_empty(self, data: pd.DataFrame, column: str) -> bool:
        """Valida se uma coluna não está vazia"""
        return not data[column].isna().all()
    
    def validate_data_types(self, data: pd.DataFrame, expected_types: Dict[str, str]) -> List[str]:
        """Valida tipos de dados das colunas"""
        errors = []
        for column, expected_type in expected_types.items():
            if column in data.columns:
                actual_type = str(data[column].dtype)
                if expected_type not in actual_type:
                    errors.append(f"Coluna {{column}}: esperado {{expected_type}}, encontrado {{actual_type}}")
        return errors
    
    def validate_required_columns(self, data: pd.DataFrame, required_columns: List[str]) -> List[str]:
        """Valida se todas as colunas obrigatórias estão presentes"""
        missing = [col for col in required_columns if col not in data.columns]
        return [f"Coluna obrigatória ausente: {{col}}" for col in missing]
    
    def execute(self, data: pd.DataFrame) -> StepResult:
        """Executa validação dos dados"""
        try:
            validation_errors = []
            
            # Validar se o DataFrame não está vazio
            if data.empty:
                validation_errors.append("DataFrame está vazio")
            
            # Validar colunas obrigatórias (customize conforme necessário)
            required_columns = ['id']  # Adicione suas colunas obrigatórias
            missing_columns = self.validate_required_columns(data, required_columns)
            validation_errors.extend(missing_columns)
            
            # Validar tipos de dados (customize conforme necessário)
            expected_types = {{
                'id': 'int',
                'name': 'object'
            }}
            type_errors = self.validate_data_types(data, expected_types)
            validation_errors.extend(type_errors)
            
            # Validar valores únicos em colunas que devem ser únicas
            unique_columns = ['id']  # Adicione suas colunas únicas
            for col in unique_columns:
                if col in data.columns:
                    if data[col].duplicated().any():
                        validation_errors.append(f"Valores duplicados encontrados na coluna {{col}}")
            
            # Validar ranges de valores
            if 'value' in data.columns:
                if (data['value'] < 0).any():
                    validation_errors.append("Valores negativos encontrados na coluna 'value'")
            
            success = len(validation_errors) == 0
            
            return StepResult(
                success=success,
                data=data,
                message="Validação concluída." if success else f"{{len(validation_errors)}} erros encontrados.",
                metadata={{
                    "validation_errors": validation_errors,
                    "rows_validated": len(data),
                    "columns_validated": len(data.columns)
                }}
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                message=f"Erro na validação: {{str(e)}}",
                metadata={{"error": str(e)}}
            )
'''
