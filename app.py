import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import io
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Import custom components
from components.sidebar import render_sidebar
from components.chat import render_chat_interface
from components.charts import render_data_visualizations
from components.analytics import render_advanced_analytics as render_analytics
from utils.database import DatabaseManager
from utils.llm_handler import LLMHandler
from utils.data_processor import DataProcessor
from utils.validators import validate_csv_file
from config import APP_CONFIG

# Page configuration
st.set_page_config(
    page_title="MedicoAI Pro 🩺",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load custom CSS
def load_css():
    css_file = Path("assets/styles.css")
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables"""
    default_states = {
        "messages": [],
        "uploaded_files": None,
        "current_file": None,
        "data_summary": None,
        "query_history": [],
        "user_preferences": {},
        "analytics_cache": {},
        "database_connected": False
    }

    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

# Main application
def main():
    load_css()
    initialize_session_state()

    # Header with branding
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"""
        <div class="main-header">
            <h1>{APP_CONFIG['logo']} {APP_CONFIG['name']}</h1>
            <p class="subtitle">{APP_CONFIG['tagline']}</p>
            <p class="version">v{APP_CONFIG['version']} - {APP_CONFIG['description']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        uploaded_files, selected_options = render_sidebar()

    # Initialize managers
    db_manager = DatabaseManager()
    # Pass the selected model to the LLMHandler
    llm_handler = LLMHandler(model_name=selected_options.get('model_choice', 'Gemini Pro'))
    data_processor = DataProcessor()


    # Main content area
    if uploaded_files:
        # File processing
        processed_data = handle_file_upload(uploaded_files, db_manager, data_processor)

        if processed_data:
            # Create tabs for different features
            tab1, tab2, tab3, tab4 = st.tabs([
                "💬 AI Chat", "📊 Visualizations", "📈 Analytics", "⚙️ Settings"
            ])

            with tab1:
                render_chat_interface(processed_data, llm_handler, db_manager)

            with tab2:
                render_data_visualizations(processed_data)

            with tab3:
                render_analytics(processed_data)

            with tab4:
                render_settings_panel()
    else:
        render_welcome_screen()

def handle_file_upload(uploaded_files, db_manager, data_processor):
    """Process uploaded files and return processed data"""
    try:
        processed_files = []

        for file in uploaded_files:
            # Validate file
            if validate_csv_file(file):
                # Process file
                df = pd.read_csv(file)
                processed_df = data_processor.clean_and_process(df, file.name)

                # Store in database
                table_name = f"data_{file.name.split('.')[0].lower()}"
                db_manager.store_dataframe(processed_df, table_name)

                processed_files.append({
                    'name': file.name,
                    'table': table_name,
                    'dataframe': processed_df,
                    'stats': data_processor.get_basic_stats(processed_df)
                })

        st.session_state.processed_files = processed_files
        return processed_files

    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return None

def render_welcome_screen():
    """Render welcome screen with features and demo"""
    st.markdown("""
    <div class="welcome-container">
        <div class="feature-grid">
            <div class="feature-card">
                <h3>🤖 AI-Powered Analysis</h3>
                <p>Ask questions in natural language and get intelligent responses</p>
            </div>
            <div class="feature-card">
                <h3>📊 Interactive Visualizations</h3>
                <p>Dynamic charts and graphs for data exploration</p>
            </div>
            <div class="feature-card">
                <h3>📈 Advanced Analytics</h3>
                <p>Statistical analysis and predictive modeling</p>
            </div>
            <div class="feature-card">
                <h3>🔒 Secure & Private</h3>
                <p>Your health data stays protected and private</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Demo section
    with st.expander("🎯 Try the Demo", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Load Sample Dataset", type="primary"):
                load_sample_data()
        with col2:
            st.info("Upload your CSV files to get started with real data analysis")

def render_settings_panel():
    """Render application settings"""
    st.subheader("⚙️ Application Settings")
    st.info("Settings panel is under construction.")

def load_sample_data():
    """Load a sample dataset."""
    st.info("Sample data loading is under construction.")


if __name__ == "__main__":
    main()