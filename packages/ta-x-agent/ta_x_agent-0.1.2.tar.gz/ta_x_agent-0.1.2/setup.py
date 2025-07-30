from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "TA_X: X (Twitter) Agent Package"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

setup(
    name="ta-x-agent",
    version="0.1.2",
    author="Soumyajit",
    author_email="soumyajit@theagentic.ai",
    description="A Python package for interacting with X (Twitter) platform using AI agents and tools",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Soumyajit22theagentic/ta_x",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=2.0.0",
        "pydantic-ai>=0.1.0",
        "requests>=2.25.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "httpx>=0.25.0",
        "asyncio",
        "dataclasses",
        "pathlib",
        "typing",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "ta-x-agent=ta_x.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "ta_x": ["*.py", "*.md", "*.txt"],
    },
    keywords="twitter x social media ai agent automation",
    project_urls={
        "Bug Reports": "https://github.com/Soumyajit22theagentic/ta_x/issues",
        "Source": "https://github.com/Soumyajit22theagentic/ta_x",
        "Documentation": "https://github.com/Soumyajit22theagentic/ta_x#readme",
    },
) 