import streamlit as st
import pandas as pd
from datetime import datetime

def render_sidebar():
    """Render enhanced sidebar with file upload and options"""
    
    # Branding
    st.markdown(f"""
    <div class="sidebar-header">
        <h2>{APP_CONFIG['logo']} {APP_CONFIG['name']}</h2>
        <p>{APP_CONFIG['tagline']}</p>
        <small>v{APP_CONFIG['version']}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown("### 📁 Data Upload")
    
    uploaded_files = st.file_uploader(
        "Upload Health Data Files",
        type=["csv", "xlsx", "json"],
        accept_multiple_files=True,
        help="Supported formats: CSV, Excel, JSON"
    )
    
    # File Information
    if uploaded_files:
        with st.expander(f"📊 {len(uploaded_files)} File(s) Uploaded", expanded=True):
            total_size = 0
            for file in uploaded_files:
                file_size = len(file.getvalue())
                total_size += file_size
                st.write(f"📄 **{file.name}** - {format_file_size(file_size)}")
            
            st.info(f"Total size: {format_file_size(total_size)}")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    quick_questions = [
        "📊 Show data overview",
        "👥 How many patients?",
        "📈 Average age distribution",
        "🩺 Health conditions summary",
        "📉 Identify missing data",
        "🔍 Find correlations"
    ]
    
    for question in quick_questions:
        if st.button(question, use_container_width=True):
            st.session_state.quick_question = question
    
    st.markdown("---")
    
    # Analysis Options
    st.markdown("### 🔧 Analysis Options")
    
    analysis_options = {
        'show_statistical_summary': st.checkbox("Statistical Summary", value=True),
        'enable_data_profiling': st.checkbox("Data Profiling", value=True),
        'auto_visualizations': st.checkbox("Auto Visualizations", value=False),
        'predictive_insights': st.checkbox("Predictive Insights", value=False),
        'export_results': st.checkbox("Export Results", value=True)
    }
    
    # Model Settings
    with st.expander("🤖 AI Model Settings"):
        model_choice = st.selectbox(
            "Choose AI Model",
            ["Gemini Pro", "Gemini Pro Vision", "GPT-4"],
            index=0
        )
        
        response_style = st.selectbox(
            "Response Style",
            ["Professional", "Detailed", "Concise", "Educational"],
            index=0
        )
    
    # Data Export
    st.markdown("---")
    if st.button("📥 Export Session Data", use_container_width=True):
        export_session_data()
    
    return uploaded_files, {
        **analysis_options,
        'model_choice': model_choice,
        'response_style': response_style
    }

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def export_session_data():
    """Export current session data"""
    try:
        session_data = {
            'timestamp': datetime.now().isoformat(),
            'messages': st.session_state.get('messages', []),
            'query_history': st.session_state.get('query_history', []),
            'user_preferences': st.session_state.get('user_preferences', {})
        }
        
        # Convert to JSON and create download
        json_data = json.dumps(session_data, indent=2)
        st.download_button(
            label="Download Session Data",
            data=json_data,
            file_name=f"healthgenai_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
        
    except Exception as e:
        st.error(f"Export failed: {str(e)}")
