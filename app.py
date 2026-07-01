import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
import requests

# Page Configuration for Premium Look
st.set_page_config(page_title="Mohammad Group of Companies - RFQ Tracker", page_icon="📊", layout="wide")

# Custom Premium CSS UI Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    h1, h2, h3 { color: #1e293b !important; font-family: 'Inter', sans-serif; font-weight: 700; }
    
    .rfq-row {
        background-color: #ffffff; padding: 16px 24px; border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.05); margin-bottom: 14px;
        border-left: 5px solid #2563eb; transition: all 0.25s ease-in-out;
    }
    .rfq-row:hover { transform: translateY(-2px); box-shadow: 0 12px 20px -3px rgba(15, 23, 42, 0.08); }
    .rfq-urgent { border-left: 5px solid #dc2626 !important; background-color: #fef2f2; }
    .rfq-submitted { border-left: 5px solid #10b981 !important; background-color: #f0fdf4; }
    .rfq-won { border-left: 5px solid #059669 !important; background-color: #ecfdf5; }
    .rfq-lost { border-left: 5px solid #94a3b8 !important; background-color: #f8fafc; }
    
    [data-testid="stSidebar"] { background-color: #0f172a !important; }
    [data-testid="stSidebar"] * { color: #f1f5f9 !important; }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label { color: #cbd5e1 !important; }

    div.stButton > button[key*="logout_btn"] {
        background-color: #dc2626 !important; border: 1px solid #dc2626 !important;
        border-radius: 6px !important; padding: 10px 16px !important;
    }
    div.stButton > button[key*="logout_btn"] * { color: #ffffff !important; font-weight: 700 !important; }
    
    .badge-company { font-size: 1.15rem; font-weight: 600; color: #0f172a; }
    .badge-number { background-color: #f1f5f9; padding: 4px 10px; border-radius: 6px; font-family: monospace; }
    .badge-status { padding: 4px 10px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 🌐 GOOGLE SHEETS CLOUD INTEGRATION
# ==========================================
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1bQW4xzwQnjs1CSiCQoC2A1Vg9w1uHtqfj5Yel_9iR3A/edit?usp=sharing"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyJci8IkG9ueY3oJmw1QQfBnFIO-FSUwMcun8cckYm_kXx0lZJ0MRvODI2-000gn9Ne/exec"

SHEET_NAME_RFQS = "Sheet1"
SHEET_NAME_CLIENTS = "Sheet2"

UPLOAD_DIR = "uploaded_rfqs"
SYNC_FILE = "server_sync.json"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def get_global_submitted_rfqs():
    if not os.path.exists(SYNC_FILE):
        return {}
    try:
        with open(SYNC_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def add_global_submission(rfq_id, rfq_data):
    sync_data = get_global_submitted_rfqs()
    sync_data[str(rfq_id)] = rfq_data
    try:
        with open(SYNC_FILE, "w") as f:
            json.dump(sync_data, f)
    except:
        pass

def remove_global_submission(rfq_id):
    sync_data = get_global_submitted_rfqs()
    if str(rfq_id) in sync_data:
        del sync_data[str(rfq_id)]
        try:
            with open(SYNC_FILE, "w") as f:
                json.dump(sync_data, f)
        except:
            pass

def get_csv_url(sheet_url, sheet_name):
    base_url = sheet_url.split('/edit')[0]
    return f"{base_url}/gviz/tq?tqx=out:csv&sheet={sheet_name}&nocache={int(datetime.now().timestamp())}"

def load_rfq_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME_RFQS)
    try:
        df = pd.read_csv(csv_url)
        df['id'] = df['id'].astype(str)
        if 'status' in df.columns:
            df['status'] = df['status'].astype(str).str.strip().str.lower()
        return df.fillna("")
    except:
        return pd.DataFrame(columns=['id', 'upload_date', 'client_name', 'rfq_number', 'last_date', 'file_paths', 'status', 'closing_date', 'submitted_file'])

def load_client_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME_CLIENTS)
    try:
        df = pd.read_csv(csv_url)
        return df.fillna("").iloc[:, 0].tolist()
    except:
        return ["Mohammad Group of Companies", "Delight Equities"]

def save_to_google_sheet(sheet_name, row_data):
    try:
        payload = {'sheet': sheet_name, 'data': json.dumps(row_data)}
        response = requests.post(APPS_SCRIPT_URL, params=payload)
        return response.text == "Success"
    except:
        return False

def update_rfq_status_on_cloud(rfq_id, status, closing_date, submitted_file):
    try:
        payload = {
            'action': 'update_status',
            'sheet': SHEET_NAME_RFQS,
            'id': str(rfq_id),
            'status': status,
            'closing_date': closing_date,
            'submitted_file': submitted_file
        }
        response = requests.post(APPS_SCRIPT_URL, params=payload)
        return response.text == "Success"
    except:
        return False

CREDENTIALS = {
    "admin": {"password": "qadeer963", "role": "Admin"},
    "staff": {"password": "staff963", "role": "User"}
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

companies = load_client_data()

# Login Screen
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
    
    tabs = ["📊 Live Dashboard", "📩 Submitted RFQs", "➕ Add New RFQ", "🏢 Manage Companies"] if st.session_state.role == "Admin" else ["📊 Live Dashboard", "➕ Add New RFQ", "📩 Submitted RFQs"]
    choice = st.sidebar.radio("Navigate Menu", tabs)
    st.sidebar.markdown("---")
    
    if st.sidebar.button("🔒 Secure Logout", key="logout_btn", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    local_rfqs = load_rfq_data()
    global_submitted = get_global_submitted_rfqs()

    # 📅 GLOBAL DATE FILTER UI ON SIDEBAR
    st.sidebar.markdown("### 📅 Filter by Upload Date")
    from_date = st.sidebar.date_input("From Date", value=pd.to_datetime("2026-01-01"))
    to_date = st.sidebar.date_input("To Date", value=pd.to_datetime("2026-12-31"))

    def is_in_date_range(date_str):
        try:
            target_dt = pd.to_datetime(date_str).date()
            return from_date <= target_dt <= to_date
        except:
            return True

    # 1. LIVE DASHBOARD
    if choice == "📊 Live Dashboard":
        col_title, col_ref = st.columns([8, 2])
        with col_title:
            st.title("📊 Live RFQ Monitor (Pending Only)")
        with col_ref:
            if st.button("🔄 Sync Panel", use_container_width=True):
                st.rerun()

        if not local_rfqs.empty and 'status' in local_rfqs.columns:
            active_df = local_rfqs[local_rfqs['status'] == 'on-process']
        else:
            active_df = pd.DataFrame()
        
        if not active_df.empty:
            active_df = active_df[~active_df['id'].astype(str).isin(list(global_submitted.keys()))]
            # Apply Date Filter
            active_df = active_df[active_df['upload_date'].apply(is_in_date_range)]
        
        if active_df.empty:
            st.info("Excellent! No pending RFQs found in this date range.")
        else:
            today_str = datetime.now().strftime("%Y-%m-%d")
            for index, row in active_df.iterrows():
                row_id = str(row['id'])
                is_urgent = str(row['last_date']) <= today_str
                status_badge = "<span class='badge-status' style='background-color: #fef2f2; color: #dc2626;'>🚨 Urgent</span>" if is_urgent else "<span class='badge-status' style='background-color: #e0f2fe; color: #0284c7;'>⚙️ On-Process</span>"
                
                st.markdown(f"""
                    <div class="rfq-row {'rfq-urgent' if is_urgent else ''}">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 2;"><span class="badge-company">{row['client_name']}</span> &nbsp;&nbsp;<span class="badge-number">#{row['rfq_number']}</span> &nbsp;&nbsp;{status_badge}</div>
                            <div style="flex: 1.5; color: #64748b;">📅 Uploaded: <b>{row['upload_date']}</b></div>
                            <div style="flex: 1.5; color: #1e293b; font-weight: bold;">⏱️ Deadline: {row['last_date']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_files, col_actions = st.columns([6, 4])
                with col_files:
                    raw_paths = row['file_paths']
                    if raw_paths:
                        try: paths = json.loads(str(raw_paths))
                        except: paths = [raw_paths]
                        for i, p in enumerate(paths):
                            if os.path.exists(str(p)):
                                with open(str(p), "rb") as file:
                                    st.download_button(label=f"📥 Doc {i+1}", data=file, file_name=os.path.basename(str(p)), key=f"dl_{row_id}_{i}")
                    else: st.caption("No initial attachments.")
                        
                with col_actions:
                    if st.button("📩 Submit Quotation", key=f"sub_panel_{row_id}", use_container_width=True, type="primary"):
                        st.session_state[f"show_upload_{row_id}"] = True

                if st.session_state.get(f"show_upload_{row_id}", False):
                    current_version = st.session_state.get(f"uploader_version_{row_id}", 0)
                    uploader_key = f"file_uploader_{row_id}_{current_version}"
                    
                    q_file = st.file_uploader("Choose final quotation file...", key=uploader_key)
                    
                    if st.button("Confirm & Save Submission", key=f"conf_sub_{row_id}", type="primary"):
                        if q_file:
                            q_file_name = f"SUBMITTED_{row['rfq_number']}_{q_file.name}"
                            q_file_path = os.path.join(UPLOAD_DIR, q_file_name)
                            with open(q_file_path, "wb") as f: f.write(q_file.getbuffer())
                            
                            today_date = datetime.now().strftime("%Y-%m-%d")
                            
                            update_rfq_status_on_cloud(row_id, "Submitted", today_date, q_file_path)
                            
                            submission_data = {
                                "id": str(row_id),
                                "client_name": row['client_name'],
                                "rfq_number": row['rfq_number'],
                                "upload_date": row['upload_date'],
                                "closing_date": today_date,
                                "submitted_file": q_file_path,
                                "status": "submitted"
                            }
                            add_global_submission(row_id, submission_data)
                            
                            st.success("🎉 Quotation submitted successfully!")
                            st.session_state[f"uploader_version_{row_id}"] = current_version + 1
                            st.session_state[f"show_upload_{row_id}"] = False
                            st.rerun()
                        else:
                            st.error("Please attach a file first before confirming.")
                st.markdown("<br>", unsafe_allow_html=True)

    # 2. SUBMITTED RFQS TAB (WITH WIN/CLOSE ACTIONS)
    elif choice == "📩 Submitted RFQs":
        st.title("📩 Archive & Management of Quotations")
        
        if not local_rfqs.empty and 'status' in local_rfqs.columns:
            cloud_submitted = local_rfqs[local_rfqs['status'].isin(['submitted', 'won', 'lost', 'closed'])]
        else:
            cloud_submitted = pd.DataFrame()
            
        display_list = []
        seen_ids = set()
        
        for r_id, r_data in global_submitted.items():
            if is_in_date_range(r_data['upload_date']):
                display_list.append(r_data)
                seen_ids.add(str(r_id))
            
        if not cloud_submitted.empty:
            for index, row in cloud_submitted.iterrows():
                c_id = str(row['id'])
                if c_id not in seen_ids and is_in_date_range(row['upload_date']):
                    display_list.append({
                        "id": c_id,
                        "client_name": row['client_name'],
                        "rfq_number": row['rfq_number'],
                        "upload_date": row['upload_date'],
                        "closing_date": row['closing_date'],
                        "submitted_file": row['submitted_file'],
                        "status": row['status']
                    })
        
        if not display_list:
            st.info("No records found for the selected date range.")
        else:
            for item in display_list:
                item_status = item.get('status', 'submitted').lower()
                
                if item_status == "won":
                    row_css = "rfq-won"
                    badge = "<span class='badge-status' style='background-color: #d1fae5; color: #065f46;'>🏆 WON</span>"
                elif item_status == "lost":
                    row_css = "rfq-lost"
                    badge = "<span class='badge-status' style='background-color: #f1f5f9; color: #475569;'>❌ LOST</span>"
                elif item_status == "closed":
                    row_css = "rfq-lost"
                    badge = "<span class='badge-status' style='background-color: #fee2e2; color: #991b1b;'>🔒 CLOSED</span>"
                else:
                    row_css = "rfq-submitted"
                    badge = "<span class='badge-status' style='background-color: #e0f2fe; color: #0369a1;'>✅ Submitted</span>"

                st.markdown(f"""
                    <div class="rfq-row {row_css}">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                            <div style="flex: 2;"><span class="badge-company">{item['client_name']}</span> &nbsp;&nbsp;<span class="badge-number">#{item['rfq_number']}</span> &nbsp;&nbsp;{badge}</div>
                            <div style="flex: 1.5; color: #64748b;">📅 Recieved: {item['upload_date']}</div>
                            <div style="flex: 1.5; color: #0f172a; font-weight: bold;">📩 Updated On: {item['closing_date']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                col_dl, col_ops = st.columns([5, 5])
                with col_dl:
                    f_path = str(item['submitted_file'])
                    if f_path and os.path.exists(f_path):
                        with open(f_path, "rb") as file:
                            st.download_button(label="📥 Download Quotation", data=file, file_name=os.path.basename(f_path), key=f"dl_sub_{item['id']}")
                    else:
                        st.caption("📄 File archived on server.")
                
                with col_ops:
                    if st.session_state.role == "Admin" and item_status == "submitted":
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button("🏆 Win", key=f"win_{item['id']}", use_container_width=True):
                                update_rfq_status_on_cloud(item['id'], "Won", datetime.now().strftime("%Y-%m-%d"), item['submitted_file'])
                                remove_global_submission(item['id'])
                                st.success("Marked as WON")
                                st.rerun()
                        with c2:
                            if st.button("❌ Lost", key=f"lost_{item['id']}", use_container_width=True):
                                update_rfq_status_on_cloud(item['id'], "Lost", datetime.now().strftime("%Y-%m-%d"), item['submitted_file'])
                                remove_global_submission(item['id'])
                                st.success("Marked as LOST")
                                st.rerun()
                        with c3:
                            if st.button("🔒 Close", key=f"close_{item['id']}", use_container_width=True):
                                update_rfq_status_on_cloud(item['id'], "Closed", datetime.now().strftime("%Y-%m-%d"), item['submitted_file'])
                                remove_global_submission(item['id'])
                                st.success("Marked as CLOSED")
                                st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

    # 3. ADD NEW RFQ (🛑 WITH DUPLICATE REF CHECK FITTED)
    elif choice == "➕ Add New RFQ":
        st.title("➕ Create New RFQ Entry")
        selected_company = st.selectbox("🏢 Select Corporate Client", companies)
        rfq_num = st.text_input("📝 RFQ Reference / Number").strip()
        last_dt = st.date_input("📅 Submission Deadline")
        uploaded_files = st.file_uploader("📎 Drop Documents here", accept_multiple_files=True)
        
        if st.button("🚀 Push to Cloud Dashboard", type="primary"):
            if not rfq_num:
                st.error("RFQ number cannot be empty.")
            # 🛑 ڈپلیکیٹ کلاؤڈ چیک: اگر یہ نمبر پہلے سے موجود ہے تو ایرر دے گا
            elif not local_rfqs.empty and 'rfq_number' in local_rfqs.columns and rfq_num in local_rfqs['rfq_number'].astype(str).str.strip().values:
                st.error(f"⚠️ RFQ Number '#{rfq_num}' پہلے سے سسٹم میں موجود ہے! براہ کرم نیا یا یونیک نمبر درج کریں۔")
            else:
                new_id = str(int(datetime.now().timestamp()))
                upload_date = datetime.now().strftime("%Y-%m-%d")
                saved_paths = []
                if uploaded_files:
                    for idx, f_obj in enumerate(uploaded_files):
                        f_path = os.path.join(UPLOAD_DIR, f"{rfq_num}_{idx}_{f_obj.name}")
                        with open(f_path, "wb") as f: f.write(f_obj.getbuffer())
                        saved_paths.append(f_path)
                
                new_row = [new_id, upload_date, selected_company, rfq_num, str(last_dt), json.dumps(saved_paths), "On-Process", "", ""]
                
                if save_to_google_sheet(SHEET_NAME_RFQS, new_row):
                    st.success("🎉 RFQ Successfully pushed to live Google Sheet!")
                    st.rerun()
                else:
                    st.error("Cloud sync failed. Please check headers or Apps Script.")

    # 4. MANAGE COMPANIES
    elif choice == "🏢 Manage Companies" and st.session_state.role == "Admin":
        st.title("🏢 Corporate Clients Database")
        col_list, col_add = st.columns([6, 4])
        
        with col_list:
            st.subheader("📋 Registered Companies")
            for comp in companies:
                st.markdown(f"🏢 **{comp}**")
                                
        with col_add:
            st.subheader("➕ Add New Corporate Client")
            new_comp_name = st.text_input("Enter Company Name", key="new_company_input").strip()
            if st.button("🚀 Register Company", type="primary", use_container_width=True):
                if not new_comp_name: st.error("Name cannot be blank.")
                elif new_comp_name in companies: st.warning("Already exists!")
                else:
                    if save_to_google_sheet(SHEET_NAME_CLIENTS, [new_comp_name]):
                        st.success(f"'{new_comp_name}' successfully added to Google Sheet!")
                        st.rerun()
                    else:
                        st.error("Failed to add company to Cloud.")