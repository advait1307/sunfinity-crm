import streamlit as st
import pandas as pd
import yaml
import re
from datetime import date
from functions_git.resume_uploader import OneDriveUploader
from functions_git.clientmanager import ClientManager
from functions_git.opportunitiesmanger import OpportunitiesManager  # fixed typo
from functions_git.resumemanager import ResumeManager
from functions_git.job_description_uploader import OneDriveJDUploader

st.set_page_config(layout="wide")
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

if 'github_token' in st.secrets:
    config['github_token'] = st.secrets['github_token']

clients_obj = ClientManager(config)
opportunities_obj = OpportunitiesManager(config)
resumes_obj = ResumeManager(config)
file_upload_obj = OneDriveUploader(config)
jd_uploader_obj = OneDriveJDUploader(config)

pages = st.sidebar.radio('Select Page', ['Clients', 'Opportunities', 'Candidate Manager'])

# -- Clients Page --
if pages == 'Clients':
    st.title('Client Manager')
    section = st.radio(' ', ['View Clients', 'Insert New Client', 'Update Client'], horizontal=True)
    df_clients = clients_obj.load_clients()

    if section == 'Insert New Client':
        with st.form('new_client'):
            client_name = st.text_input('Client Name')
            client_id = clients_obj.generate_client_id(df_clients)
            st.text(f"Client ID: {client_id}")
            company_type = st.text_input('Type of company')
            location = st.text_input('Location')
            contact1 = clients_obj.format_contact(
                st.text_input('Contact Person 1 Name'),
                st.text_input('Contact Person 1 Number'),
                st.text_input('Contact Person 1 Email')
            )
            contact2 = clients_obj.format_contact(
                st.text_input('Contact Person 2 Name'),
                st.text_input('Contact Person 2 Number'),
                st.text_input('Contact Person 2 Email')
            )
            contact3 = clients_obj.format_contact(
                st.text_input('Contact Person 3 Name'),
                st.text_input('Contact Person 3 Number'),
                st.text_input('Contact Person 3 Email')
            )
            onboarding = st.selectbox('Onboarding status', ['Completed', 'in-process', 'Rejected'])
            area_interest = st.text_area('Area of interest')
            submitted = st.form_submit_button('Submit')
            if submitted:
                new_row = {
                    'Client Name': client_name,
                    'Client ID': str(client_id),
                    'Type of Company': company_type,
                    'Location': location,
                    'Contact Person 1': contact1,
                    'Contact Person 2': contact2,
                    'Contact Person 3': contact3,
                    'Onboarding status': onboarding,
                    'Area of interest': area_interest
                }
                df_clients = pd.concat([df_clients, pd.DataFrame([new_row])], ignore_index=True)
                clients_obj.save_clients(df_clients)
                st.success(f'Client {client_name} added!')

    elif section == 'View Clients':
        if df_clients.empty:
            st.info('No clients available.')
        else:
            search_term = st.text_input('Search clients (press enter to search)')
            df_display = df_clients.copy()
            if search_term:
                mask = df_display.apply(
                    lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1
                )
                df_display = df_display[mask]
            st.dataframe(df_display)

    elif section == 'Update Client':
        if df_clients.empty:
            st.info('No clients available to update.')
        else:
            selected = st.selectbox('Select client to update', df_clients['Client Name'])
            client_row = df_clients[df_clients['Client Name'] == selected].iloc[0]
            with st.form('update_client'):
                st.info(f"Updating client: {selected} (ID: {client_row['Client ID']})")
                company_type = st.text_input('Type of company', client_row['Type of company'])
                location = st.text_input('Location', client_row['Location'])
                contact1 = st.text_input('Contact person 1 (Name/number/email)', client_row['Contact person 1'])
                contact2 = st.text_input('Contact Person 2 (Name/number/email)', client_row['Contact Person 2'])
                contact3 = st.text_input('Contact Person 3 (Name/number/email)', client_row['Contact Person 3'])
                onboarding = st.selectbox('Onboarding status', ['Completed', 'in-process', 'Rejected'], index=['Completed', 'in-process', 'Rejected'].index(client_row['Onboarding status']))
                area_interest = st.text_area('Area of interest', client_row['Area of interest'])
                submitted = st.form_submit_button('Update')
                delete_clicked = st.form_submit_button('Delete')
                idx = df_clients[df_clients['Client Name'] == selected].index[0]
                if submitted:
                    df_clients.at[idx, 'Type of Company'] = company_type
                    df_clients.at[idx, 'Location'] = location
                    df_clients.at[idx, 'Contact Person 1'] = contact1
                    df_clients.at[idx, 'Contact Person 2'] = contact2
                    df_clients.at[idx, 'Contact Person 3'] = contact3
                    df_clients.at[idx, 'Onboarding status'] = onboarding
                    df_clients.at[idx, 'Area of interest'] = area_interest
                    clients_obj.save_clients(df_clients)
                    st.success(f'Client {selected} updated!')
                if delete_clicked:
                    df_clients = df_clients.drop(idx).reset_index(drop=True)
                    clients_obj.save_clients(df_clients)
                    st.success(f'Client {selected} deleted!')

