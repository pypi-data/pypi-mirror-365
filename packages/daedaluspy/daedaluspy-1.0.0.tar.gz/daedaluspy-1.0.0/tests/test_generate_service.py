from daedaluspy.data_lib.generator.service_generator_oop import ServiceGenerator, ServiceType
import os

def test_generate_service_tmp(tmp_path):
    service_name = "TestService"
    service_type = ServiceType.API
    # Cria estrutura mínima na raiz do projeto
    root = os.path.abspath(os.path.dirname(__file__)).replace("tests", "")
    service_dir = os.path.join(root, "service", service_type.value, service_name.lower())
    if os.path.exists(service_dir):
        import shutil
        shutil.rmtree(service_dir)
    generator = ServiceGenerator(service_name=service_name, service_type=service_type)
    generator.generate()
    assert os.path.exists(os.path.join(service_dir, f"{service_name.lower()}_auth.py"))
    assert os.path.exists(os.path.join(service_dir, f"{service_name.lower()}_service.py"))
    assert os.path.exists(os.path.join(service_dir, f"{service_name.lower()}_models.py"))
    # Limpeza após o teste
    import shutil
    shutil.rmtree(service_dir)
