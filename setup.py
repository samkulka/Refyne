from setuptools import setup, find_packages

setup(
    name="refyne-data-cleanser",
    version="0.1.0",
    description="Automatically clean, validate, and transform messy data into AI-ready datasets",
    author="Refyne",
    author_email="support@refyne.ai",
    url="https://github.com/refyne/data-cleanser",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "duckdb>=0.9.0",
        "pandera>=0.17.0",
        "pydantic>=2.0.0",
        "openpyxl>=3.1.0",
        "python-dateutil>=2.8.0",
        "click>=8.1.0",
        "rich>=13.0.0",
        "tabulate>=0.9.0",
    ],
    extras_require={
        "ai": ["openai>=1.0.0"],
        "dev": ["pytest>=7.4.0", "black>=23.0.0", "isort>=5.12.0"],
    },
    entry_points={
        "console_scripts": [
            "cleanser=src.main:cli",
        ],
    },
    python_requires=">=3.9",
)