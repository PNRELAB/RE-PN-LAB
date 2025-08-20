import streamlit as st
import os
import shutil
import base64
from datetime import datetime

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

# === Streamlit config ===
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

# === Password Authentication ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        with st.form("login_form", clear_on_submit=False):
            password = st.text_input("🔐 Enter Password", type="password")
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
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"
LOCAL_SAVE_FOLDER   = r"C:\\PN-RE-LAB"
os.makedirs(LOCAL_SAVE_FOLDER, exist_ok=True)

SPOTFIRE_MI_URLS = {"TRH":"...", "HACT":"...", "HEAD WEAR":"..."}
SPOTFIRE_CHEMLAB_URLS = {"AD COBALT":"...", "ICA":"...", "GCMS":"..."}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === Tabs ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Upload Handler ===
def handle_upload(selected_test, category, urls_dict):
    file = st.file_uploader(f"Upload Excel File for {category}", type=["xlsx"])
    if file:
        # Save to temp first
        temp_path = os.path.join(SHARED_UPLOAD_FOLDER, "temp_upload.xlsx")
        with open(temp_path, "wb") as f:
            f.write(file.getbuffer())

        # Save to local folder
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        os.makedirs(local_folder, exist_ok=True)
        local_path = os.path.join(local_folder, file.name)
        shutil.copy2(temp_path, local_path)

        # Save to Spotfire folder
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        os.makedirs(spotfire_folder, exist_ok=True)
        shutil.copy2(temp_path, os.path.join(spotfire_folder, file.name))

        st.success(f"💾 File saved to local disk: {local_path}")
        st.success(f"📂 File copied to Spotfire folder: {spotfire_folder}")
        st.download_button("📥 Download This File", data=open(temp_path, "rb").read(), file_name=file.name)

# === Tab Actions ===
if selected_tab == "📁 MI Upload":
    st.subheader("🛠️ Upload MI Test File")
    selected_test = st.selectbox("Select MI Test", mi_tests)
    handle_upload(selected_test, "MI Test", SPOTFIRE_MI_URLS)

elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    handle_upload(selected_test, "Chemlab Test", SPOTFIRE_CHEMLAB_URLS)

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
        folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
        files = list_files_fast(folder)
        if files:
            with st.expander(f"📁 {test} — {len(files)} file(s)"):
                for f in files:
                    st.write(f"{f['name']} ({human_size(f['size'])})")
                    local_folder = os.path.join(LOCAL_SAVE_FOLDER, test)
                    os.makedirs(local_folder, exist_ok=True)
                    local_path = os.path.join(local_folder, f['name'])
                    if not os.path.exists(local_path):
                        if st.button(f"Copy to Local", key=f"copy_{test}_{f['name']}"):
                            shutil.copy2(f['path'], local_path)
                            st.success(f"Copied to local: {local_path}")

st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
