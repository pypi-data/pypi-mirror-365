TEMPLATE_ENTITY_AWS = '''from datetime import datetime
from {lib_name}.data.base import BaseEntity, DataLayerOptions, HandlerFactory, AWSStorageProvider
{imports}

class {classname}(BaseEntity):
    """Entidade de dados para {classname}"""

    class Columns:
{columns}

    def __init__(self):
        """Configurações da entidade"""
        self.data_layer = DataLayerOptions.{data_layer_upper}
        self.path_prefix = "{path_prefix}"
        self.filename = "{filename}"
        self.file_handler = HandlerFactory.get_file_handler("{file_extension}")
        self.storage_provider = AWSStorageProvider()    
        self.date_reference = datetime.now()
        self.path_sufix = None
'''