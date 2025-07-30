from setuptools import setup, find_packages

setup(
    name="raglight",
    version="5",
    description="A lightweight and modular framework for Retrieval-Augmented Generation (RAG)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Labess40",
    author_email="",
    url="https://github.com/Bessouat40/RAGLight",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "langchain",
        "chromadb",
        "python-dotenv",
        "langgraph",
        "langchain_ollama",
        "langchain_chroma",
        "langchain_huggingface",
        "typing",
        "mistralai",
        "smolagents",
        "langchain_community",
        "typing_extensions",
        "langchain_text_splitters",
        "langchain_core",
        "ollama",
        "typer[all]",
    ],
    entry_points={
        "console_scripts": [
            "raglight=raglight.cli.main:app",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)
