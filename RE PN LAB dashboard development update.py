import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time
from datetime import datetime
import json

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

# === File notes helpers ===
def load_notes(folder):
    notes_path = os.path.join(folder, "file_notes.json")
    if os.path.exists(notes_path):
        with open(notes_path, "r") as f:
            return json.load(f)
    return {}

def save_notes(folder, notes_dict):
    notes_path = os.path.join(folder, "file_notes.json")
    with open(notes_path, "w") as f:
        json.dump(notes_dict, f, indent=2)

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
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"
LOCAL_SAVE_FOLDER   = os.path.join(SHARED_UPLOAD_FOLDER, "DOWNLOADS")
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
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Helper: save uploaded file to local safely ===
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

# === Upload Sections ===
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        stream_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        os.makedirs(stream_folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)
        os.makedirs(local_folder, exist_ok=True)

        stream_path = os.path.join(stream_folder, file.name)
        with open(stream_path, "wb") as f:
            f.write(file.read())

        shutil.copy2(stream_path, os.path.join(spotfire_folder, file.name))
        local_path, saved = save_to_local(stream_path, local_folder)

        st.success(f"💾 File saved in Streamlit folder: `{stream_path}`")
        st.success(f"📂 Copied to Spotfire folder: `{spotfire_folder}`")
        if saved is True:
            st.success(f"💾 File saved to Downloads folder: `{local_path}`")
        elif saved is False:
            st.info(f"💾 Already exists in Downloads folder: `{local_path}`")
        else:
            st.error(f"❌ Failed saving to Downloads folder: {saved}")

        st.download_button("📥 Download This File", data=open(stream_path, "rb").read(), file_name=file.name)

# === Uploaded Log with per-file notes ===
def render_uploaded_log(test_list, title):
    st.markdown(f"### {title}")
    container = st.container()
    for test in test_list:
        stream_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
        spot_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", test)
        archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, test)
        os.makedirs(stream_folder, exist_ok=True)
        os.makedirs(spot_folder, exist_ok=True)
        os.makedirs(archive_folder, exist_ok=True)
        os.makedirs(local_folder, exist_ok=True)

        # Load saved notes
        test_notes = load_notes(stream_folder)

        files = list_files_fast(stream_folder)
        total = len(files)
        with container.expander(f"📁 {test} — {total} file(s)", expanded=False):
            if total == 0:
                st.info("No files in this test yet.")
                continue

            for f in files[:20]:
                name = f["name"]
                stream_path = f["path"]

                c1, c2, c3, c4, c5, c6 = st.columns([0.3, 0.15, 0.15, 0.15, 0.15, 0.6])
                with c1: st.write(name)
                with c2: st.write(f"Size: {human_size(f['size'])}")

                # Download
                with c3:
                    try:
                        with open(stream_path, "rb") as file_data:
                            st.download_button(
                                label="📥",
                                data=file_data.read(),
                                file_name=name,
                                key=f"download_{test}_{name}"
                            )
                    except Exception as e:
                        st.error(f"Failed to prepare download: {e}")

                # Archive
                with c4:
                    if st.button("📂 Archive", key=f"archive_{test}_{name}"):
                        shutil.move(stream_path, os.path.join(archive_folder, name))
                        if name in test_notes:
                            test_notes.pop(name)
                            save_notes(stream_folder, test_notes)
                        st.success(f"Archived: {name}")
                        st.experimental_rerun()

                # Delete
                with c5:
                    if st.button("🗑️ Delete", key=f"delete_{test}_{name}"):
                        os.remove(stream_path)
                        if name in test_notes:
                            test_notes.pop(name)
                            save_notes(stream_folder, test_notes)
                        st.success(f"Deleted: {name}")
                        st.experimental_rerun()

                # Note input
                key_note = f"note_{test}_{name}"
                if key_note not in st.session_state:
                    st.session_state[key_note] = test_notes.get(name, "")
                with c6:
                    new_note = st.text_input("Add detail", value=st.session_state[key_note], key=key_note)
                    st.session_state[key_note] = new_note
                    test_notes[name] = new_note

        # Save notes
        save_notes(stream_folder, test_notes)

# === Tabs Handling ===
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

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
