import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

def load_data():
    df = pd.read_csv('crypto_relative_price_changes_vs_bitcoin.csv')
    # Add a rank column based on the index + 1
    df['Rank'] = df.index + 1  
    # Round to two decimals and format as a percentage
    df['Relative Change 1h (%)'] = df['Relative Change 1h (%)'].map("{:.2f}%".format)
    df['Relative Change 24h (%)'] = df['Relative Change 24h (%)'].map("{:.2f}%".format)
    return df

def main():
    # Set the page layout to wide
    st.set_page_config(layout="wide")

    st.markdown("""
    <style>
    /* This sets the maximum width of the main content container */
    .main .block-container {
        max-width: 1000px;  /* Adjust this value to fit your needs */
        margin: auto;
    }
    
    /* This adjusts the padding around the Streamlit elements */
    .reportview-container .main .block-container {
        padding-top: 2rem; /* Adjust the top padding */
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)


    st.title("Bitcoin Market Watch")
    # Use AgGrid to create an interactive table
    grid_options = {
        "defaultColDef": {
            "filter": True,
            "sortable": True,
            "resizable": True,
            "autoHeight": True,
            "cellStyle": {'textAlign': 'center'},
        },
    "columnDefs": [
        {"headerName": "Rank", "field": "Rank", "width": 90,"headerClass": "center-header", "sortable": True, "filter": True},
        {"headerName": "Symbol", "field": "Symbol","headerClass": "center-header", "sortable": True, "filter": True},
        {"headerName": "Price (SATS)", "field": "Price (SATS)","headerClass": "center-header", "sortable": True, "filter": True},
        {"headerName": "Relative Change 1h (%)", "field": "Relative Change 1h (%)","headerClass": "center-header", "sortable": True, "filter": True},
        {"headerName": "Relative Change 24h (%)", "field": "Relative Change 24h (%)","headerClass": "center-header", "sortable": True, "filter": True},
    ],
    "domLayout": 'autoHeight',  # Fits the height of the grid to the number of rows
}

    df = load_data()

    AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True)

if __name__ == '__main__':
    main()
