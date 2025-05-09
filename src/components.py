import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from astropilot import AstroPilot, Journal

from utils import show_markdown_file, create_zip_in_memory

#--- 
# Components
#---

def description_comp(ap: AstroPilot) -> None:

    st.header("Data description")

    data_descr = st.text_area(
        "Describe the data and tools to be used in the project. You may also include information about the computing resources required.",
        placeholder="E.g. Analyze the experimental data stored in /path/to/data.csv using sklearn and pandas. This data includes time-series measurements from a particle detector.",
        key="data_descr",
        height=100
    )

    uploaded_file = st.file_uploader("Alternatively, upload a file with the data description in markdown format.", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        ap.set_data_description(content)   

    if data_descr:

        ap.set_data_description(data_descr)

    st.markdown("### Current data description:")

    try:
        show_markdown_file(ap.project_dir+"/input_files/data_description.md",label="data description")
    except FileNotFoundError:
        st.write("Data description not generated yet.")

def idea_comp(ap: AstroPilot) -> None:

    st.header("Research idea")
    st.write("Generate a research idea provided the data description.")
    
    # Add model selection dropdowns
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Idea Maker: Generates and selects the best research ideas based on the data description")
        idea_maker_model = st.selectbox(
            "Idea Maker Model",
            ["gpt-4o-2024-11-20", "claude-3-7-sonnet-20250219", "gemini-2.0-flash-lite"],
            index=0,
            key="idea_maker_model"
        )
    with col2:
        st.caption("Idea Hater: Critiques ideas and proposes recommendations for improvement")
        idea_hater_model = st.selectbox(
            "Idea Hater Model",
            ["gpt-4o-2024-11-20", "claude-3-7-sonnet-20250219","gemini-2.0-flash-lite"],
            index=1,
            key="idea_hater_model"
        )
    
    press_button = st.button("Generate", type="primary",key="get_idea")
    if press_button:

        with st.spinner("Generating research idea...", show_time=True):
            ap.get_idea(idea_maker_model=idea_maker_model, idea_hater_model=idea_hater_model)

        st.success("Done!")

    uploaded_file = st.file_uploader("Choose a file with the research idea", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        ap.set_idea(content)

    try:
        show_markdown_file(ap.project_dir+"/input_files/idea.md", extra_format=True, label="idea")
    except FileNotFoundError:
        st.write("Idea not generated yet.")

def method_comp(ap: AstroPilot) -> None:

    st.header("Methods")
    st.write("Generate the methods to be employed in the computation of the results, provided the idea and data description.")

    press_button = st.button("Generate", type="primary",key="get_method")
    if press_button:

        with st.spinner("Generating methods...", show_time=True):
            ap.get_method()

        st.success("Done!")

    uploaded_file = st.file_uploader("Choose a file with the research methods", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        ap.set_method(content)

    try:
        show_markdown_file(ap.project_dir+"/input_files/methods.md",label="methods")
    except FileNotFoundError:
        st.write("Methods not generated yet.")
        
def results_comp(ap: AstroPilot) -> None:

    st.header("Results")
    st.write("Compute the results, given the methods, idea and data description.")

    press_button = st.button("Generate", type="primary",key="get_results")
    if press_button:

        with st.spinner("Computing results...", show_time=True):
            ap.get_results()

        st.success("Done!")

    uploaded_file = st.file_uploader("Choose a file with the results of the research", accept_multiple_files=False)

    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        ap.set_results(content)

    try:

        zip_data = create_zip_in_memory(ap.project_dir+"/input_files/plots")

        st.download_button(
            label="Download plots",
            data=zip_data,
            file_name="plots.zip",
            mime="application/zip",
            icon=":material/download:",
        )

        show_markdown_file(ap.project_dir+"/input_files/results.md",label="results")

    except FileNotFoundError:
        st.write("Results not generated yet.")

def paper_comp(ap: AstroPilot) -> None:

    st.header("Article")
    st.write("Write the article using the computed results of the research.")

    selected_journal = st.selectbox(
        "Choose the journal for the latex style:",
        [j.value for j in Journal],
        index=0, key="journal_select")

    press_button = st.button("Generate", type="primary",key="get_paper")
    if press_button:

        with st.spinner("Writing the paper...", show_time=True):
            ap.get_paper(journal=selected_journal)

        st.success("Done!")
        st.balloons()

    try:

        texfile = ap.project_dir+"/Paper/paper_v4.tex"

        # Ensure that the .tex has been created and we can read it
        with open(texfile, "r") as f:
            f.read()

        zip_data = create_zip_in_memory(ap.project_dir+"/Paper")

        st.download_button(
            label="Download latex files",
            data=zip_data,
            file_name="paper.zip",
            mime="application/zip",
            icon=":material/download:",
        )

    except FileNotFoundError:
        st.write("Latex not generated yet.")

    try:

        pdffile = ap.project_dir+"/Paper/paper_v4.pdf"

        with open(pdffile, "rb") as pdf_file:
            PDFbyte = pdf_file.read()

        st.download_button(label="Download pdf",
                    data=PDFbyte,
                    file_name="paper.pdf",
                    mime='application/octet-stream')

        pdf_viewer(pdffile)

    except FileNotFoundError:
        st.write("Pdf not generated yet.")

def keywords_comp(ap: AstroPilot) -> None:

    st.header("Keywords")
    st.write("Generate keywords from your research text.")
    
    input_text = st.text_area(
        "Enter your research text to extract keywords:",
        placeholder="Multi-agent systems (MAS) utilizing multiple Large Language Model agents with Retrieval Augmented Generation and that can execute code locally may become beneficial in cosmological data analysis. Here, we illustrate a first small step towards AI-assisted analyses and a glimpse of the potential of MAS to automate and optimize scientific workflows in Cosmology. The system architecture of our example package, that builds upon the autogen/ag2 framework, can be applied to MAS in any area of quantitative scientific research. The particular task we apply our methods to is the cosmological parameter analysis of the Atacama Cosmology Telescope lensing power spectrum likelihood using Monte Carlo Markov Chains. Our work-in-progress code is open source and available at this https URL.",
        height=200
    )
    
    n_keywords = st.slider("Number of keywords to generate:", min_value=1, max_value=10, value=5)
    
    press_button = st.button("Generate Keywords", type="primary", key="get_keywords")
    
    if press_button and input_text:
        with st.spinner("Generating keywords..."):
            ap.get_keywords(input_text, n_keywords=n_keywords)
            
            if hasattr(ap.research, 'keywords') and ap.research.keywords:
                st.success("Keywords generated!")
                st.write("### Generated Keywords:")
                for keyword, url in ap.research.keywords.items():
                    st.markdown(f"- [{keyword}]({url})")
            else:
                st.error("No keywords were generated. Please try again with different text.")
    elif press_button and not input_text:
        st.warning("Please enter some text to generate keywords.")