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
.stTextInput label, .stTextInput div, .stTextInput input:not([type="password"]):not([type="text"]),
label, .css-10trblm, .css-1cpxqw2, .css-1v0mbdj,
.css-1qg05tj, .css-1fcdlhz, .css-14xtw13, .css-1offfwp,
.css-1d391kg, .stMarkdown p {{
    color: #ffffff !important;
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
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"  # Streamlit folders
LOCAL_SAVE_FOLDER   = r"C:\\PN-RE-LAB"   # Local disk folders (same path on local PC)
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

        # Save to local disk
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        os.makedirs(local_folder, exist_ok=True)
        local_path = os.path.join(local_folder, file.name)
        shutil.copy2(path, local_path)

        st.success(f"✅ File saved to Streamlit folder: `{path}`")
        st.success(f"📂 File copied to Spotfire folder: `{spotfire_folder}`")
        st.success(f"💾 File saved to local disk: `{local_path}`")
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

        # Save to local disk
        local_folder = os.path.join(LOCAL_SAVE_FOLDER, selected_test)
        os.makedirs(local_folder, exist_ok=True)
        local_path = os.path.join(local_folder, file.name)
        shutil.copy2(path, local_path)

        st.success(f"✅ File saved to Streamlit folder: `{path}`")
        st.success(f"📂 File copied to Spotfire folder: `{spotfire_folder}`")
        st.success(f"💾 File saved to local disk: `{local_path}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)

# === View Spotfire Dashboard ===
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category == "MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({urls[selected]})", unsafe_allow_html=True)

# === Uploaded Log (Optimized) ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")

    # Global controls
    page_size = st.slider("Rows per page", min_value=5, max_value=100, value=20, step=5)

    def render_test_section(test_list, title):
        st.markdown(f"### {title}")
        for test in test_list:
            streamlit_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
            spotfire_folder   = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", test)
            archive_folder    = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
            local_folder      = os.path.join(LOCAL_SAVE_FOLDER, test)
            os.makedirs(archive_folder, exist_ok=True)
            os.makedirs(spotfire_folder, exist_ok=True)
            os.makedirs(local_folder, exist_ok=True)

            files = list_files_fast(streamlit_folder)
            total = len(files)
            with st.expander(f"📁 {test} — {total} file(s)", expanded=False):
                if total == 0:
                    st.info("No files in this test yet.")
                    continue

                # Pagination state per test
                state_key = f"page_{test}"
                if state_key not in st.session_state:
                    st.session_state[state_key] = 1
                pages = max(1, (total + page_size - 1) // page_size)

                left, mid, right = st.columns([0.25, 0.5, 0.25])
                with left:
                    st.caption("Navigation")
                    prev = st.button("◀ Prev", key=f"prev_{test}")
                with mid:
                    st.caption("Page")
                    st.session_state[state_key] = st.number_input(
                        " ", min_value=1, max_value=pages, value=st.session_state[state_key], key=f"num_{test}")
                with right:
                    st.caption("Navigation")
                    nxt = st.button("Next ▶", key=f"next_{test}")

                if prev and st.session_state[state_key] > 1:
                    st.session_state[state_key] -= 1
                if nxt and st.session_state[state_key] < pages:
                    st.session_state[state_key] += 1

                start = (st.session_state[state_key] - 1) * page_size
                end   = min(start + page_size, total)
                page_files = files[start:end]

                # Bulk actions
                sel_all_key = f"sel_all_{test}_{start}"
                select_all = st.checkbox(f"Select all on this page ({len(page_files)})", key=sel_all_key)
                selected_files = []

                # Row header
                st.caption("Check ▸ Name ▸ Local Status ▸ Streamlit DL ▸ Local DL / Copy")

                for f in page_files:
                    name = f["name"]
                    stream_path = f["path"]
                    local_path = os.path.join(local_folder, name)
                    size = human_size(f["size"]) if os.path.exists(stream_path) else "?"
                    mtime = datetime.fromtimestamp(f["mtime"]).strftime("%Y-%m-%d %H:%M")
                    missing_local = not os.path.exists(local_path)

                    c1, c2, c3, c4, c5 = st.columns([0.06, 0.45, 0.18, 0.16, 0.15])
                    with c1:
                        if st.checkbox("", key=f"chk_{test}_{name}_{start}", value=select_all):
                            selected_files.append(name)
                    with c2:
                        row_html = f"<div class='file-row'>{name} — {size} — {mtime}</div>"
                        st.markdown(row_html, unsafe_allow_html=True)
                    with c3:
                        if missing_local:
                            st.markdown("<span class='missing-local'>Local copy missing ❌</span>", unsafe_allow_html=True)
                        else:
                            try:
                                lsize = human_size(os.path.getsize(local_path))
                                st.markdown(f"Local OK ({lsize})")
                            except FileNotFoundError:
                                st.markdown("<span class='missing-local'>Local copy missing ❌</span>", unsafe_allow_html=True)
                    with c4:
                        try:
                            with open(stream_path, "rb") as fp:
                                st.download_button("📥 Streamlit", fp.read(), file_name=name, key=f"dl_s_{test}_{name}_{start}")
                        except FileNotFoundError:
                            st.write("—")
                    with c5:
                        if os.path.exists(local_path):
                            try:
                                with open(local_path, "rb") as fp:
                                    st.download_button("💾 Local", fp.read(), file_name=name, key=f"dl_l_{test}_{name}_{start}")
                            except FileNotFoundError:
                                st.write("—")
                        else:
                            if st.button("Copy to Local", key=f"copy_{test}_{name}_{start}"):
                                try:
                                    shutil.copy2(stream_path, local_path)
                                    st.success(f"✅ Copied to local: {local_path}")
                                    st.experimental_rerun()
                                except Exception as e:
                                    st.error(f"Failed to copy: {e}")

                # Bulk buttons
                b1, b2, b3 = st.columns(3)
                with b1:
                    if st.button(f"🗑 Delete Selected (Streamlit)", key=f"del_{test}_{start}"):
                        for name in selected_files:
                            try:
                                os.remove(os.path.join(streamlit_folder, name))
                            except FileNotFoundError:
                                pass
                        st.success("✅ Deleted from Streamlit folder")
                        st.rerun()
                with b2:
                    if st.button(f"📦 Archive Selected (Streamlit)", key=f"arc_{test}_{start}"):
                        for name in selected_files:
                            src = os.path.join(streamlit_folder, name)
                            dst = os.path.join(archive_folder, name)
                            try:
                                shutil.move(src, dst)
                            except FileNotFoundError:
                                pass
                        st.success("📦 Archived in Streamlit folder")
                        st.rerun()
                with b3:
                    if st.button(f"💾 Copy All Missing to Local", key=f"copy_missing_{test}_{start}"):
                        copied = 0
                        for f in page_files:
                            name = f["name"]
                            src = f["path"]
                            dst = os.path.join(local_folder, name)
                            if not os.path.exists(dst):
                                try:
                                    shutil.copy2(src, dst)
                                    copied += 1
                                except Exception:
                                    pass
                        st.success(f"✅ Copied {copied} file(s) to local")
                        st.experimental_rerun()

                # Spotfire files
                st.divider()
                st.caption(f"Spotfire folder for {test}")
                spot_files = list_files_fast(spotfire_folder)
                if not spot_files:
                    st.info("Spotfire folder is empty.")
                else:
                    for sf in spot_files[:50]:  # safety cap
                        sp1, sp2 = st.columns([0.75, 0.25])
                        with sp1:
                            st.markdown(f"📄 {sf['name']} — {human_size(sf['size'])}")
                        with sp2:
                            try:
                                with open(sf["path"], "rb") as fp:
                                    st.download_button("Download", fp.read(), file_name=sf["name"], key=f"dl_sp_{test}_{sf['name']}")
                            except FileNotFoundError:
                                st.write("—")

    render_test_section(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_test_section(cl_tests, "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
