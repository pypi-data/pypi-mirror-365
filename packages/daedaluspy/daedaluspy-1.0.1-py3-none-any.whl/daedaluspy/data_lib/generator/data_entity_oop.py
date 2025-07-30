from enum import Enum
from typing import List, Optional
import os

class Tier(Enum):
    RAW = "raw"
    CLEAR = "clear"
    MODEL = "model"

class CloudProvider(Enum):
    AZURE = "azure"
    AWS = "aws"
    GOOGLE = "google"

class DataEntityGenerator:
    def __init__(
        self,
        classname: str,
        tier: Tier,
        cloud_provider: CloudProvider,
        columns: Optional[List[str]] = None,
        output_path: Optional[str] = None,
        extension: str = "csv",
        imports: str = "import pandas as pd",
        lib: str = "",
        data_layer: str = None,
        path_prefix: str = "",
        filename: str = ""
    ):
        self.classname = classname
        self.tier = tier
        self.cloud_provider = cloud_provider
        self.columns = columns or ["id", "name", "created_at"]
        self.output_path = output_path
        self.extension = extension
        self.imports = imports
        self.lib = lib
        self.data_layer = data_layer or tier.value
        self.path_prefix = path_prefix
        self.filename = filename

    def generate(self):
        import pathlib
        # Escolhe template correto
        from daedaluspy.data_lib.data.cloud_aws.template.container_files.entity_template import TEMPLATE_ENTITY_AWS
        from daedaluspy.data_lib.data.cloud_azure.template.container_files.entity_template import TEMPLATE_ENTITY_AZURE
        from daedaluspy.data_lib.data.cloud_google.template.container_files.entity_template import TEMPLATE_ENTITY_GOOGLE
        templates = {
            "aws": TEMPLATE_ENTITY_AWS,
            "azure": TEMPLATE_ENTITY_AZURE,
            "google": TEMPLATE_ENTITY_GOOGLE
        }
        template = templates[self.cloud_provider.value]

        # Formatar colunas para o template
        if self.columns:
            columns_formatted = "\n".join([f"        {col.upper()} = '{col}'" for col in self.columns])
        else:
            columns_formatted = ""

        # path_prefix e filename
        path_prefix = self.path_prefix or self.classname.lower()
        filename = self.filename or self.classname.lower()

        # Descobre a raiz do projeto (setup.py/pyproject.toml)
        cwd = pathlib.Path.cwd()
        lib_root = None
        for parent in [cwd] + list(cwd.parents):
            if (parent / 'pyproject.toml').exists() or (parent / 'setup.py').exists():
                lib_root = parent
                break
        if not lib_root:
            lib_root = cwd

        # Descobre o diretório de pacote Python (igual ao ServiceGenerator)
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

        entity_code = template.format(
            lib_name=lib_name,
            imports=self.imports,
            classname=self.classname,
            columns=columns_formatted,
            file_extension=self.extension,
            data_layer=self.data_layer,
            data_layer_upper=self.data_layer.upper(),
            path_prefix=path_prefix,
            filename=filename
        )

        # Sempre gera dentro do pacote Python detectado, nunca no root do projeto
        output_path = pathlib.Path(lib_root) / lib_name / "data" / self.data_layer
        output_path.mkdir(parents=True, exist_ok=True)
        # Garante __init__.py em cada nível da estrutura
        pkg_parts = [lib_root, lib_name, "data"] + self.data_layer.split(os.sep)
        for i in range(3, len(pkg_parts)+1):
            init_path = pathlib.Path(*pkg_parts[:i]) / "__init__.py"
            if not init_path.exists():
                init_path.touch()
        output_file = output_path / f"{self.classname.lower()}.py"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(entity_code)

        print(f"Entidade gerada em: {output_file}")
