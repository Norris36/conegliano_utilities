"""
Finance App - Transaction Categorization and Analysis

A Streamlit app for analyzing financial transactions from CSV files.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from csv_parser import CSVParser
from categorizer import VendorCategorizer


def main():
    """Main Streamlit application."""

    st.set_page_config(
        page_title="Finance Transaction Analyzer",
        page_icon="💰",
        layout="wide"
    )

    st.title("💰 Finance Transaction Analyzer")
    st.markdown("Upload your transaction CSV file to analyze and categorize your spending.")

    # Initialize session state
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'categorized_df' not in st.session_state:
        st.session_state.categorized_df = None

    # Sidebar for configuration
    with st.sidebar:
        st.header("Settings")

        # File upload
        uploaded_file = st.file_uploader(
            "Upload Transaction CSV",
            type=['csv', 'txt'],
            help="Upload a CSV file containing your financial transactions"
        )

        if uploaded_file is not None:
            if st.button("Process File"):
                process_file(uploaded_file)

        st.markdown("---")

        # Category management
        if st.session_state.categorized_df is not None:
            st.subheader("Category Filters")
            categories = sorted(st.session_state.categorized_df['category'].unique())
            selected_categories = st.multiselect(
                "Filter by Category",
                categories,
                default=categories
            )
        else:
            selected_categories = []

    # Main content area
    if st.session_state.categorized_df is not None:
        display_analysis(st.session_state.categorized_df, selected_categories)
    else:
        display_welcome_message()


def process_file(uploaded_file):
    """Process the uploaded CSV file."""

    with st.spinner("Processing file..."):
        try:
            # Save uploaded file temporarily
            temp_path = Path(f"/tmp/{uploaded_file.name}")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # Parse CSV
            parser = CSVParser()
            df = parser.read_csv(str(temp_path))

            if df is None:
                st.error("Failed to read CSV file. Please check the file format.")
                return

            # Parse transaction data
            df = parser.parse_transaction_data(df)

            # Validate data
            is_valid, errors = parser.validate_data(df)
            if not is_valid:
                st.error("Invalid data format:")
                for error in errors:
                    st.error(f"- {error}")
                st.info("Required columns: date, amount, vendor")
                st.info("Your columns: " + ", ".join(df.columns.tolist()))
                return

            # Categorize transactions
            categorizer = VendorCategorizer()
            categorized_df = categorizer.categorize_transactions(df)

            # Store in session state
            st.session_state.df = df
            st.session_state.categorized_df = categorized_df

            st.success(f"Successfully processed {len(categorized_df)} transactions!")

        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


def display_welcome_message():
    """Display welcome message when no file is uploaded."""

    st.info("👈 Upload a CSV file to get started!")

    st.markdown("""
    ### How to use this app:

    1. **Upload your CSV file** using the sidebar
    2. The app will automatically:
       - Parse your transaction data
       - Categorize each transaction based on vendor name
       - Generate visualizations and summaries

    ### Required CSV Format:

    Your CSV should contain at least these columns (names may vary):
    - **Date**: Transaction date
    - **Amount**: Transaction amount
    - **Vendor/Description**: Merchant or vendor name

    ### Example CSV Format:
    ```
    Date,Amount,Description
    2024-01-15,45.67,Walmart Grocery
    2024-01-16,12.50,Starbucks Coffee
    2024-01-17,125.00,Shell Gas Station
    ```
    """)


def display_analysis(df, selected_categories):
    """Display the analysis dashboard."""

    # Filter by selected categories
    if selected_categories:
        filtered_df = df[df['category'].isin(selected_categories)]
    else:
        filtered_df = df

    # Overview metrics
    st.header("📊 Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_spent = filtered_df['amount'].sum()
        st.metric("Total Spending", f"${total_spent:,.2f}")

    with col2:
        avg_transaction = filtered_df['amount'].mean()
        st.metric("Average Transaction", f"${avg_transaction:,.2f}")

    with col3:
        num_transactions = len(filtered_df)
        st.metric("Total Transactions", f"{num_transactions:,}")

    with col4:
        num_categories = filtered_df['category'].nunique()
        st.metric("Categories", num_categories)

    st.markdown("---")

    # Category breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Spending by Category")
        category_summary = filtered_df.groupby('category')['amount'].sum().reset_index()
        category_summary = category_summary.sort_values('amount', ascending=False)

        fig_pie = px.pie(
            category_summary,
            values='amount',
            names='category',
            title='Spending Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("Top Categories")
        top_categories = category_summary.head(10)

        fig_bar = px.bar(
            top_categories,
            x='amount',
            y='category',
            orientation='h',
            title='Top 10 Categories by Spending',
            labels={'amount': 'Total Spent ($)', 'category': 'Category'}
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

    # Time series analysis
    if 'date' in filtered_df.columns:
        st.markdown("---")
        st.subheader("📈 Spending Over Time")

        # Daily spending
        daily_spending = filtered_df.groupby(filtered_df['date'].dt.date)['amount'].sum().reset_index()
        daily_spending.columns = ['date', 'amount']

        fig_time = px.line(
            daily_spending,
            x='date',
            y='amount',
            title='Daily Spending Trend',
            labels={'amount': 'Amount Spent ($)', 'date': 'Date'}
        )
        st.plotly_chart(fig_time, use_container_width=True)

    # Category summary table
    st.markdown("---")
    st.subheader("📋 Category Summary")

    categorizer = VendorCategorizer()
    summary = categorizer.get_category_summary(filtered_df)

    # Format the summary table
    summary_display = summary.copy()
    summary_display['total'] = summary_display['total'].apply(lambda x: f"${x:,.2f}")
    summary_display['average'] = summary_display['average'].apply(lambda x: f"${x:,.2f}")
    summary_display['percentage'] = summary_display['percentage'].apply(lambda x: f"{x}%")

    st.dataframe(summary_display, use_container_width=True)

    # Transaction details
    st.markdown("---")
    st.subheader("📝 Transaction Details")

    # Sort options
    sort_col = st.selectbox("Sort by:", ['date', 'amount', 'vendor', 'category'])
    sort_order = st.radio("Order:", ['Descending', 'Ascending'], horizontal=True)

    sorted_df = filtered_df.sort_values(
        by=sort_col,
        ascending=(sort_order == 'Ascending')
    )

    # Display transactions
    display_columns = ['date', 'vendor', 'category', 'amount']
    st.dataframe(
        sorted_df[display_columns].head(100),
        use_container_width=True
    )

    # Download options
    st.markdown("---")
    st.subheader("💾 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download Full Dataset (CSV)",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    with col2:
        summary_csv = summary.to_csv(index=False)
        st.download_button(
            label="Download Category Summary (CSV)",
            data=summary_csv,
            file_name=f"category_summary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
