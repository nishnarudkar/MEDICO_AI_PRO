import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import plotly.express as px
import plotly.graph_objects as go

def render_advanced_analytics(processed_data):
    """Render advanced analytics and insights"""
    
    if not processed_data:
        st.info("No data available for analytics")
        return
    
    st.subheader("📈 Advanced Analytics & Insights")
    
    # Dataset selection
    dataset_names = [data['name'] for data in processed_data]
    selected_dataset = st.selectbox("Select Dataset for Analysis", dataset_names, key="analytics_dataset")
    
    # Get selected dataframe
    selected_data = None
    for data in processed_data:
        if data['name'] == selected_dataset:
            selected_data = data
            break
    
    if not selected_data:
        return
    
    df = selected_data['dataframe']
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Statistical Summary", "🎯 Clustering", "📈 Trends", "🔍 Outliers"
    ])
    
    with tab1:
        render_statistical_summary(df)
    
    with tab2:
        render_clustering_analysis(df)
    
    with tab3:
        render_trend_analysis(df)
    
    with tab4:
        render_outlier_detection(df)

def render_statistical_summary(df):
    """Comprehensive statistical summary"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📊 Dataset Overview**")
        
        overview_metrics = {
            "Total Records": len(df),
            "Total Columns": len(df.columns),
            "Numeric Columns": len(df.select_dtypes(include=['number']).columns),
            "Categorical Columns": len(df.select_dtypes(include=['object']).columns),
            "Missing Values": df.isnull().sum().sum(),
            "Duplicate Rows": df.duplicated().sum()
        }
        
        for metric, value in overview_metrics.items():
            st.metric(metric, value)
    
    with col2:
        st.markdown("**🎯 Data Quality Metrics**")
        
        # Completeness
        completeness = (1 - df.isnull().sum() / len(df)) * 100
        avg_completeness = completeness.mean()
        
        st.metric("Average Completeness", f"{avg_completeness:.1f}%")
        
        # Show completeness by column
        if st.checkbox("Show Completeness by Column"):
            completeness_df = pd.DataFrame({
                'Column': completeness.index,
                'Completeness %': completeness.values
            }).sort_values('Completeness %')
            
            fig = px.bar(completeness_df, x='Completeness %', y='Column', 
                        orientation='h', title="Data Completeness by Column")
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed statistics for numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        st.markdown("**📈 Numeric Column Statistics**")
        
        # Enhanced describe
        desc_stats = df[numeric_cols].describe()
        
        # Add additional statistics
        additional_stats = pd.DataFrame({
            col: {
                'skewness': stats.skew(df[col].dropna()),
                'kurtosis': stats.kurtosis(df[col].dropna()),
                'cv': df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
            } for col in numeric_cols
        }).T
        
        # Combine statistics
        full_stats = pd.concat([desc_stats.T, additional_stats], axis=1)
        st.dataframe(full_stats.round(3))

def render_clustering_analysis(df):
    """Perform clustering analysis"""
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) < 2:
        st.warning("Need at least 2 numeric columns for clustering")
        return
    
    st.markdown("**🎯 Clustering Analysis**")
    
    # Feature selection
    selected_features = st.multiselect(
        "Select Features for Clustering", 
        numeric_cols, 
        default=numeric_cols[:min(3, len(numeric_cols))]
    )
    
    if len(selected_features) < 2:
        st.warning("Please select at least 2 features")
        return
    
    # Number of clusters
    n_clusters = st.slider("Number of Clusters", 2, 8, 3)
    
    # Prepare data
    cluster_data = df[selected_features].dropna()
    
    if len(cluster_data) == 0:
        st.warning("No data available after removing missing values")
        return
    
    # Standardize features
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(cluster_data)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Add clusters to dataframe
    cluster_df = cluster_data.copy()
    cluster_df['Cluster'] = clusters
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cluster distribution
        cluster_counts = pd.Series(clusters).value_counts().sort_index()
        fig_pie = px.pie(values=cluster_counts.values, 
                        names=[f"Cluster {i}" for i in cluster_counts.index],
                        title="Cluster Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Cluster centers
        centers_df = pd.DataFrame(
            scaler.inverse_transform(kmeans.cluster_centers_),
            columns=selected_features
        )
        centers_df.index = [f"Cluster {i}" for i in range(n_clusters)]
        
        st.markdown("**📊 Cluster Centers**")
        st.dataframe(centers_df.round(2))
    
    # Visualization
    if len(selected_features) >= 2:
        fig_scatter = px.scatter(
            cluster_df, 
            x=selected_features[0], 
            y=selected_features[1],
            color='Cluster',
            title=f"Clusters: {selected_features[0]} vs {selected_features[1]}"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

def render_trend_analysis(df):
    """Analyze trends in data"""
    
    st.markdown("**📈 Trend Analysis**")
    
    # Check for date columns
    date_cols = []
    for col in df.columns:
        if df[col].dtype == 'datetime64[ns]' or 'date' in col.lower():
            date_cols.append(col)
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not date_cols and not numeric_cols:
        st.warning("No suitable columns found for trend analysis")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if date_cols:
            date_col = st.selectbox("Select Date Column", date_cols)
        else:
            # Use index as proxy for time
            st.info("No date column found. Using row index as time proxy.")
            date_col = None
    
    with col2:
        if numeric_cols:
            value_col = st.selectbox("Select Value Column", numeric_cols)
        else:
            st.warning("No numeric columns available")
            return
    
    # Create trend visualization
    trend_df = df.copy()
    
    if date_col:
        # Ensure date column is datetime
        if trend_df[date_col].dtype != 'datetime64[ns]':
            try:
                trend_df[date_col] = pd.to_datetime(trend_df[date_col])
            except:
                st.error(f"Could not convert {date_col} to datetime")
                return
        
        # Sort by date
        trend_df = trend_df.sort_values(date_col)
        x_axis = date_col
    else:
        # Use index
        trend_df = trend_df.reset_index()
        x_axis = 'index'
    
    # Create trend plot
    fig = px.line(trend_df, x=x_axis, y=value_col, title=f"Trend: {value_col} over Time")
    
    # Add moving average if requested
    if st.checkbox("Add Moving Average"):
        window = st.slider("Moving Average Window", 3, 30, 7)
        trend_df[f'{value_col}_MA'] = trend_df[value_col].rolling(window=window).mean()
        
        fig.add_trace(go.Scatter(
            x=trend_df[x_axis],
            y=trend_df[f'{value_col}_MA'],
            mode='lines',
            name=f'{window}-period Moving Average',
            line=dict(color='red')
        ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Trend statistics
    if len(trend_df) > 1:
        # Calculate trend slope
        y_values = trend_df[value_col].dropna()
        x_values = range(len(y_values))
        
        if len(y_values) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Trend Slope", f"{slope:.4f}")
            with col2:
                st.metric("R-squared", f"{r_value**2:.4f}")
            with col3:
                st.metric("P-value", f"{p_value:.4f}")
            with col4:
                trend_direction = "📈 Increasing" if slope > 0 else "📉 Decreasing"
                st.metric("Direction", trend_direction)

def render_outlier_detection(df):
    """Detect and visualize outliers"""
    
    st.markdown("**🔍 Outlier Detection**")
    
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if not numeric_cols:
        st.warning("No numeric columns available for outlier detection")
        return
    
    # Column selection
    selected_col = st.selectbox("Select Column for Outlier Detection", numeric_cols)
    
    # Outlier detection method
    method = st.selectbox("Detection Method", ["IQR", "Z-Score", "Modified Z-Score"])
    
    data = df[selected_col].dropna()
    
    if len(data) == 0:
        st.warning("No data available after removing missing values")
        return
    
    # Detect outliers based on method
    if method == "IQR":
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        outliers = data[(data < lower_bound) | (data > upper_bound)]
        
    elif method == "Z-Score":
        z_scores = np.abs(stats.zscore(data))
        threshold = st.slider("Z-Score Threshold", 1.5, 4.0, 3.0, 0.1)
        outliers = data[z_scores > threshold]
        
    else:  # Modified Z-Score
        median = np.median(data)
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad
        threshold = st.slider("Modified Z-Score Threshold", 2.0, 5.0, 3.5, 0.1)
        outliers = data[np.abs(modified_z_scores) > threshold]
    
    # Display results
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Data Points", len(data))
        st.metric("Outliers Detected", len(outliers))
        st.metric("Outlier Percentage", f"{len(outliers)/len(data)*100:.2f}%")
    
    with col2:
        if len(outliers) > 0:
            st.markdown("**📊 Outlier Statistics**")
            st.write(f"Min Outlier: {outliers.min():.2f}")
            st.write(f"Max Outlier: {outliers.max():.2f}")
            st.write(f"Mean Outlier: {outliers.mean():.2f}")
    
    # Visualization
    fig = go.Figure()
    
    # Box plot
    fig.add_trace(go.Box(
        y=data,
        name=selected_col,
        boxpoints='outliers',
        marker_color='blue'
    ))
    
    fig.update_layout(
        title=f"Outlier Detection: {selected_col} ({method} Method)",
        yaxis_title=selected_col,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show outlier values
    if len(outliers) > 0 and st.checkbox("Show Outlier Values"):
        outlier_df = pd.DataFrame({
            'Index': outliers.index,
            'Value': outliers.values
        })
        st.dataframe(outlier_df)
