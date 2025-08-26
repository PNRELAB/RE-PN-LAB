import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time
import pandas as pd
from datetime import datetime

# === Auto-start file server (optional) ===
def start_file_server():
    try:
        folder_to_serve = r"C:\PN-RE-LAB"
        port = 8502
        command = [sys.executable, "-m", "http.server", str(port), "--directory", folder_to_serve]
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    except Exception as e:
        st.warning(f"⚠️ Failed to start file server: {e}")

start_file_server()

# === Helpers ===
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
                    "employee": os.path.basename(os.path.dirname(path))  # Employee folder name
                })
            except FileNotFoundError:
                continue
    files_list.sort(key=lambda x: x["mtime"], reverse=True)
    return files_list

def save_to_local(src_path, dst_folder):
    os.makedirs(dst_folder, exist_ok=True)
    dst_path = os.path.join(dst_folder, os.path.basename(src_path))
    try:
        if os.path.abspath(src_path) != os.path.abspath(dst_path):
            shutil.copy2(src_path, dst_path)
        return dst_path, True
    except shutil.SameFileError:
        return dst_path, False
    except Exception as e:
        return dst_path, str(e)

# === Employee ID Login ===
EMPLOYEE_FILE = r"C:\PN-RE-LAB\employee_list.xlsx"
try:
    employee_df = pd.read_excel(EMPLOYEE_FILE, dtype=str)
    employee_ids = employee_df['EmployeeID'].tolist()
except Exception as e:
    st.error(f"Failed to load employee list: {e}")
    employee_ids = []

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["employee_id"] = None

def check_employee_id():
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            emp_id = st.text_input("Enter Employee ID")
            submitted = st.form_submit_button("Login")
            if submitted:
                if emp_id in employee_ids:
                    st.session_state["authenticated"] = True
                    st.session_state["employee_id"] = emp_id
                    st.success(f"Welcome Employee {emp_id}")
                    st.rerun()
                else:
                    st.error("❌ Invalid Employee ID")
        return False
    return True

if not check_employee_id():
    st.stop()

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"C:\PN-RE-LAB\UPLOADS"
LOCAL_SAVE_FOLDER   = os.path.join(SHARED_UPLOAD_FOLDER, "DOWNLOADS")
os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

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

# === Tabs ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Upload Section ===
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        user_id = st.session_state["employee_id"]
        user_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test, user_id)
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test, user_id)
        os.makedirs(user_folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)
        os.makedirs(local_folder, exist_ok=True)

        stream_path = os.path.join(user_folder, file.name)
        with open(stream_path, "wb") as f:
            f.write(file.read())

        # Copy to Spotfire
        shutil.copy2(stream_path, os.path.join(spotfire_folder, file.name))

        # Copy to local DOWNLOADS
        local_path, saved = save_to_local(stream_path, local_folder)

        st.success(f"💾 File saved in `{stream_path}`")
        st.success(f"📂 Copied to Spotfire folder: `{spotfire_folder}`")
        if saved is True:
            st.success(f"💾 Saved to Downloads: `{local_path}`")
        elif saved is False:
            st.info(f"💾 Already exists in Downloads: `{local_path}`")
        else:
            st.error(f"❌ Failed saving to Downloads: {saved}")

        st.download_button("📥 Download This File", data=open(stream_path, "rb").read(), file_name=file.name)

# === Uploaded Log Section (multi-user view) ===
def render_uploaded_log(test_list, title):
    st.markdown(f"### {title}")
    container = st.container()
    page_size = st.slider("Rows per page", 5, 50, 20, 5)

    for test in test_list:
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
                name = f["name"]
                employee = f["employee"]
                c1, c2, c3 = st.columns([0.4, 0.3, 0.3])
                with c1: st.write(f"{name} (by {employee})")
                with c2: st.write(f"Size: {human_size(f['size'])}")
                with c3:
                    try:
                        with open(f["path"], "rb") as file_data:
                            st.download_button("📥", data=file_data.read(), file_name=name)
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
    st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({urls[selected]})", unsafe_allow_html=True)
elif selected_tab == "📋 Uploaded Log":
    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
