import streamlit as st
import os
import shutil
import base64
import subprocess
import sys
import time

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

# === Image to base64 ===
def get_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

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

SPOTFIRE_MI_URLS = {
    "TRH": "/ADHOC/RELIABILITY/TRH",
    "HACT": "/ADHOC/RELIABILITY/HACT",
    "HEAD WEAR": "/ADHOC/RELIABILITY/HeadWear",
    "FLYABILITY": "/ADHOC/RELIABILITY/flyability",
    "HBOT": "/ADHOC/RELIABILITY/hbot",
    "SBT": "/ADHOC/RELIABILITY/sbt",
    "ADT": "/ADHOC/RELIABILITY/adt"
}

SPOTFIRE_CHEMLAB_URLS = {
    "AD COBALT": "/ADHOC/RELIABILITY/ADCobalt",
    "ICA": "/ADHOC/RELIABILITY/ICA",
    "GCMS": "/ADHOC/RELIABILITY/gcms",
    "LCQTOF": "/ADHOC/RELIABILITY/lcqtof",
    "FTIR": "/ADHOC/RELIABILITY/ftir"
}

SPOTFIRE_BASE_URL = "https://spotfiremypn.wdc.com/spotfire/wp/OpenAnalysis?file="

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# === Helper functions ===
def save_file(uploaded_file, test_name):
    folder = os.path.join(SHARED_UPLOAD_FOLDER, test_name.replace(" ", "_"))
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, uploaded_file.name)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path

def get_spotfire_url(test_name, category):
    if category == "MI":
        folder = SPOTFIRE_MI_URLS.get(test_name)
    else:
        folder = SPOTFIRE_CHEMLAB_URLS.get(test_name)
    if folder:
        return SPOTFIRE_BASE_URL + folder
    return None

# === Tabs ===
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 View Spotfire Dashboard", "📋 Uploaded Log"]
selected_tab = st.selectbox("🗭 Navigate", tabs, label_visibility="collapsed")

# === Upload MI ===
if selected_tab == "📁 MI Upload":
    st.subheader("🛠️ Upload MI Test File")
    selected_test = st.selectbox("Select MI Test", mi_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        path = save_file(file, selected_test)
        st.success(f"✅ File saved to `{path}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"🔗 [Open in Spotfire]({get_spotfire_url(selected_test,'MI')})", unsafe_allow_html=True)

# === Upload Chemlab ===
elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        path = save_file(file, selected_test)
        st.success(f"✅ File saved to `{path}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"🔗 [Open in Spotfire]({get_spotfire_url(selected_test,'Chemlab')})", unsafe_allow_html=True)

# === View Spotfire Dashboard ===
elif selected_tab == "📈 View Spotfire Dashboard":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    selected = st.selectbox("Select Dashboard", tests)
    url = get_spotfire_url(selected, category)
    if url:
        st.markdown(f"🔗 [Open {selected} Dashboard in Spotfire]({url})", unsafe_allow_html=True)

# === Uploaded Log ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")

    def show_uploaded_files(test_list, category, title):
        st.markdown(f"### {title}")
        for test in test_list:
            folder = os.path.join(SHARED_UPLOAD_FOLDER, test.replace(" ","_"))
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test.replace(" ","_"))
            os.makedirs(archive_folder, exist_ok=True)
            if os.path.isdir(folder):
                files = os.listdir(folder)
                if files:
                    st.markdown(f"#### 📁 {test}")
                    selected_files = []
                    select_all = st.checkbox(f"Select All ({test})", key=f"all_{test}")
                    for f in files:
                        file_path = os.path.join(folder, f)
                        col1, col2, col3 = st.columns([0.05, 0.5, 0.45])
                        with col1:
                            if st.checkbox("", key=f"{test}_{f}", value=select_all):
                                selected_files.append(f)
                        with col2:
                            st.markdown(f"**{f}** ({os.path.getsize(file_path)//1024} KB)")
                        with col3:
                            with open(file_path, "rb") as fh:
                                st.download_button("📥 Download", fh.read(), file_name=f, key=f"dl_{test}_{f}")
                            url = get_spotfire_url(test, category)
                            if url:
                                st.markdown(f"[🔗 Open in Spotfire]({url})", unsafe_allow_html=True)
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"🗑 Delete Selected in {test}", key=f"del_{test}"):
                            for f in selected_files:
                                os.remove(os.path.join(folder, f))
                            st.success("✅ Files deleted")
                            st.experimental_rerun()
                    with colB:
                        if st.button(f"📦 Archive Selected in {test}", key=f"arc_{test}"):
                            for f in selected_files:
                                shutil.move(os.path.join(folder, f), os.path.join(archive_folder, f))
                            st.success("📦 Files archived")
                            st.experimental_rerun()

    show_uploaded_files(mi_tests, "MI", "🛠 MI Tests")
    st.markdown("---")
    show_uploaded_files(cl_tests, "Chemlab", "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)

