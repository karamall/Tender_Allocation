import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

@st.cache(allow_output_mutation=True)
def get_dataframe(n_users):
    df = pd.DataFrame(columns=['Bidder', 'Quote'])
    df['Bidder'] = [f'Bidder #{i+1}' for i in range(int(n_users))]
    df['Quote'] = [0 for i in range(int(n_users))]
    return df

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

def run_model(data_df, total_capacity):
    weights = data_df['Quote'].values[::-1]
    print("Weights List : " , weights)
    weights = weights / sum(weights)
    allocations = weights * total_capacity
    data_df['Weights'] = np.round(np.asarray(weights).astype(float), decimals=3)
    data_df['Allocation'] = np.round(np.asarray(weights * total_capacity).astype(float), decimals=0)
    data_df = data_df.append({'Bidder' : None, 'Quote' : None, 'Weights' : None, 'Allocation':None},ignore_index = True)
    data_df = data_df.append({'Bidder' : "Total Allocated", 'Quote' : None, 'Weights' : None, 'Allocation':data_df['Allocation'].sum()},ignore_index = True)
    return data_df

def home_page():
    im_sidebar = Image.open('./assets/images/TEDA-Logo.jpg')
    sidebar_placeholder = st.sidebar.empty()
    with sidebar_placeholder.container():
        with st.sidebar:
            st.markdown("<h1 style='text-align: center; color: #f76497;'>Tender Capacity Allocation</h1>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([0.35, 2.5, 0.35])
            with col2:
                st.image(im_sidebar)

            col1, col2, col3, col4, col5 = st.columns([0.25, 1, 0.5, 1, 0.25])
            with col2:
                form_button = st.button('NEW')
            with col4:
                calculate_button = st.button('ALLOCATE')

            st.markdown('---')

    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns(2)
        with col1:
            # n_users = st.number_input("⦿ Enter Number of Users", value=5)
            n_users = st.slider("⦿ Enter Number of Bidders",1,20, value=5)
            st.markdown(' ')
        with col2:
            total_capacity = st.number_input("⦿ Enter Total Capacity (MW)", value=10000)
            st.markdown(' ')
        df = get_dataframe(n_users)

        with st.container():
            gd = GridOptionsBuilder.from_dataframe(df)
            gd.configure_pagination(enabled=True)
            gd.configure_default_column(editable=True, groupable=True)
            #gd.configure_selection(selection_mode="multiple", use_checkbox=True)
            gridoptions = gd.build()
            grid_table = AgGrid(
                df,
                gridOptions=gridoptions,
                update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SORTING_CHANGED,
                fit_columns_on_grid_load=True,
                theme="blue",
            )

            data_df = grid_table.data.sort_values('Quote')

    if calculate_button:
        sidebar_placeholder.empty()
        placeholder.empty()

        with st.spinner('Running Model'):
            result_df = run_model(data_df, total_capacity)

        with st.container():
            gd = GridOptionsBuilder.from_dataframe(result_df)
            gd.configure_pagination(enabled=True)
            gd.configure_default_column(editable=True, groupable=True)
            #gd.configure_selection(selection_mode="multiple", use_checkbox=True)
            gridoptions = gd.build()
            grid_table = AgGrid(
                result_df,
                gridOptions=gridoptions,
                update_mode=GridUpdateMode.VALUE_CHANGED | GridUpdateMode.SORTING_CHANGED,
                fit_columns_on_grid_load=True,
                theme="blue",
            )
        
        csv = convert_df(result_df)
        st.download_button(label="Download data as CSV", data=csv, file_name='database.csv', mime='text/csv',)

    return 0
