# setup.py

"""
Setup configuration for PerfectPizza HTML parser package.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "A blazing-fast, functional HTML parser for Python"

# Read version from __init__.py
def read_version():
    version_file = os.path.join(os.path.dirname(__file__), 'perfectpizza', '__init__.py')
    with open(version_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '1.0.0'

setup(
    # Package metadata
    name='perfectpizza',
    version=read_version(),
    description='A blazing-fast, functional HTML parser for Python',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    
    # Author information
    author='Harry Graham',
    author_email='Harry@actionsmartai.com',  # Replace with your email
    
    # URLs
    url='https://github.com/Harrygithubportfolio/PerfectPizza',  # Replace with your repo
    project_urls={
        'Bug Reports': 'https://github.com/Harrygithubportfolio/PerfectPizza/issues',
        'Source': 'https://github.com/Harrygithubportfolio/PerfectPizza',
        'Documentation': 'https://github.com/Harrygithubportfolio/PerfectPizza/wiki',
    },
    
    # Package discovery
    packages=find_packages(exclude=['test*', 'tests*']),
    
    # Dependencies
    python_requires='>=3.8',
    install_requires=[
        # No external dependencies! Pure Python stdlib only
    ],
    
    # Optional dependencies for development and extras
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-cov>=2.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.900',
        ],
        'pandas': [
            'pandas>=1.0',
        ],
        'requests': [
            'requests>=2.25',
        ],
        'performance': [
            'lxml>=4.6',  # For performance comparisons
        ],
    },
    
    # Package classification
    classifiers=[
        # Development status
        'Development Status :: 4 - Beta',
        
        # Intended audience
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        
        # Topic
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
        
        # License
        'License :: OSI Approved :: MIT License',
        
        # Python versions
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        
        # Operating systems
        'Operating System :: OS Independent',
        
        # Framework
        'Framework :: Django',
        'Framework :: Flask',
    ],
    
    # Keywords for PyPI search
    keywords='html parser css selectors web scraping dom beautifulsoup alternative functional',
    
    # Entry points (CLI commands)
    entry_points={
        'console_scripts': [
            'perfectpizza=perfectpizza.cli:main',  # We'll create this CLI tool
        ],
    },
    
    # Include additional files
    include_package_data=True,
    
    # Package data
    package_data={
        'perfectpizza': [
            'py.typed',  # Mark as typed package
        ],
    },
    
    # Zip safety
    zip_safe=False,
    
    # Test suite
    test_suite='test',
    
    # Platforms
    platforms=['any'],
)