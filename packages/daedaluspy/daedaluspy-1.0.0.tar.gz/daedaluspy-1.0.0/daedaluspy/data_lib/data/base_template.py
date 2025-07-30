"""
Template para base.py - classes base para entidades de dados
"""
BASE_DATA_TEMPLATE = '''"""
Base classes para entidades de dados
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional, Type
from datetime import datetime
from io import BytesIO
from enum import StrEnum
import pandas as pd
import json


class FileExtensionHandler(ABC):
    """Classe abstrata para handlers de extensões de arquivo"""
    
    @property
    @abstractmethod
    def extension(self) -> str:
        """Retorna a extensão do arquivo"""
        pass
    
    @abstractmethod
    def read_data(self, buffer: BytesIO) -> Any:
        """Lê dados do buffer"""
        pass
    
    @abstractmethod
    def write_data(self, data: Any, buffer: BytesIO) -> None:
        """Escreve dados no buffer"""
        pass


class StorageProvider(ABC):
    """Classe abstrata para providers de storage"""
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Retorna o nome do provider"""
        pass
    
    @abstractmethod
    def get_data_buffer(self, path: str, storage_client) -> BytesIO:
        """Obtém buffer de dados do storage pelo caminho"""
        pass
    
    @abstractmethod
    def save_data_buffer(self, buffer: BytesIO, path: str, storage_client) -> bool:
        """Salva buffer de dados no storage pelo caminho"""
        pass
    
    @abstractmethod
    def validate_client(self, storage_client) -> bool:
        """Valida se o cliente de storage é válido para este provider"""
        pass


class CSVHandler(FileExtensionHandler):
    """Handler para arquivos CSV"""
    
    @property
    def extension(self) -> str:
        return "csv"
    
    def read_data(self, buffer: BytesIO) -> pd.DataFrame:
        return pd.read_csv(buffer)
    
    def write_data(self, data: pd.DataFrame, buffer: BytesIO) -> None:
        data.to_csv(buffer, index=False)


class JSONHandler(FileExtensionHandler):
    """Handler para arquivos JSON"""
    
    @property
    def extension(self) -> str:
        return "json"
    
    def read_data(self, buffer: BytesIO) -> Dict[str, Any]:
        return json.load(buffer)
    
    def write_data(self, data: Dict[str, Any], buffer: BytesIO) -> None:
        json.dump(data, buffer, ensure_ascii=False, indent=2)


class ParquetHandler(FileExtensionHandler):
    """Handler para arquivos Parquet"""
    
    @property
    def extension(self) -> str:
        return "parquet"
    
    def read_data(self, buffer: BytesIO) -> pd.DataFrame:
        return pd.read_parquet(buffer)
    
    def write_data(self, data: pd.DataFrame, buffer: BytesIO) -> None:
        data.to_parquet(buffer, index=False)


class ExcelHandler(FileExtensionHandler):
    """Handler para arquivos Excel"""
    
    @property
    def extension(self) -> str:
        return "xlsx"
    
    def read_data(self, buffer: BytesIO) -> pd.DataFrame:
        return pd.read_excel(buffer)
    
    def write_data(self, data: pd.DataFrame, buffer: BytesIO) -> None:
        data.to_excel(buffer, index=False)


class AzureStorageProvider(StorageProvider):
    """Provider para Azure Blob Storage"""
    
    @property
    def provider_name(self) -> str:
        return "azure"
    
    def get_data_buffer(self, path: str, storage_client) -> BytesIO:
        """Obtém dados do Azure Blob Storage"""
        blob = storage_client.get_blob_client(blob=path)
        return BytesIO(blob.download_blob().readall())
    
    def save_data_buffer(self, buffer: BytesIO, path: str, storage_client) -> bool:
        """Salva dados no Azure Blob Storage"""
        try:
            blob = storage_client.get_blob_client(blob=path)
            buffer.seek(0)
            blob.upload_blob(buffer.read(), overwrite=True)
            return True
        except Exception as e:
            print(f"Erro ao salvar no Azure: {e}")
            return False
    
    def validate_client(self, storage_client) -> bool:
        """Valida se é um cliente Azure válido"""
        return hasattr(storage_client, 'get_blob_client')


class AWSStorageProvider(StorageProvider):
    """Provider para AWS S3"""
    
    @property
    def provider_name(self) -> str:
        return "aws"
    
    def get_data_buffer(self, path: str, storage_client) -> BytesIO:
        """Obtém dados do AWS S3"""
        bucket, key = self._parse_s3_path(path)
        response = storage_client.get_object(Bucket=bucket, Key=key)
        return BytesIO(response['Body'].read())
    
    def save_data_buffer(self, buffer: BytesIO, path: str, storage_client) -> bool:
        """Salva dados no AWS S3"""
        try:
            bucket, key = self._parse_s3_path(path)
            buffer.seek(0)
            storage_client.put_object(Bucket=bucket, Key=key, Body=buffer.read())
            return True
        except Exception as e:
            print(f"Erro ao salvar no AWS: {e}")
            return False
    
    def validate_client(self, storage_client) -> bool:
        """Valida se é um cliente AWS S3 válido"""
        return hasattr(storage_client, 'get_object') and hasattr(storage_client, 'put_object')
    
    def _parse_s3_path(self, path: str) -> tuple:
        """Parse do caminho S3 para bucket e key"""
        # Implementar lógica de parsing do path S3
        # Por exemplo: s3://bucket/path/file.csv -> (bucket, path/file.csv)
        if path.startswith('s3://'):
            path = path[5:]
        parts = path.split('/', 1)
        return parts[0], parts[1] if len(parts) > 1 else ''


class GoogleStorageProvider(StorageProvider):
    """Provider para Google Cloud Storage"""
    
    @property
    def provider_name(self) -> str:
        return "google"
    
    def get_data_buffer(self, path: str, storage_client) -> BytesIO:
        """Obtém dados do Google Cloud Storage"""
        bucket_name, blob_name = self._parse_gcs_path(path)
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        return BytesIO(blob.download_as_bytes())
    
    def save_data_buffer(self, buffer: BytesIO, path: str, storage_client) -> bool:
        """Salva dados no Google Cloud Storage"""
        try:
            bucket_name, blob_name = self._parse_gcs_path(path)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            buffer.seek(0)
            blob.upload_from_file(buffer)
            return True
        except Exception as e:
            print(f"Erro ao salvar no Google: {e}")
            return False
    
    def validate_client(self, storage_client) -> bool:
        """Valida se é um cliente Google Cloud válido"""
        return hasattr(storage_client, 'bucket')
    
    def _parse_gcs_path(self, path: str) -> tuple:
        """Parse do caminho GCS para bucket e blob"""
        # Implementar lógica de parsing do path GCS
        # Por exemplo: gs://bucket/path/file.csv -> (bucket, path/file.csv)
        if path.startswith('gs://'):
            path = path[5:]
        parts = path.split('/', 1)
        return parts[0], parts[1] if len(parts) > 1 else ''

        
class DataLayerOptions(StrEnum):
    """Opções de camada de dados"""
    RAW = "raw"
    CLEAR = "clear"
    MODEL = "model"

@dataclass
class BaseEntity(ABC):
    """Classe base para todas as entidades de dados"""
    
    # Propriedades base que devem ser definidas nas classes filhas
    data_layer: DataLayerOptions
    path_prefix: str
    filename: str
    file_handler: FileExtensionHandler
    storage_provider: StorageProvider
    date_reference: Optional[datetime] = None  # data de referência
    path_sufix: Optional[str] = None  # sufixo opcional para o caminho
    
    class Columns:
        """Classe para definir colunas de entidades"""
        pass
    
    def _build_path_by_date(self) -> str:
        """Constrói caminho baseado na data de referência"""
        return "/".join([
            self.data_layer.value,
            self.path_prefix,
            f"{self.date_reference.year:04d}",
            f"{self.date_reference.month:02d}",
            f"{self.date_reference.year:04d}.{self.date_reference.month:02d}.{self.date_reference.day:02d}",
            f"{self.filename}.{self.file_handler.extension}"
        ])

    def _build_path_by_sufix(self) -> str:
        """Constrói caminho baseado no sufixo"""
        return "/".join([
            self.data_layer.value,
            self.path_prefix,
            self.path_sufix,
            f"{self.filename}.{self.file_handler.extension}"
        ])

    def read_data_by_date(self, storage_client=None) -> Any:
        """Lê dados baseado na data de referência"""
        if not self.date_reference:
            raise ValueError("date_reference deve ser definida para leitura por data")
        
        if not self.storage_provider.validate_client(storage_client):
            raise ValueError(f"Cliente de storage inválido para provider {self.storage_provider.provider_name}")
        
        # Constrói o caminho e obtém os dados do storage
        path = self._build_path_by_date()
        buffer = self.storage_provider.get_data_buffer(path, storage_client)
        
        # Usa o file handler para processar os dados
        return self.file_handler.read_data(buffer)
    
    def write_data_by_date(self, data: Any, storage_client=None) -> bool:
        """Escreve dados baseado na data de referência"""
        if not self.date_reference:
            raise ValueError("date_reference deve ser definida para escrita por data")
        
        if not self.storage_provider.validate_client(storage_client):
            raise ValueError(f"Cliente de storage inválido para provider {self.storage_provider.provider_name}")
        
        try:
            # Cria buffer e usa o file handler para escrever os dados
            buffer = BytesIO()
            self.file_handler.write_data(data, buffer)
            
            # Constrói o caminho e salva no storage
            path = self._build_path_by_date()
            return self.storage_provider.save_data_buffer(buffer, path, storage_client)
        except Exception as e:
            print(f"Erro ao escrever dados por data: {e}")
            return False

    def read_data_by_sufix(self, storage_client=None) -> Any:
        """Lê dados baseado no sufixo"""
        if not self.path_sufix:
            raise ValueError("path_sufix deve ser definido para leitura por sufixo")
        
        if not self.storage_provider.validate_client(storage_client):
            raise ValueError(f"Cliente de storage inválido para provider {self.storage_provider.provider_name}")
        
        # Constrói o caminho e obtém os dados do storage
        path = self._build_path_by_sufix()
        buffer = self.storage_provider.get_data_buffer(path, storage_client)
        
        # Usa o file handler para processar os dados
        return self.file_handler.read_data(buffer)
    
    def write_data_by_sufix(self, data: Any, storage_client=None) -> bool:
        """Escreve dados baseado no sufixo"""
        if not self.path_sufix:
            raise ValueError("path_sufix deve ser definido para escrita por sufixo")
        
        if not self.storage_provider.validate_client(storage_client):
            raise ValueError(f"Cliente de storage inválido para provider {self.storage_provider.provider_name}")
        
        try:
            # Cria buffer e usa o file handler para escrever os dados
            buffer = BytesIO()
            self.file_handler.write_data(data, buffer)
            
            # Constrói o caminho e salva no storage
            path = self._build_path_by_sufix()
            return self.storage_provider.save_data_buffer(buffer, path, storage_client)
        except Exception as e:
            print(f"Erro ao escrever dados por sufixo: {e}")
            return False

class HandlerFactory:
    """Factory para criar handlers e storage providers"""
    
    _file_handlers = {
        "csv": CSVHandler,
        "json": JSONHandler,
        "parquet": ParquetHandler,
        "xlsx": ExcelHandler
    }
    
    _storage_providers = {
        "aws": AWSStorageProvider,
        "azure": AzureStorageProvider,
        "google": GoogleStorageProvider
    }
    
    @classmethod
    def get_file_handler(cls, extension: str) -> FileExtensionHandler:
        """Cria handler baseado na extensão"""
        handler_class = cls._file_handlers.get(extension.lower())
        if not handler_class:
            raise ValueError(f"Handler não encontrado para extensão: {extension}")
        return handler_class()
    
    @classmethod
    def get_storage_provider(cls, provider_name: str) -> StorageProvider:
        """Cria storage provider baseado no nome"""
        provider_class = cls._storage_providers.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Storage provider não encontrado: {provider_name}")
        return provider_class()
'''