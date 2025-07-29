# VoilaData

**VoilaData** is a versatile Python library designed to streamline the entire data quality workflow: loading data from numerous sources, performing a deep analysis of its health, and generating a professional, shareable HTML report—all in just a few lines of code.

It provides three main components:

1.  `DataFrameReader`: Reads various file formats into a pandas DataFrame, with robust, automatic flattening of nested data structures.
2.  `DataFrameHealthChecker`: Performs a comprehensive suite of data quality and validation checks on a DataFrame.
3.  `HTMLReportGenerator`: Creates a clean, modern, and interactive HTML report from the health check results.

This package provides a single, convenient interface to load data and immediately assess and report on its health, making it an essential tool for data scientists and analysts.

## Key Features

*   **Unified Data Loading**: A single `read()` method for all supported file types.
*   **Wide Format Support**: Natively handles a large variety of common data file formats.
*   **Intelligent Flattening**: Automatically converts deeply nested JSON, YAML, and TOML files into a flat, wide DataFrame, ready for analysis.
*   **Comprehensive Health Checks**: Includes a suite of checks for missing data, duplicates, data types, and format validation for emails, URLs, dates, and coordinates.
*   **Automatic HTML Reporting**: Generate a clean, professional, and shareable HTML report of the data health checks with a single command.
*   **Extensible and Modular**: Install support for only the file formats you need, keeping the installation lightweight.

## Installation

You can install the core library from PyPI:

```bash
pip install voiladata
```

The library uses "extras" to manage optional dependencies for specific file formats. To install support for additional formats, use one of the following commands:

```bash
# To install support for Excel files
pip install voiladata[excel]

# To install support for YAML files
pip install voiladata[yaml]

# To install support for Parquet, ORC, Feather, and Avro
pip install voiladata[arrow]

# To install support for all formats
pip install voiladata[all]
```

The available extras are: `excel`, `yaml`, `toml`, `html`, `arrow`, and `spss`.

## Supported Formats

| Extension(s) | Required Extra |
| :--- | :--- |
| `.csv`, `.tsv` | (core) |
| `.json`, `.ndjson` | (core) |
| `.dta` (Stata) | (core) |
| `.xls`, `.xlsx` | `[excel]` |
| `.yaml`, `.yml` | `[yaml]` |
| `.toml` | `[toml]` |
| `.html` | `[html]` |
| `.parquet` | `[arrow]` |
| `.orc` | `[arrow]` |
| `.feather` | `[arrow]` |
| `.avro` | `[arrow]` |
| `.sav` (SPSS) | `[spss]` |

---

## Quickstart

Load any supported file, run a full health check, and generate an HTML report in a single, simple workflow.

```python
from voiladata import DataFrameReader, DataFrameHealthChecker, HTMLReportGenerator
import pandas as pd
import os

# --- Create a dummy data file for this example ---
# In a real scenario, you would use your own existing file path.
sample_data = """
[
    {
        "id": "user1",
        "email": "alice@example.com",
        "website": "https://datascience.com",
        "profile": { "name": "Alice", "age": 30 },
        "logins": [
            {"timestamp": "2024-01-10T10:00:00Z", "ip": "192.168.1.1"},
            {"timestamp": "2024-01-11T12:30:00Z", "ip": "invalid-ip"}
        ]
    },
    {
        "id": "user2",
        "email": "bob-at-work.com",
        "website": "ftp://files.server.io",
        "profile": { "name": "Bob", "age": 45 },
        "logins": []
    }
]
"""
file_path = "quickstart_data.json"
with open(file_path, "w") as f:
    f.write(sample_data)
# --- End of dummy file creation ---


# 1. Load the data using DataFrameReader
# The reader will automatically flatten the nested JSON structure.
reader = DataFrameReader(file_path)
df = reader.read()

# 2. Check the data's health
# This runs a comprehensive suite of checks.
health_checker = DataFrameHealthChecker(df)
report = health_checker.run_all_checks()

# 3. Generate and open an HTML report
# The report is saved to a file and automatically opened in your browser.
html_reporter = HTMLReportGenerator(df, report, output_path='data_health_report.html')
html_reporter.generate_report(open_in_browser=True)

print(f"HTML report has been generated and opened. You can find it at: {os.path.realpath(html_reporter.output_path)}")

```

---

## `DataFrameReader` In-Depth

The `DataFrameReader` is designed for simplicity and power.

### Basic Usage

The `read()` method automatically detects the file type and uses the best loader.

```python
from voiladata import DataFrameReader

reader = DataFrameReader('path/to/data.csv')
df = reader.read()
print(df.head())
```

