import pandas as pd
import numpy as np
from datetime import datetime
import re

class DataProcessor:
    """Advanced data processing utilities"""
    
    def __init__(self):
        self.processing_log = []
    
    def clean_and_process(self, df, filename):
        """Clean and process DataFrame with comprehensive operations"""
        
        processed_df = df.copy()
        self.processing_log = []
        
        # Log original state
        self.log_operation(f"Original data: {len(df)} rows, {len(df.columns)} columns")
        
        # 1. Clean column names
        processed_df = self.clean_column_names(processed_df)
        
        # 2. Handle missing values
        processed_df = self.handle_missing_values(processed_df)
        
        # 3. Detect and convert data types
        processed_df = self.detect_and_convert_types(processed_df)
        
        # 4. Remove duplicates
        processed_df = self.remove_duplicates(processed_df)
        
        # 5. Handle outliers (optional)
        processed_df = self.handle_outliers(processed_df)
        
        # Log final state
        self.log_operation(f"Processed data: {len(processed_df)} rows, {len(processed_df.columns)} columns")
        
        return processed_df
    
    def clean_column_names(self, df):
        """Clean and standardize column names"""
        original_columns = df.columns.tolist()
        
        # Clean column names
        new_columns = []
        for col in df.columns:
            # Remove special characters and extra spaces
            clean_col = re.sub(r'[^\w\s]', '', str(col))
            clean_col = re.sub(r'\s+', '_', clean_col.strip())
            
            # Convert to title case
            clean_col = clean_col.title()
            
            new_columns.append(clean_col)
        
        df.columns = new_columns
        
        # Log changes
        changes = [f"{orig} -> {new}" for orig, new in zip(original_columns, new_columns) if orig != new]
        if changes:
            self.log_operation(f"Cleaned column names: {len(changes)} columns renamed")
        
        return df
    
    def handle_missing_values(self, df):
        """Handle missing values intelligently"""
        
        missing_before = df.isnull().sum().sum()
        
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / len(df)) * 100
            
            if missing_count == 0:
                continue
            
            if missing_percentage > 50:
                # Drop columns with >50% missing values
                df = df.drop(columns=[column])
                self.log_operation(f"Dropped column '{column}' ({missing_percentage:.1f}% missing)")
                continue
            
            # Handle based on data type
            if df[column].dtype in ['int64', 'float64']:
                # For numeric: fill with median
                median_val = df[column].median()
                df[column].fillna(median_val, inplace=True)
                self.log_operation(f"Filled numeric column '{column}' with median: {median_val}")
                
            else:
                # For categorical: fill with mode
                mode_val = df[column].mode()
                if len(mode_val) > 0:
                    df[column].fillna(mode_val[0], inplace=True)
                    self.log_operation(f"Filled categorical column '{column}' with mode: {mode_val[0]}")
                else:
                    df[column].fillna('Unknown', inplace=True)
                    self.log_operation(f"Filled column '{column}' with 'Unknown'")
        
        missing_after = df.isnull().sum().sum()
        self.log_operation(f"Missing values reduced from {missing_before} to {missing_after}")
        
        return df
    
    def detect_and_convert_types(self, df):
        """Detect and convert appropriate data types"""
        
        for column in df.columns:
            # Skip if already numeric
            if df[column].dtype in ['int64', 'float64']:
                continue
            
            # Try to convert to numeric
            numeric_df = pd.to_numeric(df[column], errors='coerce')
            numeric_nulls = numeric_df.isnull().sum()
            original_nulls = df[column].isnull().sum()
            
            # If conversion doesn't create too many new nulls, convert to numeric
            if (numeric_nulls - original_nulls) / len(df) < 0.1:
                df[column] = numeric_df
                self.log_operation(f"Converted '{column}' to numeric")
                continue
            
            # Try to convert to datetime
            try:
                if df[column].dtype == 'object':
                    # Check if it looks like a date
                    sample_values = df[column].dropna().head(10)
                    date_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{2}/\d{2}/\d{4}', r'\d{2}-\d{2}-\d{4}']
                    
                    for pattern in date_patterns:
                        if sample_values.astype(str).str.match(pattern).any():
                            df[column] = pd.to_datetime(df[column], errors='coerce')
                            self.log_operation(f"Converted '{column}' to datetime")
                            break
            except:
                pass
        
        return df
    
    def remove_duplicates(self, df):
        """Remove duplicate rows"""
        
        initial_rows = len(df)
        df_deduplicated = df.drop_duplicates()
        final_rows = len(df_deduplicated)
        
        duplicates_removed = initial_rows - final_rows
        if duplicates_removed > 0:
            self.log_operation(f"Removed {duplicates_removed} duplicate rows")
        
        return df_deduplicated
    
    def handle_outliers(self, df, method='iqr', action='cap'):
        """Handle outliers in numeric columns"""
        
        numeric_columns = df.select_dtypes(include=['number']).columns
        
        for column in numeric_columns:
            if method == 'iqr':
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
                
                if len(outliers) > 0:
                    if action == 'cap':
                        df[column] = df[column].clip(lower_bound, upper_bound)
                        self.log_operation(f"Capped {len(outliers)} outliers in '{column}'")
                    elif action == 'remove':
                        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
                        self.log_operation(f"Removed {len(outliers)} outlier rows based on '{column}'")
        
        return df
    
    def get_basic_stats(self, df):
        """Get basic statistics about the dataframe"""
        
        stats = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'numeric_columns': len(df.select_dtypes(include=['number']).columns),
            'categorical_columns': len(df.select_dtypes(include=['object']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime']).columns),
            'missing_values': df.isnull().sum().sum(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum()
        }
        
        return stats
    
    def get_processing_log(self):
        """Get the processing log"""
        return self.processing_log
    
    def log_operation(self, operation):
        """Log a processing operation"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.processing_log.append(f"[{timestamp}] {operation}")
    
    def generate_data_summary(self, df, filename):
        """Generate comprehensive data summary"""
        
        summary = {
            'filename': filename,
            'shape': df.shape,
            'columns': df.columns.tolist(),
            'dtypes': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'basic_stats': self.get_basic_stats(df),
            'processing_log': self.processing_log
        }
        
        # Add numeric summaries
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            summary['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Add categorical summaries
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            summary['categorical_summary'] = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts().head(10)
                summary['categorical_summary'][col] = value_counts.to_dict()
        
        return summary
