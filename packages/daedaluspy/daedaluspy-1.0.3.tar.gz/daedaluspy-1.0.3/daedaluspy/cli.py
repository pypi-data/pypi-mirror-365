from daedaluspy.data_pipeline.template.complete_templates import get_template_set
from daedaluspy.data_pipeline.generator.pipeline_generator_oop import PipelineGenerator, PipelineTier, CloudProvider as PipelineCloudProvider
import argparse
import sys
from enum import Enum
from daedaluspy.data_lib.generator.library_generator import LibraryGenerator
from daedaluspy.data_lib.generator.data_entity_oop import DataEntityGenerator, CloudProvider
from daedaluspy.data_lib.generator.service_generator_oop import ServiceGenerator

class Tier(Enum):
    RAW = "raw"
    CLEAR = "clear"
    MODEL = "model"

class ServiceType(Enum):
    API = "api"
    DATABASE = "database"

class Command:
    def execute(self, args):
        raise NotImplementedError

class CreateLibCommand(Command):
    def execute(self, args):
        generator = LibraryGenerator(
            name=args.name,
            data_name=args.dataname,
            system_name=args.systemname
        )
        generator.generate()
        print(f"Estrutura da biblioteca '{args.name}' criada com sucesso!")

class CreateDataCommand(Command):
    def execute(self, args):
        if not args.tier:
            print("Erro: --tier é obrigatório (raw, clear, model)")
            sys.exit(1)
        tier = Tier(args.tier)
        extra_kwargs = {}
        if hasattr(args, 'output') and args.output:
            extra_kwargs['output_path'] = args.output
        if hasattr(args, 'lib') and args.lib:
            extra_kwargs['lib'] = args.lib
        generator = DataEntityGenerator(
            classname=args.name,
            tier=tier,
            cloud_provider=CloudProvider(args.cloud),
            columns=args.columns or [],
            **extra_kwargs
        )
        generator.generate()
        print(f"Entidade '{args.name}' criada com sucesso na camada {tier.value}.")

class CreateServiceCommand(Command):
    def execute(self, args):
        service_type = ServiceType(args.type)
        # Permite argumentos opcionais futuros
        extra_kwargs = {}
        if hasattr(args, 'output') and args.output:
            extra_kwargs['output_path'] = args.output
        if hasattr(args, 'lib') and args.lib:
            extra_kwargs['lib'] = args.lib
        # Converter models de lista de strings JSON para lista de dicts
        import json
        models = []
        if args.models:
            for m in args.models:
                if isinstance(m, dict):
                    models.append(m)
                else:
                    try:
                        models.append(json.loads(m))
                    except Exception:
                        pass
        generator = ServiceGenerator(
            service_name=args.name,
            service_type=service_type,
            models=models,
            **extra_kwargs
        )
        generator.generate()
        print(f"Serviço '{args.name}' ({service_type.value}) criado com sucesso.")

class CreatePipelineCommand(Command):
    def execute(self, args):
        tier = PipelineTier(args.tier)
        # Permitir todos os parâmetros opcionais igual ao create-pipeline-project
        def enum_from_value(enum_cls, value):
            for e in enum_cls:
                if value == e.value or value == e.name or value.upper() == e.name:
                    return e
            raise ValueError(f"{value} não é válido para {enum_cls.__name__}")

        generator = PipelineGenerator(
            system_name=args.system_name,
            dataname=args.dataname,
            tier=tier,
            output_path=args.output if args.output else ".",
            template_type=getattr(args, "template_type", "all"),
            lib_name=getattr(args, "lib_name", "atlaspy"),
            cloud_provider=enum_from_value(PipelineCloudProvider, getattr(args, "cloud_provider", "cloud_azure")),
            entity_target=getattr(args, "entity_target", None),
            entity_target_class=getattr(args, "entity_target_class", None)
        )
        generator.generate()
        print(f"Pipeline '{args.system_name}/{args.dataname}/{tier.value}' criado com sucesso.")


def main():
    parser = argparse.ArgumentParser(description="DaedalusPy CLI")
    subparsers = parser.add_subparsers(dest="command")
    # create pipeline project (completo)
    parser_pipeline_project = subparsers.add_parser("create-pipeline-project")
    parser_pipeline_project.add_argument("system_name")
    parser_pipeline_project.add_argument("dataname")
    parser_pipeline_project.add_argument("tier", choices=["raw", "clear", "model"])
    parser_pipeline_project.add_argument("--output", "-o", default=".")
    parser_pipeline_project.add_argument("--template-type", "-t", choices=["essential", "dev", "all"], default="all")
    parser_pipeline_project.add_argument("--lib-name", default="atlaspy")
    parser_pipeline_project.add_argument("--cloud-provider", default="cloud_azure")
    parser_pipeline_project.add_argument("--entity-target", default="azure_sql_database")
    parser_pipeline_project.add_argument("--entity-target-class", default="AzureSQLDatabase")

    # create lib
    parser_lib = subparsers.add_parser("create-lib")
    parser_lib.add_argument("name")
    parser_lib.add_argument("--dataname")
    parser_lib.add_argument("--systemname")

    # create data
    parser_data = subparsers.add_parser("create-data")
    parser_data.add_argument("name")
    parser_data.add_argument("--tier", required=True, choices=[t.value for t in Tier])
    parser_data.add_argument("--cloud", required=True)
    parser_data.add_argument("--extension")
    parser_data.add_argument("--columns", nargs="*")
    parser_data.add_argument("--imports")
    parser_data.add_argument("--read_code")
    parser_data.add_argument("--write_code")
    parser_data.add_argument("--output")
    parser_data.add_argument("--lib")


    # create service
    parser_service = subparsers.add_parser("create-service")
    parser_service.add_argument("name")
    parser_service.add_argument("--type", required=True, choices=[t.value for t in ServiceType])
    parser_service.add_argument("--models", nargs="*")
    parser_service.add_argument("--output")

    # create pipeline
    parser_pipeline = subparsers.add_parser("create-pipeline")
    parser_pipeline.add_argument("system_name")
    parser_pipeline.add_argument("dataname")
    parser_pipeline.add_argument("--tier", required=True, choices=[t.value for t in PipelineTier])
    parser_pipeline.add_argument("--output", default=".")
    parser_pipeline.add_argument("--template_type", default="all")
    parser_pipeline.add_argument("--lib_name", default="atlaspy")
    parser_pipeline.add_argument("--cloud_provider", default="cloud_azure")
    parser_pipeline.add_argument("--entity_target", default="azure_sql_database")
    parser_pipeline.add_argument("--entity_target_class", default="AzureSQLDatabase")

    args = parser.parse_args()


    commands = {
        "create-lib": CreateLibCommand(),
        "create-data": CreateDataCommand(),
        "create-service": CreateServiceCommand(),
        "create-pipeline": CreatePipelineCommand(),
    }

    if args.command in commands:
        commands[args.command].execute(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
