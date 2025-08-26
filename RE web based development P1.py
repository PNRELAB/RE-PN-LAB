import streamlit as st  ## streamlit library for building web apps easily in python. alias it as "st"

###this imports the Streamlit library, which is used to create web apps quickly in Python
###The "as st" part is an alias, meaning instead of typing "streamlit.function()", just can type "st.function()"
###ex:"st.write("Hello") will display text on the web app"

import os ##used for operating system tasks (folders, paths, checking files)

###imports os module for interacting with the operating system
###used for tasks like creating folders, checking files, and working with paths

import shutil ##used for copying, moving, and deleting files

###imports shutil module for high-level file operations
###can copy, move or delete files/folder

import base64 ##converts files (like images) to a base64 string so they can be embedded in HTML/CSS

###imports base64 module to encode files (like images) into a base64 string
###lets us embed images directly into HTML/CSS without separate image files

import subprocess ##run external commands, like strating a file server

###imports subprocess module to run external commands/programs from python
###ex:starting a small web server to serve files

import sys ##system-level operations (used here to find Python executable)

###imports sys module to access system-specific parameters and functions
###ex : "sys.executable" gives the path to the Python interpreter running the script

import time ##for delays (sleep)

### imports time module to work with time-related tasks
### ex: time.sleep(1) pauses the program for 1 second

from datetime import datetime ##work with date and time

###imports the "datetime" class from the datetime module
###used to work with dates and times, e.g. getting current time or formatting timestamps

# === Auto-start file server ===
def start_file_server():
    ###defines a function named start_file_server
    ###functions are reusable blocks of code that can be called later
    try:
        ###starts a try block to catch error
        ###if something inside fails, it jumps to the "except" block
        folder_to_serve = r"C:\\PN-RE-LAB"
        ###defines the folder that will be served by the file server
        ###the "r" before the string makes it a raw string, so "\\" is treated as a single backslash
        port = 8502
        ###sets the port number where the server will run
        ###http://localhost:8502 will be the address to access the files
        command = [sys.executable, "-m", "http.server", str(port), "--directory", folder_to_serve]
        ###creates a command to run the Python HTTP server
        ###"sys.executable" --> path to Python interpreter
        ###"-m http.server" --> run built-in HTTP server module
        ###"str(port)" --> port number as string
        ###"--directory folder_to_serve" --> specify which folder to serve
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        ###runs the command in the background without blocking Python
        ###"stdout" and "stderr" are redirected to DEVNULL --> no console output
        time.sleep(1)
        ###waits 1 second to give the server time to start
    except Exception as e:
        ###catches any error that happens in the try block
        st.warning(f"⚠️ Failed to start file server: {e}")
        ###shows a warning message in Streamlit if starting the server fails
        ###"{e}" contains the error message

start_file_server()
###calls the function to start the file server immediately

# === Helpers ===
def get_base64(image_path: str) -> str:
    ###defines a function "get_base64" that takes an image path and returns a base64 string
    ###"image_path: str" --> input is a string (path to the image)
    ###"--> str" --> output will be a string (base64)
    with open(image_path, "rb") as img_file:
        ###opens the image file in binary read mode ("rb")
        ###"with" ensures the file is automatically closed after reading
        return base64.b64encode(img_file.read()).decode()
    ### reads the image as bytes --> encodes it to base64 --> converts to string
    ### this string can be embedded directly in HTML or CSS

def human_size(num_bytes: int) -> str:
    ###defines a function to convert bytes into a human-readable string like KB, MB, GB
    ###"num_bytes" is an integer input
    ###output is a string
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        ###Loops through different units of digital storage
        if num_bytes < 1024.0:
            ###checks if the number of bytes is small enough for the current unit
            return f"{num_bytes:.1f} {unit}"
        ###returns the size formatted with one decimal place and the unit
        ###ex: 1023 --> "1023.0 B" or "2048 --> "2.0 KB"
        num_bytes /= 1024.0
        ###converts bytes to the next higher unit (e.g. B --> KB --> MB)
    return f"{num_bytes:.1f} PB"
###if the number is extremely large, defaults to petabytes(PB)

