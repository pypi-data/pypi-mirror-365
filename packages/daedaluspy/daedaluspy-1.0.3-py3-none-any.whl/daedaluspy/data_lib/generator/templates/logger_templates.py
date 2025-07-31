"""
Templates for logger tools with multi-cloud support
"""

LOGGER_INIT_TEMPLATE = '''"""
Logger tools for DaedalusPy generated libraries
"""

from .core import Logger, log
from .result import Result, ResultStatus
from .destinations import (
    LogDestination, 
    BlobStorageDestination,  # Azure
    S3StorageDestination,    # AWS
    GCSStorageDestination,   # Google Cloud
    EmailDestination
)

__all__ = [
    'Logger',
    'log', 
    'Result',
    'ResultStatus',
    'LogDestination',
    'BlobStorageDestination',
    'S3StorageDestination',
    'GCSStorageDestination',
    'EmailDestination'
]
'''

LOGGER_CORE_TEMPLATE = '''from typing import Any, Callable, List, Dict
import logging
import traceback
from datetime import datetime
import uuid
from functools import wraps
from .result import Result, ResultStatus
from .destinations import LogDestination

class Logger:
    def __init__(self, destinations: List[LogDestination]):
        self.destinations = destinations

    def log(self, result: Result) -> None:
        for destination in self.destinations:
            try:
                destination.log(result)
            except Exception as e:
                logging.error(f"Failed to log to destination: {str(e)}")

    def close(self) -> None:
        for destination in self.destinations:
            try:
                destination.close()
            except Exception as e:
                logging.error(f"Failed to close destination: {str(e)}")

def log(logger: Logger, success_message: str, error_message: str):
    """
    Decorador para logging automático de funções
    
    Args:
        logger: Instância do Logger configurado
        success_message: Mensagem para caso de sucesso
        error_message: Mensagem para caso de erro
    
    Example:
        from tools.logger import Logger, log, BlobStorageDestination
        
        # Configurar logger
        blob_dest = BlobStorageDestination(container_client, "logs/app")
        logger = Logger([blob_dest])
        
        @log(logger, "Dados processados com sucesso", "Erro ao processar dados")
        def process_data(df):
            return df.dropna()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__name__
            start_time = datetime.now()
            correlation_id = str(uuid.uuid4())
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = end_time - start_time
                
                context = {
                    "function": func_name,
                    "module": func.__module__,
                    "duration_seconds": duration.total_seconds(),
                    "args_count": len(args),
                    "kwargs_count": len(kwargs)
                }
                
                if isinstance(result, Result):
                    result.correlation_id = correlation_id
                    logger.log(result)
                else:
                    success_result = Result.success(
                        context=context, 
                        message=success_message, 
                        data={"result_type": type(result).__name__}, 
                        correlation_id=correlation_id
                    )
                    logger.log(success_result)
                
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration = end_time - start_time
                
                context = {
                    "function": func_name,
                    "module": func.__module__,
                    "duration_seconds": duration.total_seconds(),
                    "args_count": len(args),
                    "kwargs_count": len(kwargs),
                    "error_type": type(e).__name__,
                    "traceback": traceback.format_exc()
                }
                
                error_result = Result.error(
                    context=context, 
                    data={"error": str(e)}, 
                    message=error_message, 
                    correlation_id=correlation_id
                )
                logger.log(error_result)
                raise
                
        return wrapper
    return decorator
'''

