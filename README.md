# AstroPilotApp

GUI for [AstroPilot](https://github.com/AstroPilot-AI/AstroPilot.git) powered by [streamlit](https://streamlit.io).

## Run locally

Run with:

```bash
streamlit run app.py
```

## Run in Docker

You need the wheel of a build of astropilot. You may need `sudo` permission [or use this link](https://docs.docker.com/engine/install/linux-postinstall/). To build the docker run:

```bash
docker build -t astropilot-app .
```

To run the app:
```bash
docker run --rm -v "$PWD" astropilot-app
```

## TODO

- [x] Prerender markdown files if they exist
- [x] Add option to browse files
- [x] Add option to set ideas, methods, results, through files
- [ ] Improve figures being shown in results
- [x] Render latex pdf in app
- [ ] Refactor components code since there is a lot of duplication
- [x] Add keywords tab
- [ ] Allow for providing API keys through the sidebar
- [ ] Show total computing time
- [ ] Run in Docker

