from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="datatidy",
    version="1.0.1",
    author="DataTidy Development Team",
    author_email="maintainer@example.com",
    description="A powerful, configuration-driven data processing and cleaning package",
    url="https://github.com/wwd1015/datatidy",
    project_urls={
        "Bug Reports": "https://github.com/wwd1015/datatidy/issues",
        "Source": "https://github.com/wwd1015/datatidy",
        "Documentation": "https://github.com/wwd1015/datatidy#readme",
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="data processing, data cleaning, ETL, configuration-driven, pandas, data transformation",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "PyYAML>=6.0",
        "sqlalchemy>=1.4.0",
        "openpyxl>=3.0.0",
        "snowflake-sqlalchemy>=1.4.0",
        "psycopg2-binary>=2.9.0",
        "pymysql>=1.0.0",
        "jsonschema>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "datatidy=datatidy.cli:main",
        ],
    },
)