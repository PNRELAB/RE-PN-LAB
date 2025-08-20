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
.stTextInput > div > input[type="password"],
.stTextInput > div > input[type="text"] {{
    color: #000000 !important;
    background-color: #ffffff !important;
    font-weight: bold !important;
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
.stForm > div > button[type="submit"] {{
    color: #000000 !important;
    background-color: #ffffff !important;
    font-weight: bold !important;
    border-radius: 10px !important;
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
LOCAL_SAVE_FOLDER   = r"C:\\PN-RE-LAB"
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

# === Upload MI ===
if selected_tab == "📁 MI Upload":
    st.subheader("🛠️ Upload MI Test File")
    selected_test = st.selectbox("Select MI Test", mi_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        os.makedirs(folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)

        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        shutil.copy2(path, os.path.join(spotfire_folder, file.name))

        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        local_path, saved = save_to_local(path, local_folder)
        if saved is True:
            st.success(f"💾 File saved to local disk: `{local_path}`")
        elif saved is False:
            st.info(f"💾 File already exists in local folder: `{local_path}`")
        else:
            st.error(f"❌ Failed to save to local: {saved}")

        st.success(f"✅ File saved to Streamlit folder: `{path}`")
        st.success(f"📂 File copied to Spotfire folder: `{spotfire_folder}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)

# === Upload Chemlab ===
elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        os.makedirs(folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)

        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        shutil.copy2(path, os.path.join(spotfire_folder, file.name))

        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        local_path, saved = save_to_local(path, local_folder)
        if saved is True:
            st.success(f"💾 File saved to local disk: `{local_path}`")
        elif saved is False:
            st.info(f"💾 File already exists in local folder: `{local_path}`")
        else:
            st.error(f"❌ Failed to save to local: {saved}")

        st.success(f"✅ File saved to Streamlit folder: `{path}`")
        st.success(f"📂 File copied to Spotfire folder: `{spotfire_folder}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)

# === View Spotfire Dashboard ===
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category == "MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({urls[selected]})", unsafe_allow_html=True)

# === Uploaded Log (Professional with Select All) ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")
    page_size = st.slider("Rows per page", 5, 100, 20, 5)

    # --- Function defined first ---
    def render_uploaded_log(test_list, title):
        st.markdown(f"### {title}")

        for test in test_list:
            stream_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
            local_folder = os.path.join(LOCAL_SAVE_FOLDER, test)

            os.makedirs(stream_folder, exist_ok=True)
            os.makedirs(archive_folder, exist_ok=True)
            os.makedirs(local_folder, exist_ok=True)

            files = list_files_fast(stream_folder)
            total = len(files)

            with st.expander(f"📁 {test} — {total} file(s)", expanded=False):
                if total == 0:
                    st.info("No files in this test yet.")
                    continue

                # --- Select All checkbox ---
                all_selected = st.checkbox(f"Select All for {test}", key=f"select_all_{test}")
                if all_selected:
                    selected_files = [f["name"] for f in files]
                else:
                    selected_files = st.multiselect("Select files", [f["name"] for f in files], key=f"select_{test}")

                # --- Batch action buttons ---
                col_download, col_archive, col_delete = st.columns([1,1,1])
                with col_download:
                    if st.button("📥 Download Selected", key=f"batch_download_{test}"):
                        for fname in selected_files:
                            path = os.path.join(stream_folder, fname)
                            if os.path.exists(path):
                                with open(path, "rb") as f:
                                    st.download_button(
                                        label=f"Download {fname}",
                                        data=f.read(),
                                        file_name=fname,
                                        key=f"download_{test}_{fname}_batch"
                                    )
                with col_archive:
                    if st.button("🗄 Archive Selected", key=f"batch_archive_{test}"):
                        st.warning("⚠️ Are you sure you want to archive the selected files?")
                        confirm = st.button("✅ Yes, archive selected", key=f"confirm_batch_archive_{test}")
                        if confirm:
                            for fname in selected_files:
                                src = os.path.join(stream_folder, fname)
                                dst = os.path.join(archive_folder, fname)
                                try:
                                    shutil.move(src, dst)
                                except Exception as e:
                                    st.error(f"Failed to archive {fname}: {e}")
                            st.success("Selected files archived.")
                            st.experimental_rerun()
                with col_delete:
                    if st.button("❌ Delete Selected", key=f"batch_delete_{test}"):
                        st.warning("⚠️ Are you sure you want to delete the selected files?")
                        confirm = st.button("✅ Yes, delete selected", key=f"confirm_batch_delete_{test}")
                        if confirm:
                            for fname in selected_files:
                                path = os.path.join(stream_folder, fname)
                                try:
                                    os.remove(path)
                                except Exception as e:
                                    st.error(f"Failed to delete {fname}: {e}")
                            st.success("Selected files deleted.")
                            st.experimental_rerun()

                st.markdown("---")
                # --- Individual file rows ---
                for f in files:
                    name = f["name"]
                    stream_path = f["path"]
                    missing_local = not os.path.exists(os.path.join(local_folder, name))

                    st.markdown(f"<div class='file-row'>", unsafe_allow_html=True)
                    c1, c2, c3, c4, c5 = st.columns([0.5, 0.1, 0.1, 0.1, 0.1])
                    with c1:
                        st.markdown(f"**{name}**")
                        if missing_local:
                            st.caption("⚠️ Missing locally")
                    with c2:
                        st.markdown(f"<span class='file-size'>{human_size(f['size'])}</span>", unsafe_allow_html=True)
                    with c3:
                        st.markdown("<div class='download-btn'>", unsafe_allow_html=True)
                        st.download_button(
                            label="📥",
                            data=open(stream_path, "rb").read(),
                            file_name=name,
                            help="Download this file",
                            key=f"download_{test}_{name}",
                            use_container_width=True
                        )
                        st.markdown("</div>", unsafe_allow_html=True)
                    with c4:
                        if st.button("🗄", key=f"archive_{test}_{name}_prompt"):
                            st.warning(f"⚠️ Are you sure you want to archive **{name}**?")
                            confirm = st.button(f"✅ Yes, archive {name}", key=f"confirm_archive_{test}_{name}")
                            if confirm:
                                try:
                                    shutil.move(stream_path, os.path.join(archive_folder, name))
                                    st.success(f"Archived: {name}")
                                    st.experimental_rerun()
                    with c5:
                        if st.button("❌", key=f"delete_{test}_{name}_prompt"):
                            st.warning(f"⚠️ Are you sure you want to delete **{name}**?")
                            confirm = st.button(f"✅ Yes, delete {name}", key=f"confirm_delete_{test}_{name}")
                            if confirm:
                                try:
                                    os.remove(stream_path)
                                    st.success(f"Deleted: {name}")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete: {e}")
                    st.markdown("</div>", unsafe_allow_html=True)

    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
