import streamlit as st
from astropilot import AstroPilot

#--- 
# Utils
#---

def show_markdown_file(file_path: str, extra_format = False) -> None:

    with open(file_path, "r") as f:
        response = f.read()

    #For the idea case, need further formatting, workaround for now:
    if extra_format:
        response = response.replace("\nProject Idea:\n\t","### Project Idea:\n").replace("\t\t","    ")

    st.markdown(response)

#--- 
# Components
#---

def data_description(ap: AstroPilot) -> None:

    st.header("Data description")

    data_descr = st.text_input(
        "Describe the data and tools to be used in the project.",
        placeholder="E.g. Use CAMELS cosmological simulations data https://github.com/franciscovillaescusa/CAMELS",
        key=f"data_descr"
    )

    if data_descr:

        ap.set_data_description(data_descr)

        try:
            show_markdown_file(ap.project_dir+"/input_files/data_description.md")
        except FileNotFoundError:
            st.write("Data description not generated yet.")

def get_idea(ap: AstroPilot) -> None:
    st.header("Research idea")

    st.write("Generate a research idea provided the data description.")
    press_button = st.button("Generate", type="primary",key="get_idea")
    if press_button:

        with st.spinner("Generating research idea...", show_time=True):
            ap.get_idea()

        st.success("Done!")

    try:
        show_markdown_file(ap.project_dir+"/input_files/idea.md", extra_format=True)
    except FileNotFoundError:
        st.write("Idea not generated yet.")

def get_methods(ap: AstroPilot) -> None:
    st.header("Methods")

    st.write("Generate the methods to be employed in the computation of the results, provided the idea and data description.")
    press_button = st.button("Generate", type="primary",key="get_method")
    if press_button:

        with st.spinner("Generating methods...", show_time=True):
            ap.get_method()

        st.success("Done!")

    try:
        show_markdown_file(ap.project_dir+"/input_files/methods.md")
    except FileNotFoundError:
        st.write("Methods not generated yet.")
        
def get_results(ap: AstroPilot) -> None:
    st.header("Results")

    st.write("Compute the results, given the methods, idea and data description.")
    press_button = st.button("Generate", type="primary",key="get_results")
    if press_button:

        with st.spinner("Computing results...", show_time=True):
            ap.get_results()

        st.success("Done!")

    try:
        show_markdown_file(ap.project_dir+"/input_files/results.md")
    except FileNotFoundError:
        st.write("Results not generated yet.")

def get_paper(ap: AstroPilot) -> None:
    st.header("Article")

    st.write("Write the article using the computed results of the research.")
    press_button = st.button("Generate", type="primary",key="get_paper")
    if press_button:

        with st.spinner("Writing the paper...", show_time=True):
            ap.get_paper()

        st.success("Done!")
        st.balloons()

#---
# Initialize session
#--- 

ap = AstroPilot(project_dir="project_app", clear_project_dir=False)

astropilotimg = 'https://avatars.githubusercontent.com/u/206478071?s=400&u=b2da27eb19fb77adbc7b12b43da91fbc7309fb6f&v=4'

# streamlit configuration
st.set_page_config(
    page_title="AstroPilot",         # Title of the app (shown in browser tab)
    page_icon=astropilotimg,         # Favicon (icon in browser tab)
    layout="wide",                   # Page layout (options: "centered" or "wide")
    initial_sidebar_state="auto",    # Sidebar behavior
    menu_items=None                  # Custom options for the app menu
)

defaults = {"messages": [],
            "state": {"memory": []},
            "task_reset_key": "task_0",
            "LLM_API_KEYS": {}}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.title('AstroPilot')

#---
# Sidebar UI
#---

st.sidebar.image(astropilotimg)

st.sidebar.header("LLM API keys")

LLMs = ["Google","OpenAI","Anthropic","Perplexity"]

# If API key doesn't exist, show the input field
for llm in LLMs:
    api_key = st.sidebar.text_input(
        f"{llm} API key for {llm}:",
        type="password",
        key=f"{llm}_api_key_input"
    )
    
    # If the user enters a key, save it and rerun to refresh the interface
    if api_key:
        st.session_state["LLM_API_KEYS"][llm] = api_key
        st.rerun()

    # Display status after the key is saved
    if llm in st.session_state["LLM_API_KEYS"]:
        st.sidebar.markdown(f"<small style='color:green;'> ✅: {llm} API key set</small>",unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"<small style='color:red;'>❌: No {llm} API key</small>", unsafe_allow_html=True)

#---
# Main
#---

st.write("AI agents to assist the development of a scientific research process. From getting research ideas, developing the methods, computing the results and writing the paper.")

st.caption("[Get the source code here](https://github.com/AstroPilot-AI/AstroPilot.git).")

tab_descr, tab_idea, tab_method, tab_restults, tab_paper = st.tabs(["Description", "Idea", "Methods", "Results", "Paper"])

with tab_descr:
    data_description(ap)

with tab_idea:
    get_idea(ap)

with tab_method:
    get_methods(ap)

with tab_restults:
    get_results(ap)

with tab_paper:
    get_paper(ap)