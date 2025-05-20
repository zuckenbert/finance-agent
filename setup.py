from setuptools import setup, find_packages

setup(
    name="finance_agent",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "google-auth",
        "google-api-python-client",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "openai",
        "pandasql"
    ],
) 