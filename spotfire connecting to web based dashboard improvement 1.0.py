import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time
import urllib.parse

# === Auto-start file server ===
def start_file_server():
    folder_to_serve = r"C:\\PN-RE-LAB"
    if not os.path.exists(folder_to_serve):
        os.makedirs(folder_to_serve, exist_ok=True)
    try:
        port = 8080  # changed from 8502 to 8080 for example
        command = [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--directory",
            folder_to_serve,
        ]
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        st.info(f"File server started on http://localhost:{port}")
    except Exception as e:
        st.warning(f"⚠️ Failed to start file server: {e}")

# Uncomment this if you want the server to start automatically
# start_file_server()

# === Image to base64 ===
def get_base64(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_path = "WD logo.png"
background_path = "Slide1.PNG"

logo_base64 = get_base64(logo_path)
bg_base64 = get_base64(background_path)

# === Streamlit config and styles ===
st.set_page_config("RE PN LAB Dashboard", layout="wide")

st.markdown(
    f"""
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
.footer {{
    text-align: center;
    margin-top: 20px;
    font-size: 14px;
    color: #00ffe1;
}}
</style>
""",
    unsafe_allow_html=True,
)

# === WD Logo Header ===
st.markdown(
    f'<div style="display: flex; justify-content: center; align-items: center; gap: 12px;">'
    f'<img src="data:image/png;base64,{logo_base64}" style="height: 40px;">'
    f'<h1>RE PN LAB Dashboard</h1></div>',
    unsafe_allow_html=True,
)

# === Password Authentication ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "rerun_needed" not in st.session_state:
        st.session_state["rerun_needed"] = False

    if not st.session_state["authenticated"]:
        with st.form("login_form", clear_on_submit=False):
            password = st.text_input("🔐 Enter Password", type="password", key="password_input")
            submitted = st.form_submit_button("Login")
            if submitted:
                if password == "PNRELAB":
                    st.session_state["authenticated"] = True
                    st.session_state["rerun_needed"] = True
                else:
                    st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

if st.session_state.get("rerun_needed", False):
    st.session_state["rerun_needed"] = False
    st.experimental_rerun()

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"

SPOTFIRE_MI_URLS = {
    "TRH": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/TRH/Overview",
    "HACT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/HACT/Report",
    "HEAD WEAR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/HeadWear/Dashboard",
    "FLYABILITY": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/flyability/Dashboard",
    "HBOT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/hbot/Dashboard",
    "SBT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/sbt/Dashboard",
    "ADT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/adt/Dashboard",
}

SPOTFIRE_CHEMLAB_URLS = {
    "AD COBALT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADCobalt/Dashboard",
    "ICA": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ICA/Dashboard",
    "GCMS": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/gcms/Dashboard",
    "LCQTOF": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/lcqtof/Dashboard",
    "FTIR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ftir/Dashboard",
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
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        url_path = f"{urllib.parse.quote(selected_test)}/{urllib.parse.quote(file.name)}"
        web_file_url = f"http://localhost:8080/{url_path}"

        st.success(f"✅ File saved to `{path}`")
        with open(path, "rb") as f_read:
            st.download_button("📥 Download This File", data=f_read.read(), file_name=file.name)
        st.markdown(f"🔗 [🌐 Open File for Spotfire]({web_file_url})", unsafe_allow_html=True)
        st.markdown(f"🔗 [📈 Open {selected_test} Dashboard in Spotfire]({SPOTFIRE_MI_URLS[selected_test]})", unsafe_allow_html=True)

# === Upload Chemlab ===
elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        url_path = f"{urllib.parse.quote(selected_test)}/{urllib.parse.quote(file.name)}"
        web_file_url = f"http://localhost:8080/{url_path}"

        st.success(f"✅ File saved to `{path}`")
        with open(path, "rb") as f_read:
            st.download_button("📥 Download This File", data=f_read.read(), file_name=file.name)
        st.markdown(f"🔗 [🌐 Open File for Spotfire]({web_file_url})", unsafe_allow_html=True)
        st.markdown(f"🔗 [📈 Open {selected_test} Dashboard in Spotfire]({SPOTFIRE_CHEMLAB_URLS[selected_test]})", unsafe_allow_html=True)

# === View Spotfire Dashboard ===
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category == "MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({urls[selected]})", unsafe_allow_html=True)

# === Uploaded Log ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")

    def show_uploaded_files(test_list, spotfire_dict, title):
        st.markdown(f"### {title}")
        for test in test_list:
            folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
            os.makedirs(archive_folder, exist_ok=True)
            if os.path.isdir(folder):
                files = os.listdir(folder)
                if files:
                    st.markdown(f"#### 📁 {test}")
                    selected_files = []
                    select_all = st.checkbox(f"Select All ({test})", key=f"all_{test}")
                    for file in files:
                        file_path = os.path.join(folder, file)
                        col1, col2, col3 = st.columns([0.05, 0.5, 0.45])
                        with col1:
                            checked = st.checkbox("", key=f"{test}_{file}", value=select_all)
                            if checked:
                                selected_files.append(file)
                        with col2:
                            size_kb = os.path.getsize(file_path) // 1024
                            st.markdown(f"**{file}** ({size_kb} KB)")
                        with col3:
                            with open(file_path, "rb") as f_read:
                                st.download_button("📥 Download", f_read.read(), file_name=file, key=f"dl_{test}_{file}")
                            link = spotfire_dict.get(test)
                            if link:
                                st.markdown(f"[🔗 Open in Spotfire]({link})", unsafe_allow_html=True)
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"🗑 Delete Selected in {test}", key=f"del_{test}"):
                            for file in selected_files:
                                try:
                                    os.remove(os.path.join(folder, file))
                                except Exception as e:
                                    st.error(f"Failed to delete {file}: {e}")
                            st.success("✅ Files deleted")
                            st.experimental_rerun()
                    with colB:
                        if st.button(f"📦 Archive Selected in {test}", key=f"arc_{test}"):
                            for file in selected_files:
                                try:
                                    shutil.move(os.path.join(folder, file), os.path.join(archive_folder, file))
                                except Exception as e:
                                    st.error(f"Failed to archive {file}: {e}")
                            st.success("📦 Files archived")
                            st.experimental_rerun()

    show_uploaded_files(mi_tests, SPOTFIRE_MI_URLS, "🛠 MI Tests")
    st.markdown("---")
    show_uploaded_files(cl_tests, SPOTFIRE_CHEMLAB_URLS, "🧪 Chemlab Tests")

# === Footer ===
st.markdown(
    "<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True
)
