import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

def render_chat_interface(processed_data, llm_handler, db_manager):
    """Render advanced chat interface with AI capabilities"""
    
    st.markdown("### 💬 AI-Powered Data Analysis")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            render_message(message, i)
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.chat_input(
            "Ask anything about your health data...",
            key="chat_input"
        )
    
    with col2:
        if st.button("🎯 Suggest Questions"):
            show_suggested_questions(processed_data)
    
    # Process user input
    if user_input:
        handle_user_input(user_input, processed_data, llm_handler, db_manager)
    
    # Quick question handler
    if 'quick_question' in st.session_state:
        handle_user_input(
            st.session_state.quick_question, 
            processed_data, 
            llm_handler, 
            db_manager
        )
        del st.session_state.quick_question

def render_message(message, index):
    """Render individual chat message with enhanced styling"""
    
    if message["role"] == "user":
        with st.chat_message("user", avatar="🧑‍💼"):
            st.markdown(f"**You:** {message['content']}")
            
    elif message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🤖"):
            
            # Main response
            st.markdown(message["content"])
            
            # Display results if available
            if "results" in message:
                render_query_results(message["results"], message.get("query_type", "table"))
            
            # Display visualizations if available
            if "visualization" in message:
                st.plotly_chart(
                    message["visualization"], 
                    use_container_width=True,
                    key=f"viz_{index}"
                )
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("👍", key=f"like_{index}"):
                    handle_feedback(index, "like")
            with col2:
                if st.button("👎", key=f"dislike_{index}"):
                    handle_feedback(index, "dislike")
            with col3:
                if st.button("📊", key=f"visualize_{index}"):
                    create_visualization(message.get("results"))
            with col4:
                if st.button("📥", key=f"export_{index}"):
                    export_message_data(message)

def handle_user_input(user_input, processed_data, llm_handler, db_manager):
    """Process user input and generate AI response"""
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Show typing indicator
    with st.spinner("🤖 HealthGenAI is analyzing..."):
        
        try:
            # Determine query type and process
            query_result = llm_handler.process_natural_language_query(
                user_input, 
                processed_data,
                db_manager
            )
            
            # Create response message
            response_message = {
                "role": "assistant",
                "content": query_result.get("response", "I couldn't process that query."),
                "timestamp": datetime.now(),
                "query_type": query_result.get("type", "general")
            }
            
            # Add results if available
            if "data" in query_result and query_result["data"] is not None:
                response_message["results"] = query_result["data"]
            
            # Add visualization if suggested
            if query_result.get("suggest_visualization"):
                viz = create_smart_visualization(
                    query_result["data"], 
                    query_result["type"]
                )
                if viz:
                    response_message["visualization"] = viz
            
            # Add to session state
            st.session_state.messages.append(response_message)
            
            # Update query history
            st.session_state.query_history.append({
                "query": user_input,
                "timestamp": datetime.now(),
                "success": True
            })
            
        except Exception as e:
            error_message = {
                "role": "assistant",
                "content": f"❌ **Error:** {str(e)}\n\nPlease try rephrasing your question or check your data format.",
                "timestamp": datetime.now(),
                "error": True
            }
            st.session_state.messages.append(error_message)
    
    # Rerun to show new messages
    st.rerun()

def render_query_results(results, query_type):
    """Render query results with appropriate formatting"""
    
    if results is None or len(results) == 0:
        st.info("No data found for this query.")
        return
    
    # Convert to DataFrame if needed
    if not isinstance(results, pd.DataFrame):
        df = pd.DataFrame(results)
    else:
        df = results
    
    # Display based on query type
    if query_type == "count" or len(df) == 1:
        # Show as metric
        if len(df.columns) == 1:
            value = df.iloc[0, 0]
            st.metric(label="Result", value=value)
        else:
            st.dataframe(df, use_container_width=True)
            
    elif len(df) <= 100:
        # Show full table for small results
        st.dataframe(df, use_container_width=True)
        
    else:
        # Show paginated results for large datasets
        st.write(f"**Showing top 100 results out of {len(df)} total**")
        st.dataframe(df.head(100), use_container_width=True)
        
        if st.button("📥 Download Full Results"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

def show_suggested_questions(processed_data):
    """Show suggested questions based on data"""
    
    if not processed_data:
        return
    
    # Generate smart suggestions based on data structure
    suggestions = generate_smart_suggestions(processed_data)
    
    with st.popover("🎯 Suggested Questions"):
        st.markdown("**Click any question to ask:**")
        
        for suggestion in suggestions:
            if st.button(suggestion, key=f"suggest_{suggestion}"):
                st.session_state.quick_question = suggestion

def generate_smart_suggestions(processed_data):
    """Generate intelligent question suggestions"""
    
    suggestions = []
    
    for data in processed_data:
        df = data['dataframe']
        
        # Basic statistics
        suggestions.extend([
            f"How many records are in {data['name']}?",
            f"What are the main statistics for {data['name']}?",
            "Show me a summary of missing data"
        ])
        
        # Column-specific suggestions
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            suggestions.extend([
                f"What is the average {col}?",
                f"Show distribution of {col}",
                f"Find outliers in {col}"
            ])
        
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            col = categorical_cols[0]
            suggestions.extend([
                f"What are the unique values in {col}?",
                f"Show frequency distribution of {col}"
            ])
    
    return suggestions[:10]  # Limit to top 10

def create_smart_visualization(data, query_type):
    """Create intelligent visualizations based on query type and data"""
    
    if data is None or len(data) == 0:
        return None
    
    try:
        df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
        
        # Simple count or metric
        if query_type == "count" or len(df) == 1:
            return create_metric_chart(df)
        
        # Distribution charts
        elif "distribution" in query_type.lower():
            return create_distribution_chart(df)
        
        # Correlation analysis
        elif "correlation" in query_type.lower():
            return create_correlation_chart(df)
        
        # Default: smart chart selection
        else:
            return create_auto_chart(df)
            
    except Exception as e:
        st.error(f"Visualization error: {str(e)}")
        return None

def create_metric_chart(df):
    """Create a metric display chart"""
    if len(df.columns) == 1 and len(df) == 1:
        value = df.iloc[0, 0]
        fig = go.Figure(go.Indicator(
            mode="number",
            value=value,
            title={"text": df.columns[0]}
        ))
        fig.update_layout(height=200)
        return fig
    return None

def handle_feedback(message_index, feedback_type):
    """Handle user feedback on messages"""
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    
    st.session_state.feedback[message_index] = {
        "type": feedback_type,
        "timestamp": datetime.now()
    }
    
    # Show confirmation
    if feedback_type == "like":
        st.success("👍 Thanks for the feedback!")
    else:
        st.info("👎 Feedback noted. We'll improve!")

def export_message_data(message):
    """Export individual message data"""
    try:
        if "results" in message:
            df = pd.DataFrame(message["results"])
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Data",
                data=csv,
                file_name=f"message_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"Export failed: {str(e)}")
