from enum import Enum
from typing import Optional
import os
from daedaluspy.data_lib.data.base_template import BASE_DATA_TEMPLATE
from daedaluspy.data_lib.generator.templates.logger_templates import (
    LOGGER_INIT_TEMPLATE, LOGGER_CORE_TEMPLATE, LOGGER_RESULT_TEMPLATE, LOGGER_DESTINATIONS_TEMPLATE, EXAMPLE_USAGE_TEMPLATE
)
from daedaluspy.data_lib.generator.templates.data_quality_templates import (
    DATA_QUALITY_INIT_TEMPLATE, DATA_QUALITY_VALIDATOR_TEMPLATE, DATA_QUALITY_RULES_TEMPLATE, DATA_QUALITY_EXAMPLE_TEMPLATE
)
from daedaluspy.data_lib.generator.templates.config_templates import CONFIG_TEMPLATE
from daedaluspy.data_lib.generator.data_entity_oop import DataEntityGenerator
from daedaluspy.data_lib.generator.service_generator_oop import ServiceGenerator

class LibraryType(Enum):
    CORPORATE = "corporate"
    PROJECT = "project"

class LibraryGenerator:
    def __init__(self, name: str, data_name: Optional[str] = None, system_name: Optional[str] = None, lib_type: LibraryType = LibraryType.CORPORATE):
        self.name = name
        self.data_name = data_name
        self.system_name = system_name
        self.lib_type = lib_type

    def generate(self):
        self._import_templates()
        self._create_directories()
        self._create_init_files()
        self._create_base_data_file()
        self._create_logger_files()
        self._create_data_quality_files()
        self._create_config_file()
        self._create_tools_init()
        self._create_data_entity()
        self._create_service()
        self._create_root_files()
        self._create_main_init()
        print(f"Biblioteca '{self.name}' criada com sucesso.")

    def _import_templates(self):
        try:
            self._BASE_DATA_TEMPLATE = BASE_DATA_TEMPLATE
            self._LOGGER_INIT_TEMPLATE = LOGGER_INIT_TEMPLATE
            self._LOGGER_CORE_TEMPLATE = LOGGER_CORE_TEMPLATE
            self._LOGGER_RESULT_TEMPLATE = LOGGER_RESULT_TEMPLATE
            self._LOGGER_DESTINATIONS_TEMPLATE = LOGGER_DESTINATIONS_TEMPLATE
            self._EXAMPLE_USAGE_TEMPLATE = EXAMPLE_USAGE_TEMPLATE
            self._DATA_QUALITY_INIT_TEMPLATE = DATA_QUALITY_INIT_TEMPLATE
            self._DATA_QUALITY_VALIDATOR_TEMPLATE = DATA_QUALITY_VALIDATOR_TEMPLATE
            self._DATA_QUALITY_RULES_TEMPLATE = DATA_QUALITY_RULES_TEMPLATE
            self._DATA_QUALITY_EXAMPLE_TEMPLATE = DATA_QUALITY_EXAMPLE_TEMPLATE
            self._CONFIG_TEMPLATE = CONFIG_TEMPLATE
            self._DataEntityGenerator = DataEntityGenerator
            self._ServiceGenerator = ServiceGenerator
        except ImportError as e:
            raise RuntimeError(f"Erro ao importar templates ou generators: {e}")

    def _create_file(self, path, content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _create_directories(self):
        base_path = self.name
        dirs = [
            os.path.join(base_path, "data", "raw"),
            os.path.join(base_path, "data", "clear"),
            os.path.join(base_path, "data", "model"),
            os.path.join(base_path, "service"),
            os.path.join(base_path, "tools"),
            os.path.join(base_path, "tools", "logger"),
            os.path.join(base_path, "tools", "data_quality"),
            os.path.join(base_path, "config")
        ]
        if self.system_name:
            dirs.append(os.path.join(base_path, "service", self.system_name))
        for d in dirs:
            os.makedirs(d, exist_ok=True)

    def _create_init_files(self):
        base_path = self.name
        init_dirs = [
            base_path,
            os.path.join(base_path, "data"),
            os.path.join(base_path, "data", "raw"),
            os.path.join(base_path, "data", "clear"),
            os.path.join(base_path, "data", "model"),
            os.path.join(base_path, "service"),
            os.path.join(base_path, "tools"),
            os.path.join(base_path, "tools", "logger"),
            os.path.join(base_path, "tools", "data_quality"),
            os.path.join(base_path, "config")
        ]
        if self.system_name:
            init_dirs.append(os.path.join(base_path, "service", self.system_name))
        for init_dir in init_dirs:
            init_file = os.path.join(init_dir, "__init__.py")
            self._create_file(init_file, f'"""\n{os.path.basename(init_dir)} module\n"""\n')

    def _create_base_data_file(self):
        base_py_file = os.path.join(self.name, "data", "base.py")
        self._create_file(base_py_file, self._BASE_DATA_TEMPLATE)

    def _create_logger_files(self):
        base_path = self.name
        self._create_file(os.path.join(base_path, "tools", "logger", "__init__.py"), self._LOGGER_INIT_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "logger", "core.py"), self._LOGGER_CORE_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "logger", "result.py"), self._LOGGER_RESULT_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "logger", "destinations.py"), self._LOGGER_DESTINATIONS_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "logger", "examples.py"), self._EXAMPLE_USAGE_TEMPLATE)

    def _create_data_quality_files(self):
        base_path = self.name
        self._create_file(os.path.join(base_path, "tools", "data_quality", "__init__.py"), self._DATA_QUALITY_INIT_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "data_quality", "validator.py"), self._DATA_QUALITY_VALIDATOR_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "data_quality", "rules.py"), self._DATA_QUALITY_RULES_TEMPLATE)
        self._create_file(os.path.join(base_path, "tools", "data_quality", "examples.py"), self._DATA_QUALITY_EXAMPLE_TEMPLATE)

    def _create_config_file(self):
        config_file = os.path.join(self.name, "config", "config.py")
        self._create_file(config_file, self._CONFIG_TEMPLATE)

    def _create_tools_init(self):
        base_path = self.name
        tools_init_content = '''"""
Ferramentas utilitárias para a biblioteca
"""

from .logger import Logger, log, Result, ResultStatus
from .data_quality import DataQuality, QualityRules

__all__ = ['Logger', 'log', 'Result', 'ResultStatus', 'DataQuality', 'QualityRules']
'''
        tools_init_file = os.path.join(base_path, "tools", "__init__.py")
        self._create_file(tools_init_file, tools_init_content)

    def _create_data_entity(self):
        if not self.data_name:
            return
        raw_dir = os.path.join(self.name, "data", "raw")
        try:
            entity_gen = self._DataEntityGenerator(
                classname=self.data_name.capitalize(),
                tier="raw",
                cloud_provider="azure",
                columns=["id", "name", "created_at"],
                output_path=raw_dir,
                extension="csv",
                imports="import pandas as pd",
                read_code="return pd.read_csv(buffer)",
                write_code="data.to_csv(buffer, index=False)",
                lib=self.name
            )
            entity_gen.generate()
        except Exception as e:
            raw_file = os.path.join(raw_dir, f"{self.data_name}.py")
            self._create_file(raw_file, f"# Script de ingestão para {self.data_name}\n")

    def _create_service(self):
        if not self.system_name:
            return
        service_dir = os.path.join(self.name, "service", self.system_name)
        os.makedirs(service_dir, exist_ok=True)
        try:
            service_gen = self._ServiceGenerator(
                service_name=self.system_name.capitalize(),
                service_type="api",
                output_path=service_dir,
                models=None
            )
            service_gen.generate()
        except Exception as e:
            auth_file = os.path.join(service_dir, f"{self.system_name}_auth.py")
            service_file = os.path.join(service_dir, f"{self.system_name}_service.py")
            models_file = os.path.join(service_dir, f"{self.system_name}_models.py")
            self._create_file(auth_file, f"# Autenticação para {self.system_name}\n")
            self._create_file(service_file, f"# Serviço para {self.system_name}\n")
            self._create_file(models_file, f"# Modelos de dados para {self.system_name}\n")

    def _create_root_files(self):
        setup_file = os.path.join(self.name, "setup.py")
        readme_file = os.path.join(self.name, "README.md")
        gitignore_file = os.path.join(self.name, ".gitignore")
        self._create_file(setup_file, "# setup.py para instalar a biblioteca\n")
        self._create_file(readme_file, f"# {self.name}\n\nDocumentação da biblioteca.\n")
        self._create_file(gitignore_file, "__pycache__/\n*.pyc\n.env\n")

    def _create_main_init(self):
        main_init = os.path.join(self.name, "__init__.py")
        self._create_file(main_init, f"# Biblioteca {self.name} ({self.lib_type.value})\n")