LOGGER_RESULT_TEMPLATE = '''from enum import Enum
from typing import Any, Optional, Dict
from datetime import datetime
import uuid

class ResultStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"

class Result:
    def __init__(self, status: ResultStatus, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None):
        self.status = status
        self.context = context
        self.data = data
        self.message = message
        self.timestamp = timestamp or datetime.now()
        self.correlation_id = correlation_id or str(uuid.uuid4())

    @classmethod
    def success(cls, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None) -> 'Result':
        return cls(status=ResultStatus.SUCCESS, context=context, data=data, message=message, timestamp=timestamp, correlation_id=correlation_id)

    @classmethod
    def error(cls, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None) -> 'Result':
        return cls(status=ResultStatus.ERROR, context=context, data=data, message=message, timestamp=timestamp, correlation_id=correlation_id)

    @classmethod
    def warning(cls, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None) -> 'Result':
        return cls(status=ResultStatus.WARNING, context=context, data=data, message=message, timestamp=timestamp, correlation_id=correlation_id)

    @classmethod
    def info(cls, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None) -> 'Result':
        return cls(status=ResultStatus.INFO, context=context, data=data, message=message, timestamp=timestamp, correlation_id=correlation_id)

    @classmethod
    def debug(cls, context: Dict, data: Optional[Any] = None, message: Optional[str] = None, timestamp: Optional[datetime] = None, correlation_id: Optional[str] = None) -> 'Result':
        return cls(status=ResultStatus.DEBUG, context=context, data=data, message=message, timestamp=timestamp, correlation_id=correlation_id)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "context": self.context,
            "data": self.data,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id
        }
'''

