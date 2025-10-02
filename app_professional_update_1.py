import streamlit as st
import os
import pandas as pd
from datetime import datetime

#==================CONFIG================
#NAS / Shared folder
SHARED_UPLOAD_FOLDER = r"\\mpl-op-genmp01.wdc.com\PN-RELAB\RE Ctrl Nasuni\Digitalization"
os.makedirs(SHARED_UPLOAD_FOLDER, exist_ok=True)

# Employee list paths
NAS_EMPLOYEE_LIST_PATH = os.path.join(SHARED_UPLOAD_FOLDER, "EMPLOYEE_LIST.xlsx")
FALLBACK_EMPLOYEE_LIST = "EMPLOYEE_LIST.xlsx"  # fallback copy in repo

# ====== STYLING ==========
st.set_page_config(
    page_title="RE PN LAB Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.header {
    background-color:#0a3d62;
    color:white;
    padding:10px;
    border-radius:5px;
    text-align:center;
    font-size:28px;
    font-weight:bold;
}
.card {
    background-color:#f1f2f6;
    padding:15px;
    border-radius:10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
    margin-bottom:10px;
    transition: transform 0.2s;
}
.card:hover {
    transform: scale(1.02);
}
.footer {
    text-align:center;
    color: gray;
    font-size:14px;
    margin-top:20px;
}
</style>            
""", unsafe_allow_html=True)    

st.markdown('<div class="header">📊 RE PN LAB Dashboard</div>', unsafe_allow_html=True)

#========HELPERS===========
def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"

def list_files_fast(folder: str):
    files_list = []
    for root, _, files in os.walk(folder):
        for file in files:
            try:
                path = os.path.join(root, file)
                stat = os.stat(path)
                files_list.append({
                    "name": file,
                    "path": path,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime,
                    "folder": os.path.basename(root)
                })
            except FileNotFoundError:
                continue
    files_list.sort(key=lambda x: x["mtime"], reverse=True)
    return files_list

#==========LOAD EMPLOYEE LIST===========
def load_employee_list():
    # Try NAS first
    if os.path.exists(NAS_EMPLOYEE_LIST_PATH):
        try:
            return pd.read_excel(NAS_EMPLOYEE_LIST_PATH, dtype=str)
        except Exception as e:
            st.warning(f"⚠️ Could not load from NAS: {e}")

    # Try fallback copy inside repo
    if os.path.exists(FALLBACK_EMPLOYEE_LIST):
        try:
            return pd.read_excel(FALLBACK_EMPLOYEE_LIST, dtype=str)
        except Exception as e:
            st.error(f"❌ Fallback employee list failed to load: {e}")
            st.stop()

    # If both fail
    st.error("❌ Employee list not found! Please make sure EMPLOYEE_LIST.xlsx is in the repo.")
    st.stop()

employee_df = load_employee_list()
employee_ids = employee_df['Employee #'].tolist()

#===========LOGIN===========
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["employee_id"] = None

def check_employee_id():
    if not st.session_state["authenticated"]:
        with st.form("login_form"):
            emp_id = st.text_input("Enter Employee #")
            submitted = st.form_submit_button("Login")
            if submitted:
                if emp_id in employee_ids:
                    st.session_state["authenticated"] = True
                    st.session_state["employee_id"] = emp_id
                    employee_name = employee_df.loc[employee_df['Employee #']==emp_id, 'Name'].values[0]
                    st.success(f"Welcome {employee_name}")
                    st.rerun()
                else:
                    st.error("Invalid Employee")
        return False
    return True

if not check_employee_id():
    st.stop()

emp_name = employee_df.loc[employee_df['Employee #']==st.session_state["employee_id"], 'Name'].values[0]
st.sidebar.success(f"Logged in as: {emp_name}")

#==========SPOTFIRE URLS==========
SPOTFIRE_MI_URLS = {
    "TRH": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/TRH",
    "HACT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HACT",
    "HEAD WEAR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HEADWEAR",
    "FLYABILITY": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/FLYABILITY",
    "HBOT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/HBOT",
    "SBT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/SBT"
}

SPOTFIRE_CHEMLAB_URLS = {
    "GCMS": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/GCMS",
    "LCQTOF": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/LCQTOF",
    "AD COBALT": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/ADCOBALT",
    "ICA": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/ICA",
    "FTIR": "https://spotfiremypn.wdc.com/spotfire/wp/analysis?file=/ADHOC/RELIABILITY/FTIR"
}

mi_tests = list(SPOTFIRE_MI_URLS.keys())
cl_tests = list(SPOTFIRE_CHEMLAB_URLS.keys())

# ================== SIDEBAR ==================
tabs = ["📁 MI Upload", "📁 Chemlab Upload", "📈 Spotfire Dashboards", "📋 Uploaded Log"]
selected_tab = st.sidebar.radio("Navigate", tabs)

#==============UPLOAD HANDLER===========
def handle_upload(test_type, tests_list):
    st.subheader(f"🛠️ Upload {test_type} Test File")
    selected_test = st.selectbox(f"Select {test_type} Test", tests_list)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        emp_id = st.session_state["employee_id"]
        employee_name = employee_df.loc[employee_df['Employee #']==emp_id, 'Name'].values[0]

        test_folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        os.makedirs(test_folder, exist_ok=True)

        save_path = os.path.join(test_folder, file.name)
        with open(save_path, "wb") as f:
            f.write(file.read())

        st.success(f"💾 File saved to shared folder: `{save_path}`")
        st.download_button("📥 Download This File", data=open(save_path, "rb").read(), file_name=file.name)

#========FILE LOG=======
def render_uploaded_log(tests_list, title):
    st.markdown(f"### {title}")
    container = st.container()
    page_size = st.slider("Rows per page", 5, 50, 20, 5, key=f"{title}_slider")
    for test in tests_list:
        test_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
        os.makedirs(test_folder, exist_ok=True)
        files = list_files_fast(test_folder)
        total = len(files)
        with container.expander(f"📁 {test} — {total} file(s)", expanded=True):
            if total == 0:
                st.info("No files in this test yet.")
                continue
            for f in files[:page_size]:
                st.markdown(f"""
                <div class="card">
                    <b>{f['name']}</b><br>
                    Folder: {f['folder']} | Size: {human_size(f['size'])} | Date: {datetime.fromtimestamp(f['mtime']).strftime('%d-%b-%Y %H:%M')}
                </div>
                """, unsafe_allow_html=True)
                c1, c2 = st.columns([0.8, 0.2])
                with c2:
                    try:
                        with open(f["path"], "rb") as file_data:
                            st.download_button("📥", data=file_data.read(), file_name=f['name'])
                    except:
                        st.error("Download failed!")

#===========MAIN=================
if selected_tab == "📁 MI Upload":
    handle_upload("MI", mi_tests)
elif selected_tab == "📁 Chemlab Upload":
    handle_upload("Chemlab", cl_tests)
elif selected_tab == "📈 Spotfire Dashboards":
    st.subheader("📈 Spotfire Dashboards")
    category = st.radio("Category", ["MI", "Chemlab"], horizontal=True)
    tests = mi_tests if category=="MI" else cl_tests
    urls = SPOTFIRE_MI_URLS if category=="MI" else SPOTFIRE_CHEMLAB_URLS

    cols = st.columns(3)
    for idx, test in enumerate(tests):
        col = cols[idx % 3]
        col.markdown(f"""
        <div class="card" style="text-align:center; background-color:#74b9ff;">
            <b>{test}</b><br>
            <a href="{urls[test]}" target="_blank" style="color:white; text-decoration:none;">Open Dashboard</a>
        </div>
        """, unsafe_allow_html=True)
elif selected_tab == "📋 Uploaded Log":
    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

st.markdown("<div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
