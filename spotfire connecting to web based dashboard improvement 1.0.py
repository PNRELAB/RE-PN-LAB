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
        port = 8502
        command = [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--directory",
            folder_to_serve,
        ]
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

st.markdown(f"""<style>...<style>""", unsafe_allow_html=True)  # OMITTED STYLING BLOCK FOR BREVITY

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
    if not st.session_state["authenticated"]:
        with st.form("login_form", clear_on_submit=False):
            password = st.text_input("🔐 Enter Password", type="password", key="password_input")
            submitted = st.form_submit_button("Login")
            if submitted:
                if password == "PNRELAB":
                    st.session_state["authenticated"] = True
                    return True  # Removed experimental_rerun
                else:
                    st.error("❌ Incorrect password")
        return False
    return True

if not check_password():
    st.stop()

# === Config Constants ===
SHARED_UPLOAD_FOLDER = r"C:\\PN-RE-LAB"

SPOTFIRE_MI_URLS = {...}  # OMITTED FOR BREVITY
SPOTFIRE_CHEMLAB_URLS = {...}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

tabs = ["\ud83d\udcc1 MI Upload", "\ud83d\udcc1 Chemlab Upload", "\ud83d\udcc8 View Spotfire Dashboard", "\ud83d\udccb Uploaded Log"]
selected_tab = st.selectbox("\ud83d\udf2d Navigate", tabs, label_visibility="collapsed")

if selected_tab == "\ud83d\udcc1 MI Upload":
    st.subheader("\ud83d\udee0\ufe0f Upload MI Test File")
    selected_test = st.selectbox("Select MI Test", mi_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        url_path = f"{urllib.parse.quote(selected_test)}/{urllib.parse.quote(file.name)}"
        web_file_url = f"http://localhost:8502/{url_path}"

        st.success(f"✅ File saved to `{path}`")
        st.download_button("\ud83d\udcc5 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"\ud83d\udd17 [\ud83c\udf10 Open File for Spotfire]({web_file_url})", unsafe_allow_html=True)
        st.markdown(f"\ud83d\udd17 [\ud83d\udcc8 Open {selected_test} Dashboard in Spotfire]({SPOTFIRE_MI_URLS[selected_test]})", unsafe_allow_html=True)

elif selected_tab == "\ud83d\udcc1 Chemlab Upload":
    st.subheader("\ud83e\uddea Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        url_path = f"{urllib.parse.quote(selected_test)}/{urllib.parse.quote(file.name)}"
        web_file_url = f"http://localhost:8502/{url_path}"

        st.success(f"✅ File saved to `{path}`")
        st.download_button("\ud83d\udcc5 Download This File", data=open(path, "rb").read(), file_name=file.name)
        st.markdown(f"\ud83d\udd17 [\ud83c\udf10 Open File for Spotfire]({web_file_url})", unsafe_allow_html=True)
        st.markdown(f"\ud83d\udd17 [\ud83d\udcc8 Open {selected_test} Dashboard in Spotfire]({SPOTFIRE_CHEMLAB_URLS[selected_test]})", unsafe_allow_html=True)

elif selected_tab == "\ud83d\udcc8 View Spotfire Dashboard":
    st.subheader("\ud83d\udcc8 Spotfire Dashboards")
    category = st.radio("Choose Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category == "MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category == "MI" else SPOTFIRE_CHEMLAB_URLS
    selected = st.selectbox("Select Dashboard", tests)
    st.markdown(f"\ud83d\udd17 [Open {selected} Dashboard in Spotfire]({urls[selected]})", unsafe_allow_html=True)

elif selected_tab == "\ud83d\udccb Uploaded Log":
    st.subheader("\ud83d\udccb Uploaded Log")
    def show_uploaded_files(test_list, spotfire_dict, title):
        ...  # No changes needed here except rerun fix if required

    show_uploaded_files(mi_tests, SPOTFIRE_MI_URLS, "\ud83d\udee0 MI Tests")
    st.markdown("---")
    show_uploaded_files(cl_tests, SPOTFIRE_CHEMLAB_URLS, "\ud83e\uddea Chemlab Tests")

st.markdown("<hr><div class='footer'>\ud83d\udcd8 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
