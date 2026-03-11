import streamlit as st
import pandas as pd
import sqlite3
import os

st.set_page_config(page_title="LinkedIn Post Extractor dashboard", layout="wide")

def load_data():
    """Load data from SQLite database."""
    db_path = os.path.join("data", "linkedin_data.db")
    if not os.path.exists(db_path):
        return pd.DataFrame()
        
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query("SELECT * FROM posts", conn)
        conn.close()
        
        # Deduplicate based on post_url
        df = df.drop_duplicates(subset=['post_url'])
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return pd.DataFrame()

def main():
    st.title("LinkedIn Post Extractor Dashboard")
    st.markdown("Displays LinkedIn posts containing specific keywords from the last 6 months.")

    df = load_data()

    if df.empty:
        st.warning("No data found! Please run the scraper first by executing `python main.py`.")
        return

    # Sidebar Filters
    st.sidebar.header("Filters")
    
    # Optional search by Keyword (if search_keyword column was saved)
    if 'search_keyword' in df.columns:
        keywords = ["All"] + list(df['search_keyword'].unique())
        selected_keyword = st.sidebar.selectbox("Filter by Search Keyword", keywords)
        
        if selected_keyword != "All":
            df = df[df['search_keyword'] == selected_keyword]

    # Optional text search inside content
    text_search = st.sidebar.text_input("Search in Post Content", "")
    if text_search:
        df = df[df['content'].str.contains(text_search, case=False, na=False)]

    # Metrics Layout
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Posts Found", value=len(df))
    with col2:
        num_authors = df['author'].nunique() if 'author' in df.columns else 0
        st.metric(label="Unique Authors", value=num_authors)

    st.subheader("Extracted Posts")
    
    # Display the dataframe
    # We display a select set of columns to be clean
    display_columns = ['search_keyword', 'author', 'published_date', 'content', 'post_url']
    # Filter columns that actually exist
    display_columns = [col for col in display_columns if col in df.columns]
    
    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    # Download Data Button
    st.subheader("Export Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download full data as CSV",
        data=csv,
        file_name='linkedin_extracted_posts.csv',
        mime='text/csv',
    )

if __name__ == "__main__":
    main()
