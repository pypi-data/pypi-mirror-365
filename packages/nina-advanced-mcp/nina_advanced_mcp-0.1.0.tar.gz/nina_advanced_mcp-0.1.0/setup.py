from setuptools import setup, find_packages

setup(
    name="nina_advanced_mcp",
    version="0.1.0",
    description="NINA Advanced MCP API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="justToDeploy",
    author_email="justToDeploy@foxmail.com",
    url="https://github.com/justToDeploy/nina_advanced_mcp", 
    packages=find_packages(),
    install_requires=[
        "fastmcp>=0.1.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
        "aiohttp>=3.8.0",
        "python-dotenv>=1.0.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "structlog>=23.1.0",
        "typing-extensions>=4.5.0"
    ],
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
) 