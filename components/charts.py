import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime

def render_data_visualizations(processed_data):
    """Render comprehensive data visualizations"""
    
    if not processed_data:
        st.info("No data available for visualization")
        return
    
    st.subheader("📊 Interactive Data Visualizations")
    
    # Dataset selection
    dataset_names = [data['name'] for data in processed_data]
    selected_dataset = st.selectbox("Select Dataset for Visualization", dataset_names)
    
    # Get selected dataframe
    selected_data = None
    for data in processed_data:
        if data['name'] == selected_dataset:
            selected_data = data
            break
    
    if not selected_data:
        return
    
    df = selected_data['dataframe']
    
    # Visualization tabs
    viz_tab1, viz_tab2, viz_tab3, viz_tab4 = st.tabs([
        "📈 Basic Charts", "🔍 Advanced Analytics", "📊 Correlations", "🎯 Custom Viz"
    ])
    
    with viz_tab1:
        render_basic_charts(df)
    
    with viz_tab2:
        render_advanced_analytics(df)
    
    with viz_tab3:
        render_correlation_analysis(df)
    
    with viz_tab4:
        render_custom_visualizations(df)

def render_basic_charts(df):
    """Render basic chart types"""
    
    col1, col2 = st.columns(2)
    
    # Column type analysis
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    with col1:
        st.markdown("**📈 Numeric Data Charts**")
        
        if numeric_cols:
            selected_numeric = st.selectbox("Select Numeric Column", numeric_cols, key="basic_numeric")
            
            # Histogram
            fig_hist = px.histogram(df, x=selected_numeric, nbins=30, 
                                  title=f"Distribution of {selected_numeric}")
            fig_hist.update_layout(height=300)
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Box plot
            fig_box = px.box(df, y=selected_numeric, title=f"Box Plot - {selected_numeric}")
            fig_box.update_layout(height=300)
            st.plotly_chart(fig_box, use_container_width=True)
    
    with col2:
        st.markdown("**📊 Categorical Data Charts**")
        
        if categorical_cols:
            selected_categorical = st.selectbox("Select Categorical Column", categorical_cols, key="basic_categorical")
            
            # Value counts
            value_counts = df[selected_categorical].value_counts().head(10)
            
            # Bar chart
            fig_bar = px.bar(x=value_counts.index, y=value_counts.values,
                           title=f"Distribution of {selected_categorical}")
            fig_bar.update_layout(height=300)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Pie chart
            fig_pie = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"Pie Chart - {selected_categorical}")
            fig_pie.update_layout(height=300)
            st.plotly_chart(fig_pie, use_container_width=True)

def render_advanced_analytics(df):
    """Render advanced analytical visualizations"""
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for advanced analytics")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_col = st.selectbox("X-axis", numeric_cols, key="adv_x")
        y_col = st.selectbox("Y-axis", numeric_cols, index=1, key="adv_y")
    
    with col2:
        chart_type = st.selectbox("Chart Type", ["Scatter", "Line", "Density"])
        color_by = st.selectbox("Color by", [None] + df.columns.tolist())
    
    # Create visualization based on selection
    if chart_type == "Scatter":
        fig = px.scatter(df, x=x_col, y=y_col, color=color_by,
                        title=f"{x_col} vs {y_col}",
                        trendline="ols" if st.checkbox("Add Trendline") else None)
    elif chart_type == "Line":
        fig = px.line(df, x=x_col, y=y_col, color=color_by,
                     title=f"{x_col} vs {y_col}")
    else:  # Density
        fig = px.density_contour(df, x=x_col, y=y_col,
                               title=f"Density Plot - {x_col} vs {y_col}")
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def render_correlation_analysis(df):
    """Render correlation analysis"""
    
    numeric_df = df.select_dtypes(include=['number'])
    
    if numeric_df.empty:
        st.warning("No numeric columns available for correlation analysis")
        return
    
    # Correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Heatmap
    fig_heatmap = px.imshow(corr_matrix, 
                           text_auto=True,
                           aspect="auto",
                           title="Correlation Matrix",
                           color_continuous_scale="RdBu")
    
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Strong correlations
    st.markdown("**🔍 Strong Correlations (|r| > 0.7)**")
    strong_corrs = []
    
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_val = corr_matrix.iloc[i, j]
            if abs(corr_val) > 0.7:
                strong_corrs.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Correlation': corr_val
                })
    
    if strong_corrs:
        st.dataframe(pd.DataFrame(strong_corrs))
    else:
        st.info("No strong correlations found")

def render_custom_visualizations(df):
    """Allow users to create custom visualizations"""
    
    st.markdown("**🎨 Create Custom Visualization**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        viz_type = st.selectbox("Visualization Type", [
            "Scatter Plot", "Line Chart", "Bar Chart", "Histogram",
            "Box Plot", "Violin Plot", "Heatmap", "3D Scatter"
        ])
    
    with col2:
        x_axis = st.selectbox("X-axis", df.columns.tolist())
    
    with col3:
        y_axis = st.selectbox("Y-axis", df.columns.tolist())
    
    # Additional options
    color_col = st.selectbox("Color by (optional)", [None] + df.columns.tolist())
    size_col = st.selectbox("Size by (optional)", [None] + df.select_dtypes(include=['number']).columns.tolist())
    
    # Create custom visualization
    try:
        if viz_type == "Scatter Plot":
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col, size=size_col)
        elif viz_type == "Line Chart":
            fig = px.line(df, x=x_axis, y=y_axis, color=color_col)
        elif viz_type == "Bar Chart":
            fig = px.bar(df, x=x_axis, y=y_axis, color=color_col)
        elif viz_type == "Histogram":
            fig = px.histogram(df, x=x_axis, color=color_col)
        elif viz_type == "Box Plot":
            fig = px.box(df, x=x_axis, y=y_axis, color=color_col)
        elif viz_type == "Violin Plot":
            fig = px.violin(df, x=x_axis, y=y_axis, color=color_col)
        elif viz_type == "3D Scatter":
            z_axis = st.selectbox("Z-axis", df.select_dtypes(include=['number']).columns.tolist())
            fig = px.scatter_3d(df, x=x_axis, y=y_axis, z=z_axis, color=color_col)
        
        fig.update_layout(height=500, title=f"Custom {viz_type}")
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating visualization: {str(e)}")
