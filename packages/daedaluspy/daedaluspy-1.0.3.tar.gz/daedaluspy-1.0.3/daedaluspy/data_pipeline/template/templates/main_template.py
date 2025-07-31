"""
Template para main.py - Função principal do pipeline
"""

MAIN_TEMPLATE = '''"""
Função principal do {project_name}
"""
from datetime import datetime
from .flowbuilder import {project_class_name}FlowBuilder
from .steps import DataCleaningStep, DataTransformStep, DataValidationStep, ProcessStep

def main(date_reference: datetime = None):
    """Função principal do pipeline {project_name}"""
    if date_reference is None:
        date_reference = datetime.now()

    builder = {project_class_name}FlowBuilder()

    try:
        process_1 = ProcessStep()
        process_2 = ProcessStep()
        process_3 = ProcessStep()
        process_4 = ProcessStep()
        builder = builder.set_date_reference(date_reference)
        builder = builder.collect()
        builder = builder.process(process_1)
        builder = builder.process(process_2)
        builder = builder.process(process_3)
        builder = builder.process(process_4)
        builder = builder.save()
        summary = builder.get_summary()
        return summary

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "date_reference": date_reference.isoformat()
        }

if __name__ == "__main__":
    result = main()
'''
