"""
Streamlit GUI for ML Sniff.

This module provides a comprehensive web interface for the ML Sniff package
with advanced features and excellent user experience.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from pathlib import Path
import tempfile
import os
from typing import Optional, Dict, Any

from .sniffer import Sniffer


def clean_dataframe_for_streamlit(df):
    """Clean dataframe to ensure compatibility with Streamlit's PyArrow conversion."""
    df_clean = df.copy()
    for col in df_clean.columns:
        try:
            if df_clean[col].dtype == 'object':
                # Convert all object types to strings, handling any non-serializable objects
                df_clean[col] = df_clean[col].astype(str)
            elif df_clean[col].dtype in ['int64', 'int32']:
                df_clean[col] = df_clean[col].astype(int)
            elif df_clean[col].dtype in ['float64', 'float32']:
                df_clean[col] = df_clean[col].astype(float)
            else:
                # For any other dtype, convert to string to be safe
                df_clean[col] = df_clean[col].astype(str)
        except Exception:
            # If any conversion fails, convert to string
            df_clean[col] = df_clean[col].astype(str)
    return df_clean


def safe_convert_to_native_types(obj):
    """Safely convert any object to native Python types for JSON serialization."""
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Series):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif hasattr(obj, 'dtype'):  # Handle numpy/pandas dtypes
        return str(obj)
    else:
        return obj