### Passing Arguments to Pandas

You can pass keyword arguments (`**kwargs`) directly to the underlying pandas read function. For example, to read a specific sheet from an Excel file:

```python
# Requires 'pip install voiladata[excel]'
reader = DataFrameReader('path/to/data.xlsx')
df = reader.read(sheet_name='SalesData') 
```

### Automatic Flattening of Nested Data

This is the standout feature of `DataFrameReader`. For nested formats like JSON, it automatically flattens the structure.

**Sample `data.json`:**
```json
[
    {
        "id": "user1",
        "profile": { "name": "Alice", "age": 30 },
        "logins": [
            {"timestamp": "2024-01-10T10:00:00Z", "ip": "192.168.1.1"},
            {"timestamp": "2024-01-11T12:30:00Z", "ip": "192.168.1.2"}
        ]
    }
]
```

**Code:**
```python
reader = DataFrameReader('data.json')
df = reader.read()
print(df)
```

**Output DataFrame:**

| id | profile\_name | profile\_age | logins\_0\_timestamp | logins\_0\_ip | logins\_1\_timestamp | logins\_1\_ip |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| user1 | Alice | 30 | 2024-01-10T10:00:00Z | 192.168.1.1 | 2024-01-11T12:30:00Z | 192.168.1.2 |

You can customize the separator for flattened keys:
```python
df = reader.read(sep='.')
# Columns would be: profile.name, logins.0.ip, etc.
```

---

## `DataFrameHealthChecker` In-Depth

After loading your data, use `DataFrameHealthChecker` to perform a wide range of quality checks.

```python
from voiladata import DataFrameHealthChecker
import pandas as pd

# Sample DataFrame
data = {
    "email": ["test@example.com", "invalid-email", "another@test.com"],
    "website": ["https://example.com", "http://test.com", "bad-url"],
    "lat": [40.7128, 95.0, 34.0522],
    "lon": [-74.0060, -190.0, -118.2437],
    "created_date": ["2023-01-10", "2023/01/11", "2023-01-12"],
}
df = pd.DataFrame(data)

# Initialize the checker
checker = DataFrameHealthChecker(df)
```

### Full Report

The most convenient method is `run_all_checks()`, which generates a comprehensive report dictionary.

```python
report = checker.run_all_checks()
# This report contains missing values, duplicate rows, data types,
# summary statistics, and automated format validation.
```

### Individual Check Methods

You can also run specific checks individually for programmatic access.

#### Column Type Identification
Identifies numerical, categorical, and datetime columns.
```python
types = checker.identify_column_types()
# {'numerical_columns': ['lat', 'lon'], 'categorical_columns': [...], ...}
```

#### Date and Time Format Validation
Check if string columns conform to a specific format.
```python
# Check for YYYY-MM-DD format
valid_dates = checker.check_date_format('created_date', date_format='%Y-%m-%d')
# Returns a boolean Series: [True, False, True]
```

#### Coordinate Validation
Finds rows where latitude or longitude values are out of the valid range.
```python
invalid_coords_df = checker.check_latitude_longitude(lat_col='lat', lon_col='lon')
# Returns a DataFrame containing the rows with invalid lat/lon values
```

#### Email and URL Format Validation
Uses regular expressions to validate common string formats.
```python
# Check emails
valid_emails = checker.check_email_format('email')
# Returns a boolean Series: [True, False, True]

# Check URLs
valid_urls = checker.check_website_url_format('website')
# Returns a boolean Series: [True, True, False]
```

---

## `HTMLReportGenerator` In-Depth

The `HTMLReportGenerator` turns the dictionary from `DataFrameHealthChecker` into a polished and human-readable report.

It creates a self-contained HTML file with modern CSS styling that includes:
*   An overall summary (total rows, columns, duplicates).
*   A preview of the first and last rows of your data.
*   A detailed, column-by-column breakdown of data types, missing values, and summary statistics.
*   A dedicated section for format validation results (e.g., email and URL checks).
*   A summary of identified column types (Numerical, Categorical, etc.).

### Usage

The generator is simple to use. Just provide the DataFrame and the report dictionary.

```python

# Initialize the code with the DataFrame and the health check report.
# You can specify a custom output path for the file.
html_reporter = HTMLReportGenerator(
    df=df,
    report=report,
    output_path='data_quality_archive/q1_2025_report.html'
)

# Generate the report and save it.
# The `open_in_browser` argument defaults to True.
html_reporter.generate_report()

# To generate the file without opening it automatically:
html_reporter.generate_report(open_in_browser=False)
```

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.