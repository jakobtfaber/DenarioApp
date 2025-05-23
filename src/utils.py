import os
import io
import zipfile
import re
import sys
import uuid
from contextlib import contextmanager
import streamlit as st
from astropilot import KeyManager

from constants import PROJECT_DIR

#--- 
# Utils
#---

def show_markdown_file(file_path: str, extra_format = False, label: str = "") -> None:

    with open(file_path, "r") as f:
        response = f.read()

    #For the idea case, need further formatting, workaround for now:
    if extra_format:
        response = response.replace("\nProject Idea:\n\t","### Project Idea\n").replace("\t\t","    ")

    st.download_button(
            label="Download "+label,
            data=response,
            file_name=file_path.replace(PROJECT_DIR+"/input_files/",""),
            mime="text/plain",
            icon=":material/download:",
        )

    st.markdown(response)

def extract_api_keys(uploaded_file):
    pattern = re.compile(r'^\s*([A-Z_]+_API_KEY)\s*=\s*"([^"]+)"')
    keys = {}

    content = uploaded_file.read().decode("utf-8").split("\n")

    for line in content:
        match = pattern.match(line)
        if match:
            key_name, key_value = match.groups()
            if key_name in KeyManager.model_fields.keys():
                keys[key_name] = key_value
            if "GOOGLE" in key_name:
                keys["GEMINI"] = key_value

    return keys

def create_zip_in_memory(folder_path: str):
    """Create a zip in memory"""

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zip_file.write(file_path, arcname)
    
    zip_buffer.seek(0)

    return zip_buffer

def get_project_dir():

    if "project_dir" not in st.session_state:
        
        temp_dir = f"project_{uuid.uuid4().hex}"
        os.makedirs(temp_dir, exist_ok=True)
        
        st.session_state.project_dir = temp_dir

    return st.session_state.project_dir

class StreamToBuffer(io.StringIO):
    def __init__(self, update_callback):
        super().__init__()
        self.update_callback = update_callback

    def write(self, s):
        super().write(s)
        self.seek(0)
        self.update_callback(self.read())
        self.seek(0, io.SEEK_END)  # Move to end again

@contextmanager
def stream_to_streamlit(container):

    buffer = StreamToBuffer(update_callback=lambda text: container.markdown(
        f"""<div class="log-box">{text.replace('\n', '<br>')}</div>""",
        unsafe_allow_html=True
    ))

    old_stdout = sys.stdout
    sys.stdout = buffer
    try:
        yield
    finally:
        sys.stdout = old_stdout