LOGGER_DESTINATIONS_TEMPLATE = '''from abc import ABC, abstractmethod
from typing import Optional, Dict, List
import logging
import json
from datetime import datetime
from io import BytesIO
import uuid
from azure.storage.blob import ContainerClient
import boto3
from google.cloud import storage as gcs
from msal import ConfidentialClientApplication
import requests

from .result import Result, ResultStatus


class LogDestination(ABC):
    """Abstract base class for log destinations."""
    
    @abstractmethod
    def log(self, result: Result) -> None:
        """Log the result to the destination."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close any resources used by the destination."""
        pass


class BlobStorageDestination(LogDestination):
    """Log destination that saves to Azure Blob Storage."""
    
    def __init__(self, container_client: ContainerClient, prefix: str = "logs/app", filename: str = "app_logs", file_extension: str = "json"):
        self.container_client = container_client
        self.prefix = prefix
        self.filename = filename
        self.file_extension = file_extension

    def _get_blob_path(self) -> str:
        """Generate standardized blob path."""
        now = datetime.now()
        blob_path = "/".join([
            self.prefix,
            f"{now.year:04d}",
            f"{now.month:02d}",
            f"{now.year:04d}.{now.month:02d}.{now.day:02d}",
            f"{self.filename}_{now.strftime('%H%M%S')}_{uuid.uuid4().hex[:8]}.{self.file_extension}"
        ])
        return blob_path

    def log(self, result: Result) -> None:
        """Log the result to Azure Blob Storage."""
        try:
            blob_path = self._get_blob_path()
            log_data = result.to_dict()
            json_data = json.dumps(log_data, indent=2, ensure_ascii=False)
            blob_data = BytesIO(json_data.encode('utf-8'))
            
            blob_client = self.container_client.get_blob_client(blob=blob_path)
            blob_client.upload_blob(data=blob_data, overwrite=True)
            
        except Exception as e:
            logging.error(f"Failed to upload log to Azure Blob Storage: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in BlobStorageDestination: {str(e)}")

    def close(self) -> None:
        """No resources to close for Azure Blob Storage."""
        pass


class S3StorageDestination(LogDestination):
    """Log destination that saves to AWS S3."""
    
    def __init__(self, bucket_name: str, s3_client=None, prefix: str = "logs/app", filename: str = "app_logs", file_extension: str = "json"):
        self.bucket_name = bucket_name
        self.s3_client = s3_client or boto3.client('s3')
        self.prefix = prefix
        self.filename = filename
        self.file_extension = file_extension

    def _get_s3_key(self) -> str:
        """Generate standardized S3 key."""
        now = datetime.now()
        s3_key = "/".join([
            self.prefix,
            f"{now.year:04d}",
            f"{now.month:02d}",
            f"{now.year:04d}.{now.month:02d}.{now.day:02d}",
            f"{self.filename}_{now.strftime('%H%M%S')}_{uuid.uuid4().hex[:8]}.{self.file_extension}"
        ])
        return s3_key

    def log(self, result: Result) -> None:
        """Log the result to AWS S3."""
        try:
            s3_key = self._get_s3_key()
            log_data = result.to_dict()
            json_data = json.dumps(log_data, indent=2, ensure_ascii=False)
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data.encode('utf-8'),
                ContentType='application/json'
            )
            
        except Exception as e:
            logging.error(f"Failed to upload log to AWS S3: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in S3StorageDestination: {str(e)}")

    def close(self) -> None:
        """No resources to close for AWS S3."""
        pass


class GCSStorageDestination(LogDestination):
    """Log destination that saves to Google Cloud Storage."""
    
    def __init__(self, bucket_name: str, client=None, prefix: str = "logs/app", filename: str = "app_logs", file_extension: str = "json"):
        self.bucket_name = bucket_name
        self.client = client or gcs.Client()
        self.prefix = prefix
        self.filename = filename
        self.file_extension = file_extension

    def _get_blob_name(self) -> str:
        """Generate standardized blob name for GCS."""
        now = datetime.now()
        blob_name = "/".join([
            self.prefix,
            f"{now.year:04d}",
            f"{now.month:02d}",
            f"{now.year:04d}.{now.month:02d}.{now.day:02d}",
            f"{self.filename}_{now.strftime('%H%M%S')}_{uuid.uuid4().hex[:8]}.{self.file_extension}"
        ])
        return blob_name

    def log(self, result: Result) -> None:
        """Log the result to Google Cloud Storage."""
        try:
            blob_name = self._get_blob_name()
            log_data = result.to_dict()
            json_data = json.dumps(log_data, indent=2, ensure_ascii=False)
            
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            blob.upload_from_string(
                json_data,
                content_type='application/json'
            )
            
        except Exception as e:
            logging.error(f"Failed to upload log to Google Cloud Storage: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error in GCSStorageDestination: {str(e)}")

    def close(self) -> None:
        """No resources to close for Google Cloud Storage."""
        pass


class EmailDestination(LogDestination):
    """Log destination that sends emails using Microsoft Graph API."""

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, sender_email: str, recipient_email: str, log_only_on: List[ResultStatus] = None):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.sender_email = sender_email
        self.recipient_email = recipient_email
        self.log_only_on = log_only_on or [ResultStatus.ERROR]

        self.token_url = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.graph_url = "https://graph.microsoft.com/v1.0"

        self.app = ConfidentialClientApplication(
            self.client_id,
            authority=self.token_url,
            client_credential=self.client_secret
        )

    def log(self, result: Result) -> None:
        """Send email notification for specified result statuses."""
        try:
            if result.status not in self.log_only_on:
                return
                
            subject = f"Log Alert - {result.status.value.upper()} - {result.correlation_id}"
            body = self._format_email_body(result)
            self._send_email(subject, body)
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {str(e)}")

    def _format_email_body(self, result: Result) -> str:
        """Format the email body with log information."""
        body = f"""
Log Alert from DaedalusPy Application

Status: {result.status.value.upper()}
Message: {result.message or 'No message provided'}
Timestamp: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
Correlation ID: {result.correlation_id}

Context:
{json.dumps(result.context, indent=2)}

Data:
{json.dumps(result.data, indent=2) if result.data else 'No data provided'}

---
This is an automated message from DaedalusPy Logger.
        """.strip()
        return body

    def _send_email(self, subject: str, body: str) -> None:
        """Send email using Microsoft Graph API."""
        try:
            token_response = self.app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            access_token = token_response.get("access_token")

            if not access_token:
                raise Exception("Failed to obtain access token from Microsoft Graph")

            message = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": self.recipient_email
                            }
                        }
                    ]
                },
                "saveToSentItems": "true"
            }

            url = f"{self.graph_url}/users/{self.sender_email}/sendMail"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers, json=message)

            if response.status_code >= 400:
                raise Exception(f"Graph API returned {response.status_code}: {response.text}")

        except Exception as e:
            logging.error(f"Error sending email via Graph API: {str(e)}")

    def close(self) -> None:
        """No resources to close for email destination."""
        pass


class ConsoleDestination(LogDestination):
    """Simple console log destination for development."""
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = getattr(logging, log_level.upper())
        self.logger = logging.getLogger("DaedalusPyLogger")
        self.logger.setLevel(self.log_level)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, result: Result) -> None:
        """Log the result to console."""
        try:
            message = f"[{result.correlation_id}] {result.message or 'No message'}"
            
            if result.status == ResultStatus.SUCCESS:
                self.logger.info(message)
            elif result.status == ResultStatus.ERROR:
                self.logger.error(message)
            elif result.status == ResultStatus.WARNING:
                self.logger.warning(message)
            elif result.status == ResultStatus.DEBUG:
                self.logger.debug(message)
            else:
                self.logger.info(message)
                
        except Exception as e:
            print(f"Error in console logging: {str(e)}")

    def close(self) -> None:
        """No resources to close for console destination."""
        pass


class FileDestination(LogDestination):
    """Log destination that writes to local files."""
    
    def __init__(self, file_path: str = "app.log", max_file_size: int = 10*1024*1024):  # 10MB default
        self.file_path = file_path
        self.max_file_size = max_file_size

    def log(self, result: Result) -> None:
        """Log the result to a file."""
        try:
            log_entry = {
                "timestamp": result.timestamp.isoformat(),
                "status": result.status.value,
                "correlation_id": result.correlation_id,
                "message": result.message,
                "context": result.context,
                "data": result.data
            }
            
            # Check file size and rotate if needed
            self._rotate_if_needed()
            
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\\n')
                
        except Exception as e:
            logging.error(f"Failed to write to log file {self.file_path}: {str(e)}")

    def _rotate_if_needed(self) -> None:
        """Rotate log file if it exceeds max size."""
        try:
            import os
            if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > self.max_file_size:
                backup_path = f"{self.file_path}.bak"
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(self.file_path, backup_path)
        except Exception as e:
            logging.error(f"Failed to rotate log file: {str(e)}")

    def close(self) -> None:
        """No resources to close for file destination."""
        pass
'''

