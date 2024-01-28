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
        .big-font {
            font-size:300% !important;
            font-weight: bold;
        }
        .text-bold {
            font-weight: bold;
        }
        .blue-font {
            color: #2589bd;
        }
        .dataframe {width:100% !important;}
        .streamlit-container {
            padding-top: 2rem;
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
        },
    "columnDefs": [
        {"headerName": "Rank", "field": "Rank", "width": 90, "sortable": True, "filter": True},
        {"headerName": "Symbol", "field": "Symbol", "sortable": True, "filter": True},
        {"headerName": "Price (SATS)", "field": "Price (SATS)", "sortable": True, "filter": True},
        {"headerName": "Relative Change 1h (%)", "field": "Relative Change 1h (%)", "sortable": True, "filter": True},
        {"headerName": "Relative Change 24h (%)", "field": "Relative Change 24h (%)", "sortable": True, "filter": True},
    ],
    "domLayout": 'autoHeight',  # Fits the height of the grid to the number of rows
}

    df = load_data()

    # Use AgGrid to create an interactive table
    AgGrid(df, gridOptions=grid_options, fit_columns_on_grid_load=True)

if __name__ == '__main__':
    main()