def main():
    """Main Streamlit application."""
    
    # Page configuration
    st.set_page_config(
        page_title="ML Sniff - Advanced ML Problem Detection",
        page_icon="🕵️‍♂️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Enhanced Custom CSS for light theme styling
    st.markdown("""
    <style>
    /* Light theme background */
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
    }
    
    /* Main Header */
    .main-header {
        font-size: 4rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
        line-height: 1.2;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center;
        color: #2c3e50;
        font-size: 1.5rem;
        font-weight: 500;
        margin-bottom: 2rem;
        letter-spacing: 0.5px;
        line-height: 1.4;
    }
    
    /* Enhanced Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 1rem;
        border-left: 6px solid #667eea;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin: 0.8rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2c3e50;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    /* Success Box */
    .success-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border: 2px solid #28a745;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(40, 167, 69, 0.1);
        font-size: 1.1rem;
        line-height: 1.6;
        color: #155724;
    }
    
    /* Warning Box */
    .warning-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #ffc107;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(255, 193, 7, 0.1);
        font-size: 1.1rem;
        line-height: 1.6;
        color: #856404;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border: 2px solid #2196f3;
        border-radius: 1rem;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 4px 8px rgba(33, 150, 243, 0.1);
        font-size: 1.1rem;
        line-height: 1.6;
        color: #0d47a1;
    }
    
    /* Section Headers */
    .section-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        padding: 10px 16px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Light theme tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        color: #2c3e50;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
        border-color: #667eea;
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
    }
    
    /* File Uploader Styling */
    .stFileUploader {
        border: 2px dashed #667eea;
        border-radius: 1rem;
        padding: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    }
    
    /* Dataframe Styling */
    .dataframe {
        border-radius: 0.5rem;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: #667eea;
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a6fd8;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">🕵️‍♂️ ML Sniff</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advanced Machine Learning Problem Detection</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #1976d2; margin-bottom: 0; font-size: 1.8rem; font-weight: 700;">📁 Data Input</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload
        uploaded_file = st.file_uploader(
            "📄 Upload your CSV file",
            type=['csv'],
            help="Upload a CSV file to analyze (max 200MB)"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        st.markdown("---")
        
        # Manual target column specification
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #1976d2; margin-bottom: 0; font-size: 1.6rem; font-weight: 700;">🎯 Target Column</h3>
        </div>
        """, unsafe_allow_html=True)
        
        target_column = st.text_input(
            "Specify target column (optional)",
            help="Manually specify the target column name if auto-detection fails"
        )
        
        if target_column.strip() == "":
            target_column = None
        
        st.markdown("---")
        
        # Analysis options
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #1976d2; margin-bottom: 0; font-size: 1.6rem; font-weight: 700;">⚙️ Analysis Options</h3>
        </div>
        """, unsafe_allow_html=True)
        
        auto_analyze = st.checkbox(
            "🔄 Auto-analyze on load",
            value=True,
            help="Automatically analyze data when file is loaded"
        )
        
        show_visualizations = st.checkbox(
            "📊 Show Visualizations",
            value=True,
            help="Display interactive charts and plots"
        )
        
        show_advanced = st.checkbox(
            "🔬 Show Advanced Analysis",
            value=True,
            help="Display feature importance and data quality analysis"
        )
    
    # Main content
    if uploaded_file is not None:
        try:
            # Load data
            df = pd.read_csv(uploaded_file)
            
            # Create sniffer instance
            with st.spinner("Analyzing your data..."):
                try:
                    sniffer = Sniffer(df, target_column=target_column, auto_analyze=auto_analyze)
                    # Display success message
                    st.success(f"✅ Successfully loaded and analyzed {len(df)} rows and {len(df.columns)} columns!")
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.info("Please check your data and try again.")
                    return
            
            # Main tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📊 Overview", 
                "🎯 Target Analysis", 
                "🏆 Feature Analysis",
                "🔍 Data Quality",
                "📈 Visualizations"
            ])
            
            with tab1:
                display_overview(sniffer, df)
            
            with tab2:
                display_target_analysis(sniffer)
            
            with tab3:
                if show_advanced:
                    display_feature_analysis(sniffer)
                else:
                    st.info("Enable 'Show Advanced Analysis' in the sidebar to view feature analysis.")
            
            with tab4:
                if show_advanced:
                    display_data_quality(sniffer)
                else:
                    st.info("Enable 'Show Advanced Analysis' in the sidebar to view data quality analysis.")
            
            with tab5:
                if show_visualizations:
                    display_visualizations(sniffer, df)
                else:
                    st.info("Enable 'Show Visualizations' in the sidebar to view charts.")
            
            # Export section
            st.markdown("---")
            display_export_section(sniffer)
            
        except Exception as e:
            st.error(f"❌ Error analyzing file: {str(e)}")
            st.info("Please check that your file is a valid CSV file.")
    
    else:
        # Welcome screen
        display_welcome_screen()


def display_welcome_screen():
    """Display welcome screen with instructions."""
    
    # Main welcome section
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div class="info-box" style="max-width: 800px; margin: 0 auto; background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);">
            <h2 style="color: #1976d2; margin-bottom: 1rem; font-size: 2.5rem; font-weight: 800;">🚀 Welcome to ML Sniff!</h2>
            <p style="font-size: 1.3rem; margin-bottom: 1.5rem; line-height: 1.6; font-weight: 500; color: #0d47a1;">
                Upload a CSV file to automatically detect and analyze your machine learning dataset
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1976d2; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 700;">🎯 What ML Sniff Detects</h4>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🎯 Target column identification</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🔍 Problem type classification</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🤖 Model recommendations</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🏆 Feature importance analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #1976d2; margin-bottom: 1rem; font-size: 1.4rem; font-weight: 700;">📊 Analysis Features</h4>
            <ul style="list-style: none; padding: 0;">
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🔍 Data quality assessment</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">📈 Interactive visualizations</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">📤 Export capabilities</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500; color: #2c3e50;">🛠️ Preprocessing suggestions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Sample data section
    st.markdown("""
    <div style="text-align: center; margin: 2rem 0;">
        <h3 style="color: #2c3e50; margin-bottom: 1rem; font-size: 2rem; font-weight: 700;">📋 Get Started</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🎲 Generate Sample Data", use_container_width=True):
            sample_data = create_sample_data()
            st.download_button(
                label="📥 Download Sample CSV",
                data=sample_data.to_csv(index=False),
                file_name="sample_data.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # How to use section
    st.markdown("""
    <div style="margin: 2rem 0;">
        <h3 style="color: #2c3e50; margin-bottom: 1rem; font-size: 2rem; font-weight: 700;">📖 How to Use</h3>
        <div class="info-box">
            <ol style="margin: 0; padding-left: 1.5rem;">
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500;">Upload your CSV file using the sidebar</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500;">Optionally specify a target column</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500;">Configure analysis options</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500;">Explore results through the interactive tabs</li>
                <li style="margin: 0.8rem 0; font-size: 1.1rem; font-weight: 500;">Export your analysis report</li>
            </ol>
        </div>
    </div>
    """, unsafe_allow_html=True)


def create_sample_data() -> pd.DataFrame:
    """Create sample data for demonstration."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'feature1': np.random.normal(0, 1, n_samples),
        'feature2': np.random.normal(0, 1, n_samples),
        'feature3': np.random.normal(0, 1, n_samples),
        'feature4': np.random.normal(0, 1, n_samples),
        'categorical_feature': np.random.choice(['A', 'B', 'C'], n_samples),
        'target': np.random.choice([0, 1], n_samples, p=[0.6, 0.4])
    }
    
    return pd.DataFrame(data)


def display_overview(sniffer: Sniffer, df: pd.DataFrame):
    """Display overview of the analysis."""
    
    # Section header
    st.markdown('<h2 class="section-header">📊 Dataset Overview</h2>', unsafe_allow_html=True)
    
    # Basic statistics with enhanced styling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <h3 style="color: #667eea; margin: 0; font-size: 2rem;">{len(df):,}</h3>
                <p style="margin: 0; color: #666;">📊 Rows</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <h3 style="color: #667eea; margin: 0; font-size: 2rem;">{len(df.columns)}</h3>
                <p style="margin: 0; color: #666;">📋 Columns</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        missing_pct = float(sniffer.analysis_results['basic_stats']['missing_percentage'])
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <h3 style="color: #667eea; margin: 0; font-size: 2rem;">{missing_pct:.1f}%</h3>
                <p style="margin: 0; color: #666;">❌ Missing Data</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        memory_mb = float(sniffer.analysis_results['basic_stats']['memory_usage_mb'])
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <h3 style="color: #667eea; margin: 0; font-size: 2rem;">{memory_mb:.2f} MB</h3>
                <p style="margin: 0; color: #666;">💾 Memory</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Data types section
    st.markdown('<h3 class="section-header">📋 Data Types</h3>', unsafe_allow_html=True)
    dtype_counts = df.dtypes.value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Convert dtype objects to strings for JSON serialization
        dtype_names = [str(dtype) for dtype in dtype_counts.index]
        fig = px.pie(
            values=dtype_counts.values,
            names=dtype_names,
            title="Data Types Distribution",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(
            title_font_size=16,
            title_font_color="#2c3e50",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea; margin-bottom: 1rem;">Data Type Summary</h4>
        </div>
        """, unsafe_allow_html=True)
        
        dtype_df = pd.DataFrame({
            'Data Type': dtype_names,
            'Count': dtype_counts.values
        })
        
        # Clean dataframe for Streamlit compatibility
        dtype_df_clean = clean_dataframe_for_streamlit(dtype_df)
        
        # Style the dataframe
        st.dataframe(
            dtype_df_clean,
            use_container_width=True,
            hide_index=True
        )
    
    # Analysis results section
    st.markdown('<h3 class="section-header">🎯 Analysis Results</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if sniffer.target_column:
            st.markdown(f"""
            <div class="success-box">
                <div style="text-align: center;">
                    <h4 style="color: #28a745; margin-bottom: 0.5rem;">🎯 Target Column</h4>
                    <p style="font-size: 1.2rem; font-weight: 600; margin: 0; color: #155724;">{sniffer.target_column}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="warning-box">
                <div style="text-align: center;">
                    <h4 style="color: #856404; margin-bottom: 0.5rem;">🎯 Target Column</h4>
                    <p style="font-size: 1.1rem; margin: 0; color: #856404;">No clear target identified</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-box">
            <div style="text-align: center;">
                <h4 style="color: #17a2b8; margin-bottom: 0.5rem;">🔍 Problem Type</h4>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0; color: #0c5460;">{sniffer.problem_type}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        model_name = sniffer.suggested_model['name']
        st.markdown(f"""
        <div class="metric-card">
            <div style="text-align: center;">
                <h4 style="color: #667eea; margin-bottom: 0.5rem;">🤖 Suggested Model</h4>
                <p style="font-size: 1.2rem; font-weight: 600; margin: 0; color: #2c3e50;">{model_name}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_target_analysis(sniffer: Sniffer):
    """Display target column analysis."""
    
    if sniffer.target_column is None:
        st.markdown("""
        <div class="warning-box">
            <h3 style="color: #856404; margin-bottom: 1rem;">⚠️ No Target Column Identified</h3>
            <p style="margin: 0; color: #856404;">This appears to be a clustering problem. No target column was detected in your dataset.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    target_data = sniffer.data[sniffer.target_column]
    
    # Section header
    st.markdown(f'<h2 class="section-header">🎯 Target Analysis: {sniffer.target_column}</h2>', unsafe_allow_html=True)
    
    # Target statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-header">📊 Target Statistics</h3>', unsafe_allow_html=True)
        
        stats_data = {
            'Metric': ['Data Type', 'Unique Values', 'Missing Values', 'Mean', 'Std', 'Min', 'Max'],
            'Value': [
                str(target_data.dtype),
                int(target_data.nunique()),
                int(target_data.isnull().sum()),
                f"{float(target_data.mean()):.4f}" if pd.api.types.is_numeric_dtype(target_data) else "N/A",
                f"{float(target_data.std()):.4f}" if pd.api.types.is_numeric_dtype(target_data) else "N/A",
                f"{float(target_data.min()):.4f}" if pd.api.types.is_numeric_dtype(target_data) else str(target_data.min()),
                f"{float(target_data.max()):.4f}" if pd.api.types.is_numeric_dtype(target_data) else str(target_data.max())
            ]
        }
        
        # Style the statistics table
        stats_df = pd.DataFrame(stats_data)
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #667eea; margin-bottom: 1rem;">Statistical Summary</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Clean dataframe for Streamlit compatibility
        stats_df_clean = clean_dataframe_for_streamlit(stats_df)
        
        st.dataframe(
            stats_df_clean,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown('<h3 class="section-header">📈 Target Distribution</h3>', unsafe_allow_html=True)
        
        if sniffer.problem_type == "Classification":
            # Classification: show bar chart
            value_counts = target_data.value_counts()
            fig = px.bar(
                x=value_counts.index,
                y=value_counts.values,
                title=f"Target Distribution: {sniffer.target_column}",
                labels={'x': 'Class', 'y': 'Count'},
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                title_font_size=16,
                title_font_color="#2c3e50",
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show percentages in styled cards
            percentages = (value_counts / len(target_data)) * 100
            col_a, col_b = st.columns(2)
            
            for i, (class_val, pct) in enumerate(percentages.items()):
                with col_a if i % 2 == 0 else col_b:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div style="text-align: center;">
                            <h4 style="color: #667eea; margin: 0;">Class {class_val}</h4>
                            <p style="font-size: 1.1rem; font-weight: 600; margin: 0; color: #2c3e50;">
                                {value_counts[class_val]} ({pct:.1f}%)
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        else:
            # Regression: show histogram
            fig = px.histogram(
                target_data,
                title=f"Target Distribution: {sniffer.target_column}",
                nbins=30,
                color_discrete_sequence=['#667eea']
            )
            fig.update_layout(
                title_font_size=16,
                title_font_color="#2c3e50",
                xaxis_title_font_size=14,
                yaxis_title_font_size=14,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Model recommendations section
    st.markdown('<h3 class="section-header">🤖 Model Recommendations</h3>', unsafe_allow_html=True)
    
    model_info = sniffer.suggested_model
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #667eea; margin-bottom: 1rem;">🏆 Primary Model</h4>
            <p style="font-size: 1.3rem; font-weight: 700; color: #2c3e50; margin-bottom: 1rem;">{model_info['name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #17a2b8; margin-bottom: 1rem;">⚙️ Hyperparameters</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for param, value in model_info['hyperparameters'].items():
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                <strong>{param}:</strong> <code>{value}</code>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-box">
            <h4 style="color: #17a2b8; margin-bottom: 1rem;">🔄 Alternative Models</h4>
        </div>
        """, unsafe_allow_html=True)
        
        for alt_model in model_info['alternatives']:
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                • <strong>{alt_model}</strong>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="warning-box">
            <h4 style="color: #856404; margin-bottom: 1rem;">💡 Recommendations</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if sniffer.problem_type == "Classification":
            st.markdown("""
            <div style="background: #fff3cd; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                • Consider class imbalance
            </div>
            <div style="background: #fff3cd; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                • Use accuracy, precision, recall, F1-score
            </div>
            """, unsafe_allow_html=True)
        elif sniffer.problem_type == "Regression":
            st.markdown("""
            <div style="background: #fff3cd; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                • Consider feature scaling
            </div>
            <div style="background: #fff3cd; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;">
                • Use MSE, MAE, R² metrics
            </div>
            """, unsafe_allow_html=True)


def display_feature_analysis(sniffer: Sniffer):
    """Display feature importance analysis."""
    
    if not sniffer.feature_importance:
        st.info("No feature importance analysis available. This might be a clustering problem.")
        return
    
    st.subheader("🏆 Feature Importance Analysis")
    
    # Method selector
    method = st.selectbox(
        "Select importance method:",
        ['random_forest', 'mutual_info', 'correlation'],
        format_func=lambda x: x.replace('_', ' ').title()
    )
    
    importance = sniffer.get_feature_importance(method)
    
    if importance:
        # Feature importance chart
        fig = px.bar(
            x=list(importance.keys()),
            y=list(importance.values()),
            title=f"Feature Importance ({method.replace('_', ' ').title()})",
            labels={'x': 'Features', 'y': 'Importance Score'}
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top features table
        st.subheader("📋 Top Features")
        
        sorted_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)
        top_features_df = pd.DataFrame(sorted_features, columns=['Feature', 'Importance'])
        top_features_df['Importance'] = top_features_df['Importance'].round(4)
        
        # Clean dataframe for Streamlit compatibility
        top_features_df_clean = clean_dataframe_for_streamlit(top_features_df)
        
        st.dataframe(top_features_df_clean, use_container_width=True)
        
        # Download top features
        csv = top_features_df.to_csv(index=False)
        st.download_button(
            label="Download Feature Importance CSV",
            data=csv,
            file_name=f"feature_importance_{method}.csv",
            mime="text/csv"
        )


def display_data_quality(sniffer: Sniffer):
    """Display data quality analysis."""
    
    st.subheader("🔍 Data Quality Assessment")
    
    # Quality issues summary
    quality_issues = sniffer.get_data_quality_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("High Missing", len(quality_issues['high_missing']))
    
    with col2:
        st.metric("High Duplicates", len(quality_issues['high_duplicates']))
    
    with col3:
        st.metric("Low Variance", len(quality_issues['low_variance']))
    
    with col4:
        st.metric("Many Outliers", len(quality_issues['many_outliers']))
    
    # Detailed quality report
    st.subheader("📊 Detailed Quality Report")
    
    quality_data = []
    for col, metrics in sniffer.data_quality_report.items():
        quality_data.append({
            'Column': col,
            'Missing (%)': f"{float(metrics['missing_percentage']):.1f}%",
            'Unique (%)': f"{float(metrics['unique_percentage']):.1f}%",
            'Duplicates (%)': f"{float(metrics['duplicate_percentage']):.1f}%",
            'Issues': get_quality_issues(col, quality_issues)
        })
    
    quality_df = pd.DataFrame(quality_data)
    
    # Clean dataframe for Streamlit compatibility
    quality_df_clean = clean_dataframe_for_streamlit(quality_df)
    
    st.dataframe(quality_df_clean, use_container_width=True)
    
    # Preprocessing suggestions
    st.subheader("🛠️ Preprocessing Suggestions")
    
    suggestions = sniffer.suggest_preprocessing()
    
    for category, items in suggestions.items():
        if items:
            st.markdown(f"**{category.replace('_', ' ').title()}:**")
            for item in items:
                st.text(f"  • {item}")
            st.markdown("---")


def get_quality_issues(col: str, quality_issues: Dict) -> str:
    """Get quality issues for a column."""
    issues = []
    for issue_type, columns in quality_issues.items():
        if col in columns:
            issues.append(issue_type.replace('_', ' ').title())
    return ", ".join(issues) if issues else "None"


def display_visualizations(sniffer: Sniffer, df: pd.DataFrame):
    """Display interactive visualizations."""
    
    st.subheader("📈 Interactive Visualizations")
    
    # Visualization selector
    viz_type = st.selectbox(
        "Select visualization:",
        ['Correlation Matrix', 'Missing Data Heatmap', 'Feature Distributions', 'Outlier Analysis']
    )
    
    if viz_type == 'Correlation Matrix':
        display_correlation_matrix(df)
    elif viz_type == 'Missing Data Heatmap':
        display_missing_heatmap(df)
    elif viz_type == 'Feature Distributions':
        display_feature_distributions(df)
    elif viz_type == 'Outlier Analysis':
        display_outlier_analysis(sniffer)


def display_correlation_matrix(df: pd.DataFrame):
    """Display correlation matrix."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        
        fig = px.imshow(
            corr_matrix,
            title="Correlation Matrix",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 2 numeric columns for correlation matrix.")


def display_missing_heatmap(df: pd.DataFrame):
    """Display missing data heatmap."""
    missing_data = df.isnull()
    
    if missing_data.sum().sum() > 0:
        fig = px.imshow(
            missing_data,
            title="Missing Data Heatmap",
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("No missing data found!")


def display_feature_distributions(df: pd.DataFrame):
    """Display feature distributions."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) > 0:
        # Select features to plot
        selected_features = st.multiselect(
            "Select features to plot:",
            numeric_cols,
            default=numeric_cols[:3].tolist()
        )
        
        if selected_features:
            fig = make_subplots(
                rows=len(selected_features),
                cols=1,
                subplot_titles=selected_features
            )
            
            for i, feature in enumerate(selected_features, 1):
                fig.add_trace(
                    go.Histogram(x=df[feature], name=feature),
                    row=i, col=1
                )
            
            fig.update_layout(height=300 * len(selected_features), title="Feature Distributions")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No numeric columns found for distribution plots.")


def display_outlier_analysis(sniffer: Sniffer):
    """Display outlier analysis."""
    if not sniffer.outlier_info:
        st.info("No outlier analysis available.")
        return
    
    st.subheader("📊 Outlier Analysis")
    
    # Outlier counts
    outlier_counts = []
    outlier_labels = []
    
    for col, info in sniffer.outlier_info.items():
        outlier_counts.append(info['iqr']['count'])
        outlier_labels.append(col)
    
    if outlier_counts:
        fig = px.bar(
            x=outlier_labels,
            y=outlier_counts,
            title="Outlier Count (IQR Method)",
            labels={'x': 'Features', 'y': 'Outlier Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Outlier details table
        outlier_data = []
        for col, info in sniffer.outlier_info.items():
            outlier_data.append({
                'Feature': col,
                'IQR Outliers': int(info['iqr']['count']),
                'IQR %': f"{float(info['iqr']['percentage']):.1f}%",
                'Z-Score Outliers': int(info['zscore']['count']),
                'Z-Score %': f"{float(info['zscore']['percentage']):.1f}%"
            })
        
        outlier_df = pd.DataFrame(outlier_data)
        
        # Clean dataframe for Streamlit compatibility
        outlier_df_clean = clean_dataframe_for_streamlit(outlier_df)
        
        st.dataframe(outlier_df_clean, use_container_width=True)
    else:
        st.success("No outliers detected!")


def display_export_section(sniffer: Sniffer):
    """Display export options."""
    
    st.subheader("📤 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export JSON Report"):
            export_report(sniffer, "json")
    
    with col2:
        if st.button("📊 Export CSV Report"):
            export_report(sniffer, "csv")
    
    with col3:
        if st.button("📝 Export Text Report"):
            export_report(sniffer, "txt")


def export_report(sniffer: Sniffer, format_type: str):
    """Export analysis report."""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format_type}', delete=False) as f:
        temp_path = f.name
    
    try:
        # Export report
        sniffer.export_report(temp_path, format_type)
        
        # Read file and create download button
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Determine MIME type
        mime_types = {
            'json': 'application/json',
            'csv': 'text/csv',
            'txt': 'text/plain'
        }
        
        st.download_button(
            label=f"Download {format_type.upper()} Report",
            data=content,
            file_name=f"ml_sniff_report.{format_type}",
            mime=mime_types.get(format_type, 'text/plain')
        )
        
    finally:
        # Clean up temporary file
        os.unlink(temp_path)


if __name__ == "__main__":
    main() 