import streamlit as st
from web_pages.home import *
from web_pages.footer import *

#-------------------------------------------------------

st.set_page_config(
    page_title = 'K Vikas Mahendar',
    page_icon = './assets/images/logo.png',
    layout = 'wide',
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "### Project developed by K Vikas Mahendar."
    })

st.set_option('deprecation.showPyplotGlobalUse', False)

root_dir = '/home/sanvik/Workspace/Kotak/lead-scoring-and-segmentation-main/'
 

def web_app():

    home_page()              
    footer()

if __name__ == "__main__":
    web_app()