import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

# Page Configuration for Premium Look (Choice A Layout)
st.set_page_config(page_title="Mohammad Group of Companies - RFQ Tracker", page_icon="📊", layout="wide")

# Custom Premium CSS UI Styling
st.markdown("""
    <style>
    /* Main App Background & Fonts */
    .stApp {
        background-color: #f8f9fa;
    }
    h1, h2, h3 {
        color: #1e293b !important;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
    }
    
    /* Choice A: Enhanced Custom Card Design for Rows */
    .rfq-row {
        background-color: #ffffff;
        padding: 16px 24px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05), 0 2px 4px -1px rgba(15, 23, 42, 0.02);
        margin-bottom: 14px;
        border-left: 5px solid #2563eb;
        transition: all 0.25s ease-in-out;
    }
    .rfq-row:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 20px -3px rgba(15, 23, 42, 0.08);
        border-left-width: 7px;
    }
    .rfq-urgent {
        border-left: 5px solid #dc2626 !important;
        background-color: #fef2f2;
    }
    .rfq-submitted {
        border-left: 5px solid #f59e0b !important; /* Orange/Yellow for Submitted */
        background-color: #fef3c7;
    }
    
    /* Sidebar Premium Customization */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }

    /* RED BACKGROUND WITH WHITE TEXT FOR LOGOUT BUTTON */
    div.stButton > button[key*="logout_btn"] {
        background-color: #dc2626 !important;
        border: 1px solid #dc2626 !important;
        border-radius: 6px !important;
        padding: 10px 16px !important;
    }
    div.stButton > button[key*="logout_btn"] p, 
    div.stButton > button[key*="logout_btn"] span,
    div.stButton > button[key*="logout_btn"] * {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    /* Custom Badges */
    .badge-company {
        font-size: 1.15rem;
        font-weight: 600;
        color: #0f172a;
    }
    .badge-number {
        background-color: #f1f5f9;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: monospace;
        color: #475569;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }
    .badge-status {
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 GOOGLE SHEETS CLOUD STORAGE CONFIGURATION
# ==========================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit#gid=0"
SHEET_NAME_RFQS = "Sheet1"
SHEET_NAME_CLIENTS = "Sheet2"

UPLOAD_DIR = "uploaded_rfqs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_csv_url(sheet_url, sheet_name):
    try:
        base_url = sheet_url.split('/edit')[0]
        return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    except:
        return ""

def create_empty_rfq_df():
    return pd.DataFrame(columns=['id', 'upload_date', 'client_name', 'rfq_number', 'last_date', 'file_paths', 'status', 'closing_date', 'submitted_file'])

def load_rfq_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME_RFQS)
    try:
        df = pd.read_csv(csv_url)
        df['id'] = df['id'].astype(str)
        return df
    except:
        return create_empty_rfq_df()

def load_client_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME_CLIENTS)
    try:
        df = pd.read_csv(csv_url)
        return df['name'].tolist()
    except:
        return ["Mohammad Group of Companies", "ABC Company", "XYZ Corporation", "Delight Equities"]

CREDENTIALS = {
    "admin": {"password": "qadeer963", "role": "Admin"},
    "staff": {"password": "staff963", "role": "User"}
}

# Session State Initializations
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.local_rfqs = None
    st.session_state.local_companies = None

if st.session_state.local_rfqs is None:
    st.session_state.local_rfqs = load_rfq_data()

# Ensure missing columns exist
for col in ['id', 'upload_date', 'client_name', 'rfq_number', 'last_date', 'file_paths', 'status', 'closing_date', 'submitted_file']:
    if col not in st.session_state.local_rfqs.columns:
        st.session_state.local_rfqs[col] = ""

st.session_state.local_rfqs = st.session_state.local_rfqs.fillna("")
st.session_state.local_rfqs['id'] = st.session_state.local_rfqs['id'].astype(str)

if st.session_state.local_companies is None:
    st.session_state.local_companies = load_client_data()

# Login Screen Layout
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("""
            <div style='background-color: white; padding: 40px; border-radius: 16px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border-top: 6px solid #2563eb;'>
                <h2 style='text-align: center; margin-bottom: 5px; font-size: 1.8rem;'>MOHAMMAD GROUP</h2>
                <p style='text-align: center; color: #64748b; font-size: 1rem; letter-spacing: 2px;'>Of Companies</p>
                <h4 style='text-align: center; color: #1e293b; font-weight: 500;'>🚀 RFQ Portal Cloud Sign In</h4>
            </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username").strip().lower()
        password = st.text_input("Password", type="password")
        
        if st.button("Secure Login", use_container_width=True):
            if username in CREDENTIALS and CREDENTIALS[username]["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = CREDENTIALS[username]["role"]
                st.rerun()
            else:
                st.error("Invalid Username or Password.")
else:
    st.sidebar.markdown("<h2 style='text-align:center; color:#ffffff;'>MOHAMMAD GROUP</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align:center; color:#3b82f6;'>Active Role: <b>{st.session_state.role}</b></p>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    companies = st.session_state.local_companies

    # Added New Tab "📩 Submitted RFQs" for Admin to view and close/win
    if st.session_state.role == "Admin":
        tabs = ["📊 Live Dashboard", "📩 Submitted RFQs", "➕ Add New RFQ", "🔍 Smart Reports", "🏢 Manage Companies"]
    else:
        tabs = ["📊 Live Dashboard", "➕ Add New RFQ"]
        
    choice = st.sidebar.radio("Navigate Menu", tabs)
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔒 Secure Logout", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # 1. LIVE DASHBOARD (Now shows ONLY On-Process/Pending RFQs)
    if choice == "📊 Live Dashboard":
        st.title("📊 Live RFQ Monitor (Pending Only)")
        
        df = st.session_state.local_rfqs
        active_df = df[df['status'] == 'On-Process'] if not df.empty else pd.DataFrame()
        
        if active_df.empty:
            st.info("Excellent! No pending RFQs to process.")
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            for index, row in active_df.iterrows():
                is_urgent = str(row['last_date']) <= today_str
                
                if is_urgent:
                    row_class = "rfq-row rfq-urgent"
                    status_badge = "<span class='badge-status' style='background-color: #fef2f2; color: #dc2626;'>🚨 Urgent / Overdue</span>"
                else:
                    row_class = "rfq-row"
                    status_badge = "<span class='badge-status' style='background-color: #e0f2fe; color: #0284c7;'>⚙️ On-Process</span>"
                
                st.markdown(f"""
                    <div class="{row_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 2; min-width: 200px;">
                                <span class="badge-company">{row['client_name']}</span> &nbsp;&nbsp;
                                <span class="badge-number">#{row['rfq_number']}</span> &nbsp;&nbsp;
                                {status_badge}
                            </div>
                            <div style="flex: 1.5; min-width: 150px; color: #64748b; font-size: 0.9rem;">
                                📅 Uploaded: <b>{row['upload_date']}</b>
                            </div>
                            <div style="flex: 1.5; min-width: 150px; color: #1e293b; font-weight: bold;">
                                ⏱️ Target Date: {row['last_date']}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_files, col_actions = st.columns([6, 4])
                with col_files:
                    st.markdown("<b>Enquiry Files:</b>", unsafe_allow_html=True)
                    raw_paths = row['file_paths']
                    paths = []
                    if raw_paths:
                        try:
                            paths = json.loads(str(raw_paths))
                        except:
                            paths = [raw_paths]
                    
                    if paths:
                        file_cols = st.columns(5)
                        for i, p in enumerate(paths):
                            if os.path.exists(str(p)):
                                with open(str(p), "rb") as file:
                                    with file_cols[i % 5]:
                                        st.download_button(label=f"📥 Doc {i+1}", data=file, file_name=os.path.basename(str(p)), key=f"dl_{row['id']}_{i}")
                    else:
                        st.caption("No initial attachments.")
                        
                with col_actions:
                    if st.button("📩 Submit Quotation", key=f"sub_panel_{row['id']}", use_container_width=True, type="primary"):
                        st.session_state[f"show_upload_{row['id']}"] = True

                if st.session_state.get(f"show_upload_{row['id']}", False):
                    st.markdown("<div style='background-color: #fef3c7; padding: 15px; border-radius: 8px; margin-top: 10px;'>", unsafe_allow_html=True)
                    st.markdown("🔒 **Attach Final Quotation File:**")
                    q_file = st.file_uploader("Choose file...", type=["pdf", "xlsx", "xls", "docx", "doc", "jpg", "jpeg", "png"], key=f"file_uploader_{row['id']}")
                    
                    col_sub1, col_sub2 = st.columns(2)
                    with col_sub1:
                        if st.button("Confirm & Save Submission", key=f"conf_sub_{row['id']}", type="primary"):
                            if q_file is not None:
                                q_file_name = f"SUBMITTED_{row['rfq_number']}_{q_file.name}"
                                q_file_path = os.path.join(UPLOAD_DIR, q_file_name)
                                with open(q_file_path, "wb") as f:
                                    f.write(q_file.getbuffer())
                                
                                st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'status'] = 'Submitted'
                                st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'submitted_file'] = q_file_path
                                st.session_state[f"show_upload_{row['id']}"] = False
                                st.success("Quotation submitted! Moved to 'Submitted' section.")
                                st.rerun()
                            else:
                                st.error("Please select a file first.")
                    with col_sub2:
                        if st.button("Cancel", key=f"cancel_sub_{row['id']}"):
                            st.session_state[f"show_upload_{row['id']}"] = False
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # 1b. NEW TAB: SUBMITTED RFQS (Admin Room to Win or Close)
    elif choice == "📩 Submitted RFQs" and st.session_state.role == "Admin":
        st.title("📩 Submitted Quotations Room")
        st.markdown("Review outgoing quotes and update final project conversions here.")
        
        df = st.session_state.local_rfqs
        submitted_df = df[df['status'] == 'Submitted'] if not df.empty else pd.DataFrame()
        
        if submitted_df.empty:
            st.info("No submitted quotations awaiting review right now.")
        else:
            for index, row in submitted_df.iterrows():
                st.markdown(f"""
                    <div class="rfq-row rfq-submitted">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 2; min-width: 200px;">
                                <span class="badge-company">{row['client_name']}</span> &nbsp;&nbsp;
                                <span class="badge-number">#{row['rfq_number']}</span> &nbsp;&nbsp;
                                <span class='badge-status' style='background-color: #fef3c7; color: #d97706;'>📩 Submitted</span>
                            </div>
                            <div style="flex: 1.5; min-width: 150px; color: #1e293b;">
                                ⏱️ Target Date: <b>{row['last_date']}</b>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_view, col_decision = st.columns([6, 4])
                with col_view:
                    sub_file_path = str(row['submitted_file'])
                    if sub_file_path and os.path.exists(sub_file_path):
                        with open(sub_file_path, "rb") as sf:
                            st.download_button(
                                label="📄 Download Outgoing Quotation File", 
                                data=sf, 
                                file_name=os.path.basename(sub_file_path), 
                                key=f"dl_sub_room_{row['id']}",
                                type="secondary"
                            )
                    else:
                        st.caption("No submission file found.")
                        
                with col_decision:
                    b_win, b_close = st.columns(2)
                    with b_win:
                        if st.button("🏆 Win Order", key=f"win_room_{row['id']}", use_container_width=True, type="primary"):
                            st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'status'] = 'Win'
                            st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'closing_date'] = datetime.now().strftime("%Y-%m-%d")
                            st.success("Deal logged as WON!")
                            st.rerun()
                    with b_close:
                        if st.button("❌ Close / Lost", key=f"close_room_{row['id']}", use_container_width=True):
                            st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'status'] = 'Closed'
                            st.session_state.local_rfqs.loc[st.session_state.local_rfqs['id'] == str(row['id']), 'closing_date'] = datetime.now().strftime("%Y-%m-%d")
                            st.success("Deal marked as Closed.")
                            st.rerun()
                st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

    # 2. Add New RFQ Screen
    elif choice == "➕ Add New RFQ":
        st.title("➕ Create New RFQ Entry")
        with st.container():
            selected_company = st.selectbox("🏢 Select Corporate Client", companies)
            rfq_num = st.text_input("📝 RFQ Reference / Number")
            last_dt = st.date_input("📅 Submission Deadline")
            uploaded_files = st.file_uploader("📎 Drop Documents / Sample Images here", type=["pdf", "xlsx", "xls", "docx", "doc", "jpg", "jpeg", "png"], accept_multiple_files=True)
            
            if st.button("🚀 Push to Cloud Dashboard", type="primary"):
                if rfq_num.strip() == "":
                    st.error("RFQ number cannot be empty.")
                else:
                    upload_date = datetime.now().strftime("%Y-%m-%d")
                    saved_paths = []
                    if uploaded_files:
                        for idx, file_obj in enumerate(uploaded_files):
                            file_name = f"{rfq_num}_{idx}_{file_obj.name}"
                            file_path = os.path.join(UPLOAD_DIR, file_name)
                            with open(file_path, "wb") as f:
                                f.write(file_obj.getbuffer())
                            saved_paths.append(file_path)
                    
                    new_id = str(len(st.session_state.local_rfqs) + 1)
                    new_row = {
                        'id': new_id, 'upload_date': upload_date, 'client_name': selected_company,
                        'rfq_number': rfq_num, 'last_date': str(last_dt), 'file_paths': json.dumps(saved_paths),
                        'status': 'On-Process', 'closing_date': '', 'submitted_file': ''
                    }
                    st.session_state.local_rfqs = pd.concat([st.session_state.local_rfqs, pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Data secured and pushed to dashboard successfully!")

    # 3. Reports & History View (Admin Only)
    elif choice == "🔍 Smart Reports" and st.session_state.role == "Admin":
        st.title("🔍 Advanced Audits & Reports")
        col1, col2, col3 = st.columns(3)
        with col1: from_date = st.date_input("Start Date", value=datetime.now().replace(day=1))
        with col2: to_date = st.date_input("End Date")
        with col3: status_filter = st.selectbox("Filter Status", ["All", "On-Process", "Submitted", "Win", "Closed"])
                
        df_report = st.session_state.local_rfqs.copy()
        
        if not df_report.empty:
            df_report = df_report[(df_report['upload_date'] >= str(from_date)) & (df_report['upload_date'] <= str(to_date))]
            if status_filter != "All":
                df_report = df_report[df_report['status'] == status_filter]
        
        st.markdown(f"📊 Summary Total Logs Found: **{len(df_report)}**")
        
        if not df_report.empty:
            processed_df = df_report.copy()
            processed_df['closing_date'] = processed_df['closing_date'].apply(lambda x: '⏱️ Pending / Active' if str(x).strip() == "" else x)
            
            display_cols = {
                'id': 'ID',
                'upload_date': 'Upload Date',
                'client_name': 'Corporate Client',
                'rfq_number': 'RFQ Reference',
                'last_date': 'Target Deadline',
                'status': 'Current Status',
                'closing_date': 'Closing Date',
                'submitted_file': 'Saved Attachment Path'
            }
            
            available_cols = [col for col in display_cols.keys() if col in processed_df.columns]
            df_display = processed_df[available_cols].rename(columns=display_cols)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No records match the selected date range or filter.")

    # 4. Manage Companies View
    elif choice == "🏢 Manage Companies" and st.session_state.role == "Admin":
        st.title("🏢 Corporate Clients Database")
        
        col_list, col_add = st.columns([6, 4])
        
        with col_list:
            st.subheader("📋 Registered Companies")
            if not companies:
                st.info("No companies registered yet.")
            else:
                for comp in companies:
                    c1, c2 = st.columns([7, 3])
                    with c1:
                        st.markdown(f"🏢 **{comp}**")
                    with c2:
                        if st.button(f"🗑️ Delete", key=f"del_{comp}", use_container_width=True):
                            st.session_state.local_companies.remove(comp)
                            st.success(f"'{comp}' has been removed!")
                            st.rerun()
                                
        with col_add:
            st.subheader("➕ Add New Corporate Client")
            new_comp_name = st.text_input("Enter Company Name", placeholder="e.g., Delight Equities", key="new_company_input").strip()
            
            if st.button("🚀 Register Company", type="primary", use_container_width=True):
                if new_comp_name == "":
                    st.error("Company name cannot be blank.")
                elif new_comp_name in companies:
                    st.warning("This company is already registered!")
                else:
                    st.session_state.local_companies.append(new_comp_name)
                    st.success(f"'{new_comp_name}' successfully added to database!")
                    st.rerun()