# pip install streamlit pandas google-genai python-dotenv matplotlib seaborn

"""
Streamlit Data Analysis Agent

A simple web application for analyzing CSV files using an AI agent.
Features:
- Upload CSV files
- Descriptive statistics
- Histograms and bar plots
- AI-powered insights
"""

import streamlit as st
import pandas as pd
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# Try to import genai with better error handling
try:
    from google import genai
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("""
    **Troubleshooting steps:**
    1. Make sure you're in your virtual environment (venv)
    2. Run: `pip uninstall google-generativeai`
    3. Run: `pip install --upgrade google-genai`
    4. Verify: `python -c 'from google import genai; print("OK")'`
    """)
    st.stop()

# Load .env from parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Configure page
st.set_page_config(
    page_title="Data Analysis Agent",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'client' not in st.session_state:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY is not set in .env file")
        st.stop()
    st.session_state.client = genai.Client(api_key=api_key)

# Set style for plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


# -----------------------------------
# Tool Functions
# -----------------------------------

def get_summary(df):
    """Get descriptive statistics for the entire dataset."""
    return df.describe().to_string()


def get_correlation(df):
    """Get correlation matrix for numeric columns."""
    numeric_df = df.select_dtypes(include=['number'])
    if numeric_df.empty:
        return "No numeric columns found for correlation analysis."
    return numeric_df.corr().to_string()


def describe_column(df, column_name):
    """Get descriptive statistics for a specific column."""
    if column_name not in df.columns:
        return f"Column '{column_name}' does not exist. Available columns: {list(df.columns)}"
    return df[column_name].describe().to_string()


def plot_histogram(df, column_name):
    """Create a histogram for a numeric column."""
    if column_name not in df.columns:
        return None
    if not pd.api.types.is_numeric_dtype(df[column_name]):
        return None
    
    fig, ax = plt.subplots()
    df[column_name].hist(bins=30, ax=ax, edgecolor='black')
    ax.set_title(f'Histogram of {column_name}')
    ax.set_xlabel(column_name)
    ax.set_ylabel('Frequency')
    plt.tight_layout()
    return fig


def plot_bar_chart(df, column_name):
    """Create a bar chart for a categorical or numeric column."""
    if column_name not in df.columns:
        return None
    
    fig, ax = plt.subplots()
    
    # For categorical or low-cardinality numeric columns
    if pd.api.types.is_categorical_dtype(df[column_name]) or df[column_name].nunique() <= 20:
        value_counts = df[column_name].value_counts().head(20)
        value_counts.plot(kind='bar', ax=ax, edgecolor='black')
        ax.set_title(f'Bar Chart of {column_name}')
        ax.set_xlabel(column_name)
        ax.set_ylabel('Count')
        plt.xticks(rotation=45, ha='right')
    else:
        # For high-cardinality numeric, create bins
        df[column_name].hist(bins=20, ax=ax, edgecolor='black')
        ax.set_title(f'Distribution of {column_name}')
        ax.set_xlabel(column_name)
        ax.set_ylabel('Frequency')
    
    plt.tight_layout()
    return fig


# -----------------------------------
# JSON Extraction Function
# -----------------------------------

def extract_json_from_response(text):
    """Extract JSON from text, handling markdown code blocks."""
    if not text:
        return None
        
    text = text.strip()
    
    # Remove markdown code blocks if present
    if text.startswith("```"):
        lines = text.split("\n")
        if len(lines) > 1:
            text = "\n".join(lines[1:])
        if text.endswith("```"):
            text = text[:-3].strip()
        else:
            end_idx = text.rfind("```")
            if end_idx != -1:
                text = text[:end_idx].strip()
    
    # Find JSON object
    start_brace = text.find("{")
    end_brace = text.rfind("}")
    
    if start_brace != -1 and end_brace != -1 and end_brace > start_brace:
        json_str = text[start_brace:end_brace + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            json_str = json_str.strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    return None


# -----------------------------------
# Agent Functions
# -----------------------------------

def agent_decide(user_query, df):
    """Ask the agent to decide which analysis to perform."""
    available_tools = ["summary", "correlation", "describe_column", "histogram", "bar_chart"]
    
    prompt = f"""
You are a data analysis agent. The user wants to analyze a dataset.

Available tools:
- "summary" - Get descriptive statistics for the entire dataset
- "correlation" - Get correlation matrix for numeric columns
- "describe_column" - Get statistics for a specific column (requires column name)
- "histogram" - Create histogram for a numeric column (requires column name)
- "bar_chart" - Create bar chart for a column (requires column name)

Dataset columns: {list(df.columns)}
Dataset shape: {df.shape[0]} rows, {df.shape[1]} columns

User request: {user_query}

Return JSON only (no markdown) in this format:
{{
  "action": "<tool_name>",
  "column": "<column_name_or_empty>"
}}

If the user asks for a plot/chart/graph, use "histogram" or "bar_chart".
If the user asks for statistics/stats, use "summary" or "describe_column".
If the user asks about relationships, use "correlation".
"""
    
    response = st.session_state.client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text or ""


def execute_action(action, column_name, df):
    """Execute the chosen analysis action."""
    if action == "summary":
        return get_summary(df)
    elif action == "correlation":
        return get_correlation(df)
    elif action == "describe_column":
        if not column_name:
            return "Error: Column name required for describe_column"
        return describe_column(df, column_name)
    elif action == "histogram":
        if not column_name:
            return "Error: Column name required for histogram"
        return plot_histogram(df, column_name)
    elif action == "bar_chart":
        if not column_name:
            return "Error: Column name required for bar_chart"
        return plot_bar_chart(df, column_name)
    else:
        return f"Unknown action: {action}"


# -----------------------------------
# Main Application
# -----------------------------------

st.title("📊 Data Analysis Agent")
st.markdown("Upload a CSV file and analyze it with AI-powered insights")

# Sidebar for file upload
with st.sidebar:
    st.header("📁 Upload Data")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=['csv'],
        help="Upload a CSV file to analyze"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.session_state.df = df
            st.success(f"✅ File loaded: {uploaded_file.name}")
            st.info(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
        except Exception as e:
            st.error(f"Error loading file: {e}")
            st.session_state.df = None

# Main content area
if st.session_state.df is not None:
    df = st.session_state.df
    
    # Display dataset info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", df.shape[0])
    with col2:
        st.metric("Columns", df.shape[1])
    with col3:
        st.metric("Numeric Columns", len(df.select_dtypes(include=['number']).columns))
    
    # Show data preview
    with st.expander("📋 Data Preview", expanded=False):
        st.dataframe(df.head(10))
        st.caption(f"Showing first 10 rows of {len(df)} total rows")
    
    # Show column info
    with st.expander("📊 Column Information", expanded=False):
        col_info = pd.DataFrame({
            'Column': df.columns,
            'Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values
        })
        st.dataframe(col_info, use_container_width=True)
    
    st.divider()
    
    # Analysis section
    st.header("🔍 Analysis")
    
    # Quick analysis buttons
    st.subheader("Quick Analysis")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Summary Statistics"):
            result = get_summary(df)
            st.text_area("Summary Statistics", result, height=300)
    
    with col2:
        if st.button("🔗 Correlation Matrix"):
            result = get_correlation(df)
            st.text_area("Correlation Matrix", result, height=300)
    
    with col3:
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numeric_cols:
            selected_col = st.selectbox("Select Column for Histogram", numeric_cols)
            if st.button("📊 Show Histogram"):
                fig = plot_histogram(df, selected_col)
                if fig:
                    st.pyplot(fig)
                    plt.close()
                else:
                    st.warning("Cannot create histogram for this column")
        else:
            st.info("No numeric columns available")
    
    with col4:
        all_cols = df.columns.tolist()
        selected_col = st.selectbox("Select Column for Bar Chart", all_cols, key="bar_chart")
        if st.button("📊 Show Bar Chart"):
            fig = plot_bar_chart(df, selected_col)
            if fig:
                st.pyplot(fig)
                plt.close()
            else:
                st.warning("Cannot create bar chart for this column")
    
    st.divider()
    
    # AI Agent section
    st.subheader("🤖 AI Agent Analysis")
    
    # Agent capabilities info
    with st.expander("ℹ️ What can the AI Agent do?", expanded=True):
        st.markdown("""
        The AI Agent can understand natural language questions and automatically perform data analysis. 
        Here's what it can do:
        
        **📊 Statistical Analysis:**
        - Get summary statistics for the entire dataset
        - Get descriptive statistics for specific columns
        - Calculate correlation matrices between numeric variables
        
        **📈 Visualizations:**
        - Create histograms for numeric columns (shows distribution)
        - Create bar charts for categorical columns (shows frequency)
        
        **💬 Example Questions You Can Ask:**
        - "Show me summary statistics"
        - "What are the correlations in my data?"
        - "Create a histogram of the price column"
        - "Show me statistics for the sales column"
        - "Draw a bar chart of the category column"
        - "What's the distribution of units sold?"
        
        Just type your question in natural language and the AI will automatically choose the right analysis tool!
        """)
    
    user_query = st.text_input(
        "Ask a question about your data:",
        placeholder="e.g., 'Show me statistics for the sales column' or 'Create a histogram of price'"
    )
    
    if st.button("Analyze", type="primary") and user_query:
        with st.spinner("AI is analyzing your data..."):
            # Get agent decision
            decision = agent_decide(user_query, df)
            
            # Extract JSON from response
            data = extract_json_from_response(decision)
            
            if data:
                action = data.get("action", "")
                column = data.get("column", "")
                
                st.info(f"**Agent Action:** {action}" + (f" on column: {column}" if column else ""))
                
                # Execute the action
                result = execute_action(action, column, df)
                
                if isinstance(result, str):
                    # Text result (statistics)
                    st.text_area("Results", result, height=300)
                elif hasattr(result, 'savefig') or hasattr(result, 'show'):
                    # Plot result
                    st.pyplot(result)
                    plt.close()
                else:
                    st.write(result)
            else:
                st.error("Could not parse agent response. Try rephrasing your question.")
                st.code(decision)
    
    st.divider()
    
    # Manual column analysis
    st.subheader("📋 Manual Column Analysis")
    selected_column = st.selectbox("Select a column to analyze:", df.columns)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Get Statistics"):
            stats = describe_column(df, selected_column)
            st.text_area("Column Statistics", stats, height=200)
    
    with col2:
        if pd.api.types.is_numeric_dtype(df[selected_column]):
            if st.button("Show Histogram"):
                fig = plot_histogram(df, selected_column)
                if fig:
                    st.pyplot(fig)
                    plt.close()
        else:
            if st.button("Show Bar Chart"):
                fig = plot_bar_chart(df, selected_column)
                if fig:
                    st.pyplot(fig)
                    plt.close()

else:
    st.info("👈 Please upload a CSV file using the sidebar to get started")
    
    st.markdown("---")
    st.header("📋 Application Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📊 Quick Analysis Tools
        
        **Summary Statistics**
        - Get descriptive statistics (mean, median, std, min, max, quartiles)
        - Works on the entire dataset
        
        **Correlation Matrix**
        - See relationships between numeric variables
        - Identify which variables are correlated
        
        **Histograms**
        - Visualize distributions of numeric columns
        - See how data is distributed
        
        **Bar Charts**
        - Visualize categorical data
        - See frequency of categories
        """)
    
    with col2:
        st.markdown("""
        ### 🤖 AI Agent Capabilities
        
        The AI Agent understands natural language and can:
        
        **Statistical Analysis:**
        - Generate summary statistics
        - Calculate correlations
        - Analyze specific columns
        
        **Visualizations:**
        - Create histograms automatically
        - Generate bar charts
        - Choose the right chart type
        
        **Example Questions:**
        - "Show me statistics for sales"
        - "Create a histogram of price"
        - "What are the correlations?"
        - "Draw a bar chart of category"
        
        Just ask in plain English!
        """)
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 How to Use:
    1. Upload a CSV file using the sidebar
    2. Explore your data with Quick Analysis buttons
    3. Ask the AI Agent questions in natural language
    4. View results and visualizations
    """)

