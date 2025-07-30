"""
Template para __init__.py - Exportações do módulo
"""

INIT_TEMPLATE = '''"""
Pipeline {project_name}
Sistema: {system_name}
Dados: {dataname}
Tier: {tier}
"""

from .main import main
from .flowbuilder import {project_class_name}FlowBuilder
from .config import pipeline_config
from .steps import DataCleaningStep, DataTransformStep, DataValidationStep
from .base import StepResult, ProcessStep, BaseValidator

__version__ = "0.1.0"
__author__ = "Data Engineering Team"

# Exportações principais
__all__ = [
    "main",
    "{project_class_name}FlowBuilder",
    "pipeline_config",
    "DataCleaningStep",
    "DataTransformStep", 
    "DataValidationStep",
    "StepResult",
    "ProcessStep",
    "BaseValidator"
]
'''
