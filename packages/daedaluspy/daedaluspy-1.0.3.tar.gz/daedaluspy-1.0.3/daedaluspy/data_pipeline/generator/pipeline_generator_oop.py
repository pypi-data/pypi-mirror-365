from enum import Enum
from ..template.complete_templates import get_template_set
from datetime import datetime
from typing import Dict, Any
import os

class CloudProvider(Enum):
    AZURE = "azure"
    AWS = "aws"
    GOOGLE = "google"



class PipelineTier(Enum):
    RAW = "raw"
    CLEAR = "clear"
    MODEL = "model"

class PipelineGenerator:
    def __init__(self,
        system_name: str,
        dataname: str,
        tier: PipelineTier,
        output_path: str = ".",
        template_type: str = "all",
        lib_name: str = "atlaspy",
        cloud_provider: CloudProvider = CloudProvider.AZURE,
        entity_target: str = None,  # nome da entidade (arquivo ou classe) da lib
        entity_target_class: str = None  # nome da classe da entidade da lib
    ):
        self.system_name = system_name
        self.dataname = dataname
        if not isinstance(tier, PipelineTier):
            raise ValueError("tier deve ser uma instância de PipelineTier")
        if not isinstance(cloud_provider, CloudProvider):
            raise ValueError("cloud_provider deve ser uma instância de CloudProvider")
        self.tier = tier
        self.output_path = output_path
        self.template_type = template_type
        self.lib_name = lib_name
        self.cloud_provider = cloud_provider
        self.entity_target = entity_target
        self.entity_target_class = entity_target_class

    def to_camel_case(self, text):
        return "".join(word.capitalize() for word in text.replace("_", " ").split())

    def generate(self):
        project_name = f"{self.system_name}_{self.dataname}_{self.tier.value}"
        project_class_name = f"{self.to_camel_case(self.system_name)}{self.to_camel_case(self.dataname)}{self.to_camel_case(self.tier.value)}"
        template_vars = {
            'project_name': project_name,
            'project_class_name': project_class_name,
            'system_name': self.system_name,
            'dataname': self.dataname,
            'tier': self.tier.value,
            'lib_name': self.lib_name,
            'cloud_provider': self.cloud_provider.value,
            'entity_target': self.entity_target or "",
            'entity_target_class': self.entity_target_class or "",
            'entity_target_name': (self.entity_target or "").lower(),
            'current_date': datetime.now().strftime('%Y-%m-%d')
        }

        # Corrigir: nunca criar subpastas extras (ex: TestLib/pipeline), só a pasta do pipeline direto no output_path
        # Se output_path já termina com project_name, não duplique
        # Se output_path termina com 'pipeline' ou 'TestLib', ignore e crie no diretório pai
        norm_output = os.path.normpath(self.output_path)
        base = os.path.basename(norm_output)
        parent = os.path.dirname(norm_output)
        if base.lower() in ["pipeline", "testlib"]:
            project_dir = os.path.join(parent, project_name)
        elif base == project_name:
            project_dir = norm_output
        else:
            project_dir = os.path.join(norm_output, project_name)

        os.makedirs(project_dir, exist_ok=True)
        templates = get_template_set(self.template_type)
        created_files = []
        for file_path, template in templates.items():
            # Não criar subpastas extras, só arquivos diretamente na pasta do pipeline
            # Se file_path contém subpastas, só pegue o nome do arquivo
            file_name = os.path.basename(file_path)
            full_path = os.path.join(project_dir, file_name)
            try:
                content = template.format(**template_vars)
            except Exception as e:
                aviso = f"""# AVISO: Erro ao preencher template ({e})\n# Algumas variáveis podem estar faltando.\n"""
                try:
                    import re
                    def safe_format(tpl, vars):
                        def replace_double(m):
                            var = m.group(1)
                            return str(vars[var]) if var in vars else f"<FALTANDO:{var}>"
                        def replace_single(m):
                            var = m.group(1)
                            return str(vars[var]) if var in vars else f"<FALTANDO:{var}>"
                        tpl = re.sub(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', replace_double, tpl)
                        tpl = re.sub(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', replace_single, tpl)
                        return tpl
                    content = aviso + safe_format(template, template_vars)
                except Exception as e2:
                    content = aviso + f"# Falha ao gerar template: {e2}\n"
                print(f"Erro ao gerar {file_path}: {e}")
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(file_name)
        print(f"Projeto '{project_name}' criado em: {project_dir}")
        print(f"Tipo de template: {self.template_type}")
        print(f"Arquivos gerados ({len(created_files)}):")
        for file_name in sorted(created_files):
            print(f"  - {file_name}")
        return project_dir
