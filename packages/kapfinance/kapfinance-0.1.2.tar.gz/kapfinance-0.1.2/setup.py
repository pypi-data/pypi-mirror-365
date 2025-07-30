from setuptools import setup, find_packages

setup(
    name='kapfinance',
    version='0.1.2', # Start with 0.1.0 and increment for future releases
    author='Mert Kurtçu', # Replace with your name
    author_email='mertkurtcu.official@gmail.com.com', # Replace with your email
    description='A Python class for managing financial statement data from HTML-based XLS files.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/mertkurtcu/kapfinance', # Replace with your GitHub repository URL
    packages=find_packages(),
    install_requires=[
        'pandas>=1.0.0',
        'numpy>=1.18.0',
        'matplotlib>=3.0.0', # Matplotlib is used in the example usage, good to include
        'lxml', # pandas.read_html often relies on lxml, particularly for .xls files
        'openpyxl', # Good practice for general Excel file handling with pandas
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Or choose another appropriate license
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha', # Indicates early stage of development
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8', # Specify minimum Python version
    keywords='financial data manager, financial statements, balance sheet, income statement, html xls, pandas',
)