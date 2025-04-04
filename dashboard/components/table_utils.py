import pandas as pd
import streamlit as st

def create_styled_dataframe(df, hide_index=True):
    """
    Create a styled DataFrame for display in Streamlit.
    
    Args:
        df (pandas.DataFrame): DataFrame to be styled
        hide_index (bool): If True, hide the DataFrame index
    
    Returns:
        pandas.io.formats.style.Styler: Styled DataFrame
    """
    # Return the dataframe without complex styling, just hiding the index if needed
    if hide_index:
        return df.style.hide(axis="index")
    else:
        return df.style

def display_dataframe_with_config(df, use_container_width=True, column_config=None):
    """
    Display a DataFrame with custom column configurations.
    
    Args:
        df (pandas.DataFrame): DataFrame to be displayed
        use_container_width (bool): If True, use the full available width
        column_config (dict): Column configuration for st.dataframe
    """
    # If no column configuration is provided, create a default one
    if column_config is None:
        column_config = {}
        for col in df.columns:
            # Apply number formatting for numeric columns
            if pd.api.types.is_numeric_dtype(df[col]):
                column_config[col] = st.column_config.NumberColumn(format="%.2f")
            else:
                # Apply standard text formatting for non-numeric columns
                column_config[col] = st.column_config.TextColumn(width="medium")
    
    # Display the dataframe with the provided configuration
    st.dataframe(
        data=df,
        use_container_width=use_container_width,
        column_config=column_config
    )

def create_filterable_dataframe(df, key_prefix="filter"):
    """
    Create a filterable DataFrame with filter widgets for each column.
    
    This function adds appropriate filter widgets based on the data type of each column:
    - Sliders for numeric columns
    - Multi-select dropdowns for categorical columns
    - Date range selectors for date columns
    
    Args:
        df (pandas.DataFrame): DataFrame to be filtered
        key_prefix (str): Prefix for filter widget keys
        
    Returns:
        pandas.DataFrame: Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Create an appropriate filter for each column
    for i, col in enumerate(df.columns):
        # For numeric columns, create a range slider
        if pd.api.types.is_numeric_dtype(df[col]):
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            
            # Avoid min and max being equal (happens if there's only one unique value)
            if min_val == max_val:
                min_val = min_val * 0.9
                max_val = max_val * 1.1
                
            # Create a slider to filter
            filter_values = st.slider(
                f"Filter by {col}",
                min_value=min_val,
                max_value=max_val,
                value=(min_val, max_val),
                key=f"{key_prefix}_{i}"
            )
            
            # Apply the filter
            filtered_df = filtered_df[
                (filtered_df[col] >= filter_values[0]) & 
                (filtered_df[col] <= filter_values[1])
            ]
            
        # For categorical columns, create a multi-select dropdown
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            options = df[col].unique().tolist()
            selected = st.multiselect(
                f"Filter by {col}",
                options=options,
                default=options,
                key=f"{key_prefix}_{i}"
            )
            
            # Apply the filter if selections are made
            if selected:
                filtered_df = filtered_df[filtered_df[col].isin(selected)]
                
        # For date columns, create a date range selector
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            min_date = df[col].min().date()
            max_date = df[col].max().date()
            
            filter_dates = st.date_input(
                f"Filter by {col}",
                value=(min_date, max_date),
                key=f"{key_prefix}_{i}"
            )
            
            # Apply the filter if a date range is selected
            if len(filter_dates) == 2:
                start_date, end_date = filter_dates
                filtered_df = filtered_df[
                    (filtered_df[col].dt.date >= start_date) & 
                    (filtered_df[col].dt.date <= end_date)
                ]
    
    return filtered_df

def format_currency(value, prefix="R$", decimal_places=2):
    """
    Format a value as currency with Brazilian formatting.
    
    Args:
        value (float): Value to be formatted
        prefix (str): Currency prefix
        decimal_places (int): Number of decimal places
        
    Returns:
        str: Formatted currency value
    """
    # Format using Brazilian convention (comma as decimal separator, period as thousands separator)
    return f"{prefix} {value:,.{decimal_places}f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_percentage(value, decimal_places=2, include_symbol=True):
    """
    Format a value as a percentage.
    
    Args:
        value (float): Value to be formatted (0.1 = 10%)
        decimal_places (int): Number of decimal places
        include_symbol (bool): If True, include the percentage symbol
        
    Returns:
        str: Formatted percentage value
    """
    # Format percentage using Brazilian convention (comma as decimal separator)
    formatted = f"{value * 100:.{decimal_places}f}".replace(".", ",")
    if include_symbol:
        return f"{formatted}%"
    return formatted