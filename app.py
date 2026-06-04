# app.py

import streamlit as st
import database as db
import email_utils as email
from datetime import date, datetime
import pandas as pd
import os

# Set up page configurations
st.set_page_config(page_title="Leave Management System", layout="centered")

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'email' not in st.session_state:
    st.session_state['email'] = None
if 'bg_color' not in st.session_state:
    st.session_state['bg_color'] = '#f0f2f6'
if 'form_success' not in st.session_state:
    st.session_state['form_success'] = False
if 'show_email_config' not in st.session_state:
    st.session_state['show_email_config'] = False
if 'department' not in st.session_state:
    st.session_state['department'] = None
if 'email_config' not in st.session_state:
    st.session_state['email_config'] = {'sender_email': '', 'app_password': ''}
if 'db_initialized' not in st.session_state:
    st.session_state['db_initialized'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None
if 'current_view' not in st.session_state:
    st.session_state['current_view'] = 'dashboard'

def apply_custom_theme():
    """Applies a professional, clean theme to the Streamlit app with dynamic background color."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {st.session_state['bg_color']};
        }}
        .css-1d37b8r {{ /* Main container */
            background-color: #ffffff;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            padding: 2rem;
        }}
        .stButton>button {{
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 20px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #45a049;
        }}
        .stTextInput>div>div>input {{
            border-radius: 8px;
        }}
        .stSelectbox>div>div {{
            border-radius: 8px;
        }}
        .css-1g6x55m {{ /* Login/Register tabs */
            background-color: #f9f9f9;
            border-radius: 10px;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: #f0f2f6;
            border-radius: 4px 4px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: #fff;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def registration_page():
    """Renders the user registration form."""
    st.title("User Registration 📝")
    departments = db.get_departments()
    with st.form(key='registration_form'):
        role = st.selectbox("Select Role", ["Student", "Staff", "HOD"])
        email_addr = st.text_input("Email", key='reg_email')
        username = st.text_input("Username", key='reg_username')
        password = st.text_input("Password", type="password", key='reg_password')
        
        name = st.text_input("Full Name")
        
        # Display department dropdown based on role
        if departments:
            department_name = st.selectbox("Department", [d['Deptname'] for d in departments])
        else:
            department_name = st.text_input("Department (e.g., MCA, B.Tech)")
        
        phone = st.text_input("Mobile Number")

        submit_button = st.form_submit_button(label="Register")
        if submit_button:
            if role == "Student":
                if db.register_student(name, email_addr, username, password, department_name, phone):
                    st.success("Student registration successful! You can now log in.")
                    
                    # Check if email credentials are set before attempting to send.
                    sender_email = st.session_state['email_config']['sender_email']
                    app_password = st.session_state['email_config']['app_password']
                    if sender_email and app_password:
                        subject = "Welcome to Leave Management System"
                        body = (
                            f"Dear {name},\n\n"
                            f"You have been successfully registered to the Leave Management System as a {role}.\n\n"
                            f"Your username is: {username}\n\n"
                            "Regards,\nLeave Management System"
                        )
                        email.send_email(email_addr, subject, body, sender_email, app_password)
                    else:
                        st.warning("Registration successful, but email notifications are disabled.")
                    
                    st.session_state['form_success'] = True
                    st.rerun()
                else:
                    st.error("Student registration failed. Email or username might already exist.")
                    st.session_state['form_success'] = False
            
            elif role == "Staff":
                if db.register_staff(name, email_addr, username, password, department_name, phone):
                    st.success("Staff registration successful! You can now log in.")

                    sender_email = st.session_state['email_config']['sender_email']
                    app_password = st.session_state['email_config']['app_password']
                    if sender_email and app_password:
                        subject = "Welcome to Leave Management System"
                        body = (
                            f"Dear {name},\n\n"
                            f"You have been successfully registered to the Leave Management System as a {role}.\n\n"
                            f"Your username is: {username}\n\n"
                            "Regards,\nLeave Management System"
                        )
                        email.send_email(email_addr, subject, body, sender_email, app_password)
                    else:
                        st.warning("Registration successful, but email notifications are disabled.")
                    st.session_state['form_success'] = True
                    st.rerun()
                else:
                    st.error("Staff registration failed. Email or username might already exist.")
                    st.session_state['form_success'] = False

            elif role == "HOD":
                if db.register_hod(name, email_addr, username, password, department_name, phone):
                    st.success("HOD registration successful! You can now log in.")
                    
                    sender_email = st.session_state['email_config']['sender_email']
                    app_password = st.session_state['email_config']['app_password']
                    if sender_email and app_password:
                        subject = "Welcome to Leave Management System"
                        body = (
                            f"Dear {name},\n\n"
                            f"You have been successfully registered to the Leave Management System as a {role}.\n\n"
                            f"Your username is: {username}\n\n"
                            "Regards,\nLeave Management System"
                        )
                        email.send_email(email_addr, subject, body, sender_email, app_password)
                    else:
                        st.warning("Registration successful, but email notifications are disabled.")
                    st.session_state['form_success'] = True
                    st.rerun()
                else:
                    st.error("HOD registration failed. Email or username might already exist.")
                    st.session_state['form_success'] = False
            else:
                st.error("Invalid role selected.")
                st.session_state['form_success'] = False


def login_page():
    """Renders the user login form."""
    st.title("User Login 🔑")
    with st.form(key='login_form'):
        role = st.selectbox("Select Role", ["Student", "Staff", "HOD"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button(label="Log In")
        if submit_button:
            user = db.get_user(username, password, role)
            if user:
                print(f"User data fetched from database for {username}: {user}")
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.session_state['username'] = username
                st.session_state['email'] = user.get('email')
                st.session_state['department'] = user.get('department')
                st.session_state['user_data'] = user
                st.session_state['current_view'] = 'dashboard'
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username, password, or role.")

def email_configuration_page():
    """Allows users to configure email credentials."""
    st.title("Email Configuration ⚙️")
    st.warning("Please use an App Password for security, not your regular email password.")
    
    current_email_config = db.get_email_credentials()
    if current_email_config:
        current_email = current_email_config.get('sender_email', '')
    else:
        current_email = ''

    with st.form(key='email_config_form'):
        sender_email = st.text_input("Sender Email", value=current_email)
        app_password = st.text_input("App Password", type="password")
        
        save_button = st.form_submit_button(label="Save Credentials")
        if save_button:
            if db.update_email_credentials(sender_email, app_password):
                st.session_state['email_config'] = {'sender_email': sender_email, 'app_password': app_password}
                st.success("Email credentials saved successfully!")
                st.rerun()
            else:
                st.error("Failed to save credentials.")

def my_profile_page():
    """Renders the user's profile information."""
    st.title(f"My Profile - {st.session_state['username']}")
    st.write("Here are your details:")
    
    user_data = st.session_state['user_data']
    
    if user_data:
        st.subheader("Personal Information")
        st.write(f"**Name:** {user_data.get('name', 'N/A')}")
        st.write(f"**Username:** {user_data.get('username', 'N/A')}")
        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
        st.write(f"**Role:** {st.session_state['user_role']}")
        st.write(f"**Department:** {user_data.get('department', 'N/A')}")
        st.write(f"**Mobile No.:** {user_data.get('phone', 'N/A')}")
    else:
        st.error("User data not found.")

def student_dashboard():
    """Renders the dashboard for a Student user."""
    st.title(f"Student Dashboard - {st.session_state['username']}")
    st.write("Apply for leave here.")
    
    st.markdown("---")
    
    # Leave application form
    with st.form("leave_application_form"):
        st.subheader("New Leave Application")
        leave_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Vacation Leave"])
        start_date = st.date_input("Start Date", date.today())
        end_date = st.date_input("End Date", date.today())
        reason = st.text_area("Reason for Leave")
        
        apply_button = st.form_submit_button("Submit Application")
        
        if apply_button:
            if start_date > end_date:
                st.error("Start date cannot be after end date.")
            else:
                application_successful = db.apply_for_leave(
                    username=st.session_state['username'],
                    role=st.session_state['user_role'],
                    email=st.session_state['email'],
                    leave_type=leave_type,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    reason=reason,
                )
                
                if application_successful:
                    st.success("Leave application submitted successfully!")
                    
                    # Notify HOD by email
                    hod_email = db.get_hod_email_by_department(st.session_state['department'])
                    sender_email = st.session_state['email_config']['sender_email']
                    app_password = st.session_state['email_config']['app_password']
                    
                    if hod_email and sender_email and app_password:
                        subject = "New Leave Request from a Student"
                        body = (
                            f"Dear HOD,\n\n"
                            f"A new leave request has been submitted by student {st.session_state['username']}.\n\n"
                            f"Details:\n"
                            f"Name: {st.session_state['user_data']['name']}\n"
                            f"Department: {st.session_state['department']}\n"
                            f"Leave Type: {leave_type}\n"
                            f"Period: {start_date} to {end_date}\n"
                            f"Reason: {reason}\n\n"
                            f"Please log in to the system to review and approve the request.\n\n"
                            "Regards,\nLeave Management System"
                        )
                        email.send_email(hod_email, subject, body, sender_email, app_password)
                        st.info(f"Notification email sent to HOD at {hod_email}")
                    else:
                        st.warning("HOD email not found or email configuration is missing. Notification not sent.")
                    st.rerun()
                else:
                    st.error("Failed to submit application. There might be an overlapping leave request.")
                    
    st.markdown("---")
        # ==========================
    # Leave summary (Student)
    # ==========================
    my_requests_df = db.get_my_leave_requests(st.session_state['username'])

    st.markdown("### 📊 Leave Summary")
    if not my_requests_df.empty:
        total = len(my_requests_df)
        approved = len(my_requests_df[my_requests_df['status'] == 'Approved'])
        rejected = len(my_requests_df[my_requests_df['status'] == 'Rejected'])
        pending = len(my_requests_df[my_requests_df['status'] == 'Pending'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
        col2.metric("Approved", approved)
        col3.metric("Rejected", rejected)
        col4.metric("Pending", pending)

        st.markdown("---")
        st.subheader("My Leave History")
        st.dataframe(my_requests_df)
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", 0)
        col2.metric("Approved", 0)
        col3.metric("Rejected", 0)
        col4.metric("Pending", 0)

        st.markdown("---")
        st.subheader("My Leave History")
        st.info("You have not submitted any leave requests yet.")

    
    # Display my leave requests
    #st.subheader("My Leave History")
   # my_requests_df = db.get_my_leave_requests(st.session_state['username'])
    #if not my_requests_df.empty:
        #st.dataframe(my_requests_df)
    #else:
        #st.info("You have not submitted any leave requests yet.")


def staff_dashboard():
    """Renders the dashboard for a Staff user."""
    st.title(f"Staff Dashboard - {st.session_state['username']}")
    st.write("Apply for leave here.")
    
    st.markdown("---")
    
    # Leave application form
    with st.form("leave_application_form_staff"):
        st.subheader("New Leave Application")
        leave_type = st.selectbox("Leave Type", ["Casual Leave", "Sick Leave", "Maternity/Paternity Leave"])
        start_date = st.date_input("Start Date", date.today())
        end_date = st.date_input("End Date", date.today())
        reason = st.text_area("Reason for Leave")
        
        apply_button = st.form_submit_button("Submit Application")
        
        if apply_button:
            if start_date > end_date:
                st.error("Start date cannot be after end date.")
            else:
                application_successful = db.apply_for_leave(
                    username=st.session_state['username'],
                    role=st.session_state['user_role'],
                    email=st.session_state['email'],
                    leave_type=leave_type,
                    start_date=start_date.strftime("%Y-%m-%d"),
                    end_date=end_date.strftime("%Y-%m-%d"),
                    reason=reason,
                )
                
                if application_successful:
                    st.success("Leave application submitted successfully!")
                    
                    # Notify HOD by email
                    hod_email = db.get_hod_email_by_department(st.session_state['department'])
                    sender_email = st.session_state['email_config']['sender_email']
                    app_password = st.session_state['email_config']['app_password']
                    
                    if hod_email and sender_email and app_password:
                        subject = "New Leave Request from Staff"
                        body = (
                            f"Dear HOD,\n\n"
                            f"A new leave request has been submitted by staff member {st.session_state['username']}.\n\n"
                            f"Details:\n"
                            f"Name: {st.session_state['user_data']['name']}\n"
                            f"Department: {st.session_state['department']}\n"
                            f"Leave Type: {leave_type}\n"
                            f"Period: {start_date} to {end_date}\n"
                            f"Reason: {reason}\n\n"
                            f"Please log in to the system to review and approve the request.\n\n"
                            "Regards,\nLeave Management System"
                        )
                        email.send_email(hod_email, subject, body, sender_email, app_password)
                        st.info(f"Notification email sent to HOD at {hod_email}")
                    else:
                        st.warning("HOD email not found or email configuration is missing. Notification not sent.")
                    st.rerun()
                else:
                    st.error("Failed to submit application. There might be an overlapping leave request.")

    st.markdown("---")
        # ==========================
    # Leave summary (Staff)
    # ==========================
    my_requests_df = db.get_my_leave_requests(st.session_state['username'])

    st.markdown("### 📊 Leave Summary")
    if not my_requests_df.empty:
        total = len(my_requests_df)
        approved = len(my_requests_df[my_requests_df['status'] == 'Approved'])
        rejected = len(my_requests_df[my_requests_df['status'] == 'Rejected'])
        pending = len(my_requests_df[my_requests_df['status'] == 'Pending'])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", total)
        col2.metric("Approved", approved)
        col3.metric("Rejected", rejected)
        col4.metric("Pending", pending)

        st.markdown("---")
        st.subheader("My Leave History")
        st.dataframe(my_requests_df)
    else:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total", 0)
        col2.metric("Approved", 0)
        col3.metric("Rejected", 0)
        col4.metric("Pending", 0)

        st.markdown("---")
        st.subheader("My Leave History")
        st.info("You have not submitted any leave requests yet.")

    
    # Display my leave requests
    #st.subheader("My Leave History")
    #my_requests_df = db.get_my_leave_requests(st.session_state['username'])
    #if not my_requests_df.empty:
        #st.dataframe(my_requests_df)
    #else:
        #st.info("You have not submitted any leave requests yet.")


def hod_dashboard():
    """Renders the dashboard for an HOD user."""
    st.title(f"HOD Dashboard - {st.session_state['username']}")
    st.write(f"Welcome, Head of Department ({st.session_state['department']}). Here you can manage leave requests.")
    # 📊 Leave Summary by Name
st.subheader("📊 Leave Summary")

leave_summary = db.get_leave_summary_by_name(st.session_state['department'])

if leave_summary["Student"]:
    st.write("### Student Leave Summary:")
    for name, count in leave_summary["Student"].items():
        st.write(f"- {name}: {count} Approved Leaves")
else:
    st.info("No approved student leaves yet.")

if leave_summary["Staff"]:
    st.write("### Staff Leave Summary:")
    for name, count in leave_summary["Staff"].items():
        st.write(f"- {name}: {count} Approved Leaves")
else:
    st.info("No approved staff leaves yet.")

        # Display total approved leaves summary
    totals = db.get_total_leaves_by_role(st.session_state['department'])
    st.markdown("### 📊 Leave Summary")
    st.write(f"**Total Approved Student Leaves:** {totals['Student']}")
    st.write(f"**Total Approved Staff Leaves:** {totals['Staff']}")
    st.markdown("---")


    st.markdown("---")

    # Display pending leave requests
    st.subheader("Pending Leave Requests")
    pending_requests_df = db.get_leave_requests(st.session_state['department'], "Pending")
    
    if not pending_requests_df.empty:
        for index, row in pending_requests_df.iterrows():
            with st.expander(f"Leave Request from {row['username']} ({row['leave_type']})"):
                st.write(f"**Name:** {row['name']}")
                st.write(f"**Role:** {row['role']}")
                st.write(f"**Email:** {row['email']}")
                st.write(f"**Leave Type:** {row['leave_type']}")
                st.write(f"**Period:** {row['start_date']} to {row['end_date']}")
                st.write(f"**Reason:** {row['reason']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Approve", key=f"approve_{row['id']}"):
                        db.update_leave_status(row['id'], "Approved")
                        st.success(f"Approved leave for {row['username']}.")
                        
                        # Send approval email to the user who requested the leave and HOD
                        sender_email = st.session_state['email_config']['sender_email']
                        app_password = st.session_state['email_config']['app_password']

                        # Email to the applicant
                        if sender_email and app_password:
                            subject = "Leave Request Approved"
                            body = f"Dear {row['name']},\n\nYour leave request from {row['start_date']} to {row['end_date']} has been APPROVED.\n\nRegards,\nLeave Management System"
                            email.send_email(row['email'], subject, body, sender_email, app_password)
                        
                        # Email to HOD
                        if sender_email and app_password:
                            hod_email = st.session_state['email']
                            subject_hod = "Leave Request Status Update"
                            body_hod = f"You have successfully APPROVED the leave request for {row['name']}."
                            email.send_email(hod_email, subject_hod, body_hod, sender_email, app_password)
                        
                        if not sender_email or not app_password:
                            st.warning("Email credentials not configured. Emails not sent.")
                        st.rerun()
                with col2:
                    if st.button("Reject", key=f"reject_{row['id']}"):
                        db.update_leave_status(row['id'], "Rejected")
                        st.error(f"Rejected leave for {row['username']}.")
                        
                        # Send rejection email to the user who requested the leave and HOD
                        sender_email = st.session_state['email_config']['sender_email']
                        app_password = st.session_state['email_config']['app_password']

                        # Email to the applicant
                        if sender_email and app_password:
                            subject = "Leave Request Rejected"
                            body = f"Dear {row['name']},\n\nYour leave request from {row['start_date']} to {row['end_date']} has been REJECTED.\n\nRegards,\nLeave Management System"
                            email.send_email(row['email'], subject, body, sender_email, app_password)

                        # Email to HOD
                        if sender_email and app_password:
                            hod_email = st.session_state['email']
                            subject_hod = "Leave Request Status Update"
                            body_hod = f"You have successfully REJECTED the leave request for {row['name']}."
                            email.send_email(hod_email, subject_hod, body_hod, sender_email, app_password)

                        if not sender_email or not app_password:
                            st.warning("Email credentials not configured. Emails not sent.")
                        st.rerun()
    else:
        st.info("No pending leave requests at the moment.")

    st.markdown("---")
    
    # Display previous requests (Approved/Rejected)
    st.subheader("Previous Leave Requests")
    previous_requests_df = db.get_leave_requests(st.session_state['department'], "Previous")
    if not previous_requests_df.empty:
        st.dataframe(previous_requests_df)
    else:
        st.info("No previous leave requests to display.")

def db_setup_page():
    """Renders a page for database initialization."""
    st.title("Database Setup")
    st.info("It looks like this is the first time you're running the app. Click the button to initialize the database with some default users.")
    if st.button("Initialize Database"):
        if db.init_db():
            st.success("Database initialized successfully! You can now log in.")
            st.session_state['db_initialized'] = True
            st.rerun()
        else:
            st.error("Failed to initialize database. Please check the logs.")

def main():
    """Main function to run the Streamlit app."""
    apply_custom_theme()
    
    # Check if email credentials exist in the database and load them into session state
    if not st.session_state['email_config']['sender_email']:
        email_config_from_db = db.get_email_credentials()
        if email_config_from_db:
            st.session_state['email_config'] = email_config_from_db

    with st.sidebar:
        st.title("Leave Management System")
        if st.session_state['logged_in']:
            st.sidebar.success(f"Logged in as {st.session_state['username']} ({st.session_state['user_role']})")
            
            # Navigation buttons for the main content
            if st.button("Dashboard", key="nav_dashboard"):
                st.session_state['current_view'] = 'dashboard'
            if st.button("My Profile", key="nav_profile"):
                st.session_state['current_view'] = 'profile'

            if st.sidebar.button("Logout", key="sidebar_logout"):
                st.session_state['logged_in'] = False
                st.session_state['user_role'] = None
                st.session_state['username'] = None
                st.session_state['email'] = None
                st.session_state['department'] = None
                st.session_state['user_data'] = None
                st.rerun()
        else:
            st.warning("Please log in to continue.")

    # Main content based on login status and DB existence
    if not st.session_state['db_initialized']:
        db_setup_page()
    elif st.session_state['logged_in']:
        if st.session_state['current_view'] == 'dashboard':
            if st.session_state['user_role'] == "Student":
                student_dashboard()
            elif st.session_state['user_role'] == "Staff":
                staff_dashboard()
            elif st.session_state['user_role'] == "HOD":
                hod_dashboard()
            
            # Add email configuration to the sidebar for logged-in users
            st.markdown("---")
            st.subheader("App Configuration")
            with st.expander("Configure Email"):
                email_configuration_page()
        elif st.session_state['current_view'] == 'profile':
            my_profile_page()

    else:
        # Default view for not logged in users after DB is initialized
        st.title("Leave Management System")
        st.info("A simple and efficient way to manage leave applications for students and staff.")
        
        # Tabs for login, registration, and email configuration
        tab1, tab2, tab3 = st.tabs(["Log In", "Register", "Email Configuration"])
        
        with tab1:
            login_page()
            
        with tab2:
            registration_page()
        
        with tab3:
            email_configuration_page()


if __name__ == "__main__":
    main()
