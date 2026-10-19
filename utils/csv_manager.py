import pandas as pd
import os

DEFAULT_COLUMNS = ['Item Name', 'Sector', 'Quantity', 'Log Date', 'Status', 'Notes']

# Exact header mapping based on your waste CSV datasets
EXACT_HEADER_MAP = {
    'food_type': 'Item Name',
    'source_type': 'Sector',
    'quantity_kg': 'Quantity',
    'date_added': 'Log Date',
    'status': 'Status',
    'location': 'Notes'
}


class BaseCSVManager:
    """Base manager handling CSV loading, column normalization, and analytics."""
    def __init__(self, file_path):
        self.file_path = file_path

    def read_data(self):
        """Reads CSV data into a DataFrame and maps CSV columns to UI expectations."""
        if not os.path.exists(self.file_path):
            return pd.DataFrame(columns=DEFAULT_COLUMNS)
        try:
            df = pd.read_csv(self.file_path)

            # 1. Map lowercase/cleaned CSV column headers to template standards
            rename_dict = {}
            for col in df.columns:
                c_clean = str(col).strip().lower()
                if c_clean in EXACT_HEADER_MAP:
                    rename_dict[col] = EXACT_HEADER_MAP[c_clean]

            df = df.rename(columns=rename_dict)

            # 2. Normalize Status column capitalization (e.g., 'available' -> 'Available')
            if 'Status' in df.columns:
                df['Status'] = df['Status'].astype(str).str.strip().str.title()

            # 3. Ensure required template columns exist
            for col in DEFAULT_COLUMNS:
                if col not in df.columns:
                    df[col] = ''

            return df
        except Exception:
            return pd.DataFrame(columns=DEFAULT_COLUMNS)

    def save_data(self, df):
        """Saves a Pandas DataFrame back to CSV."""
        df.to_csv(self.file_path, index=False)

    def get_summary_statistics(self):
        """Calculates summary stats expected by app.py for dashboard aggregation."""
        df = self.read_data()

        status_counts = {}
        if not df.empty and 'Status' in df.columns:
            status_counts = df['Status'].value_counts().to_dict()

        if df.empty:
            return {
                'total_records': 0,
                'total_items': 0,
                'total_quantity': 0.0,
                'available_items': 0,
                'claimed_items': 0,
                'co2_saved': 0.0,
                'status_counts': status_counts
            }

        quantity_series = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        total_qty = float(quantity_series.sum())

        return {
            'total_records': len(df),
            'total_items': len(df),
            'total_quantity': round(total_qty, 2),
            'available_items': int((df['Status'] == 'Available').sum()),
            'claimed_items': int((df['Status'].isin(['Booked', 'Claimed', 'Donated'])).sum()),
            'co2_saved': round(total_qty * 2.5, 2),
            'status_counts': status_counts
        }


class CanteenManager(BaseCSVManager):
    def __init__(self):
        super().__init__('data/canteen_waste.csv')


class RestaurantManager(BaseCSVManager):
    def __init__(self):
        super().__init__('data/restaurant_waste.csv')


class SupermarketManager(BaseCSVManager):
    def __init__(self):
        super().__init__('data/supermarket_waste.csv')


class EventManager(BaseCSVManager):
    def __init__(self):
        super().__init__('data/event_waste.csv')