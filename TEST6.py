import streamlit as st
import os
import shutil
import pandas as pd
from datetime import datetime

#===Config: Shared folder paths ====
SHARED_UPLOAD_FOLDER = r"\\mpl-op-genmp01.wdc.com\PN-RELAB\RE Ctrl Nasuni\Digitalization"
os.makedirs(SHARED_UPLOAD_FOLDER, exist_ok=True)

#===Helpers====
def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

def list_files_fast(folder: str):
    files_list = []
    for root, _, files in os.walk(folder):
        for file in files:
            try:
                path = os.path.join(root, file)
                stat = os.stat(path)
                files_list.append({
                    "name": file,
                    "path": path,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "folder": os.path.basename(root)
                })
            except FileNotFoundError:
                continue
    files_list.sort(key=lambda x: x["mtime"], reverse=True)
    return files_list

#===Load Employee List====
EMPLOYEE_LIST_PATH = os.path.join(SHARED_UPLOAD_FOLDER, "EMPLOYEE_LIST.xlsx")
def load_employee_list():
    if not os.path.exists(EMPLOYEE_LIST_PATH):
        st.error(f"Employee list file not found at {EMPLOYEE_LIST_PATH}")
        st.stop()
    try:
        df = pd.read_excel(EMPLOYEE_LIST_PATH, dtype=str)
        if 'Employee #' not in df.columns or 'Name' not in df.columns:
            st.error("Excel must have columns: 'Employee #' and 'Name'")
            st.stop()
        return df
    except Exception as e:
        st.error(f"Failed to read employee list: {e}")
        st.stop()

employee_df = load_employee_list()
employee_ids = employee_df['Employee #'].tolist()

#===Employee Login===
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["employee_id"] = None

def check_employee_id():
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            emp_id = st.text_input("Enter Employee #")
            submitted = st.form_submit_button("Login")
            if submitted:
                if emp_id in employee_ids:
                    st.session_state["authenticated"] = True
                    st.session_state["employee_id"] = emp_id
                    employee_name = employee_df.loc[employee_df['Employee #']==emp_id, 'Name'].values[0]
                    st.success(f"Welcome {employee_name}")
                    st.experimental_rerun()
                else:
                    st.error("Invalid Employee")
        return False
    return True

if not check_employee_id():
    st.stop()

# === Spotfire URLs ===
SPOTFIRE_MI_URLS = {
    "TRH": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/TRH",
    "HACT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HACT",
    "HEAD WEAR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HeadWear",
}

SPOTFIRE_CHEMLAB_URLS = {
    "GCMS": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/gcms",
    "LCQTOF": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/lcqtof",
}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

#===Tabs====
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Upload Section ===
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        emp_id = st.session_state["employee_id"]
        employee_name = employee_df.loc[employee_df['Employee #']==emp_id, 'Name'].values[0]

        test_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(test_folder, exist_ok=True)

        save_path = os.path.join(test_folder, file.name)
        with open(save_path, "wb") as f:
            f.write(file.read())

        st.success(f"💾 File saved to shared folder: `{save_path}`")
        st.download_button("📥 Download This File", data=open(save_path, "rb").read(), file_name=file.name)

# === Uploaded Log Section ===
def render_uploaded_log(tests_list, title):
    st.markdown(f"### {title}")
    container = st.container()
    page_size = st.slider("Rows per page", 5, 50, 20, 5, key=f"{title}_slider")
    for test in tests_list:
        test_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
        os.makedirs(test_folder, exist_ok=True)
        files = list_files_fast(test_folder)
        total = len(files)
        with container.expander(f"📁 {test} — {total} file(s)", expanded=False):
            if total == 0:
                st.info("No files in this test yet.")
                continue
            page_files = files[:page_size]
            for f in page_files:
                folder = f["folder"]
                c1, c2, c3 = st.columns([0.5, 0.2, 0.3])
                with c1: st.write(f"{f['name']} (Folder: {folder})")
                with c2: st.write(f"Size: {human_size(f['size'])}")
                with c3:
                    try:
                        with open(f["path"], "rb") as file_data:
                            st.download_button("📥", data=file_data.read(), file_name=f['name'])
                    except Exception as e:
                        st.error(f"Download failed: {e}")

# === Main Tabs ===
if selected_tab == "📁 MI Upload":
    handle_upload("MI", mi_tests)
elif selected_tab == "📁 Chemlab Upload":
    handle_upload("Chemlab", cl_tests)
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category == "MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f'<a href="{urls[selected]}" target="_blank">Open {selected} Dashboard in Spotfire</a>', unsafe_allow_html=True)
elif selected_tab == "📋 Uploaded Log":
    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
                     