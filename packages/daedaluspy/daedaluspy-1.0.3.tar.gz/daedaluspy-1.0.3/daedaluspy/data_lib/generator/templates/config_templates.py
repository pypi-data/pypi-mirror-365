CONFIG_TEMPLATE = '''
import os
from dataclasses import dataclass, fields, field
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Union
from abc import ABC, abstractmethod
from pyspark.sql import SparkSession
from enum import Enum

class EnvSource(Enum):
    """Enum para definir a fonte das variáveis de ambiente"""
    SPARK = "spark"
    DOTENV = "dotenv"

@dataclass
class BaseConfig:
    """Classe base para configurações usando variáveis de ambiente"""
    env_source: EnvSource = EnvSource.DOTENV
    spark_session: Optional[SparkSession] = None
    env_file_path: Optional[str] = None
    
    def __post_init__(self):
        """Valida e carrega variáveis de ambiente após inicialização"""
        if self.env_source == EnvSource.SPARK and self.spark_session is None:
            raise ValueError("Para usar a fonte 'SPARK', é necessário fornecer uma SparkSession.")
        if self.env_source == EnvSource.DOTENV and self.env_file_path is None:
            raise ValueError("Para usar a fonte 'DOTENV', é necessário fornecer o caminho do arquivo .env.")
        self._load_env_vars()

    def _load_env_vars(self):
        """Carrega as variáveis de ambiente conforme a fonte escolhida"""
        if self.env_source == EnvSource.SPARK:
            self._load_from_spark()
        elif self.env_source == EnvSource.DOTENV:
            self._load_from_dotenv()
        else:
            raise ValueError(f"Fonte de ambiente inválida: {self.env_source}")

    def _load_from_spark(self):
        """Carrega variáveis do Spark Context"""
        for field in fields(self):
            if field.name in ['env_source', 'spark_session', 'env_file_path']:
                continue
            env_key = field.name.upper()
            val = self.spark_session.sparkContext.environment.get(env_key)
            if val is None:
                raise ValueError(f"Variável de ambiente obrigatória '{env_key}' não está definida no Spark.")
            setattr(self, field.name, val)

    def _load_from_dotenv(self):
        """Carrega variáveis de arquivo .env"""
        try:
            from dotenv import load_dotenv
            load_dotenv(self.env_file_path)
        except ImportError:
            raise ValueError("python-dotenv não está instalado.")
        
        for field in fields(self):
            if field.name in ['env_source', 'spark_session', 'env_file_path']:
                continue
            env_key = field.name.upper()
            val = os.getenv(env_key)
            if val is None:
                raise ValueError(f"Variável de ambiente obrigatória '{env_key}' não está definida no .env.")
            setattr(self, field.name, val)

@dataclass
class AzureConfig(BaseConfig):
    """Configurações base compartilhadas entre os ambientes.
    OBS: attribute name has to be equal to the environment variable name."""

    AZURE_APP_CLIENT_ID: str = field(init=False) 
    AZURE_APP_CLIENT_SECRET: str = field(init=False)
    AZURE_APP_TENANT: str = field(init=False)

    
@dataclass
class GoogleConfig(BaseConfig):
    """Configurações base compartilhadas entre os ambientes.
    OBS: attribute name has to be equal to the environment variable name."""

    GOOGLE_APP_CLIENT_ID: str = field(init=False)
    GOOGLE_APP_CLIENT_SECRET: str = field(init=False)
    GOOGLE_APP_TENANT: str = field(init=False)


@dataclass
class AWSConfig(BaseConfig):
    """Configurações base compartilhadas entre os ambientes.
    OBS: attribute name has to be equal to the environment variable name."""

    AWS_ACCESS_KEY_ID: str = field(init=False)
    AWS_SECRET_ACCESS_KEY: str = field(init=False)
    AWS_REGION: str = field(init=False)

    
@dataclass
class DatabaseConfig(BaseConfig):
    """Configurações base compartilhadas entre os ambientes.
    OBS: attribute name has to be equal to the environment variable name."""
        
    DB_HOST: str = field(init=False)
    DB_PORT: int = field(init=False)
    DB_NAME: str = field(init=False)
    DB_USER: str = field(init=False)
    DB_PASSWORD: str = field(init=False)
    DB_DRIVER: str = field(init=False, default="postgresql")

    
@dataclass
class PipelineConfig:
    """Configuração unificada para pipeline"""    
    configurations: Dict[str, Union[AzureConfig, GoogleConfig, AWSConfig, DatabaseConfig]] = field(default_factory=dict, init=False)
    services: Dict[str, Any] = field(default_factory=dict, init=False)
    data_target: Dict[str, Any] = field(default_factory=dict, init=False)
    data_sources: Dict[str, Any] = field(default_factory=dict, init=False)
    
    def add_configuration(self, config: Union[AzureConfig, GoogleConfig, AWSConfig, DatabaseConfig], name: str):
        """Adiciona uma configuração ao pipeline"""
        self.configurations[name] = config
        return self

    def add_service(self, service_name: str, service_instance: Any):
        """Adiciona um serviço ao pipeline"""
        self.services[service_name] = service_instance
        return self

    def add_data_target(self, target_name: str, target_instance: Any):
        """Adiciona um target de dados ao pipeline"""
        self.data_target[target_name] = target_instance
        return self

    def add_data_source(self, source_name: str, source_instance: Any):
        """Adiciona uma fonte de dados ao pipeline"""
        self.data_sources[source_name] = source_instance
        return self
    
    def get_configuration(self, name: str):
        """Obtém uma configuração específica"""
        return self.configurations.get(name)
    
    def get_service(self, service_name: str):
        """Obtém um serviço específico"""
        return self.services.get(service_name)
    
    def get_data_target(self, target_name: str):
        """Obtém um target de dados específico"""
        return self.data_target.get(target_name)
    
    def get_data_source(self, source_name: str):
        """Obtém uma fonte de dados específica"""
        return self.data_sources.get(source_name)
    
    def list_configurations(self) -> List[str]:
        """Lista todas as configurações disponíveis"""
        return list(self.configurations.keys())
    
    def list_services(self) -> List[str]:
        """Lista todos os serviços disponíveis"""
        return list(self.services.keys())
    
    def list_data_target(self) -> List[str]:
        """Lista todos os targets de dados disponíveis"""
        return list(self.data_target.keys())
    
    def list_data_sources(self) -> List[str]:
        """Lista todas as fontes de dados disponíveis"""
        return list(self.data_sources.keys())
    
    def get_pipeline_summary(self) -> Dict[str, Any]:
        """Retorna um resumo completo do pipeline"""
        return {
            'configurations': self.list_configurations(),
            'services': self.list_services(),
            'data_target': self.list_data_target(),
            'data_sources': self.list_data_sources(),
            'total_components': len(self.configurations) + len(self.services) + len(self.data_target) + len(self.data_sources)
        }

'''