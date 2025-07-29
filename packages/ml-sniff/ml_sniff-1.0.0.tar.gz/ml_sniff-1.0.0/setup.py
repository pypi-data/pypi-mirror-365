"""
Setup script for ML Sniff package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "ML Sniff - Automatic Machine Learning Problem Detection"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return [
        'pandas>=1.3.0',
        'numpy>=1.20.0',
        'matplotlib>=3.3.0',
        'seaborn>=0.11.0',
    ]

setup(
    name="ml-sniff",
    version="1.0.0",
    author="Sherin Joseph Roy",
    author_email="sherin.joseph2217@gmail.com",
    description="Advanced Machine Learning Problem Detection with CLI and GUI interfaces",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sherin-SEF-AI/ml-sniffer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "ml-sniff=ml_sniff.cli:main",
            "ml-sniff-gui=ml_sniff.gui:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="machine-learning, data-analysis, classification, regression, clustering, automation",
    project_urls={
        "Bug Reports": "https://github.com/Sherin-SEF-AI/ml-sniffer/issues",
        "Source": "https://github.com/Sherin-SEF-AI/ml-sniffer",
        "Documentation": "https://github.com/Sherin-SEF-AI/ml-sniffer#readme",
        "Author Website": "https://sherin-sef-ai.github.io/",
    },
) 