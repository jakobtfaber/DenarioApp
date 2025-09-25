import os
import sys
try:
    from .utils import extract_api_keys, get_project_dir, set_api_keys, create_zip_in_memory, delete_old_folders
    from .components import description_comp, idea_comp, method_comp, results_comp, paper_comp, keywords_comp, check_idea_comp, wolfram_hitl_review_comp
    from .constants import PROJECT_DIR, LLMs
except Exception:
    # Fallback when executed as a plain script (no package context)
    _HERE = os.path.dirname(__file__)
    if _HERE not in sys.path:
        sys.path.insert(0, _HERE)
    from utils import extract_api_keys, get_project_dir, set_api_keys, create_zip_in_memory, delete_old_folders
    from components import description_comp, idea_comp, method_comp, results_comp, paper_comp, keywords_comp, check_idea_comp, wolfram_hitl_review_comp
    from constants import PROJECT_DIR, LLMs
try:
    from .preflight import run_checks  # type: ignore
except Exception:
    # Fallback when running as plain script (no package context)
    import importlib.util as _ilu
    _pf_path = os.path.join(os.path.dirname(__file__), 'preflight.py')
    _spec = _ilu.spec_from_file_location('denario_app_preflight', _pf_path)
    assert _spec and _spec.loader
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    run_checks = getattr(_mod, 'run_checks')
import argparse
import streamlit as st
# Ensure local Denario source is importable in single-user setups
DENARIO_SRC = '/data/cmbagents/Denario'
try:
    from denario import Denario
except ModuleNotFoundError:
    sys.path.insert(0, DENARIO_SRC)
    try:
        from denario import Denario
    except ModuleNotFoundError:
        # Fallback: force-load module from source path
        import importlib.util
        import types
        init_path = os.path.join(DENARIO_SRC, 'denario', '__init__.py')
        spec = importlib.util.spec_from_file_location('denario', init_path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(mod)
        sys.modules['denario'] = mod
        from denario import Denario

# * Run preflight checks (exit with error if blocking issues)
_pf = run_checks()
if not _pf['summary']['ok']:
    # Print minimal banner in UI and stop
    st.error('Preflight failed. See terminal logs for details.')
    st.json(_pf)
    st.stop()


denarioimg = 'https://avatars.githubusercontent.com/u/206478071?s=400&u=b2da27eb19fb77adbc7b12b43da91fbc7309fb6f&v=4'

# streamlit configuration
st.set_page_config(
    page_title="Denario",         # Title of the app (shown in browser tab)
    # page_icon=denarioimg,         # Favicon (icon in browser tab)
    # Page layout (options: "centered" or "wide")
    layout="wide",
    initial_sidebar_state="auto",    # Sidebar behavior
    menu_items=None                  # Custom options for the app menu
)

st.session_state["LLM_API_KEYS"] = {}

st.title('Denario')

# Initialize Denario project instance early for use throughout the UI
_project_dir = get_project_dir()
den = Denario(project_dir=_project_dir)

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


# ---
# Sidebar UI
# ---

with st.sidebar:

    # st.image(astropilotimg)

    st.header("API keys")
    st.markdown(
        "*Input OpenAI, Anthropic, Gemini and Perplexity API keys below. See [here](https://denario.readthedocs.io/en/latest/apikeys/) for more information.*")

    with st.expander("Set API keys"):

        # If API key doesn't exist, show the input field
        for llm in LLMs:
            api_key = st.text_input(
                f"{llm} API key:",
                type="password",
                key=f"{llm}_api_key_input"
            )

            # If the user enters a key, save it and rerun to refresh the
            # interface
            if api_key:
                st.session_state["LLM_API_KEYS"][llm] = api_key
                set_api_keys(den.keys, api_key, llm)

            # Check session state
            has_key = st.session_state["LLM_API_KEYS"].get(llm)

            # # Display status after the key is saved
            # if has_key:
            #     st.markdown(f"<small style='color:green;'> ✅: {llm} API key set</small>",unsafe_allow_html=True)
            # else:
            #     st.markdown(f"<small style='color:red;'>❌: No {llm} API key</small>", unsafe_allow_html=True)

        st.markdown(
            """Or just upload a .env file with the following keys and reload the page:

```
OPENAI_API_KEY="..."
ANTHROPIC_API_KEY="..."
GEMINI_API_KEY="..."
PERPLEXITY_API_KEY="..."
```
                    """)
        uploaded_dotenv = st.file_uploader(
            "Upload the .env file", accept_multiple_files=False)

        if uploaded_dotenv:
            keys = extract_api_keys(uploaded_dotenv)

            for key, value in keys.items():
                st.session_state["LLM_API_KEYS"][key] = value
                den.keys[key] = value

    st.header("Upload data")

    uploaded_data = st.file_uploader(
        "Upload the data files",
        accept_multiple_files=True)

    if uploaded_data:
        os.makedirs(f"{den.project_dir}/data/", exist_ok=True)
        for uploaded_file in uploaded_data:
            with open(f"{den.project_dir}/data/{uploaded_file.name}", "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success("Files uploaded successfully!")

    st.header("Download project")

    project_zip = create_zip_in_memory(den.project_dir)

    st.download_button(
        label="Download all project files",
        data=project_zip,
        file_name="project.zip",
        mime="application/zip",
        icon=":material/download:",
    )

# ---
# Main
# ---

st.write("AI agents to assist the development of a scientific research process. From getting research ideas, developing methods, computing results and writing papers.")

st.caption(
    "[Get the source code here](https://github.com/AstroPilot-AI/Denario.git).")

tab_descr, tab_idea, tab_method, tab_restults, tab_paper, tab_check_idea, tab_keywords, tab_wolfram = st.tabs([
    "**Description**",
    "**Idea**",
    "**Methods**",
    "**Results**",
    "**Paper**",
    "Check idea",
    "Keywords",
    "Wolfram Alpha"
])

with tab_descr:
    description_comp(den)

with tab_idea:
    idea_comp(den)

with tab_method:
    method_comp(den)

with tab_restults:
    results_comp(den)

with tab_paper:
    paper_comp(den)

with tab_check_idea:
    check_idea_comp(den)

with tab_keywords:
    keywords_comp(den)

with tab_wolfram:
    wolfram_hitl_review_comp()
