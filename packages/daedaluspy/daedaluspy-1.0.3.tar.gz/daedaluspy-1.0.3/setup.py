from setuptools import setup, find_packages

setup(
    name="daedaluspy",
    version="1.0.2",
    description="Code generation toolkit for data engineering",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Golden Valley Consulting LTDA",
    author_email="coutod@goldenvalleyc.com",
    url="https://github.com/Golden-Valley-Consulting/DaedalusPy",
    license="MIT",
    packages=find_packages(include=["daedaluspy*"]),
    include_package_data=True,
    install_requires=[
        # Adicione dependências de runtime aqui, ex: "pandas"
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="code-generation data-engineering python cli",
    entry_points={
        "console_scripts": [
            "daedaluspy=daedaluspy.cli:main"
        ]
    },
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
            "mypy",
        ]
    },
    package_data={
        "daedaluspy": ["**/*.py", "**/*.txt", "**/*.md"],
    },
)
