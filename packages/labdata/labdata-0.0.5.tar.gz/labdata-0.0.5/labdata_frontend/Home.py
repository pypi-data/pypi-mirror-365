import streamlit as st
from pathlib import Path
from labdata.schema import *
from labdata.utils import prefs

st.set_page_config(
page_title="LabData",
page_icon="🧪",
)

st.write('# Welcome to LabData! 🧪')
# TODO: if we want to preserve user upload privleges, get user and pw and create new connection
#st.write(f'## Please enter your database credentials for:')
# TODO: check connection first?
db_name = prefs['database']['database.host']
st.write('## Sucessfully connected to:')
st.markdown(f'`{db_name}`')
#animal = st.selectbox('empty', ['a','b','c'], label_visibility='collapsed')

st.sidebar.success('Select a page to view.')

st.markdown("""

    ### Usage

    ### Availible Pages

    - Page 1
    - Page 1
    - Page 1

    ### Questions or Bugs?

    GitHub issue link

    #### Authors
    Joao Couto and Max Melin
"""
)