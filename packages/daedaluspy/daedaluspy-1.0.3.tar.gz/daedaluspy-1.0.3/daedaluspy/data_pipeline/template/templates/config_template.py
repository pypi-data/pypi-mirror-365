"""
Template para config.py - Configuração do pipeline com serviços Sankhya
"""

CONFIG_TEMPLATE = '''"""
Configuração do pipeline {project_name}
"""
from {lib_name}.config import PipelineConfig, AzureConfig, DatabaseConfig
from {lib_name}.services.sankhya import SankhyaServices, SankhyaAuth
from {lib_name}.data.{cloud_provider}.{entity_target} import {entity_target_class}
from {lib_name}.tools.logger import Logger, EmailDestination, BlobStorageDestination, ResultStatus
from pyspark.sql import SparkSession

# Configuração do Spark
spark = SparkSession.builder.appName('{project_name}').getOrCreate()

# Configurações base
azure_config = AzureConfig(env_source="spark", spark_session=spark)
db_config = DatabaseConfig(env_source="spark", spark_session=spark)

# Serviços Sankhya
sankhya_auth = SankhyaAuth()
sankhya_services = SankhyaServices(sankhya_auth)

# Entidade de destino
target_entity = {entity_target_class}()

# Cliente de armazenamento Azure
# backoffice_container = azure_config.get_container_client("backoffice")

# Pipeline Config
pipeline_config = PipelineConfig()
pipeline_config.add_configuration(azure_config, "azure")
pipeline_config.add_configuration(db_config, "database")

# Configurar serviços
pipeline_config.add_service("sankhya", sankhya_services)
pipeline_config.add_service("sankhya_auth", sankhya_auth)
# pipeline_config.add_service("storage_client", backoffice_container)

# Configurar entidade de destino
pipeline_config.add_data_target("{entity_target_name}", target_entity)

## LOGGER CONFIGURATION
email_destination = EmailDestination(
    tenant_id=azure_config.get_tenant_id(), 
    client_id=azure_config.get_client_id(), 
    client_secret=azure_config.get_client_secret(), 
    sender_email=azure_config.get_sender_email(), 
    recipient_email=azure_config.get_recipient_email(),
    log_only_on=[ResultStatus.ERROR]
)

file_destination = BlobStorageDestination(
    container_client=azure_config.get_container_client("logs"), 
    prefix="{project_name}/logs", 
    filename="{project_name}_{{date}}", 
    file_extension=".log"
)

logger = Logger([email_destination, file_destination])
error_message = "Error: Processamento de coleta de dados de {dataname} no {system_name}."
success_message = "Success: Processamento de coleta de dados {dataname} no {system_name}."
'''
