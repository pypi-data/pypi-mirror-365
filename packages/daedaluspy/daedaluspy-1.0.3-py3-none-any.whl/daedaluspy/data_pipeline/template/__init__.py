"""
Templates para geração de projetos de pipeline
Contém os templates oficiais utilizados pelo DaedalusPy
"""

# Imports dos templates oficiais
from .complete_templates import (
    CONFIG_TEMPLATE,
    FLOWBUILDER_TEMPLATE,
    MAIN_TEMPLATE,
    INIT_TEMPLATE,
    BASE_TEMPLATE,
    STEPS_TEMPLATE,
    README_TEMPLATE,
    REQUIREMENTS_TEMPLATE,
    GITIGNORE_TEMPLATE,
    get_template_set,
    ESSENTIAL_TEMPLATES,
    ALL_TEMPLATES
)

__all__ = [
    'CONFIG_TEMPLATE',
    'BASE_TEMPLATE',
    'STEPS_TEMPLATE',
    'FLOWBUILDER_TEMPLATE',
    'MAIN_TEMPLATE',
    'INIT_TEMPLATE',
    'README_TEMPLATE',
    'REQUIREMENTS_TEMPLATE',
    'GITIGNORE_TEMPLATE',
    'get_template_set',
    'ESSENTIAL_TEMPLATES',
    'ALL_TEMPLATES'
]
