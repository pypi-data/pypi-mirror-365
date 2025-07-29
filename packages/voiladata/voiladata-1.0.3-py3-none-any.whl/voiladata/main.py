import json
import logging
import pandas as pd
import numpy as np
import re
import toml
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Dict, List, Union
import webbrowser
import os

# Configure basic logging for informative output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFrameReader:
    """
    A comprehensive and robust class to read various file formats from a file path
    and return a pandas DataFrame. It is designed to handle both flat and
    deeply nested data structures by flattening them into a wide format.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initializes the DataFrameReader with the file path.

        Args:
            file_path (Union[str, Path]): The path to the input file.

        Raises:
            FileNotFoundError: If the file does not exist at the given path.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"The file was not found at path: {self.file_path}")
        self.file_extension = self.file_path.suffix.lower()

    def _flatten_data(self, data_obj: Union[Dict, List], parent_key: str = '', sep: str = '_') -> Dict:
        """
        Recursively flattens a nested dictionary or list into a single dictionary.

        Args:
            data_obj (Union[Dict, List]): The object to flatten.
            parent_key (str): The base key to use for the flattened keys.
            sep (str): The separator to use between keys.

        Returns:
            Dict: A flattened dictionary.
        """
        items: Dict[str, Any] = {}
        if isinstance(data_obj, MutableMapping):
            for k, v in data_obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                items.update(self._flatten_data(v, new_key, sep=sep))
        elif isinstance(data_obj, list):
            if not data_obj:
                items[parent_key] = []
            else:
                for i, v in enumerate(data_obj):
                    new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                    items.update(self._flatten_data(v, new_key, sep=sep))
        else:
            items[parent_key] = data_obj
        return items

    def read(self, **kwargs: Any) -> pd.DataFrame:
        """
        Reads the file based on its extension and returns a DataFrame.

        This method dispatches to the appropriate reading method based on the file extension.
        Keyword arguments are passed to the underlying pandas read function.

        Args:
            **kwargs: Arbitrary keyword arguments for pandas read functions.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the file data.
        
        Raises:
            ValueError: If the file format is unsupported.
            ImportError: If a required optional dependency is not installed.
        """
        reader_map = {
            '.csv': self._read_csv,
            '.tsv': self._read_tsv,
            '.xls': self._read_excel,
            '.xlsx': self._read_excel,
            '.html': self._read_html,
            '.json': self._read_json,
            '.yaml': self._read_yaml,
            '.yml': self._read_yaml,
            '.toml': self._read_toml,
            '.ndjson': self._read_ndjson,
            '.parquet': self._read_parquet,
            '.orc': self._read_orc,
            '.feather': self._read_feather,
            '.avro': self._read_avro,
            '.dta': self._read_stata,
            '.sav': self._read_spss,
        }

        reader_func = reader_map.get(self.file_extension)

        if not reader_func:
            msg = f"Unsupported file format: '{self.file_extension}'"
            logging.error(msg)
            raise ValueError(msg)

        try:
            logging.info(f"Reading file '{self.file_path}' with extension '{self.file_extension}'...")
            return reader_func(**kwargs)
        except Exception as e:
            logging.error(f"An error occurred while reading '{self.file_path}': {e}", exc_info=True)
            raise

    def _read_csv(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_csv(self.file_path, **kwargs)

    def _read_tsv(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep='\t', **kwargs)

    def _read_json(self, **kwargs: Any) -> pd.DataFrame:
        sep = kwargs.pop('sep', '_')
        with self.file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            flattened_data = [self._flatten_data(item, sep=sep) for item in data]
            return pd.DataFrame(flattened_data, **kwargs)
        elif isinstance(data, dict):
            return pd.DataFrame([self._flatten_data(data, sep=sep)], **kwargs)
        else:
            logging.warning(f"Top-level object in '{self.file_path}' is not a list or dict.")
            return pd.DataFrame()

    def _read_yaml(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import yaml
        except ImportError:
            raise ImportError("Reading YAML files requires PyYAML. Install with: pip install dataframe-loader[yaml]")
        
        sep = kwargs.pop('sep', '_')
        with self.file_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if isinstance(data, list):
            flattened_data = [self._flatten_data(item, sep=sep) for item in data]
            return pd.DataFrame(flattened_data, **kwargs)
        elif isinstance(data, dict):
            return pd.DataFrame([self._flatten_data(data, sep=sep)], **kwargs)
        else:
            logging.warning(f"Top-level object in '{self.file_path}' is not a list or dict.")
            return pd.DataFrame()

    def _read_excel(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import openpyxl
        except ImportError:
            raise ImportError("Reading Excel files requires openpyxl. Install with: pip install dataframe-loader[excel]")
        return pd.read_excel(self.file_path, **kwargs)

    def _read_arrow_format(self, read_func, format_name, extra_name, **kwargs):
        try:
            import pyarrow
        except ImportError:
            raise ImportError(f"Reading {format_name} files requires pyarrow. Install with: pip install dataframe-loader[{extra_name}]")
        return read_func(self.file_path, **kwargs)

    def _read_parquet(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_parquet, "Parquet", "arrow", **kwargs)

    def _read_orc(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_orc, "ORC", "arrow", **kwargs)

    def _read_feather(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_feather, "Feather", "arrow", **kwargs)

    def _read_avro(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import pyarrow.avro
        except ImportError:
            raise ImportError("Reading Avro files requires pyarrow. Install with: pip install dataframe-loader[arrow]")
        with pyarrow.avro.open_file(self.file_path, 'rb') as reader:
            return reader.read(**kwargs).to_pandas()

    def _read_toml(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import toml
        except ImportError:
            raise ImportError("Reading TOML files requires toml. Install with: pip install dataframe-loader[toml]")
        with self.file_path.open('r', encoding='utf-8') as f:
            data = toml.load(f)
        return pd.json_normalize(data, **kwargs)

    def _read_ndjson(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_json(self.file_path, lines=True, **kwargs)

    def _read_html(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import lxml
        except ImportError:
            raise ImportError("Reading HTML files requires lxml. Install with: pip install dataframe-loader[html]")
        tables = pd.read_html(self.file_path, **kwargs)
        if tables:
            return tables[0]
        else:
            logging.warning(f"No tables found in HTML file: {self.file_path}")
            return pd.DataFrame()

    def _read_stata(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_stata(self.file_path, **kwargs)

    def _read_spss(self, **kwargs: Any) -> pd.DataFrame:
        try:
            return pd.read_spss(self.file_path, **kwargs)
        except ImportError:
            raise ImportError("Reading SPSS files requires pyreadstat. Install with: pip install dataframe-loader[spss]")



class DataFrameHealthChecker:
    """
    A comprehensive class to perform a wide range of data health checks on a pandas DataFrame,
    including validation for specialized data types like emails, URLs, and coordinates.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the DataFrameHealthChecker with a DataFrame.

        :param df: The pandas DataFrame to be checked.
        """
        self.df = df.copy()

    def identify_column_types(self) -> dict:
        """
        Identifies numerical, categorical, and potential datetime columns.

        :return: A dictionary with lists of column names for each identified type.
        """
        numerical_cols = self.df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = self.df.select_dtypes(include=['datetime', 'datetimetz', 'timedelta']).columns.tolist()

        # Refine categorical columns by excluding obviously non-categorical ones
        # (This is a heuristic and may need adjustment)
        for col in numerical_cols + datetime_cols:
            if col in categorical_cols:
                categorical_cols.remove(col)

        return {
            "numerical_columns": numerical_cols,
            "categorical_columns": categorical_cols,
            "datetime_columns": datetime_cols
        }

    def check_date_format(self, column: str, date_format: str = '%Y-%m-%d') -> pd.Series:
        """
        Checks if a string column conforms to a specified date format.

        :param column: The column to check.
        :param date_format: The expected date format string.
        :return: A Series of boolean values indicating if each entry is a valid date.
        """
        return pd.to_datetime(self.df[column], format=date_format, errors='coerce').notna()

    def check_datetime_format(self, column: str, datetime_format: str = '%Y-%m-%d %H:%M:%S') -> pd.Series:
        """
        Checks if a string column conforms to a specified datetime format.

        :param column: The column to check.
        :param datetime_format: The expected datetime format string.
        :return: A Series of boolean values indicating if each entry is a valid datetime.
        """
        return pd.to_datetime(self.df[column], format=datetime_format, errors='coerce').notna()

    def check_time_format(self, column: str, time_format: str = '%H:%M:%S') -> pd.Series:
        """
        Checks if a string column conforms to a specified time format.

        :param column: The column to check.
        :param time_format: The expected time format string.
        :return: A Series of boolean values indicating if each entry is a valid time.
        """
        return pd.to_datetime(self.df[column], format=time_format, errors='coerce').notna()

    def check_latitude_longitude(self, lat_col: str, lon_col: str) -> pd.DataFrame:
        """
        Validates latitude and longitude columns to ensure they are within the valid range.

        :param lat_col: The name of the latitude column.
        :param lon_col: The name of the longitude column.
        :return: A DataFrame containing rows with invalid coordinate values.
        """
        invalid_lat = (self.df[lat_col] < -90) | (self.df[lat_col] > 90)
        invalid_lon = (self.df[lon_col] < -180) | (self.df[lon_col] > 180)
        return self.df[invalid_lat | invalid_lon]

    def check_email_format(self, column: str) -> pd.Series:
        """
        Validates the format of email addresses in a column using a regular expression.

        :param column: The column containing email addresses to validate.
        :return: A Series of boolean values indicating if each email has a valid format.
        """
        email_regex = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        return self.df[column].astype(str).apply(lambda x: bool(email_regex.match(x)))

    def check_website_url_format(self, column: str) -> pd.Series:
        """
        Validates the format of website URLs in a column using a regular expression.

        :param column: The column containing URLs to validate.
        :return: A Series of boolean values indicating if each URL has a valid format.
        """
        url_regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return self.df[column].astype(str).apply(lambda x: bool(url_regex.match(x)))

    def run_all_checks(self) -> dict:
        """
        Runs a comprehensive suite of data health checks.

        :return: A dictionary containing a detailed report of all checks.
        """
        report = {
            "Column Identification": self.identify_column_types(),
            "Basic Checks": {
                "Missing Values": self.df.isnull().sum().to_dict(),
                "Duplicate Rows": self.df.duplicated().sum(),
                "Data Types": self.df.dtypes.apply(str).to_dict(),
                "Summary Statistics": self.df.describe(include='all').to_dict()
            },
            "Format Validation": {}
        }

        # Automatically run format checks on relevant columns
        col_types = self.identify_column_types()
        for col in col_types['categorical_columns']:
            if 'email' in col.lower():
                report['Format Validation'][f'{col} (Email)'] = {
                    'valid_count': self.check_email_format(col).sum(),
                    'invalid_count': (~self.check_email_format(col)).sum()
                }
            if 'url' in col.lower() or 'website' in col.lower():
                 report['Format Validation'][f'{col} (URL)'] = {
                    'valid_count': self.check_website_url_format(col).sum(),
                    'invalid_count': (~self.check_website_url_format(col)).sum()
                }

        return report


class HTMLReportGenerator:
    """
    Generates a well-formatted HTML health report for a pandas DataFrame
    based on a provided health check dictionary.
    """

    def __init__(self, df, report, output_path='data_health_report.html'):
        """
        Initializes the report generator.

        Args:
            df (pd.DataFrame): The DataFrame that was analyzed.
            report (dict): The health check report dictionary.
            output_path (str): The path to save the generated HTML file.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df must be a pandas DataFrame.")
        if not isinstance(report, dict):
            raise TypeError("report must be a dictionary.")

        self.df = df
        self.report = report
        self.output_path = output_path

    def _generate_css(self):
        """Generates the CSS for the HTML report for a clean, modern look."""
        return """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                margin: 0;
                background-color: #f4f7f6;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            h1, h2, h3 {
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }
            h1 { font-size: 2.5em; text-align: center; }
            h2 { font-size: 2em; margin-top: 40px; }
            h3 { font-size: 1.5em; margin-top: 30px; }
            table.dataframe {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                font-size: 0.9em;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border: 1px solid #ddd;
            }
            th {
                background-color: #3498db;
                color: #ffffff;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f2f2f2;
            }
            tr:hover {
                background-color: #ecf0f1;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                background-color: #ecf0f1;
                margin: 5px 0;
                padding: 10px;
                border-left: 5px solid #3498db;
            }
            .section {
                margin-bottom: 40px;
            }
            .summary-table {
                width: 50%;
            }
        </style>
        """

    def _generate_summary_section(self):
        """Generates the HTML for the overall summary and data preview."""
        num_rows, num_cols = self.df.shape
        duplicate_rows = self.report['Basic Checks'].get('Duplicate Rows', 'N/A')

        summary_data = {
            "Metric": ["Total Rows", "Total Columns", "Duplicate Rows"],
            "Value": [num_rows, num_cols, duplicate_rows]
        }
        summary_df = pd.DataFrame(summary_data)

        html = "<div class='section'><h2>Overall Summary</h2>"
        html += summary_df.to_html(classes=['dataframe', 'summary-table'], index=False)
        html += "<h3>Data Preview (First 5 Rows)</h3>"
        html += self.df.head().to_html(classes='dataframe', index=False)
        html += "<h3>Data Preview (Last 5 Rows)</h3>"
        html += self.df.tail().to_html(classes='dataframe', index=False)
        html += "</div>"
        return html

    def _generate_column_details_section(self):
        """Generates a detailed table for all columns."""
        num_rows = len(self.df)
        col_data = []

        for col in self.df.columns:
            stats = self.report['Basic Checks']['Summary Statistics'].get(col, {})
            missing = self.report['Basic Checks']['Missing Values'].get(col, 0)
            
            col_info = {
                "Column Name": col,
                "Data Type": self.report['Basic Checks']['Data Types'].get(col, 'N/A'),
                "Missing Values": missing,
                "Missing (%)": f"{(missing / num_rows * 100):.2f}%",
                "Unique Values": stats.get('unique', 'N/A'),
                "Mean / Top": stats.get('mean', stats.get('top', 'N/A')),
                "Std Dev / Freq": stats.get('std', stats.get('freq', 'N/A'))
            }
            col_data.append(col_info)

        details_df = pd.DataFrame(col_data)
        # Clean up display for non-numeric columns
        details_df['Mean / Top'] = details_df['Mean / Top'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and not np.isnan(x) else x)
        details_df['Std Dev / Freq'] = details_df['Std Dev / Freq'].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) and not np.isnan(x) else x)


        html = "<div class='section'><h2>Column-wise Details</h2>"
        html += details_df.to_html(classes='dataframe', index=False)
        html += "</div>"
        return html

    def _generate_validation_section(self):
        """Generates HTML for the format validation checks."""
        validation_report = self.report.get('Format Validation')
        if not validation_report:
            return ""

        validation_df = pd.DataFrame.from_dict(validation_report, orient='index').reset_index()
        validation_df.columns = ["Check", "Valid Count", "Invalid Count"]

        html = "<div class='section'><h2>Format Validation</h2>"
        html += validation_df.to_html(classes='dataframe', index=False)
        html += "</div>"
        return html
        
    def _generate_column_id_section(self):
        """Generates HTML for the identified column types."""
        id_report = self.report.get('Column Identification')
        if not id_report:
            return ""
            
        html = "<div class='section'><h2>Identified Column Types</h2><ul>"
        for col_type, columns in id_report.items():
            title = col_type.replace('_', ' ').title()
            if columns:
                html += f"<li><strong>{title}:</strong> {', '.join(columns)}</li>"
            else:
                html += f"<li><strong>{title}:</strong> None</li>"
        html += "</ul></div>"
        return html

    def generate_report(self, open_in_browser=True):
        """
        Builds the complete HTML report and saves it to a file.
        
        Args:
            open_in_browser (bool): If True, automatically opens the report in a web browser.
        """
        print("Generating HTML report...")

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Data Health Report</title>
            {self._generate_css()}
        </head>
        <body>
            <div class="container">
                <h1>Data Health Report</h1>
                {self._generate_summary_section()}
                {self._generate_column_details_section()}
                {self._generate_validation_section()}
                {self._generate_column_id_section()}
            </div>
        </body>
        </html>
        """

        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Successfully generated report: {self.output_path}")

            if open_in_browser:
                webbrowser.open('file://' + os.path.realpath(self.output_path))

        except IOError as e:
            print(f"Error writing to file: {e}")