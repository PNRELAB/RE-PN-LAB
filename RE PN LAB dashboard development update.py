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
        download_folder = os.path.join(DOWNLOAD_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)
        os.makedirs(download_folder, exist_ok=True)

        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        shutil.copy2(path, os.path.join(spotfire_folder, file.name))
        download_path, saved = save_to_local(path, download_folder)

        if saved is True:
            st.success(f"💾 File saved to downloads: `{download_path}`")
        elif saved is False:
            st.info(f"💾 File already exists in downloads: `{download_path}`")
        else:
            st.error(f"❌ Failed to save to downloads: {saved}")

        st.download_button(
            label="📥 Download",
            data=open(download_path, "rb").read(),
            file_name=file.name,
            key=f"download_{selected_test}_{file.name}"
        )

# === Upload Chemlab ===
elif selected_tab == "📁 Chemlab Upload":
    st.subheader("🧪 Upload Chemlab Test File")
    selected_test = st.selectbox("Select Chemlab Test", cl_tests)
    file = st.file_uploader("Upload Excel File", type=["xlsx"])
    if file:
        folder = os.path.join(SHARED_UPLOAD_FOLDER, selected_test)
        spotfire_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", selected_test)
        download_folder = os.path.join(DOWNLOAD_FOLDER, selected_test)
        os.makedirs(folder, exist_ok=True)
        os.makedirs(spotfire_folder, exist_ok=True)
        os.makedirs(download_folder, exist_ok=True)

        path = os.path.join(folder, file.name)
        with open(path, "wb") as f:
            f.write(file.read())

        shutil.copy2(path, os.path.join(spotfire_folder, file.name))
        download_path, saved = save_to_local(path, download_folder)

        if saved is True:
            st.success(f"💾 File saved to downloads: `{download_path}`")
        elif saved is False:
            st.info(f"💾 File already exists in downloads: `{download_path}`")
        else:
            st.error(f"❌ Failed to save to downloads: {saved}")

        st.download_button(
            label="📥 Download",
            data=open(download_path, "rb").read(),
            file_name=file.name,
            key=f"download_{selected_test}_{file.name}"
        )

# === Uploaded Log with professional buttons ===
elif selected_tab == "📋 Uploaded Log":
    st.subheader("📋 Uploaded Log")
    page_size = st.slider("Rows per page", 5, 100, 20, 5)

    if "refresh_log" not in st.session_state:
        st.session_state["refresh_log"] = False

    def render_uploaded_log(test_list, title):
        st.markdown(f"### {title}")
        container = st.container()  # Container to rerender
        for test in test_list:
            stream_folder = os.path.join(SHARED_UPLOAD_FOLDER, test)
            spot_folder = os.path.join(SHARED_UPLOAD_FOLDER, "Spotfire", test)
            archive_folder = os.path.join(SHARED_UPLOAD_FOLDER, "archive", test)
            download_folder = os.path.join(DOWNLOAD_FOLDER, test)
            local_folder = os.path.join(LOCAL_SAVE_FOLDER, test)
            os.makedirs(stream_folder, exist_ok=True)
            os.makedirs(spot_folder, exist_ok=True)
            os.makedirs(archive_folder, exist_ok=True)
            os.makedirs(download_folder, exist_ok=True)
            os.makedirs(local_folder, exist_ok=True)

            files = list_files_fast(stream_folder)
            total = len(files)
            with container.expander(f"📁 {test} — {total} file(s)", expanded=False):
                if total == 0:
                    st.info("No files in this test yet.")
                    continue

                start = 0
                end = min(page_size, total)
                page_files = files[start:end]

                for f in page_files:
                    name = f["name"]
                    stream_path = f["path"]
                    download_path = os.path.join(download_folder, name)
                    shutil.copy2(stream_path, download_path)

                    c1, c2, c3, c4, c5 = st.columns([0.3, 0.2, 0.2, 0.2, 0.2])
                    with c1:
                        st.write(name)
                    with c2:
                        st.write(f"Stream: {human_size(f['size'])}")

                    # Download
                    with c3:
                        with open(download_path, "rb") as file_data:
                            st.download_button(
                                label="📥",
                                data=file_data,
                                file_name=name,
                                key=f"download_{test}_{name}"
                            )

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

    # Refresh container if flagged
    if st.session_state.get("refresh_log", False):
        st.session_state["refresh_log"] = False
        st.experimental_rerun()

# === Footer ===
st.markdown("<hr><div class='footer'>📘 Made with passion by RE PN LAB 2025</div>", unsafe_allow_html=True)
