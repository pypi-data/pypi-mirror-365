from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="axiomtradeapi",
    version="0.2.0",
    description="A Python client for the AxiomTrade API with token-based authentication, WebSocket support, and Telegram bot integration.",
    author="ChipaDevTeam",
    author_email="",
    url="https://github.com/ChipaDevTeam/AxiomTradeAPI-py",
    packages=find_packages(),
    install_requires=[
        "websockets>=10.0",
        "python-dotenv",
        "solders",
        "requests>=2.25.1",
        "base58>=2.1.0",
    ],
    extras_require={
        "telegram": ["python-telegram-bot>=20.0"],
        "dev": ["pytest", "black", "flake8"],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="axiom trade solana crypto trading api websocket telegram bot",
    project_urls={
        "Bug Reports": "https://github.com/ChipaDevTeam/AxiomTradeAPI-py/issues",
        "Source": "https://github.com/ChipaDevTeam/AxiomTradeAPI-py",
        "Documentation": "https://chipadevteam.github.io/AxiomTradeAPI-py/",
    },
)
