import streamlit as st
import time

from astropilot import AstroPilot

def data_description():

    st.header("Data description")
    # Accept user input
    if prompt := st.chat_input("Describe the data and tools to be used in the project."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        astro_pilot.set_data_description(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            assistant_response = astro_pilot.show_data_description()
            
            message_placeholder.markdown(assistant_response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})


astro_pilot = AstroPilot()
# astro_pilot.set_data_description("Explain your data here")
# astro_pilot.show_data_description()

astropilotimg = 'https://avatars.githubusercontent.com/u/206478071?s=400&u=b2da27eb19fb77adbc7b12b43da91fbc7309fb6f&v=4'

# streamlit configuration
st.set_page_config(
    page_title="AstroPilot",         # Title of the app (shown in browser tab)
    page_icon=astropilotimg,         # Favicon (icon in browser tab)
    layout="wide",                   # Page layout (options: "centered" or "wide")
    initial_sidebar_state="auto",    # Sidebar behavior
    menu_items=None                  # Custom options for the app menu
)

# --- Initialize Session State ---

defaults = {"messages": [],
            "state": {"memory": []},
            "task_reset_key": "task_0",
            "LLM_API_KEYS": {}}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


st.title('AstroPilot')

##### Sidebar UI #####
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

st.write("AI agents to assist the development of a scientific research process. From getting research ideas, developing the methods, computing the results and writing the paper.")

st.caption("[Get the source code here](https://github.com/AstroPilot-AI/AstroPilot.git)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Let's start chatting! 👇"}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

data_description()
