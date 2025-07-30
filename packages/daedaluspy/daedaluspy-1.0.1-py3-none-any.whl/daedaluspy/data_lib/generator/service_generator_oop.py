from enum import Enum
from typing import List, Optional, Dict
import os

# Importa templates
from daedaluspy.data_lib.services.template.database.service_template import DB_AUTH_TEMPLATE, DB_SERVICE_TEMPLATE, MODEL_TEMPLATE
from daedaluspy.data_lib.services.template.apis.service_template import SERVICE_TEMPLATE as API_SERVICE_TEMPLATE

class ServiceType(Enum):
    API = "api"
    DATABASE = "database"

class ServiceGenerator:
    def __init__(self, service_name: str, service_type:ServiceType, models: Optional[List[Dict]] = None, output_path: Optional[str] = None, lib: str = None):
        self.service_name = service_name
        self.models = models or []
        self.service_type = service_type.value
        self.output_path = output_path
        self.lib = lib

    def generate(self):
        import pathlib
        # Descobre a raiz do projeto (setup.py/pyproject.toml)
        cwd = pathlib.Path.cwd()
        lib_root = None
        for parent in [cwd] + list(cwd.parents):
            if (parent / 'pyproject.toml').exists() or (parent / 'setup.py').exists():
                lib_root = parent
                break
        if not lib_root:
            lib_root = cwd

        # Descobre o diretório de pacote Python (tem __init__.py e pelo menos um subdiretório chamado 'data' ou 'service')
        lib_name = self.lib or None
        if not lib_name:
            for child in lib_root.iterdir():
                if child.is_dir() and (child / '__init__.py').exists():
                    has_data = (child / 'data').exists() and (child / 'data').is_dir()
                    has_service = (child / 'service').exists() and (child / 'service').is_dir()
                    if has_data or has_service:
                        lib_name = child.name
                        break
        if not lib_name:
            raise RuntimeError('Não foi possível detectar o diretório da biblioteca Python (ex: gvclib) no projeto. Certifique-se de que existe um diretório com __init__.py e um subdiretório data/ ou service/.')

        service_name = self.service_name
        service_name_lower = self.service_name.lower()
        output_path = pathlib.Path(lib_root) / lib_name / "service" / self.service_type / service_name_lower
        output_path.mkdir(parents=True, exist_ok=True)
        # Garante __init__.py em cada nível da estrutura
        pkg_parts = [lib_root, lib_name, "service", self.service_type, service_name_lower]
        for i in range(3, len(pkg_parts)+1):
            init_path = pathlib.Path(*pkg_parts[:i]) / "__init__.py"
            if not init_path.exists():
                init_path.touch()

        if self.service_type == ServiceType.DATABASE.value:
            # Auth
            with open(output_path / f"{service_name_lower}_auth.py", "w", encoding="utf-8") as f:
                f.write(DB_AUTH_TEMPLATE.format(service_name=service_name))
            # Service
            with open(output_path / f"{service_name_lower}_service.py", "w", encoding="utf-8") as f:
                f.write(DB_SERVICE_TEMPLATE.format(service_name=service_name, service_name_lower=service_name_lower))
            # Models
            columns = self._generate_model_columns()
            with open(output_path / f"{service_name_lower}_models.py", "w", encoding="utf-8") as f:
                f.write(MODEL_TEMPLATE.format(data_name=f"{service_name}Model", columns=columns))
        elif self.service_type == ServiceType.API.value:
            # Auth (API pode não precisar de auth específico, mas gera stub)
            with open(output_path / f"{service_name_lower}_auth.py", "w", encoding="utf-8") as f:
                f.write(f"""from dataclasses import dataclass\n\n@dataclass\nclass {service_name}Auth:\n    api_key: str\n    base_url: str\n""")
            # Service
            with open(output_path / f"{service_name_lower}_service.py", "w", encoding="utf-8") as f:
                f.write(API_SERVICE_TEMPLATE.format(service_name=service_name, service_name_lower=service_name_lower))
            # Models
            columns = self._generate_model_columns()
            with open(output_path / f"{service_name_lower}_models.py", "w", encoding="utf-8") as f:
                f.write(MODEL_TEMPLATE.format(data_name=f"{service_name}Model", columns=columns))
        else:
            raise ValueError(f"Tipo de serviço não suportado: {self.service_type}")
        print(f"Serviço '{self.service_name}' ({self.service_type}) criado em {output_path}")

    def _generate_model_columns(self) -> str:
        # Gera os campos do dataclass model a partir de self.models
        if not self.models:
            return "id: int\n    name: str = ''"
        lines = []
        for col in self.models:
            col_name = col.get('name', 'field')
            col_type = col.get('type', 'str')
            default = col.get('default')
            if default is not None:
                lines.append(f"{col_name}: {col_type} = {repr(default)}")
            else:
                lines.append(f"{col_name}: {col_type}")
        return "\n    ".join(lines)
