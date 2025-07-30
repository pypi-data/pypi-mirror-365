import streamlit as st
import pandas as pd
import numpy as np

def intro_tab():
    from labdata.schema import Subject,Dataset,Session, Strain
    @st.cache_data
    def get_subjects():
        
        df = pd.DataFrame(Subject().fetch())
        df.insert(0, "Select", False)
        return df.set_index("subject_name").sort_index()
        
    @st.cache_data
    def get_sessions(keys):
        if len(keys):
            keys = keys.reset_index()
            dfs = []
            for i in range(len(keys)):
                dfs.append(pd.DataFrame((Session()*Dataset() &
                                            f'subject_name = "{keys["subject_name"].iloc[i]}"').fetch()))
            if len(dfs):
                df = pd.concat([d for d in dfs if len(d)])
                return df.set_index("session_datetime").sort_index()
            else:
                return None
        return None
    subjects = get_subjects() 
    st.write("### Subjects", )
    edited_df = st.data_editor(subjects.sort_index(),
                                hide_index=False,
                                disabled = ['subject_name',
                                            'subject_dob',
                                            'subject_sex',
                                            'strain_name',
                                            'user_name'])
                                #column_config={"Select":
                                #               st.column_config.CheckboxColumn(required=True)},)
    sessions = get_sessions(edited_df[edited_df['Select'] == True])
    if sessions is None:
        st.write('No subjects selected.')
    else:
        uniqueds = np.unique([s for s in sessions.dataset_type.values if not s is None])
        tx = f'### Sessions ({len(sessions)})'
        for d in uniqueds:
            if not d is None:
                tx += f' - {d}: {len(sessions[sessions.dataset_type == d])}'
        st.write(tx,sessions)

    st.write('### Add a new subject to the database')
    insert_dict = dict()

    st.cache_resource()
    def get_users():
        return LabMember.fetch('user_name')
    with st.form('add subject'):
        from labdata.schema import LabMember,Strain,Subject
        users = get_users()
        insert_dict['user_name'] = st.selectbox('__User Name__', users)
        insert_dict['subject_name'] = st.text_input('__Subject ID__',value=None)
        insert_dict['subject_dob'] = st.date_input('__Date of Birth__')
        insert_dict['subject_sex'] = st.selectbox('__Sex__', ['M', 'F', 'Unknown'])
        if insert_dict['subject_sex'] == 'Unknown':
            insert_dict['subject_sex'] = 'U'
        available_strains = Strain().fetch('strain_name')
        insert_dict['stain_name'] = st.selectbox('__Strain__', available_strains)
        #st.write(insert_dict)
        submitted = st.form_submit_button('Add Subject', type='primary') # TODO: pop-up windown for confirmation and callback to add subject
        if submitted:
            st.write('Adding subject to database')
            st.write(insert_dict)

st.set_page_config(
    page_title="labdata dashboard",
    page_icon="🧪",
    layout="wide",
      initial_sidebar_state="auto")

from compute import compute_tab
from sorting import sorting_tab
from video import video_tab

page_names_to_funcs = {
    "Subjects and sessions": intro_tab,
    "Compute tasks": compute_tab,
    "Spike sorting": sorting_tab,
     "Video": video_tab,
}

from labdata import *
for p in plugins.keys():
    if hasattr(plugins[p],'dashboard_function'):
        page_names_to_funcs[plugins[p].dashboard_name] = plugins[p].dashboard_function

tab_name = st.sidebar.radio(
    "#### labdata dashboard",
    page_names_to_funcs.keys())

page_names_to_funcs[tab_name]()