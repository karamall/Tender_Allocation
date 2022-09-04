import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import locale
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode

locale.setlocale(locale.LC_MONETARY, 'en_IN')

@st.cache(allow_output_mutation=True)
def get_dataframe(n_users):
    df = pd.DataFrame(columns=['Bidder', 'Quoted Price'])
    df['Bidder'] = [f'Bidder #{i+1}' for i in range(int(n_users))]
    df['Quoted Price'] = [0 for i in range(int(n_users))]
    return df

@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False).encode('utf-8')

def run_model(data_df, total_capacity):
    n_users = len(data_df)
    ranks = [i+1 for i in range(n_users)]
    data_df['Rank'] = ranks
    print("Ranks : " , ranks)
    quotes = data_df['Quoted Price'].values.tolist()
    print("Quotes : " , quotes)
    total_rank = sum(ranks)
    contrib = [total_rank - i for i in ranks]
    print("Contrib : " , contrib)
    total_contrib = sum(contrib)
    weights = np.asarray([i / total_contrib for i in contrib]).astype(float)
    allocations = np.asarray(weights * total_capacity).astype(float)
    data_df['Score'] = np.round(weights, decimals=3)
    data_df['Capacity Alloted (kW)'] = np.round(allocations, decimals=0)
    least_quoted_price = quotes[0]
    business_capacity = np.round(np.asarray([least_quoted_price * i for i in allocations]).astype(float), decimals=0)
    business_capacity_str = [locale.currency(i, grouping=True) for i in business_capacity]
    data_df['Contract Value'] = business_capacity_str
    data_df = data_df.append({'Bidder' : None, 'Quoted Price' : None, 'Score' : None, 'Capacity Alloted (kW)': None, 'Contract Value': None},ignore_index = True)
    data_df = data_df.append({'Bidder' : "Total Allocated", 'Quoted Price' : None, 'Score' : None, 'Capacity Alloted (kW)':data_df['Capacity Alloted (kW)'].sum(), 'Contract Value':locale.currency(business_capacity.sum(), grouping=True)},ignore_index = True)
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

            col1, col2, col3, col4, col5 = st.columns([0.35, 1, 0.25, 1, 0.25])
            with col2:
                form_button = st.button('New Form')
            with col4:
                calculate_button = st.button('Allocate')

            st.markdown('---')

    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns(2)
        with col1:
            # n_users = st.number_input("⦿ Enter Number of Users", value=5)
            n_users = st.slider("⦿ Enter Number of Bidders",1,20, value=5)
            st.markdown(' ')
        with col2:
            total_capacity = st.number_input("⦿ Enter Total Capacity (KW)", value=10000)
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

            data_df = grid_table.data.sort_values('Quoted Price')

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
