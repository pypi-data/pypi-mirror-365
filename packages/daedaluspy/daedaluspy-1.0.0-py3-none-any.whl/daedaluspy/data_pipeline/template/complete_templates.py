"""
Módulo principal com todos os templates de pipeline
"""

# Importar todos os templates
from .templates.config_template import CONFIG_TEMPLATE
from .templates.base_template import BASE_TEMPLATE
from .templates.steps_template import STEPS_TEMPLATE
from .templates.flowbuilder_template import FLOWBUILDER_TEMPLATE
from .templates.main_template import MAIN_TEMPLATE
from .templates.init_template import INIT_TEMPLATE
from .templates.readme_template import README_TEMPLATE
from .templates.requirements_template import REQUIREMENTS_TEMPLATE
from .templates.gitignore_template import GITIGNORE_TEMPLATE


# Dicionário com todos os templates disponíveis
ALL_TEMPLATES = {
    # Arquivos Python principais
    'config.py': CONFIG_TEMPLATE,
    'base.py': BASE_TEMPLATE,
    'steps.py': STEPS_TEMPLATE,
    'flowbuilder.py': FLOWBUILDER_TEMPLATE,
    'main.py': MAIN_TEMPLATE,
    '__init__.py': INIT_TEMPLATE,
    
    # Documentação
    'README.md': README_TEMPLATE,
    
    # Configuração do projeto
    

}

# Templates essenciais para um projeto mínimo
ESSENTIAL_TEMPLATES = {
    'config.py': CONFIG_TEMPLATE,
    'base.py': BASE_TEMPLATE,
    'steps.py': STEPS_TEMPLATE,
    'flowbuilder.py': FLOWBUILDER_TEMPLATE,
    'main.py': MAIN_TEMPLATE,
    '__init__.py': INIT_TEMPLATE,
    'README.md': README_TEMPLATE,


}


def get_template_set(template_type: str = 'essential'):
    """
    Retorna um conjunto de templates baseado no tipo solicitado
    
    Args:
        template_type: 'essential', 'dev', ou 'all'
    
    Returns:
        dict: Dicionário com templates
    """
    if template_type == 'essential':
        return ESSENTIAL_TEMPLATES

    elif template_type == 'all':
        return ALL_TEMPLATES
    else:
        raise ValueError(f"Tipo de template inválido: {template_type}. Use 'essential', 'dev', ou 'all'")

# Exportar templates individuais para compatibilidade
__all__ = [
    'CONFIG_TEMPLATE',
    'BASE_TEMPLATE', 
    'STEPS_TEMPLATE',
    'FLOWBUILDER_TEMPLATE',
    'MAIN_TEMPLATE',
    'INIT_TEMPLATE',
    'README_TEMPLATE',
    # 'REQUIREMENTS_TEMPLATE',
    # 'GITIGNORE_TEMPLATE',
    'TESTS_INIT_TEMPLATE',
    'CONFTEST_TEMPLATE',
    'TEST_STEPS_TEMPLATE',
    'TEST_FLOWBUILDER_TEMPLATE',
    'TEST_MAIN_TEMPLATE',
    'ALL_TEMPLATES',
    'ESSENTIAL_TEMPLATES',
    'DEV_TEMPLATES',
    'get_template_set'
]
