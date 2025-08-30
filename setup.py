from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="stock-fundamentals-analyzer",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python-based tool for extracting, analyzing, and visualizing business fundamentals to identify undervalued small-cap companies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/stock-fundamentals-analyzer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "pytest-mock>=3.10",
            "black>=22.0",
            "flake8>=5.0",
            "mypy>=1.0",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipykernel>=6.0.0",
            "notebook>=6.0.0",
        ],
        "docs": [
            "sphinx>=5.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "stock-analyzer=src.analyzer:main",
            "stock-screener=src.screener:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/stock-fundamentals-analyzer/issues",
        "Source": "https://github.com/yourusername/stock-fundamentals-analyzer",
        "Documentation": "https://stock-fundamentals-analyzer.readthedocs.io/",
    },
    keywords="finance, stocks, fundamentals, analysis, small-cap, investment, screening, valuation",
    package_data={
        "src": ["config/*.yaml"],
    },
    include_package_data=True,
    zip_safe=False,
)