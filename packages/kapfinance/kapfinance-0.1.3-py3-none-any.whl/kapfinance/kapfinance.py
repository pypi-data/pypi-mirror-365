import numpy as np
import pandas as pd
import os
import logging
# import matplotlib.pyplot as plt # Matplotlib is for example usage, not strictly required by the class itself

# Set logging level to INFO for cleaner outputs.
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class FinancialDataManager:
    """
    Reads and processes financial .xls (HTML content) files in the specified
    root folder and its subfolders, managing financial account data on a
    ticker-by-ticker basis. Data loading is performed on demand (lazy loading).
    """

    def __init__(self, folder_path: str):
        """
        Initializes a FinancialDataManager instance.
        At this stage, only the file map is built; data is not loaded.
        """
        self.folder_path = folder_path
        # Stores loaded ticker data: { 'TICKER': [((description, value_str), period), ...], ... }
        self.bilanco_data = {}
        # Map of tickers and periods in the file system
        self._file_map = self._build_file_map()

    def _build_file_map(self) -> dict:
        """
        Scans the entire folder structure and creates a map of file paths
        for each ticker-period. This map quickly determines which file to load
        for the `download` operation.
        """
        file_map = {}
        if not os.path.isdir(self.folder_path):
            logging.error(f"Error: Folder '{self.folder_path}' not found or inaccessible.")
            return file_map

        logging.info(f"Indexing files in '{self.folder_path}'...")

        for root, _, files in os.walk(self.folder_path):
            # Extract period information from the folder name
            period_parts = os.path.basename(root).split('_')
            # Assuming period format is YYYY_QQ, like '2020_01'
            period = f"{period_parts[-2]}_{period_parts[-1]}" if len(period_parts) >= 3 and period_parts[-2].isdigit() and period_parts[-1].isdigit() else None
            
            if not period:
                continue

            for filename in files:
                if filename.endswith('.xls') and len(filename) >= 5: # Ensure it's an XLS and ticker length is at least 5
                    ticker = filename[:5].upper() # Extract first 5 chars as ticker, uppercase
                    file_path = os.path.join(root, filename)
                    
                    file_map.setdefault(ticker, {}).setdefault(period, []).append(file_path)
        
        logging.info(f"File map created for a total of {len(file_map)} different tickers.")
        return file_map

    def _process_html_to_records(self, file_path: str) -> list | None:
        """
        Reads an HTML-content .xls file, extracts necessary columns, and returns
        a list of (description, value) pairs.
        """
        try:
            tables = pd.read_html(file_path, encoding='utf-8')
            # Generally, the second table is the target for financial data
            df_data = tables[1] if len(tables) > 1 else tables[0]

            results = []
            # Assuming Column 1 is the account description, Column 3 is the value.
            descriptions = df_data.iloc[:, 1].values
            values = df_data.iloc[:, 3].values
            
            length = min(len(descriptions), len(values))
            for i in range(length):
                val1 = descriptions[i]
                val2 = values[i]
                if not (pd.isna(val1) or pd.isna(val2)):
                    results.append((str(val1).strip(), str(val2).strip()))
            return results
        except Exception as e:
            logging.warning(f"Error processing file '{file_path}': {e}")
            return None

    def raw_data(self, ticker: str):
        """
        Reads all financial data for a specific ticker from disk and loads it
        into memory. If data is already loaded, it does not re-process.
        """
        ticker_upper = ticker.upper()
        if ticker_upper in self.bilanco_data:
            logging.info(f"Data for '{ticker_upper}' is already loaded.")
            return

        if ticker_upper not in self._file_map:
            logging.warning(f"No files found for '{ticker_upper}'. Please check the ticker code and folder structure.")
            return

        logging.info(f"Downloading and processing data for '{ticker_upper}'...")
        
        self.bilanco_data[ticker_upper] = []
        ticker_files_by_period = self._file_map[ticker_upper]
        
        processed_file_count = 0
        for period, file_paths in ticker_files_by_period.items():
            for file_path in file_paths:
                matched_pairs = self._process_html_to_records(file_path)
                if matched_pairs:
                    self.bilanco_data[ticker_upper].extend([((v1, v2), period) for (v1, v2) in matched_pairs])
                    processed_file_count += 1
        
        if processed_file_count == 0:
            logging.warning(f"No files were successfully processed for '{ticker_upper}'.")
            del self.bilanco_data[ticker_upper] # Delete ticker if no data was loaded
        else:
            logging.info(f"{processed_file_count} files processed and {len(self.bilanco_data[ticker_upper])} data points loaded for '{ticker_upper}'.")

    def list_available_tickers(self) -> list:
        """
        Lists all available ticker codes found in the file system.
        This comes from the file map, not from loaded data.
        """
        return list(self._file_map.keys())

    def download(self, ticker: str, start: str = None, end: str = None) -> pd.DataFrame | None:
        """
        Returns a time-series DataFrame of (account description, value) for a
        specific ticker.
        Rows: Account Descriptions, Columns: Periods.
        If data has not yet been loaded, it will be downloaded automatically.
        Optionally, you can filter the dataset by specifying start and end
        periods (in YYYY_QQ format).
        
        Parameters:
        -----------
        ticker : str
            The ticker code of the company for which to retrieve financial data (e.g., 'AKBNK')
        start : str, optional
            Start period for filtering (in YYYY_QQ format, e.g., '2020_01')
        end : str, optional
            End period for filtering (in YYYY_QQ format, e.g., '2022_04')
            
        Returns:
        -----------
        pd.DataFrame | None
            DataFrame containing the filtered financial data, or None if no data is found.
        """
        ticker_upper = ticker.upper()
        if ticker_upper not in self.bilanco_data:
            self.raw_data(ticker_upper) # Download data if not present

        raw_data = self.bilanco_data.get(ticker_upper)
        if not raw_data:
            logging.warning(f"No description-based time series data found for '{ticker_upper}'.")
            return None

        # Apply period filtering
        filtered_data = []
        for ((description, value_str), period) in raw_data:
            if start and period < start:
                continue
            if end and period > end:
                continue
            filtered_data.append(((description, value_str), period))

        if not filtered_data:
            logging.warning(f"No data found for '{ticker_upper}' within the specified period range.")
            return None

        # Keep track of the first occurrence order of account descriptions
        ordered_descriptions = []
        seen_descriptions = set()

        records = []
        for ((description, value_str), period) in filtered_data:
            if description not in seen_descriptions:
                ordered_descriptions.append(description)
                seen_descriptions.add(description)
            try:
                # Convert string values to float, handling Turkish decimal separators
                val = float(value_str.replace('.', '').replace(',', '.'))
            except ValueError:
                val = np.nan # Use NaN for non-numeric values

            records.append((description, period, val))

        if not records:
            logging.warning(f"No convertible data found for '{ticker_upper}'.")
            return None

        df = pd.DataFrame(records, columns=['Description', 'Period', 'Value'])
        wide_df = df.pivot_table(index='Description', columns='Period', values='Value', aggfunc='first')

        # Sort columns (Periods) chronologically
        if not wide_df.empty:
            sorted_columns = sorted(wide_df.columns, 
                                    key=lambda p: tuple(map(int, p.split('_'))) if isinstance(p, str) and '_' in p else (0,0))
            wide_df = wide_df[sorted_columns]

        # Reindex the DataFrame according to the first occurrence order of accounts in raw data.
        df_ordered = wide_df.reindex(ordered_descriptions)

        return df_ordered