EXAMPLE_USAGE_TEMPLATE = '''"""
Exemplo de uso do sistema de logging DaedalusPy
"""

from tools.logger import (
    Logger, 
    log, 
    Result, 
    ResultStatus,
    BlobStorageDestination,
    S3StorageDestination, 
    GCSStorageDestination,
    EmailDestination,
    ConsoleDestination,
    FileDestination
)

# Exemplo 1: Logger com múltiplos destinations
def setup_multi_cloud_logger():
    """Configura logger com destinations para múltiplas nuvens"""
    destinations = []
    
    # Console para desenvolvimento
    destinations.append(ConsoleDestination(log_level="INFO"))
    
    # Arquivo local para backup
    destinations.append(FileDestination("app.log"))
    
    # Azure Blob Storage (se disponível)
    try:
        from azure.storage.blob import ContainerClient
        container_client = ContainerClient.from_connection_string(
            "your_connection_string", 
            "logs-container"
        )
        destinations.append(BlobStorageDestination(container_client, "logs/myapp"))
    except ImportError:
        print("Azure libraries not available")
    
    # AWS S3 (se disponível)
    try:
        import boto3
        s3_client = boto3.client('s3')
        destinations.append(S3StorageDestination("my-log-bucket", s3_client, "logs/myapp"))
    except ImportError:
        print("AWS libraries not available")
    
    # Google Cloud Storage (se disponível)
    try:
        from google.cloud import storage
        gcs_client = storage.Client()
        destinations.append(GCSStorageDestination("my-log-bucket", gcs_client, "logs/myapp"))
    except ImportError:
        print("Google Cloud libraries not available")
    
    # Email para alertas críticos
    try:
        email_dest = EmailDestination(
            tenant_id="your-tenant-id",
            client_id="your-client-id", 
            client_secret="your-client-secret",
            sender_email="app@company.com",
            recipient_email="admin@company.com",
            log_only_on=[ResultStatus.ERROR]  # Apenas erros por email
        )
        destinations.append(email_dest)
    except ImportError:
        print("Email libraries not available")
    
    return Logger(destinations)


# Exemplo 2: Usando o decorador de log
logger = setup_multi_cloud_logger()

@log(logger, "Dados processados com sucesso", "Erro ao processar dados")
def process_data(data):
    """Função de exemplo com logging automático"""
    if not data:
        raise ValueError("Dados não podem estar vazios")
    
    # Simula processamento
    result = {"processed_items": len(data), "status": "completed"}
    return result


# Exemplo 3: Logging manual de resultados
def manual_logging_example():
    """Exemplo de logging manual com diferentes tipos de resultado"""
    
    # Log de sucesso
    success_result = Result.success(
        context={"operation": "data_validation", "records": 1000},
        message="Validação concluída com sucesso",
        data={"valid_records": 950, "invalid_records": 50}
    )
    logger.log(success_result)
    
    # Log de warning
    warning_result = Result.warning(
        context={"operation": "data_cleanup", "records": 1000},
        message="Alguns dados foram removidos durante a limpeza",
        data={"removed_records": 10, "reason": "duplicates"}
    )
    logger.log(warning_result)
    
    # Log de erro
    error_result = Result.error(
        context={"operation": "database_connection", "attempts": 3},
        message="Falha ao conectar com o banco de dados",
        data={"error_code": "DB_TIMEOUT", "last_attempt": "2024-01-01 10:30:00"}
    )
    logger.log(error_result)


# Exemplo 4: Logging específico por cloud provider
def azure_specific_logging():
    """Exemplo de logging específico para Azure"""
    from azure.storage.blob import ContainerClient
    
    container_client = ContainerClient.from_connection_string(
        "your_connection_string",
        "logs-container"
    )
    
    azure_logger = Logger([
        BlobStorageDestination(container_client, "logs/azure-app", "azure_logs"),
        ConsoleDestination()
    ])
    
    @log(azure_logger, "Processamento Azure concluído", "Erro no processamento Azure")
    def azure_process():
        return {"azure_service": "processed", "timestamp": "2024-01-01"}
    
    return azure_process()


def aws_specific_logging():
    """Exemplo de logging específico para AWS"""
    import boto3
    
    s3_client = boto3.client('s3')
    
    aws_logger = Logger([
        S3StorageDestination("my-aws-logs", s3_client, "logs/aws-app", "aws_logs"),
        ConsoleDestination()
    ])
    
    @log(aws_logger, "Processamento AWS concluído", "Erro no processamento AWS")
    def aws_process():
        return {"aws_service": "processed", "timestamp": "2024-01-01"}
    
    return aws_process()


def google_specific_logging():
    """Exemplo de logging específico para Google Cloud"""
    from google.cloud import storage
    
    gcs_client = storage.Client()
    
    google_logger = Logger([
        GCSStorageDestination("my-gcp-logs", gcs_client, "logs/gcp-app", "gcp_logs"),
        ConsoleDestination()
    ])
    
    @log(google_logger, "Processamento GCP concluído", "Erro no processamento GCP")
    def gcp_process():
        return {"gcp_service": "processed", "timestamp": "2024-01-01"}
    
    return gcp_process()


if __name__ == "__main__":
    # Teste o sistema de logging
    try:
        # Teste com dados válidos
        result = process_data(["item1", "item2", "item3"])
        print(f"Processamento bem-sucedido: {result}")
        
        # Teste de logging manual
        manual_logging_example()
        
        # Teste com erro
        process_data([])  # Vai gerar erro e log
        
    except Exception as e:
        print(f"Erro capturado: {e}")
    finally:
        # Fechar recursos do logger
        logger.close()
'''
