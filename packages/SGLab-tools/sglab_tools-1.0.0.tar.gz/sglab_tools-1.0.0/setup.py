from setuptools import setup, find_packages
from pathlib import Path

# Lire le contenu du README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="SGLab-tools",
    version="1.0.0",
    author="Etienne Ntumba Kabongo",
    author_email="etienne.ntumba.kabongo@umontreal.ca",
    description="Outil professionnel de comparaison de génomes et détection de scénarios évolutifs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EtienneNtumba/SGLab-tools",
    project_urls={
        "Documentation": "https://github.com/EtienneNtumba/SGLab-tools",
        "Source": "https://github.com/EtienneNtumba/SGLab-tools",
    },
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "sglab=sglabtools.cli:app",
        ],
    },
    install_requires=[
        "typer>=0.6.1",
        "pandas>=1.3",
        "biopython>=1.78",
        "matplotlib>=3.4",
        "seaborn>=0.11",
        "openpyxl>=3.0"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console"
    ],
    python_requires='>=3.8',
)
