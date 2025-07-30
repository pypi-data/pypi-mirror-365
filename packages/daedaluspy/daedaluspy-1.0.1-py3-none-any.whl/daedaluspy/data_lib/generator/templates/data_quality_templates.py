"""
Templates para Data Quality - Versão simplificada
"""

DATA_QUALITY_INIT_TEMPLATE = '''"""
Data Quality - Validação simples de dados
"""

from .validator import DataQuality
from .rules import QualityRules

__all__ = ['DataQuality', 'QualityRules']
'''

DATA_QUALITY_VALIDATOR_TEMPLATE = '''"""
Validador de qualidade de dados - Simples e direto
"""

import pandas as pd
from typing import List, Dict
from .rules import QualityRules


class DataQuality:
    """Validação simples de qualidade de dados"""
    
    custom_quality_rules: List[QualityRules] = []
    
    @staticmethod
    def validate_schema(entity, data: pd.DataFrame) -> bool:
        """Valida se DataFrame tem as colunas da entidade"""
        if not hasattr(entity, 'Columns'):
            return False
        
        expected_cols = [getattr(entity.Columns, attr) for attr in dir(entity.Columns) if not attr.startswith('_')]
        missing_cols = set(expected_cols) - set(data.columns)
        return len(missing_cols) == 0
    
    @staticmethod
    def validate_no_nulls(data: pd.DataFrame, columns: List[str] = None) -> bool:
        """Valida se não há nulos nas colunas especificadas"""
        if columns is None:
            columns = data.columns.tolist()
        
        for col in columns:
            if col in data.columns and data[col].isnull().any():
                return False
        return True
    
    @staticmethod
    def validate_unique(data: pd.DataFrame, columns: List[str]) -> bool:
        """Valida se não há duplicatas nas colunas especificadas"""
        missing_cols = set(columns) - set(data.columns)
        if missing_cols:
            return False
        return not data.duplicated(subset=columns).any()
    
    @staticmethod
    def validate_types(data: pd.DataFrame, type_map: Dict[str, str]) -> bool:
        """Valida tipos básicos das colunas"""
        for col, expected_type in type_map.items():
            if col not in data.columns:
                return False
            
            actual_type = str(data[col].dtype)
            
            if expected_type == 'int' and 'int' not in actual_type:
                return False
            elif expected_type == 'float' and 'float' not in actual_type:
                return False
            elif expected_type == 'string' and 'object' not in actual_type:
                return False
        
        return True
    
    @staticmethod
    def validate_custom_rules(data: pd.DataFrame, rules: List[QualityRules]) -> Dict[str, bool]:
        """Executa regras customizadas de validação"""
        results = {}
        
        for rule in rules:
            rule_name = rule.__class__.__name__
            try:
                results[rule_name] = rule.validate(data)
            except Exception:
                results[rule_name] = False
        
        return results
    
    @staticmethod
    def get_quality_score(data: pd.DataFrame, checks: Dict) -> float:
        """Retorna score de 0.0 a 1.0"""
        passed = 0
        total = 0
        
        if 'entity' in checks:
            total += 1
            if DataQuality.validate_schema(checks['entity'], data):
                passed += 1
        
        if 'no_nulls' in checks:
            total += 1
            if DataQuality.validate_no_nulls(data, checks['no_nulls']):
                passed += 1
        
        if 'unique' in checks:
            total += 1
            if DataQuality.validate_unique(data, checks['unique']):
                passed += 1
        
        if 'types' in checks:
            total += 1
            if DataQuality.validate_types(data, checks['types']):
                passed += 1
        
        if 'custom_rules' in checks:
            custom_results = DataQuality.validate_custom_rules(data, checks['custom_rules'])
            for result in custom_results.values():
                total += 1
                if result:
                    passed += 1
        
        return passed / total if total > 0 else 1.0
'''

DATA_QUALITY_RULES_TEMPLATE = '''"""
Classe base para regras de qualidade customizadas
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import List


class QualityRules(ABC):
    """
    Classe abstrata para regras de qualidade de dados.
    Herde desta classe e implemente o método validate.
    """
    
    @abstractmethod
    def validate(self, data: pd.DataFrame) -> bool:
        """
        Executa a validação de qualidade.
        Deve retornar True se passou, False se falhou.
        """
        pass


# Exemplo de regras básicas
class BasicDataRules(QualityRules):
    """Regras básicas de qualidade de dados"""
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Valida regras básicas: não vazio e tem colunas"""
        return len(data) > 0 and len(data.columns) > 0


class NoNegativeValuesRule(QualityRules):
    """Regra que verifica se não há valores negativos em colunas numéricas"""
    
    def __init__(self, columns: List[str] = None):
        self.columns = columns
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Verifica se não há valores negativos"""
        check_columns = self.columns if self.columns else data.select_dtypes(include=['number']).columns
        
        for col in check_columns:
            if col in data.columns:
                if (data[col] < 0).any():
                    return False
        return True


class EmailFormatRule(QualityRules):
    """Regra que verifica formato de email"""
    
    def __init__(self, email_column: str = 'email'):
        self.email_column = email_column
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Verifica formato básico de email"""
        if self.email_column not in data.columns:
            return True  # Se não tem coluna de email, passa
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$'
        return data[self.email_column].str.match(email_pattern, na=False).all()


class AgeRangeRule(QualityRules):
    """Regra que verifica range de idade válido"""
    
    def __init__(self, age_column: str = 'idade', min_age: int = 0, max_age: int = 120):
        self.age_column = age_column
        self.min_age = min_age
        self.max_age = max_age
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Verifica se idade está em range válido"""
        if self.age_column not in data.columns:
            return True
        
        return ((data[self.age_column] >= self.min_age) & 
                (data[self.age_column] <= self.max_age)).all()
'''

