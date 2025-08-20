import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time
from datetime import datetime

# === Auto-start file server ===
def start_file_server():
    try:
        folder_to_serve = r"C:\PN-RE-LAB-Server"  # server-side folder
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

def list_files_fast(folder: str):
    try:
        with os.scandir(folder) as it:
            files = []
            for entry in it:
                if entry.is_file():
                    try:
                        stat = entry.stat()
                        files.append({
                            "name": entry.name,
                            "path": entry.path,
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                        })
                    except FileNotFoundError:
                        continue
            # newest first
            files.sort(key=lambda x: x["mtime"], reverse=True)
            return files
    except FileNotFoundError:
        return []

# === Branding assets ===
logo_path = "WD logo.png"
background_path = "Slide1.PNG"
logo_base64 = get_base64(logo_path)
bg_base64 = get_base64(background_path)

# === Streamlit config and styles ===
st.set_page_config("RE PN LAB Dashboard", layout="wide")
st.markdown(f"""<style>
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
h1, h2, h3, h4, h5, h6, .stMarkdown {{
    color: #ffffff !important;
    text-shadow: 0 0 8px #00fff2;
}}
.stButton>button, .stDownloadButton>button {{
    background-color: #00ffe1;
    color: #000000;
    font-weight: bold;
    border-radius: 10px;
}}
.missing-local {{
    background-color: rgba(255, 0, 0, 0.20);
    padding: 2px 6px;
    border-radius: 6px;
}}
.file-row {{
    padding: 6px 8px;
    border-radius: 10px;
    margin-bottom: 6px;
}}
.file-row:hover {{
    background: rgba(255,255,255,0.06);
}}
</style>""", unsafe_allow_html=True)

# === WD Logo Header ===
st.markdown(
    f'<div style="display: flex; justify-content: center; align-items: center; gap: 12px;">'
    f'<img src="data:image/png;base64,{logo_base64}" style="height: 40px;">'
    f'<h1>RE PN LAB Dashboard</h1></div>',
    unsafe_allow_html=True
)

# === Password Authentication ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        with st.form("login_form", clear_on_submit=False):
            password = st.text_input("🔐 Enter Password", type="password", key="password_input")
            submitted = st.form_submit_button("Login")
            if submitted:
                if password == "PNRELAB":
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# === Config Constants ===
SERVER_FOLDER = r"C:\PN-RE-LAB-Server"  # server upload folder
LOCAL_FOLDER  = r"C:\PN-RE-LAB"         # local PC folder
os.makedirs(SERVER_FOLDER, exist_ok=True)
os.makedirs(LOCAL_FOLDER, exist_ok=True)

# === Spotfire URLs ===
SPOTFIRE_MI_URLS = { "TRH": "...", "HACT": "...", "HEAD WEAR": "..."}  # truncated for brevity
SPOTFIRE_CHEMLAB_URLS = {"GCMS":"...", "ICA":"..."}  # truncated

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === Tabs ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Upload Handler ===
def handle_upload(selected_test, category):
    file = st.file_uploader(f"Upload Excel File for {category}", type=["xlsx"])
    if file:
        # server folder
        folder = os.path.join(SERVER_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        server_path = os.path.join(folder, file.name)
        with open(server_path, "wb") as f:
            f.write(file.getbuffer())
        st.success(f"✅ Saved to server: {server_path}")

        # local sync (optional immediate copy)
        local_folder = os.path.join(LOCAL_FOLDER, selected_test)
        os.makedirs(local_folder, exist_ok=True)
        local_path = os.path.join(local_folder, file.name)
        try:
            shutil.copy2(server_path, local_path)
            st.success(f"💾 Automatically copied to local: {local_path}")
        except Exception as e:
            st.warning(f"⚠️ Could not copy to local immediately: {e}")

        st.download_button("📥 Download", data=open(server_path, "rb").read(), file_name=file.name)

# === Tab Actions ===
if selected_tab == "📁 MI Upload":
    st.subheader("🛠️ Upload MI Test File")
    selected_test = st.selectbox("Select MI Test", mi_tests)
    handle_upload(selected_test, "MI Test")

elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    handle_upload(selected_test, "Chemlab Test")

elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category=="MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category=="MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f"🔗 [Open {selected} Dashboard]({urls[selected]})", unsafe_allow_html=True)

elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")
    for test in mi_tests + cl_tests:
        folder = os.path.join(SERVER_FOLDER, test)
        files = list_files_fast(folder)
        if not files:
            st.info(f"No files in {test}")
            continue
        for f in files:
            fname = f["name"]
            file_path = f["path"]
            st.markdown(f"- {fname} ({human_size(f['size'])})")
            st.download_button("Download", data=open(file_path,"rb").read(), file_name=fname)
