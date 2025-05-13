# AstroPilotApp

GUI for [AstroPilot](https://github.com/AstroPilot-AI/AstroPilot.git), powered by [streamlit](https://streamlit.io).

## Run locally

Install the GUI from source following one of the following steps.

1. Install with pip

    ```bash
    pip install -e .
    ```

2. Install with [uv](https://docs.astral.sh/uv/)

    ```bash
    uv sync
    ```

Run the webapp with:

```bash
streamlit run src/app.py
```

## Run in Docker

You need the wheel of a build of astropilot. You may need `sudo` permission [or use this link](https://docs.docker.com/engine/install/linux-postinstall/). To build the docker run:

```bash
docker build -t astropilot-app .
```

To run the app:

```bash
docker run -p 8501:8501 --rm \
    -v $(pwd)/project_app:/app/project_app \
    -v $(pwd)/data:/app/data \
    -v $(pwd).env/app/.env \
    astropilot-app
```

That command exposes the default streamlit port `8501`, change it to use a different port. You can mount additional volumes to share data with the docker using the `-v` flag. The above command shares the `project_app` folder, where the project files are generated, a `data`folder, where the required data would be present, and a `.env` file with the API keys (so no need to parse them manually).

You can also use [docker compose](https://docs.docker.com/compose/), you can just run

```bash
docker compose up --watch
```

to build the iamge and run the container.

## TODO

- [x] Prerender markdown files if they exist
- [x] Add option to browse files
- [x] Add option to set ideas, methods, results, through files
- [ ] Ensure that plots are shown in markdown results
- [x] Render latex pdf in app
- [ ] Refactor components code since there is a lot of duplication
- [x] Add keywords tab
- [x] Allow for providing API keys through the sidebar
- [ ] Show total computing time
- [x] Run in Docker
- [ ] Include API validators
- [x] Download .md files
- [x] Upload .env directly
- [ ] Print console log in GUI
- [ ] Show files in project
- [x] Allow to download plots
- [x] Allow to download tex and pdf
- [x] Allow to upload several project files at the same time
- [x] Modify dockerfile to build with uv for faster build
- [ ] Generate pdf from latex for all journals
- [x] Allow to upload plots

