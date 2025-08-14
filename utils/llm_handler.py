import google.generativeai as genai
import pandas as pd
import json
import re
from datetime import datetime
import os
from typing import Dict, Any, Optional

class LLMHandler:
    """Advanced LLM handler with intelligent query processing"""
    
    def __init__(self):
        self.configure_gemini()
        self.query_patterns = self.load_query_patterns()
        self.context_memory = []
    
    def configure_gemini(self):
        """Configure Gemini AI with optimal settings"""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_output_tokens": 4096,
        }
        
        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )
    
    def load_query_patterns(self):
        """Load predefined query patterns for better recognition"""
        return {
            'count': r'\b(how many|count|number of|total)\b',
            'average': r'\b(average|mean|avg)\b',
            'max': r'\b(maximum|max|highest|largest)\b',
            'min': r'\b(minimum|min|lowest|smallest)\b',
            'sum': r'\b(sum|total|aggregate)\b',
            'distribution': r'\b(distribution|spread|range)\b',
            'correlation': r'\b(correlation|relationship|related|associated)\b',
            'filter': r'\b(where|filter|show me|find)\b',
            'group': r'\b(group by|grouped|category|categories)\b',
            'trend': r'\b(trend|over time|timeline|change)\b'
        }
    
    def process_natural_language_query(self, query: str, processed_data: list, db_manager) -> Dict[str, Any]:
        """Process natural language query with intelligent understanding"""
        
        # Analyze query type
        query_type = self.classify_query(query)
        
        # Get relevant data context
        data_context = self.build_data_context(processed_data)
        
        # Generate SQL query
        sql_query = self.generate_sql_query(query, data_context, query_type)
        
        # Execute query
        try:
            results = db_manager.execute_query(sql_query)
            
            # Generate natural language response
            response = self.generate_response(query, results, query_type, sql_query)
            
            return {
                "response": response,
                "data": results,
                "type": query_type,
                "sql_query": sql_query,
                "suggest_visualization": self.should_visualize(query_type, results)
            }
            
        except Exception as e:
            # Fallback to general analysis
            return self.handle_query_error(query, str(e), processed_data)
    
    def classify_query(self, query: str) -> str:
        """Classify query type using pattern matching"""
        query_lower = query.lower()
        
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, query_lower):
                return query_type
        
        return "general"
    
    def build_data_context(self, processed_data: list) -> str:
        """Build comprehensive data context for LLM"""
        context_parts = []
        
        for data in processed_data:
            df = data['dataframe']
            table_name = data['table']
            
            # Basic info
            info = f"""
Table: {table_name}
Rows: {len(df)}
Columns: {len(df.columns)}
Column Details:
"""
            
            # Column information
            for col in df.columns:
                dtype = df[col].dtype
                null_count = df[col].isnull().sum()
                unique_count = df[col].nunique()
                
                col_info = f"  - {col} ({dtype}): {unique_count} unique values, {null_count} null values"
                
                # Add sample values for categorical columns
                if dtype == 'object' and unique_count <= 10:
                    unique_values = df[col].dropna().unique()[:5]
                    col_info += f", examples: {list(unique_values)}"
                
                info += col_info + "\n"
            
            context_parts.append(info)
        
        return "\n\n".join(context_parts)
    
    def generate_sql_query(self, query: str, data_context: str, query_type: str) -> str:
        """Generate SQL query using LLM with context"""
        
        prompt = f"""
You are an expert SQL query generator for health data analysis. 

Data Context:
{data_context}

User Query: "{query}"
Query Type: {query_type}

Generate a single, syntactically correct SQLite query that answers the user's question.

Rules:
1. Return ONLY the SQL query, no explanations or formatting
2. Use proper SQLite syntax
3. Handle potential NULL values appropriately
4. For aggregations, use appropriate GROUP BY clauses
5. Use LIMIT for large result sets when appropriate
6. Table names are exact as shown in the context

SQL Query:
"""
        
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean the response
            sql_query = self.clean_sql_query(sql_query)
            
            return sql_query
            
        except Exception as e:
            raise Exception(f"Failed to generate SQL query: {str(e)}")
    
    def clean_sql_query(self, query: str) -> str:
        """Clean and validate SQL query"""
        # Remove markdown formatting
        query = re.sub(r'```
        query = re.sub(r'```\s*', '', query)
        
        # Remove trailing semicolons
        query = query.rstrip(';').strip()
        
        # Basic SQL injection protection
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper and not query_upper.startswith('SELECT'):
                raise ValueError(f"Dangerous SQL operation detected: {keyword}")
        
        return query
    
    def generate_response(self, original_query: str, results: pd.DataFrame, query_type: str, sql_query: str) -> str:
        """Generate natural language response"""
        
        if results is None or len(results) == 0:
            return "I couldn't find any data that matches your query. Please try rephrasing your question or check if the data exists."
        
        # Build response based on query type and results
        response_prompt = f"""
Generate a clear, professional response to the user's health data query.

Original Question: "{original_query}"
Query Type: {query_type}
Results Summary: {len(results)} rows, {len(results.columns)} columns

Key Statistics:
{self.get_result_summary(results)}

Provide a comprehensive but concise answer that:
1. Directly addresses the user's question
2. Highlights key findings from the data
3. Provides context and insights where relevant
4. Uses appropriate medical/health terminology
5. Suggests follow-up questions if appropriate

Response:
"""
        
        try:
            response = self.model.generate_content(response_prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Based on your query, I found {len(results)} records. Here's what the data shows:\n\n{self.get_simple_summary(results)}"
    
    def get_result_summary(self, df: pd.DataFrame) -> str:
        """Generate statistical summary of results"""
        summary_parts = []
        
        # Numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            for col in numeric_cols[:3]:  # Limit to first 3
                stats = df[col].describe()
                summary_parts.append(f"{col}: mean={stats['mean']:.2f}, median={stats['50%']:.2f}")
        
        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:  # Limit to first 2
                value_counts = df[col].value_counts()
                top_value = value_counts.index[0] if len(value_counts) > 0 else 'N/A'
                summary_parts.append(f"{col}: most common = {top_value}")
        
        return "; ".join(summary_parts)
    
    def get_simple_summary(self, df: pd.DataFrame) -> str:
        """Generate simple summary for fallback"""
        if len(df) == 1 and len(df.columns) == 1:
            return f"The answer is: {df.iloc[0, 0]}"
        
        summary = f"Found {len(df)} records"
        if len(df.columns) == 1:
            col_name = df.columns[0]
            if df[col_name].dtype in ['int64', 'float64']:
                summary += f" with an average {col_name} of {df[col_name].mean():.2f}"
        
        return summary
    
    def should_visualize(self, query_type: str, results: pd.DataFrame) -> bool:
        """Determine if results should include visualization"""
        if results is None or len(results) == 0:
            return False
        
        viz_types = ['distribution', 'correlation', 'trend', 'group']
        return query_type in viz_types and len(results) > 1
    
    def handle_query_error(self, query: str, error: str, processed_data: list) -> Dict[str, Any]:
        """Handle query errors gracefully"""
        
        # Try to provide helpful response based on available data
        if processed_data:
            sample_data = processed_data[0]['dataframe'].head(3)
            
            response = f"""
I encountered an issue processing your query: "{query}"

Error: {error}

Here's a sample of your data to help you rephrase your question:

{sample_data.to_string()}

You can try asking:
- "How many records are there?"
- "What are the column names?"
- "Show me basic statistics"
"""
        else:
            response = f"I couldn't process your query due to an error: {error}"
        
        return {
            "response": response,
            "data": None,
            "type": "error",
            "sql_query": None,
            "suggest_visualization": False
        }
