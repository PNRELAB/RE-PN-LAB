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
.missing-local {{
    background-color: rgba(255, 0, 0, 0.2);
    padding: 2px;
    border-radius: 5px;
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
LOCAL_SAVE_FOLDER = r"C:\PN-RE-LAB"     # Local disk folders
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

# === Uploaded Log ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")

    def show_uploaded_files(test_list, title):
        st.markdown(f"### {title}")
        for test in test_list:
            streamlit_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
            spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", test)
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
            local_folder = os.path.join(LOCAL_SAVE_FOLDER, test)
            os.makedirs(archive_folder, exist_ok=True)
            os.makedirs(spotfire_folder, exist_ok=True)
            os.makedirs(local_folder, exist_ok=True)

            if os.path.isdir(streamlit_folder):
                files = os.listdir(streamlit_folder)
                if files:
                    st.markdown(f"#### 📁 {test}")
                    selected = []
                    select_all = st.checkbox(f"Select All ({test})", key=f"all_{test}")
                    for file in files:
                        streamlit_file_path = os.path.join(streamlit_folder, file)
                        local_file_path = os.path.join(local_folder, file)

                        # Highlight missing local files
                        style_start = "<div class='missing-local'>" if not os.path.exists(local_file_path) else ""
                        style_end = "</div>" if not os.path.exists(local_file_path) else ""

                        col1, col2, col3, col4, col5 = st.columns([0.05, 0.3, 0.25, 0.25, 0.15])
                        with col1:
                            if st.checkbox("", key=f"{test}_{file}", value=select_all):
                                selected.append(file)
                        with col2:
                            st.markdown(f"**{file}** (Streamlit: {os.path.getsize(streamlit_file_path)//1024} KB)")
                        with col3:
                            if os.path.exists(local_file_path):
                                st.markdown(f"Local copy exists ({os.path.getsize(local_file_path)//1024} KB)")
                            else:
                                st.markdown(f"{style_start}Local copy missing ❌{style_end}", unsafe_allow_html=True)
                        with col4:
                            # Download buttons
                            with open(streamlit_file_path, "rb") as f:
                                st.download_button(f"📥 Streamlit", f.read(), file_name=file, key=f"dl_streamlit_{file}")
                            if os.path.exists(local_file_path):
                                with open(local_file_path, "rb") as f:
                                    st.download_button(f"💾 Local", f.read(), file_name=file, key=f"dl_local_{file}")
                        with col5:
                            # Copy to Local button
                            if not os.path.exists(local_file_path):
                                if st.button("💾 Copy to Local", key=f"copy_local_{file}"):
                                    shutil.copy2(streamlit_file_path, local_file_path)
                                    st.success(f"✅ File copied to local disk: {local_file_path}")
                                    st.experimental_rerun()

                    # Delete or Archive selected files (Streamlit only)
                    colA, colB = st.columns(2)
                    with colA:
                        if st.button(f"🗑 Delete Selected in {test}", key=f"del_{test}"):
                            for file in selected:
                                os.remove(os.path.join(streamlit_folder, file))
                            st.success("✅ Files deleted from Streamlit folder")
                            st.rerun()
                    with colB:
                        if st.button(f"📦 Archive Selected in {test}", key=f"arc_{test}"):
                            for file in selected:
                                shutil.move(os.path.join(streamlit_folder, file), os.path.join(archive_folder, file))
                            st.success("📦 Files archived in Streamlit folder")
                            st.rerun()

                    # Spotfire folder downloads
                    st.markdown(f"#### 🖥 Spotfire Folder for {test}")
                    spotfire_files = os.listdir(spotfire_folder)
                    if spotfire_files:
                        for f in spotfire_files:
                            file_full_path = os.path.join(spotfire_folder, f)
                            with open(file_full_path, "rb") as file_data:
                                st.download_button(
                                    label=f"📄 {f}",
                                    data=file_data,
                                    file_name=f,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )
                    else:
                        st.info("Spotfire folder is empty.")

    show_uploaded_files(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    show_uploaded_files(cl_tests, "🧪 Chemlab Tests")

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