def list_files_fast(folder: str):
    ###defines a function to list all files in a folder quickly
    ###input: folder path as string
    ###output: a list of file details (name, path, size, modified time)
    try:
        ###starts a try block to catch errors like folder not existing
        with os.scandir(folder) as it:
            ###uses "os.scandir" which is faster than os.listdir for iterating folder entries
            files = []
            ###initializes an empty list to store file info
            for entry in it:
                ###loops through each item (file/folder) in the folder
                if entry.is_file():
                    ###checks if the entry is a file(ignores folders)
                    try:
                        stat = entry.stat()
                        files.append({
                            "name": entry.name,
                            "path": entry.path,
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                        })
                        ###gets file statistics like size and modification time
                        ###appends a dictionary with name, path, size, mtime to the files list
                    except FileNotFoundError:
                        continue
                    ###if a file disappears while scanning, skip it
            files.sort(key=lambda x: x["mtime"], reverse=True)
            ###sorts files by last modified time, newest time
            return files
        ###returns the list of files
    except FileNotFoundError:
        return []
    ###if the folder does not exist, return an empty list

# === Branding assets ===
logo_path = "WD logo.png"
###stores the file path of the logo image in a variable called logo_path
background_path = "Slide1.PNG"
###stores the file path of the background image in a variable called "background_path"
logo_base64 = get_base64(logo_path)
###converts the logo image into a base64 string using the "get_base64" helper function
###this allows embedding the logo directly into HTML
bg_base64 = get_base64(background_path)
###converts the background image into a base64 string for embedding in CSS

# === Streamlit config and styles ===
st.set_page_config("RE PN LAB Dashboard", layout="wide")
###sets the title of the page to "RE PN LAB Dashboard"
###"layout="wide"" --> makes the app full-width instead of the default narrow layout
st.markdown(f"""
<style>
html, body, .stApp {{
    background: url("data:image/png;base64,{bg_base64}") no-repeat center center fixed;
    background-size: cover;
    font-family: 'Orbitron', sans-serif;
    color: #ffffff;
}}
####starts custom CSS styling using Streamlit's "st.markdown"
####sets the background image using the base64 string
####background-size: cover --> image covers the whole page
####font-family --> sets the font style
####color: #fffff --> text color white
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

        # Copy to Spotfire
        shutil.copy2(stream_path, os.path.join(spotfire_folder, file.name))

        # Copy to local DOWNLOADS folder
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
    st.subheader("📋 Uploaded Log")
    page_size = st.slider("Rows per page", 5, 100, 20, 5)
    if "refresh_log" not in st.session_state:
        st.session_state["refresh_log"] = False

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

            files = list_files_fast(stream_folder)
            total = len(files)
            with container.expander(f"📁 {test} — {total} file(s)", expanded=False):
                if total == 0:
                    st.info("No files in this test yet.")
                    continue

                page_files = files[:page_size]

                for f in page_files:
                    name = f["name"]
                    stream_path = f["path"]
                    local_path = os.path.join(local_folder, name)

                    c1, c2, c3, c4, c5 = st.columns([0.3, 0.2, 0.2, 0.2, 0.2])
                    with c1: st.write(name)
                    with c2: st.write(f"Stream: {human_size(f['size'])}")

                    # Download button
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
                            try:
                                shutil.move(stream_path, os.path.join(archive_folder, name))
                                st.success(f"Archived: {name}")
                                st.session_state["refresh_log"] = True
                            except Exception as e:
                                st.error(f"Failed to archive: {e}")

                    # Delete
                    with c5:
                        if st.button("🗑️ Delete", key=f"delete_{test}_{name}"):
                            try:
                                os.remove(stream_path)
                                st.success(f"Deleted: {name}")
                                st.session_state["refresh_log"] = True
                            except Exception as e:
                                st.error(f"Failed to delete: {e}")

    render_uploaded_log(mi_tests, "🛠 MI Tests")
    st.markdown("---")
    render_uploaded_log(cl_tests, "🧪 Chemlab Tests")

    if st.session_state.get("refresh_log", False):
        st.session_state["refresh_log"] = False
        st.experimental_rerun()

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
