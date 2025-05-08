import re
import streamlit as st

from constants import PROJECT_DIR

#--- 
# Utils
#---

def show_markdown_file(file_path: str, extra_format = False) -> None:

    with open(file_path, "r") as f:
        response = f.read()

    #For the idea case, need further formatting, workaround for now:
    if extra_format:
        response = response.replace("\nProject Idea:\n\t","### Project Idea:\n").replace("\t\t","    ")

    st.download_button(
            label="Download",
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
            keys[key_name] = key_value

    return keys