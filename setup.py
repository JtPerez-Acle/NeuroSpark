from setuptools import setup, find_packages

setup(
    name="kqml-parser-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0,<0.96.0",
        "uvicorn>=0.18.0,<0.19.0",
        "neo4j>=5.2.0,<6.0.0",
        "pydantic>=1.9.0,<2.0.0",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.18.0",
        "httpx>=0.24.0"
    ],
    python_requires=">=3.11,<4.0",
)
