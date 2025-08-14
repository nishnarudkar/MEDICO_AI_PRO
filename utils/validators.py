import pandas as pd
import streamlit as st
from pathlib import Path

def validate_csv_file(file):
    """Validate uploaded CSV file"""
    
    try:
        # Check file size (max 200MB)
        if hasattr(file, 'size') and file.size > 200 * 1024 * 1024:
            st.error(f"File {file.name} is too large. Maximum size is 200MB.")
            return False
        
        # Check file extension
        file_extension = Path(file.name).suffix.lower()
        if file_extension not in ['.csv', '.xlsx', '.json']:
            st.error(f"Unsupported file type: {file_extension}")
            return False
        
        # Try to read a sample of the file
        if file_extension == '.csv':
            # Read first few rows to validate
            sample_df = pd.read_csv(file, nrows=5)
            
            # Reset file pointer
            file.seek(0)
            
            # Check if DataFrame is empty
            if sample_df.empty:
                st.error(f"File {file.name} appears to be empty.")
                return False
            
            # Check minimum columns
            if len(sample_df.columns) < 1:
                st.error(f"File {file.name} must have at least 1 column.")
                return False
            
        return True
        
    except Exception as e:
        st.error(f"Error validating file {file.name}: {str(e)}")
        return False

def validate_query(query):
    """Validate user query input"""
    
    if not query or len(query.strip()) == 0:
        return False, "Query cannot be empty"
    
    if len(query) > 2000:
        return False, "Query is too long (max 2000 characters)"
    
    # Check for potentially dangerous SQL keywords
    dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 'TRUNCATE']
    query_upper = query.upper()
    
    for keyword in dangerous_keywords:
        if keyword in query_upper:
            return False, f"Query contains restricted keyword: {keyword}"
    
    return True, "Valid query"

def validate_database_connection(db_path):
    """Validate database connection"""
    
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        return True, "Database connection successful"
        
    except Exception as e:
        return False, f"Database connection failed: {str(e)}"
