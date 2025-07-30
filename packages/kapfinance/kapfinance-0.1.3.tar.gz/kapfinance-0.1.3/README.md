# Financial Data Manager

[![PyPI version](https://badge.fury.io/py/kapfinance.svg)](https://pypi.org/project/kapfinance/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This Python class, `kapfinance`, is designed to read, process, and manage financial `.xls` files (which contain HTML content) located within a specified root folder and its subfolders. It's particularly useful for extracting financial statement data on a **ticker-by-ticker basis**, implementing a **lazy loading** mechanism for efficient memory usage.

---

## Features

* **Automated File Mapping**: Scans a given directory to build a comprehensive map of all available financial statement files, identifying tickers and reporting periods.
* **HTML Content Processing**: Reads `.xls` files (often used for financial reports that are essentially HTML tables), extracts relevant financial account descriptions and their corresponding values.
* **Lazy Loading**: Data for a specific ticker is only loaded into memory when explicitly requested, optimizing memory usage for large datasets.
* **Time-Series Data Retrieval**: Provides a convenient method to retrieve financial data as a **pandas DataFrame**, with account descriptions as rows and reporting periods as columns, sorted chronologically.
* **Period Filtering**: Allows users to filter financial data by specifying a start and end reporting period (in `'YYYY_QQ'` format, e.g., `'2020_01'`, `'2022_04'`).
* **Robust Error Handling**: Includes logging for various scenarios, such as missing folders, file processing errors, and unavailable data.

---

## Getting Started

### Prerequisites

To use this class, you'll need the following Python libraries installed:

```bash
pip install pandas numpy lxml openpyxl