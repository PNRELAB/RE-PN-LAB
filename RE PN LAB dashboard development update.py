import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time
import csv
from datetime import datetime
import pandas as pd

# === Auto-start file server ===
def start_file_server():
    try:
        folder_to_serve = r"C:\\PN-RE-LAB"
        port = 8502
        command = [sys.executable, "-m", "http.server", str(port), "--directory", folder_to_serve]
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)
    except Exception as e:
        st.warning(f"⚠️ Failed to start file server: {e}")

start_file_server()

# === Helpers ===
def get_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

# === Branding assets ===
logo_base64 = get_base64("WD logo.png")
bg_base64 = get_base64("Slide1.PNG")

# === Streamlit styles ===
st.set_page_config("RE PN LAB Dashboard", layout="wide")
st.markdown(f"""
<style>
html, body, .stApp {{
    background: url("data:image/png;base64,{bg_base64}") no-repeat center center fixed;
    background-size: cover;
    font-family: 'Orbitron', sans-serif;
    color: #ffffff;
}}
.block-container {{
    background: rgba(0, 0, 0, 0.75);
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 0 25px #00ffe1;
    color: #ffffff;
}}
.stFileUploader > div > div {{
    border: 2px dashed #00ffe1;
    background-color: rgba(0,255,255,0.05);
    border-radius: 10px;
    font-size: 20px !important;
}}
.stButton>button, .stDownloadButton>button {{
    background-color: #00ffe1;
    color: #000000;
    font-weight: bold;
    border-radius: 10px;
}}
</style>
""", unsafe_allow_html=True)

# === WD Logo Header ===
st.markdown(
    f'<div style="display: flex; justify-content: center; align-items: center; gap: 12px;">'
    f'<img src="data:image/png;base64,{logo_base64}" style="height: 40px;">'
    f'<h1>RE PN LAB Dashboard</h1></div>',
    unsafe_allow_html=True
)

# === PASSWORD-ONLY LOGIN (streamlit-cloud safe) ===
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    password_input = st.text_input("Enter Dashboard Password:", type="password")
    login_click = st.button("Login")

    if login_click and password_input == "PNRELAB":
        st.session_state["authenticated"] = True
        st.success("✅ Login successful!")

    if not st.session_state["authenticated"]:
        st.stop()  # blocks the app until authenticated

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"W:\PN\Department\Quality\Reliability & AS Lab\AS Lab\Automation for RE"
LOCAL_SAVE_FOLDER   = os.path.join(SHARED_UPLOAD_FOLDER, "DOWNLOADS")
LOG_CSV = os.path.join(SHARED_UPLOAD_FOLDER, "upload_log.csv")
os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

SPOTFIRE_MI_URLS = {"TRH":"...","HACT":"...","HEAD WEAR":"...","FLYABILITY":"...","HBOT":"...","SBT":"...","ADT":"..."}
SPOTFIRE_CHEMLAB_URLS = {"AD COBALT":"...","ICA":"...","GCMS":"...","LCQTOF":"...","FTIR":"..."}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === Helper: Log uploads ===
def log_upload(file_name, user_name, test_type, note=""):
    os.makedirs(SHARED_UPLOAD_FOLDER, exist_ok=True)
    header_needed = not os.path.exists(LOG_CSV)
    with open(LOG_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp","user","test_type","file_name","note"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([timestamp, user_name, test_type, file_name, note])

# === Upload Section ===
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    note = st.text_input("Optional note for this file")
    if uploaded_file:
        target_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(target_folder, exist_ok=True)
        file_path = os.path.join(target_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Log upload
        log_upload(uploaded_file.name, "PNRELAB_USER", selected_test, note)
        st.success(f"💾 File saved to: `{file_path}`")
        if note:
            st.info(f"📝 Note: {note}")
        # Download button
        st.download_button("📥 Download This File", data=open(file_path, "rb").read(), file_name=uploaded_file.name)

# === Uploaded Log Tab with Multi-Select & Select All ===
def render_uploaded_log():
    st.subheader("📋 Uploaded Log")
    if not os.path.exists(LOG_CSV):
        st.info("No uploads yet.")
        return

    # Load log CSV
    df = pd.read_csv(LOG_CSV)
    df = df.sort_values("timestamp", ascending=False)

    # Select test to filter
    test_types = df["test_type"].unique()
    selected_test = st.selectbox("Select Test to view files", test_types)
    filtered_df = df[df["test_type"] == selected_test]

    archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test, "archive")
    os.makedirs(archive_folder, exist_ok=True)

    # Multi-select setup
    st.markdown("### Select files to manage:")
    file_checkboxes = {}
    for idx, row in filtered_df.iterrows():
        file_path = os.path.join(SHARED_UPLOAD_FOLDER, row["test_type"], row["file_name"])
        if os.path.exists(file_path):
            label = f"{row['file_name']} — uploaded by {row['user']} at {row['timestamp']}"
            file_checkboxes[idx] = st.checkbox(label, key=f"cb_{idx}")

    # Select All button
    if st.button("Select All"):
        for idx in file_checkboxes:
            st.session_state[f"cb_{idx}"] = True

    # Archive selected
    if st.button("📦 Archive Selected"):
        for idx, checked in file_checkboxes.items():
            if checked:
                file_path = os.path.join(SHARED_UPLOAD_FOLDER, filtered_df.loc[idx, "test_type"],
                                         filtered_df.loc[idx, "file_name"])
                if os.path.exists(file_path):
                    shutil.move(file_path, os.path.join(archive_folder, os.path.basename(file_path)))
        st.success("📦 Selected files archived successfully!")

    # Delete selected
    if st.button("🗑️ Delete Selected"):
        for idx, checked in file_checkboxes.items():
            if checked:
                file_path = os.path.join(SHARED_UPLOAD_FOLDER, filtered_df.loc[idx, "test_type"],
                                         filtered_df.loc[idx, "file_name"])
                if os.path.exists(file_path):
                    os.remove(file_path)
        st.success("🗑️ Selected files deleted successfully!")

    # Remaining files
    st.write("---")
    st.markdown("### Remaining files:")
    for idx, row in filtered_df.iterrows():
        file_path = os.path.join(SHARED_UPLOAD_FOLDER, row["test_type"], row["file_name"])
        if os.path.exists(file_path):
            st.write(f"{row['file_name']} — uploaded by {row['user']} at {row['timestamp']}")
            st.download_button("📥 Download", data=open(file_path, "rb").read(), file_name=row["file_name"])

# === Tabs ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

if selected_tab == "📁 MI Upload":
    handle_upload("MI", mi_tests)
elif selected_tab == "📁 Chemlab Upload":
    handle_upload("Chemlab", cl_tests)
elif selected_tab == "📋 Uploaded Log":
    render_uploaded_log()

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