# -- Opportunities Page --
elif pages == 'Opportunities':
    st.title('Opportunities Manager')
    df_clients = clients_obj.load_clients()
    client_list = df_clients['Client Name'].tolist() if not df_clients.empty else []
    section = st.radio(' ', ['View Opportunities', 'Insert New Opportunity', 'Update Opportunity'], horizontal=True)
    df_opps = opportunities_obj.load_opportunites()
    df_resumes = resumes_obj.load_resumes()
    resume_choices = df_resumes['Name'].tolist() if not df_resumes.empty and 'Name' in df_resumes.columns else []

    if section == 'View Opportunities':
        if df_opps.empty:
            st.info('No opportunities available.')
        else:
            search_term = st.text_input('Search opportunities (press enter to search)')
            df_display = df_opps.copy()
            if search_term:
                mask = df_display.apply(
                    lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1
                )
                df_display = df_display[mask]
            if 'JD' in df_display.columns:
                df_display['JD'] = df_display.apply(
                    lambda row: f"[View JD]({row['JD']})" if pd.notnull(row['JD']) and row['JD'] not in ['NaN', '', 'No Job Description Uploaded'] else row['JD'],
                    axis=1 )
            if 'Name of candidates shared' in df_display.columns:
                df_display['Name of candidates shared'] = df_display['Name of candidates shared'].apply(
                    lambda x: x.replace('\n', ', ') if isinstance(x, str) else x
                )
            st.markdown(df_display.to_markdown(index=False), unsafe_allow_html=True)

    elif section == 'Insert New Opportunity':
        if not client_list:
            st.info('No clients available. Please add clients first.')
        else:
            with st.form('new_opportunity'):
                client_name = st.selectbox('Client name', client_list)
                role = st.text_input('Role')
                opp_id = opportunities_obj.generate_opp_id(df_opps)
                st.text(f"Opp ID: {opp_id}")
                date_received = st.date_input('Date received', value=date.today())
                job_location = st.text_input('Job Location')
                exp_bracket = st.text_input('Exp bracket')
                budget = st.text_input('Budget')
                expected_notice = st.text_input('Expected notice period')
                priority = st.selectbox('Priority', ['High', 'Medium', 'Low'])
                special_comments = st.text_area('Special comments')
                deal_status = st.selectbox('Deal Status', ['Open', 'Closed', 'Hold', 'Won'])
                jd_file = st.file_uploader('JD (upload file)')
                candidate_names = st.multiselect('Name of candidates shared', resume_choices)
                closed_on = st.date_input('Closed on', value=date.today(), disabled=True)
                submitted = st.form_submit_button('Submit')
                if submitted:
                    jd_one_drive_path = jd_uploader_obj.outlook_jd_uploader(client_name, role, str(date_received), opp_id, jd_file) if jd_file else 'No Job Description Uploaded'
                    candidates_markdown = opportunities_obj.generate_candidate_links(candidate_names, df_resumes)
                    new_row = {
                        'Client name': client_name,
                        'Role': role,
                        'Opp ID': opp_id,
                        'Date received': date_received,
                        'JD': jd_one_drive_path,
                        'Job Location': job_location,
                        'Exp bracket': exp_bracket,
                        'Budget': budget,
                        'Expected notice period': expected_notice,
                        'Priority': priority,
                        'Special comments': special_comments,
                        'Deal Status': deal_status,
                        'Number of candidates shared': len(candidate_names),
                        'Name of candidates shared': candidates_markdown,
                        'Closed on': closed_on
                    }
                    df_opps = pd.concat([df_opps, pd.DataFrame([new_row])], ignore_index=True)
                    opportunities_obj.save_opps(df_opps)
                    st.success(f'Opportunity {opp_id} added!')

    elif section == 'Update Opportunity':
        if df_opps.empty:
            st.info('No opportunities available to update.')
        else:
            selected = st.selectbox('Select opportunity to update', df_opps['Opp ID'])
            opp_row = df_opps[df_opps['Opp ID'] == selected].iloc[0]
            with st.form('update_opportunity'):
                client_name = st.selectbox('Client name', client_list, index=client_list.index(opp_row['Client name']))
                role = st.text_input('Role', opp_row['Role'])
                date_received = st.date_input('Date received', opp_row['Date received'])
                job_location = st.text_input('Job Location', opp_row['Job Location'])
                exp_bracket = st.text_input('Exp bracket', opp_row['Exp bracket'])
                budget = st.text_input('Budget', opp_row['Budget'])
                expected_notice = st.text_input('Expected notice period', opp_row['Expected notice period'])
                priority = st.selectbox('Priority', ['High', 'Medium', 'Low'], index=['High', 'Medium', 'Low'].index(opp_row['Priority']))
                special_comments = st.text_area('Special comments', opp_row['Special comments'])
                deal_status = st.selectbox('Deal Status', ['Open', 'Closed', 'Hold', 'Won'], index=['Open', 'Closed', 'Hold', 'Won'].index(opp_row['Deal Status']))
                st.text_input('Number of candidates shared', value=str(int(opp_row['Number of candidates shared'])), disabled=True)
                current_candidates = re.findall(r'\[([^\]_]+)_resume\]', opp_row['Name of candidates shared']) if pd.notnull(opp_row['Name of candidates shared']) else []
                candidate_names = st.multiselect('Name of candidates shared', resume_choices, current_candidates)
                closed_on = st.date_input('Closed on', opp_row['Closed on'] if pd.notnull(opp_row['Closed on']) else date.today())
                jd_file = st.file_uploader('Upload JD to update the existing one')
                submitted = st.form_submit_button('Update')
                delete_clicked = st.form_submit_button('Delete')
                idx = df_opps[df_opps['Opp ID'] == selected].index[0]
                if submitted:
                    candidates_markdown = opportunities_obj.generate_candidate_links(candidate_names, df_resumes)
                    jd_one_drive_path = jd_uploader_obj.outlook_jd_uploader(client_name, role, str(date_received), selected, jd_file) if jd_file else opp_row['JD']
                    # Ensure correct dtype before assignment to avoid FutureWarning
                    if 'Name of candidates shared' in df_opps.columns:
                        df_opps['Name of candidates shared'] = df_opps['Name of candidates shared'].astype('object')
                    df_opps.at[idx, 'Client name'] = client_name
                    df_opps.at[idx, 'Role'] = role
                    df_opps.at[idx, 'Date received'] = date_received
                    df_opps.at[idx, 'Job Location'] = job_location
                    df_opps.at[idx, 'Exp bracket'] = exp_bracket
                    df_opps.at[idx, 'Budget'] = budget
                    df_opps.at[idx, 'Expected notice period'] = expected_notice
                    df_opps.at[idx, 'Priority'] = priority
                    df_opps.at[idx, 'Special comments'] = special_comments
                    df_opps.at[idx, 'Deal Status'] = deal_status
                    df_opps.at[idx, 'Closed on'] = closed_on
                    df_opps.at[idx, 'JD'] = jd_one_drive_path
                    df_opps.at[idx, 'Name of candidates shared'] = candidates_markdown
                    df_opps.at[idx, 'Number of candidates shared'] = len(candidate_names)
                    opportunities_obj.save_opps(df_opps)
                    st.success(f'Opportunity {selected} updated!')
                if delete_clicked:
                    df_opps = df_opps.drop(idx).reset_index(drop=True)
                    opportunities_obj.save_opps(df_opps)
                    st.success(f'Opportunity {selected} deleted!')

