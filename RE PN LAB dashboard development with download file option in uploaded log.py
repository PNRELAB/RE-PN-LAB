# === RE PN LAB DASHBOARD — Streamlit Script ===

import streamlit as st
import pandas as pd
import os
import datetime
import base64
import subprocess
import sys
import time
import shutil

# === AUTO-START FILE SERVER ===
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

# === IMAGE SETUP ===
def get_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

logo_path = r"C:\\Users\\1000329829\\OneDrive - Western Digital\\WEB BASED WITH PYTHON\\WD logo.png"
background_path = r"C:\\Users\\1000329829\\OneDrive - Western Digital\\UI DASHBOARD\\web interface\\Slide1.PNG"

logo_base64 = get_base64(logo_path)
bg_base64 = get_base64(background_path)

# === STREAMLIT CONFIG ===
st.set_page_config(page_title="RE PN LAB Dashboard", layout="wide")

# === CSS STYLE ===
st.markdown(f'''
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
.footer {{
    text-align: center;
    color: #ccc;
    font-size: 18px;
    margin-top: 40px;
}}
</style>
''', unsafe_allow_html=True)

# === PASSWORD CHECK ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        st.markdown("### 🔐 Enter password to access RE PN LAB")
        password = st.text_input("Password", type="password", key="password_input")
        if password == "PNRELAB":
            st.session_state["authenticated"] = True
            st.rerun()
        elif password != "":
            st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# === CONFIG ===
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"

SPOTFIRE_MI_URLS = {
    "TRH": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/TRH/Overview",
    "HACT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/HACT/Report",
    "HEAD WEAR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/HeadWear/Dashboard",
    "FLYABILITY": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/flyability/Dashboard",
    "HBOT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/hbot/Dashboard",
    "SBT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/sbt/Dashboard",
    "ADT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/adt/Dashboard"
}

SPOTFIRE_CHEMLAB_URLS = {
    "AD COBALT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADCobalt/Dashboard",
    "ICA": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ICA/Dashboard",
    "GCMS": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/gcms/Dashboard",
    "LCQTOF": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/lcqtof/Dashboard",
    "FTIR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ftir/Dashboard"
}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
chemlab_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === HEADER ===
st.markdown(f"""
<div style="display: flex; justify-content: center; align-items: center; gap: 12px;">
    <img src="data:image/png;base64,{logo_base64}" style="height: 40px;">
    <h1>RE PN LAB Dashboard</h1>
</div>
""", unsafe_allow_html=True)

# === MAIN TABS ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, key="main_tab_select", label_visibility="collapsed")

# === 📁 MI Upload ===
if selected_tab == "📁 MI Upload":
    st.subheader("🛠️ Upload MI Test File")
    selected_mi_test = st.selectbox("Select MI Test", mi_tests)
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_mi_test)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ File saved to `{file_path}`")
        with open(file_path, "rb") as f:
            st.download_button("📥 Download This File", data=f.read(), file_name=uploaded_file.name)
        st.markdown(f"🔗 [Open Spotfire]({SPOTFIRE_MI_URLS[selected_mi_test]})", unsafe_allow_html=True)
        st.stop()

# === 📁 Chemlab Upload ===
elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_cl_test = st.selectbox("Select Chemlab Test", chemlab_tests)
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if uploaded_file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_cl_test)
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"✅ File saved to `{file_path}`")
        with open(file_path, "rb") as f:
            st.download_button("📥 Download This File", data=f.read(), file_name=uploaded_file.name)
        st.markdown(f"🔗 [Open Spotfire]({SPOTFIRE_CHEMLAB_URLS[selected_cl_test]})", unsafe_allow_html=True)
        st.stop()

# === 📈 View Spotfire Dashboard ===
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("💻 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    if category == "MI":
        selected = st.selectbox("Select MI Dashboard", mi_tests)
        st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({SPOTFIRE_MI_URLS[selected]})", unsafe_allow_html=True)
    else:
        selected = st.selectbox("Select Chemlab Dashboard", chemlab_tests)
        st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({SPOTFIRE_CHEMLAB_URLS[selected]})", unsafe_allow_html=True)

# === 📋 Uploaded Log ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📂 Uploaded Log")

    def show_uploaded_files(test_list, title):
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
                        path = os.path.join(folder, file)
                        col1, col2, col3 = st.columns([0.05, 0.7, 0.25])
                        with col1:
                            if st.checkbox("", key=f"{test}_{file}", value=select_all):
                                selected_files.append(file)
                        with col2:
                            st.markdown(f"**{file}** ({os.path.getsize(path)//1024} KB)")
                        with col3:
                            with open(path, "rb") as f:
                                st.download_button("📥 Download", data=f.read(), file_name=file, key=f"dl_{test}_{file}")

                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"🗑 Delete Selected in {test}", key=f"del_{test}"):
                            for file in selected_files:
                                os.remove(os.path.join(folder, file))
                            st.success("✅ Files deleted")
                            st.rerun()
                    with colB:
                        if st.button(f"📦 Archive Selected in {test}", key=f"arc_{test}"):
                            for file in selected_files:
                                shutil.move(os.path.join(folder, file), os.path.join(archive_folder, file))
                            st.success("📦 Files archived")
                            st.rerun()

    show_uploaded_files(SPOTFIRE_MI_URLS.keys(), "🛠 MI Tests")
    st.markdown("---")
    show_uploaded_files(SPOTFIRE_CHEMLAB_URLS.keys(), "🧪 Chemlab Tests")

# === FOOTER ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
