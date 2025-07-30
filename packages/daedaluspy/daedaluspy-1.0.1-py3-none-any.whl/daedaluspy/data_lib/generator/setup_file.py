import os
import argparse
import sys
import subprocess

class SetupFileGenerator:
    def __init__(self, lib_name: str, version: str = "0.1.0", author: str = "DaedalusPy User", email: str = "user@example.com", description: str = "A data engineering library", requirements: str = "requirements.txt"):
        self.lib_name = lib_name
        self.version = version
        self.author = author
        self.email = email
        self.description = description
        self.requirements = requirements
        self.deps = self.read_requirements(requirements)

    def read_requirements(self, requirements_path):
        if not os.path.exists(requirements_path):
            print(f"Aviso: '{requirements_path}' não encontrado. Nenhuma dependência será adicionada.")
            return []
        with open(requirements_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        deps = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        return deps

    def generate_setup_py(self):
        deps_formatted = ",\n        ".join([f'"{dep}"' for dep in self.deps]) if self.deps else ""
        major = sys.version_info.major
        minor = sys.version_info.minor
        lib_name = self.lib_name
        lib_path = self.lib_name
        # Get the actual library name from the directory if lib_name is '.'
        if lib_name == '.':
            lib_name = os.path.basename(os.path.abspath(lib_path))
        content = f"""#!/usr/bin/env python3
\"\"\"Setup script for {lib_name} Library\"\"\"

import os
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ''

setup(
    name="{lib_name}",
    version="{self.version}",
    author="{self.author}",
    author_email="{self.email}",
    description="{self.description}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">={major}.{minor}",
    install_requires=[
        {deps_formatted}
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.{minor}",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="data-engineering python library analytics",
    include_package_data=True,
)
"""
        setup_path = os.path.join(lib_path, "setup.py")
        with open(setup_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"'setup.py' gerado com sucesso em '{setup_path}'.")
        if self.deps:
            print(f"Dependências incluídas: {self.deps}")
        else:
            print("Nenhuma dependência incluída (requirements.txt vazio ou ausente).")

    def build_wheel(self):
        lib_path = self.lib_name
        if not os.path.exists(os.path.join(lib_path, "setup.py")):
            raise FileNotFoundError(f"setup.py not found in {lib_path}")
        original_dir = os.getcwd()
        try:
            os.chdir(lib_path)
            result = subprocess.run([sys.executable, "setup.py", "bdist_wheel"], capture_output=True, text=True)
            if result.returncode == 0:
                print("Wheel built successfully!")
                print(f"Output: {result.stdout}")
                dist_dir = os.path.join(lib_path, "dist")
                if os.path.exists(dist_dir):
                    files = os.listdir(dist_dir)
                    print(f"Generated files in dist/: {files}")
            else:
                print("Error building wheel:")
                print(f"Error: {result.stderr}")
                raise Exception(f"Build failed: {result.stderr}")
        finally:
            os.chdir(original_dir)

    def generate_setup_file(self):
        # Check if lib_name is a directory path or name
        if os.path.exists(self.lib_name):
            lib_path = self.lib_name
            actual_lib_name = os.path.basename(os.path.abspath(self.lib_name))
        else:
            lib_path = self.lib_name
            actual_lib_name = self.lib_name
        self.deps = self.read_requirements(self.requirements)
        self.generate_setup_py()

    def generate_python_wheel(self):
        # Use current directory if lib_name is '.'
        if self.lib_name == '.':
            lib_path = '.'
            actual_lib_name = os.path.basename(os.path.abspath('.'))
        else:
            lib_path = self.lib_name
            actual_lib_name = self.lib_name
        self.deps = self.read_requirements(self.requirements)
        self.generate_setup_py()
        self.build_wheel()

def main():
    parser = argparse.ArgumentParser(description="Gerador automático de setup.py para uma biblioteca Python de engenharia de dados.")
    parser.add_argument("--lib", required=True, help="Nome da pasta da biblioteca (raiz)")
    parser.add_argument("--version", default="0.1.0", help="Versão da biblioteca (default: 0.1.0)")
    parser.add_argument("--author", required=True, help="Nome do autor")
    parser.add_argument("--email", required=True, help="Email do autor")
    parser.add_argument("--description", default="Uma biblioteca de engenharia de dados", help="Descrição da biblioteca")
    parser.add_argument("--requirements", default="requirements.txt", help="Caminho para o requirements.txt (default: requirements.txt na raiz)")
    args = parser.parse_args()
    generator = SetupFileGenerator(
        lib_name=args.lib,
        version=args.version,
        author=args.author,
        email=args.email,
        description=args.description,
        requirements=args.requirements
    )
    generator.generate_setup_file()

def generate_setup_file(
    lib_name: str,
    version: str = "0.1.0",
    author: str = "DaedalusPy User",
    email: str = "user@example.com",
    description: str = "A data engineering library",
    requirements: str = "requirements.txt"
):
    generator = SetupFileGenerator(lib_name, version, author, email, description, requirements)
    generator.generate_setup_file()

def generate_python_wheel(
    lib_name: str,
    version: str = "0.1.0",
    author: str = "DaedalusPy User",
    email: str = "user@example.com",
    description: str = "A data engineering library",
    requirements: str = "requirements.txt"
):
    generator = SetupFileGenerator(lib_name, version, author, email, description, requirements)
    generator.generate_python_wheel()

if __name__ == "__main__":
    main()
