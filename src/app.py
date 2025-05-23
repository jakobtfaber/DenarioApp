import os
import streamlit as st
from astropilot import AstroPilot

from constants import PROJECT_DIR, LLMs
from components import description_comp, idea_comp, method_comp, results_comp, paper_comp, keywords_comp
from utils import extract_api_keys, get_project_dir, set_api_keys, create_zip_in_memory

#---
# Initialize session
#--- 

deploy = False

if deploy:
    project_dir = get_project_dir()
else:
    project_dir = PROJECT_DIR

ap = AstroPilot(project_dir=project_dir, clear_project_dir=False)

astropilotimg = 'https://avatars.githubusercontent.com/u/206478071?s=400&u=b2da27eb19fb77adbc7b12b43da91fbc7309fb6f&v=4'

# streamlit configuration
st.set_page_config(
    page_title="ResearchPilot",         # Title of the app (shown in browser tab)
    # page_icon=astropilotimg,         # Favicon (icon in browser tab)
    layout="wide",                   # Page layout (options: "centered" or "wide")
    initial_sidebar_state="auto",    # Sidebar behavior
    menu_items=None                  # Custom options for the app menu
)

st.session_state["LLM_API_KEYS"] = {}

st.title('ResearchPilot')

st.markdown("""
    <style>
    .log-box {
        background-color: #111827;
        color: #d1d5db;
        font-family: monospace;
        padding: 1em;
        border-radius: 8px;
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #4b5563;
        white-space: pre-wrap;
        resize: vertical;
        min-height: 100px;
        max-height: 700px;
    }
    </style>
""", unsafe_allow_html=True)


#---
# Sidebar UI
#---

with st.sidebar:

    # st.image(astropilotimg)

    st.header("API keys")
    st.markdown("*Input OpenAI, Anthropic, Gemini and Perplexity API keys below.*")

    with st.expander("Set API keys"):

        # If API key doesn't exist, show the input field
        for llm in LLMs:
            api_key = st.text_input(
                f"{llm} API key:",
                type="password",
                key=f"{llm}_api_key_input"
            )
            
            # If the user enters a key, save it and rerun to refresh the interface
            if api_key:
                st.session_state["LLM_API_KEYS"][llm] = api_key
                set_api_keys(ap.keys, api_key, llm)
            
            # Check session state
            has_key = st.session_state["LLM_API_KEYS"].get(llm)
            
            # Display status after the key is saved
            if has_key:
                st.markdown(f"<small style='color:green;'> ✅: {llm} API key set</small>",unsafe_allow_html=True)
            else:
                st.markdown(f"<small style='color:red;'>❌: No {llm} API key</small>", unsafe_allow_html=True)

        st.markdown("""Or just upload a .env file with the following keys and reload the page:
                    ```
                    OPENAI_API_KEY="..."
                    ANTHROPIC_API_KEY="..."
                    GEMINI_API_KEY="..."
                    PERPLEXITY_API_KEY="..."
                    ```
                    """)
        uploaded_dotenv = st.file_uploader("Upload the .env file", accept_multiple_files=False)

        if uploaded_dotenv:
            keys = extract_api_keys(uploaded_dotenv)

            for key, value in keys.items():
                st.session_state["LLM_API_KEYS"][key] = value
                ap.keys[key] = value

    st.header("Download project")

    project_zip = create_zip_in_memory(ap.project_dir)

    st.download_button(
        label="Download all project files",
        data=project_zip,
        file_name="project.zip",
        mime="application/zip",
        icon=":material/download:",
    )

#---
# Main
#---

st.write("AI agents to assist the development of a scientific research process. From getting research ideas, developing methods, computing results and writing papers.")

st.caption("[Get the source code here](https://github.com/AstroPilot-AI/AstroPilot.git).")

tab_descr, tab_idea, tab_method, tab_restults, tab_paper, tab_keywords = st.tabs([
    "**Description**", 
    "**Idea**", 
    "**Methods**", 
    "**Results**", 
    "**Paper**", 
    "Keywords"
])

with tab_descr:
    description_comp(ap)

with tab_idea:
    idea_comp(ap)

with tab_method:
    method_comp(ap)

with tab_restults:
    results_comp(ap)

with tab_paper:
    paper_comp(ap)

with tab_keywords:
    keywords_comp(ap)