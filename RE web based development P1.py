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
        folder_to_serve = r"C:\PN-RE-LAB"
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
h1, h2, h3, h4, h5, h6, .stMarkdown {{
    color: #ffffff !important;
    text-shadow: 0 0 8px #00fff2;
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
.file-row {{
    padding: 6px 8px;
    border-radius: 10px;
    margin-bottom: 6px;
}}
.file-row:hover {{
    background: rgba(255,255,255,0.06);
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

# === Multi-User Authentication ===
USERS = {
    "user1": "PNRELAB",
    "user2": "PNRELAB123"
}

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["username"] = None

def check_password():
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if username in USERS and USERS[username] == password:
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.success(f"Welcome {username}")
                    st.rerun()
                else:
                    st.error("❌ Incorrect username or password")
        return False
    return True

if not check_password():
    st.stop()

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"C:\PN-RE-LAB"
LOCAL_SAVE_FOLDER = os.path.join(SHARED_UPLOAD_FOLDER, "UPLOADS")
os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

SPOTFIRE_MI_URLS = {
    "TRH": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/TRH",
    "HACT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HACT",
    "HEAD WEAR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HeadWear",
    "FLYABILITY": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/flyability",
    "HBOT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/hbot",
    "SBT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/sbt",
    "ADT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/adt"
}

SPOTFIRE_CHEMLAB_URLS = {
    "AD COBALT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/ADCobalt",
    "ICA": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/ICA",
    "GCMS": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/gcms",
    "LCQTOF": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/lcqtof",
    "FTIR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/ftir"
}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === Tabs ===
if "selected_tab" not in st.session_state:
    st.session_state.selected_tab = "📁 MI Upload"

tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, index=tabs.index(st.session_state.selected_tab), label_visibility="collapsed")
st.session_state.selected_tab = selected_tab

# === Helper: Save uploaded file persistently ===
def save_to_local(file_bytes, dst_folder, filename):
    os.makedirs(dst_folder, exist_ok=True)
    dst_path = os.path.join(dst_folder, filename)
    with open(dst_path, "wb") as f:
        f.write(file_bytes)
    return dst_path

# === Upload Sections ===
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        user_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test, st.session_state["username"])
        os.makedirs(user_folder, exist_ok=True)
        file_bytes = file.read()
        save_path = save_to_local(file_bytes, user_folder, file.name)

        # Copy to Spotfire folder
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        os.makedirs(spotfire_folder, exist_ok=True)
        shutil.copy2(save_path, os.path.join(spotfire_folder, file.name))

        st.success(f"💾 File saved to local folder: `{save_path}`")
        st.success(f"📂 Copied to Spotfire folder: `{spotfire_folder}`")
        st.download_button("📥 Download This File", data=file_bytes, file_name=file.name)

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
    st.subheader("📋 Uploaded Log")
    page_size = st.slider("Rows per page", 5, 100, 20, 5)

    def render_uploaded_log(test_list, title):
        st.markdown(f"### {title}")
        container = st.container()
        for test in test_list:
            user_folder = os.path.join(LOCAL_SAVE_FOLDER, test, st.session_state["username"])
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test, st.session_state["username"])
            os.makedirs(user_folder, exist_ok=True)
            os.makedirs(archive_folder, exist_ok=True)

            files = list_files_fast(user_folder)
            total = len(files)
            with container.expander(f"📁 {test} — {total} file(s)", expanded=False):
                if total == 0:
                    st.info("No files in this test yet.")
                    continue

                page_files = files[:page_size]

                for f in page_files:
                    name = f["name"]
                    file_path = f["path"]

                    c1, c2, c3, c4, c5 = st.columns([0.3, 0.2, 0.2, 0.2, 0.2])
                    with c1: st.write(name)
                    with c2: st.write(f"Size: {human_size(f['size'])}")

                    # Download button
                    with c3:
                        with open(file_path, "rb") as file_data:
                            st.download_button(
                                label="📥",
                                data=file_data.read(),
                                file_name=name,
                                key=f"download_{test}_{name}"
                            )

                    # Archive
                    with c4:
                        if st.button("📂 Archive", key=f"archive_{test}_{name}"):
                            try:
                                shutil.move(file_path, os.path.join(archive_folder, name))
                                st.success(f"Archived: {name}")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to archive: {e}")

                    # Delete
                    with c5:
                        if st.button("🗑️ Delete", key=f"delete_{test}_{name}"):
                            try:
                                os.remove(file_path)
                                st.success(f"Deleted: {name}")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")

    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