# The example usage block below should ideally be in a separate `example.py` or `main.py`
# file, not directly in the library file being packaged for PyPI.
# This ensures that when someone installs your library, importing it doesn't
# automatically run example code.
"""
# --- Kullanım Örneği ---
if __name__ == "__main__":
    # 1. Finansal tablolarınızın kök klasör yolunu tanımlayın
    # Lütfen burayı kendi dosya yolunuzla değiştirin!
    data_path = "C:/Users/mertk/Downloads/FinancialTable/" 

    # Veri yöneticisini başlatın (bu aşamada veri yüklenmez)
    kapfinance = FinancialDataManager(data_path)

    # Example 1: List all available tickers
    print(f"Available tickers: {kapfinance.list_available_tickers()}")

    # Example 2: Download and display data for a specific ticker
    akbnk_df = kapfinance.download('AKBNK')
    if akbnk_df is not None:
        print("\nAKBNK Financial Data (Full):")
        print(akbnk_df.head()) # Display the first few rows

    # Example 3: Download and display data for a specific ticker and period range
    garan_df_filtered = kapfinance.download('GARAN', start='2020_01', end='2022_04')
    if garan_df_filtered is not None:
        print("\nGARAN Financial Data (2020_01 - 2022_04):")
        print(garan_df_filtered.head()) # Display the first few rows

    # Example 4: Try to download data for a non-existent ticker
    non_existent_ticker_df = kapfinance.download('XYZ_T')
    if non_existent_ticker_df is None:
        print("\nAttempted to download data for 'XYZ_T'. As expected, no data found.")

    # You can now work with the pandas DataFrames for analysis, visualization, etc.
    # For instance, to plot 'Net Dönem Kar/Zararı' for AKBNK:
    # if akbnk_df is not None and 'Net Dönem Kar/Zararı' in akbnk_df.index:
    #     plt.figure(figsize=(10, 6))
    #     akbnk_df.loc['Net Dönem Kar/Zararı'].dropna().astype(float).plot(kind='bar')
    #     plt.title('AKBNK Net Dönem Kar/Zararı (Turkish: Net Period Profit/Loss)')
    #     plt.xlabel('Period')
    #     plt.ylabel('Amount')
    #     plt.xticks(rotation=45)
    #     plt.tight_layout()
    #     plt.show()
"""