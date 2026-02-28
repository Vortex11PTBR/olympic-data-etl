"""
Setup configuration for Olympic Data ETL package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="olympic-data-etl",
    version="1.0.0",
    author="Data Engineering Team",
    author_email="olympic-etl@your-org.com",
    description="Production-grade ETL pipeline for Olympic Games data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/olympic-data-etl",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.11",
    install_requires=[
        "apache-beam[gcp]>=2.54.0",
        "google-cloud-bigquery>=3.17.0",
        "google-cloud-storage>=2.10.0",
        "requests>=2.31.0",
        "great-expectations>=0.18.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
        "structlog>=24.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "pylint>=3.0.0",
            "mypy>=1.7.0",
            "isort>=5.13.0",
            "flake8>=6.1.0",
            "bandit>=1.7.5",
        ],
        "azure": [
            "azure-storage-blob>=12.19.0",
            "azure-identity>=1.15.0",
            "azure-mgmt-datafactory>=3.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "olympic-etl=src.beam.pipelines.olympic_etl_pipeline:main",
        ],
    },
)
