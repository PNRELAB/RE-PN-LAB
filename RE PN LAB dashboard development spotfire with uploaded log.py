import streamlit as st
import os, shutil, subprocess, sys, time
import requests
from io import BytesIO
from PIL import Image
import base64

# === Auto-start local file server ===
def start_file_server():
    try:
        folder_to_serve = r"C:\PN-RE-LAB"
        port = 8502
        command = [sys.executable, "-m", "http.server", str(port), "--directory", folder_to_serve]
        subprocess.Popen(command)  # Remove stdout/stderr suppression for debugging
        time.sleep(1)
    except Exception as e:
        st.warning(f"⚠️ Failed to start file server: {e}")

start_file_server()

# === Convert image from URL to base64 ===
def get_base64_from_url(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Raw GitHub URLs
logo_base64 = get_base64_from_url("https://github.com/PNRELAB/RE-PN-LAB/raw/main/WD%20logo.png")
bg_base64   = get_base64_from_url("https://github.com/PNRELAB/RE-PN-LAB/raw/main/Slide1.PNG")

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
</style>
""", unsafe_allow_html=True)

# === WD Logo Header ===
st.markdown(
    f'<div style="display: flex; justify-content: center; align-items: center; gap: 12px;">'
    f'<img src="data:image/png;base64,{logo_base64}" style="height: 40px;">'
    f'<h1>RE PN LAB Dashboard</h1></div>',
    unsafe_allow_html=True
)

# === Password Auth ===
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if not st.session_state["authenticated"]:
        password = st.text_input("🔐 Enter Password", type="password")
        if password == "PNRELAB":
            st.session_state["authenticated"] = True
            st.experimental_rerun()
        elif password != "":
            st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"C:\PN-RE-LAB"

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
        st.success(f"✅ File saved to `{path}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"🔗 [Open in Spotfire]({SPOTFIRE_MI_URLS[selected_test]})", unsafe_allow_html=True)

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
        st.success(f"✅ File saved to `{path}`")
        st.download_button("📥 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"🔗 [Open in Spotfire]({SPOTFIRE_CHEMLAB_URLS[selected_test]})", unsafe_allow_html=True)

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

                    # Session state for select_all
                    if f"select_all_{test}" not in st.session_state:
                        st.session_state[f"select_all_{test}"] = False

                    select_all = st.checkbox(f"Select All ({test})", key=f"select_all_{test}")
                    selected = []
                    for file in files:
                        file_path = os.path.join(folder, file)
                        checked = st.checkbox(f"{file} ({os.path.getsize(file_path)//1024} KB)", value=select_all, key=f"{test}_{file}")
                        if checked:
                            selected.append(file)

                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"🗑 Delete Selected in {test}", key=f"del_{test}"):
                            for file in selected:
                                os.remove(os.path.join(folder, file))
                            st.success("✅ Files deleted")
                            st.experimental_rerun()
                    with colB:
                        if st.button(f"📦 Archive Selected in {test}", key=f"arc_{test}"):
                            for file in selected:
                                shutil.move(os.path.join(folder, file), os.path.join(archive_folder, file))
                            st.success("📦 Files archived")
                            st.experimental_rerun()

    show_uploaded_files(mi_tests, SPOTFIRE_MI_URLS, "🛠 MI Tests")
    st.markdown("---")
    show_uploaded_files(cl_tests, SPOTFIRE_CHEMLAB_URLS, "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