# -- Candidate Manager Page --
elif pages == 'Candidate Manager':
    st.title('Candidate Manager')
    section = st.radio(' ', ['View Resumes', 'Insert New Resume', 'Update Resume'], horizontal=True)
    df_resumes = resumes_obj.load_resumes()
    df_opps = opportunities_obj.load_opportunites()
    opp_choices = [
        f"{row['Role']} ({row['Client name']}:{row['Opp ID']})"
        for _, row in df_opps[df_opps['Deal Status'] != 'Closed'].iterrows()
    ] if not df_opps.empty else []

    if section == 'View Resumes':
        if df_resumes.empty:
            st.info('No resumes available.')
        else:
            search_term = st.text_input('Search resumes (press enter to search)')
            df_display = df_resumes.copy()
            if search_term:
                mask = df_display.apply(
                    lambda row: row.astype(str).str.contains(search_term, case=False, na=False).any(), axis=1)
                df_display = df_display[mask]
            def parse_roles(roles_str):
                if not roles_str or roles_str == 'No Role':
                    return roles_str
                roles = []
                for role in roles_str.split(';'):
                    match = re.match(r'(.+?) \((.+?):(.+?)\)', role)
                    if match:
                        role_name, company, job_id = match.groups()
                        roles.append(f"{role_name} ({company}, {job_id})")
                    else:
                        roles.append(role)
                return ', '.join(roles)
            if 'Identified for roles' in df_display.columns:
                df_display['Identified for roles'] = df_display['Identified for roles'].apply(parse_roles)
            if 'Resume' in df_display.columns:
                df_display['Resume'] = df_display.apply(
                    lambda row: (
                        f"[{row['Name']}_resume]({row['Resume']})"
                        if pd.notnull(row['Resume'])
                           and row['Resume'] not in ['NaN', '', 'No Resume Uploaded']
                        else row['Resume']
                    ),
                    axis=1
                )
            st.markdown(df_display.to_markdown(index=False), unsafe_allow_html=True)

    elif section == 'Insert New Resume':
        with st.form('new_resume'):
            entry_id = resumes_obj.generate_resume_id(df_resumes)
            st.text(f"Entry ID: {entry_id}")
            name = st.text_input('Name')
            source = st.text_input('Source')
            top_skills = st.text_input('Top Skills')
            location = st.text_input('Location')
            current_org = st.text_input('Current organization')
            screener_name = st.text_input('Screener Name')
            screener_comments = st.text_area('Screener comments')
            first_interviewer = st.text_input('First Interviewer name')
            first_interviewer_comments = st.text_area('First interviewer comments')
            identified_roles = st.multiselect('Identified for roles', opp_choices)
            years_exp = st.text_input('Years of experience')
            current_ctc = st.text_input('Current CTC')
            resume_file = st.file_uploader('Resume (upload file)')
            submitted = st.form_submit_button('Submit')
            if submitted:
                resume_uploaded_path = file_upload_obj.outlook_file_uploader(name, resume_file) if resume_file else 'No Resume Uploaded'
                if not identified_roles:
                    identified_roles_str = 'No Role'
                else:
                    for opp in identified_roles:
                        opp_id = opp.split(':')[-1].replace(')', '')
                        opportunities_obj.update_candidate_count(df_opps, [opp_id], increment=True)
                    opportunities_obj.save_opps(df_opps)
                    identified_roles_str = ';'.join(identified_roles)
                new_row = {
                    'Entry ID': entry_id,
                    'Name': name,
                    'Source': source,
                    'Top Skills': top_skills,
                    'Resume': resume_uploaded_path,
                    'Location': location,
                    'Current organization': current_org,
                    'Screener Name': screener_name,
                    'Screener comments': screener_comments,
                    'First Interviewer name': first_interviewer,
                    'First interviewer comments': first_interviewer_comments,
                    'Identified for roles': identified_roles_str,
                    'Years of experience': years_exp,
                    'Current CTC': current_ctc
                }
                df_resumes = pd.concat([df_resumes, pd.DataFrame([new_row])], ignore_index=True)
                resumes_obj.save_resumes(df_resumes)
                st.success(f'Resume for {name} added!')

    elif section == 'Update Resume':
        if df_resumes.empty:
            st.info('No resumes available to update.')
        else:
            selected = st.selectbox('Select resume to update', df_resumes['Name'])
            resume_row = df_resumes[df_resumes['Name'] == selected].iloc[0]
            with st.form('update_resume'):
                st.info(f"Updating resume for: {selected} (Entry ID: {resume_row['Entry ID']})")
                source = st.text_input('Source', resume_row['Source'])
                top_skills = st.text_input('Top Skills', resume_row['Top Skills'])
                location = st.text_input('Location', resume_row['Location'])
                current_org = st.text_input('Current organization', resume_row['Current organization'])
                screener_name = st.text_input('Screener Name', resume_row['Screener Name'])
                screener_comments = st.text_area('Screener comments', resume_row['Screener comments'])
                first_interviewer = st.text_input('First Interviewer name', resume_row['First Interviewer name'])
                first_interviewer_comments = st.text_area('First interviewer comments', resume_row['First interviewer comments'])
                prev_roles = set(resume_row['Identified for roles'].split(';')) if resume_row['Identified for roles'] and resume_row['Identified for roles'] != 'No Role' else set()
                valid_prev_roles = [role for role in prev_roles if role in opp_choices]
                identified_roles = st.multiselect('Identified for roles', opp_choices, valid_prev_roles)
                years_exp = st.text_input('Years of experience', resume_row['Years of experience'])
                current_ctc = st.text_input('Current CTC', resume_row['Current CTC'])
                resume_file = st.file_uploader('Upload resume to change the uploaded file')
                submitted = st.form_submit_button('Update')
                delete_clicked = st.form_submit_button('Delete')
                idx = df_resumes[df_resumes['Name'] == selected].index[0]
                if submitted:
                    new_roles = set(identified_roles)
                    to_add = new_roles - prev_roles
                    to_remove = prev_roles - new_roles
                    for opp in to_add:
                        opp_id = opp.split(':')[-1].replace(')', '')
                        opportunities_obj.update_candidate_count(df_opps, [opp_id], increment=True)
                    for opp in to_remove:
                        opp_id = opp.split(':')[-1].replace(')', '')
                        opportunities_obj.update_candidate_count(df_opps, [opp_id], increment=False)
                    opportunities_obj.save_opps(df_opps)
                    if resume_file:
                        resume_path = file_upload_obj.outlook_file_uploader(selected, resume_file)
                        df_resumes.at[idx, 'Resume'] = resume_path
                    identified_roles_str = 'No Role' if not identified_roles else ';'.join(identified_roles)
                    df_resumes.at[idx, 'Identified for roles'] = identified_roles_str
                    df_resumes.at[idx, 'Source'] = source
                    df_resumes.at[idx, 'Top Skills'] = top_skills
                    df_resumes.at[idx, 'Location'] = location
                    df_resumes.at[idx, 'Current organization'] = current_org
                    df_resumes.at[idx, 'Screener Name'] = screener_name
                    df_resumes.at[idx, 'Screener comments'] = screener_comments
                    df_resumes.at[idx, 'First Interviewer name'] = first_interviewer
                    df_resumes.at[idx, 'First interviewer comments'] = first_interviewer_comments
                    df_resumes.at[idx, 'Years of experience'] = years_exp
                    df_resumes.at[idx, 'Current CTC'] = current_ctc
                    resumes_obj.save_resumes(df_resumes)
                    st.success(f'Resume for {selected} updated!')
                if delete_clicked:
                    for opp in prev_roles:
                        opp_id = opp.split(':')[-1].replace(')', '')
                        opportunities_obj.update_candidate_count(df_opps, [opp_id], increment=False)
                    opportunities_obj.save_opps(df_opps)
                    df_resumes = df_resumes.drop(idx).reset_index(drop=True)
                    resumes_obj.save_resumes(df_resumes)
                    st.success(f'Resume for {selected} deleted!')
