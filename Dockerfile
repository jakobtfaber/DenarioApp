# Use an official Python image as base
FROM python:3.13-slim

# Set environment variables to avoid interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies including LaTeX and some fonts for xelatex
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-xetex \
    texlive-science \
    texlive-publishers \
    texlive-plain-generic \
    fonts-freefont-ttf \
    fonts-dejavu \
    fonts-noto \
    fonts-liberation \
    fonts-inconsolata \
    fonts-texgyre \
    build-essential \
    git \
    curl \
    ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user

# Switch to the "user" user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Install the project into `/app`
WORKDIR $HOME/app

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
# Copy all the app code to the docker
COPY --chown=user . $HOME/app

# Install with constraints to prefer binary wheels
COPY --chown=user constraints.txt $HOME/app/constraints.txt
RUN pip install --upgrade pip && \
    pip install -c constraints.txt .

# Add the entrypoint script
COPY --chown=user entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# This informs Docker that the container will listen on port 8501 at runtime.
EXPOSE 8501

# Touch a .env so it can be shared as a volume (being a single file instead of a folder requires this)
RUN touch .env

# Command to run the app
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Use entrypoint script to handle optional local Denario installation
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["streamlit", "run", "src/denario_app/app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless", "true"]