DATA_QUALITY_EXAMPLE_TEMPLATE = '''"""
Exemplos simples de uso do Data Quality
"""

import pandas as pd
from data.base import BaseEntity
from tools.data_quality import DataQuality
from tools.data_quality.rules import QualityRules, BasicDataRules, NoNegativeValuesRule, EmailFormatRule


# Exemplo de entidade
class UserEntity(BaseEntity):
    class Columns:
        ID = "id"
        NAME = "name"
        EMAIL = "email"
        AGE = "age"


# Exemplo de regra customizada
class CustomBusinessRule(QualityRules):
    """Regra de negócio específica"""
    
    def validate(self, data: pd.DataFrame) -> bool:
        """Exemplo: nome não pode estar vazio"""
        if 'name' in data.columns:
            return not data['name'].isnull().any() and not (data['name'] == '').any()
        return True


def exemplo_validacao_basica():
    """Exemplo básico de validação"""
    print("=== Validação Básica ===")
    
    # Dados válidos
    data_valida = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['João', 'Maria', 'Pedro'],
        'email': ['joao@test.com', 'maria@test.com', 'pedro@test.com'],
        'age': [25, 30, 35]
    })
    
    # Dados inválidos
    data_invalida = pd.DataFrame({
        'id': [1, 2, 2],  # ID duplicado
        'name': ['João', '', 'Pedro'],  # Nome vazio
        'email': ['joao@test.com', 'email-invalido', 'pedro@test.com'],  # Email inválido
        'age': [25, -5, 150]  # Idade negativa e muito alta
    })
    
    entity = UserEntity()
    
    # Testando dados válidos
    print("\\nDados válidos:")
    print(f"Schema: {DataQuality.validate_schema(entity, data_valida)}")
    print(f"Sem nulos: {DataQuality.validate_no_nulls(data_valida, ['id', 'name'])}")
    print(f"IDs únicos: {DataQuality.validate_unique(data_valida, ['id'])}")
    print(f"Tipos corretos: {DataQuality.validate_types(data_valida, {'id': 'int', 'name': 'string'})}")
    
    # Testando dados inválidos
    print("\\nDados inválidos:")
    print(f"Schema: {DataQuality.validate_schema(entity, data_invalida)}")
    print(f"Sem nulos: {DataQuality.validate_no_nulls(data_invalida, ['id', 'name'])}")
    print(f"IDs únicos: {DataQuality.validate_unique(data_invalida, ['id'])}")


def exemplo_regras_customizadas():
    """Exemplo usando regras customizadas"""
    print("\\n=== Regras Customizadas ===")
    
    data_teste = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['João', 'Maria', ''],  # Nome vazio vai falhar
        'email': ['joao@test.com', 'email-invalido', 'pedro@test.com'],  # Email inválido
        'value': [100, 200, -50]  # Valor negativo vai falhar
    })
    
    # Define regras customizadas
    regras = [
        BasicDataRules(),
        CustomBusinessRule(),
        NoNegativeValuesRule(['value']),
        EmailFormatRule('email')
    ]
    
    # Executa validação com regras customizadas
    resultados = DataQuality.validate_custom_rules(data_teste, regras)
    
    print("\\nResultados das regras customizadas:")
    for regra, passou in resultados.items():
        status = "✓ PASSOU" if passou else "✗ FALHOU"
        print(f"{regra}: {status}")


def exemplo_score_qualidade():
    """Exemplo de cálculo de score de qualidade"""
    print("\\n=== Score de Qualidade ===")
    
    # Dados com problemas mistos
    data_mista = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['João', 'Maria', 'Pedro'],  # OK
        'email': ['joao@test.com', 'maria@test.com', 'pedro@test.com'],  # OK
        'age': [25, 30, 35],  # OK
        'value': [100, 200, 300]  # OK
    })
    
    entity = UserEntity()
    regras_customizadas = [BasicDataRules(), CustomBusinessRule()]
    
    # Define todas as verificações
    checks = {
        'entity': entity,
        'no_nulls': ['id', 'name'],
        'unique': ['id'],
        'types': {'id': 'int', 'name': 'string', 'age': 'int'},
        'custom_rules': regras_customizadas
    }
    
    # Calcula score
    score = DataQuality.get_quality_score(data_mista, checks)
    
    print(f"\\nScore de qualidade: {score:.1%}")
    
    if score >= 0.9:
        print("🟢 Qualidade EXCELENTE")
    elif score >= 0.7:
        print("🟡 Qualidade BOA")
    elif score >= 0.5:
        print("🟠 Qualidade REGULAR")
    else:
        print("🔴 Qualidade CRÍTICA")


if __name__ == "__main__":
    # Executa todos os exemplos
    exemplo_validacao_basica()
    exemplo_regras_customizadas()
    exemplo_score_qualidade()
'''
