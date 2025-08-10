"""
Setup configuration for Gold Trading Statistical Analysis
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements file
with open('requirements_blog.txt') as f:
    requirements = f.read().splitlines()

# Filter out comments and empty lines
requirements = [req for req in requirements if req and not req.startswith('#')]

setup(
    name="gold-trading-statistical-analysis",
    version="1.0.0",
    author="TheHaywire",
    author_email="",
    description="Advanced quantitative analysis of gold trading patterns using real MT5 account data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TheHaywire/gold-trading-statistical-analysis",
    packages=find_packages(exclude=['tests*', 'docs*']),
    
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    
    keywords="trading, quantitative-analysis, statistical-edge, metatrader5, gold-trading, financial-analysis, backtesting, algorithmic-trading, data-science",
    
    python_requires=">=3.8",
    install_requires=requirements,
    
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.900',
            'jupyter>=1.0.0'
        ],
        'web': [
            'streamlit>=1.0.0',
            'dash>=2.0.0',
            'flask>=2.0.0'
        ],
        'full': [
            'pytest>=6.0.0',
            'black>=21.0.0',
            'flake8>=3.9.0',
            'mypy>=0.900',
            'jupyter>=1.0.0',
            'streamlit>=1.0.0',
            'dash>=2.0.0',
            'flask>=2.0.0'
        ]
    },
    
    entry_points={
        'console_scripts': [
            'gold-analysis=src.main:main',
            'mt5-export=mt5_data_exporter:main',
            'generate-charts=chart_generator:main',
            'create-tools=interactive_analysis_tools:main'
        ],
    },
    
    package_data={
        'gold_trading_analysis': [
            'blog_data_exports/downloadable_tools/*.xlsx',
            'blog_data_exports/downloadable_tools/*.csv',
            'blog_data_exports/charts/*.png',
            'blog_data_exports/charts/*.html',
            'config/*.json',
            'templates/*.html'
        ],
    },
    
    include_package_data=True,
    
    project_urls={
        "Bug Reports": "https://github.com/TheHaywire/gold-trading-statistical-analysis/issues",
        "Source": "https://github.com/TheHaywire/gold-trading-statistical-analysis",
        "Documentation": "https://github.com/TheHaywire/gold-trading-statistical-analysis/blob/master/docs/",
        "Changelog": "https://github.com/TheHaywire/gold-trading-statistical-analysis/releases",
    },
    
    zip_safe=False,
)