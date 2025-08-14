import os
from pathlib import Path

# Application Configuration
APP_CONFIG = {
    "name": "MedicoAI Pro",
    "tagline": "Advanced Medical Data Intelligence Platform",
    "version": "2.0.0",
    "description": "AI-Powered Health Analytics & Insights",
    "logo": "🩺🤖",
    "colors": {
        "primary": "#2E86AB",      # Medical blue
        "secondary": "#A23B72",    # Healthcare accent
        "success": "#F18F01",      # Vital orange
        "background": "#F8F9FA"    # Clean white
    },
    "author": "Your Company",
    "contact": "support@medicoai.pro",
    "website": "https://medicoai.pro",
    "github": "https://github.com/yourusername/medicoai-pro"
}


# Paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
COMPONENTS_DIR = BASE_DIR / "components"
UTILS_DIR = BASE_DIR / "utils"

# Database Configuration
DATABASE_CONFIG = {
    "path": "healthgenai_pro.db",
    "backup_interval": 3600,  # seconds
    "max_query_history": 10000
}

# AI Model Configuration
GEMINI_CONFIG = {
    "model_name": "gemini-1.5-pro",
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 4096,
    "safety_settings": [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]
}

# File Upload Configuration
UPLOAD_CONFIG = {
    "max_file_size": 200 * 1024 * 1024,  # 200MB
    "allowed_extensions": [".csv", ".xlsx", ".json"],
    "max_files": 10
}

# UI Configuration
UI_CONFIG = {
    "theme": "light",
    "primary_color": "#1f77b4",
    "secondary_color": "#ff7f0e",
    "chart_height": 400,
    "table_height": 300
}

# Security Configuration
SECURITY_CONFIG = {
    "enable_sql_injection_protection": True,
    "max_query_length": 2000,
    "allowed_sql_keywords": ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", "LIMIT"],
    "blocked_sql_keywords": ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    "cache_ttl": 300,  # seconds
    "max_cache_size": 100,  # number of cached items
    "query_timeout": 30,  # seconds
    "chunk_size": 1000  # rows for large datasets
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "healthgenai_pro.log",
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# Environment Variables
def get_env_var(name: str, default=None):
    """Get environment variable with default fallback"""
    return os.getenv(name, default)

# Required Environment Variables
REQUIRED_ENV_VARS = {
    "GOOGLE_API_KEY": "Your Google Gemini API key"
}

# Validate Environment Variables
def validate_environment():
    """Validate that all required environment variables are set"""
    missing_vars = []
    
    for var_name, description in REQUIRED_ENV_VARS.items():
        if not get_env_var(var_name):
            missing_vars.append(f"{var_name}: {description}")
    
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables:\n" + 
            "\n".join(f"- {var}" for var in missing_vars)
        )
    
    return True
