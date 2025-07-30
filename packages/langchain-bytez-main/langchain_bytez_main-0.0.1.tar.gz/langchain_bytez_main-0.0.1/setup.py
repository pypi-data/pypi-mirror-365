import os
from setuptools import setup, find_packages

# Dynamically get absolute path to current directory
current_dir = os.path.abspath(os.path.dirname(__file__))

# Read the README.md file
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="langchain-bytez-main",
    version="0.0.1",
    author="AIMLStudent",
    # author_email="support@bytez.com",
    description="Bytez langchain integration with advanced AI capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bytez-com/langchain_bytez",
    packages=[
        "langchain_bytez_main",
    ],
    package_dir={
        "langchain_bytez_main": "langchain_bytez",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain==0.3.17",
        "requests>=2.25.0",
        "pydantic>=1.10.0",
    ],
    keywords="langchain, bytez, llm, ai, chatbot, artificial-intelligence",
    include_package_data=True,
    package_data={
        "langchain_bytez_main": ["*.md", "*.txt"],
    },
    project_urls={
        "Bug Reports": "https://github.com/Bytez-com/langchain_bytez/issues",
        "Source": "https://github.com/Bytez-com/langchain_bytez",
        "Documentation": "https://github.com/Bytez-com/langchain_bytez/blob/main/README.md",
    },
)
