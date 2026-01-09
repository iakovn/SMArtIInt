# Use the same OpenModelica base image
FROM openmodelica/openmodelica:v1.22.2-gui

# Switch to root to install system packages
USER root

# Install prerequisites, now including git and bash-completion
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update --yes && \
    apt-get upgrade --yes && \
    apt-get install --yes --no-install-recommends \
    bzip2 \
    ca-certificates \
    git \
    bash-completion \
    sudo \
    wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Configure Conda environment variables
ENV CONDA_DIR=/opt/conda
ENV MAMBA_ROOT_PREFIX=/opt/conda
ENV PATH="${CONDA_DIR}/bin:${PATH}"

# Create a non-root user and set up permissions
RUN useradd -ms /bin/bash -u 1000 vscode && \
    mkdir -p "${CONDA_DIR}" && \
    chown -R vscode:vscode "${CONDA_DIR}" && \
    # Add micromamba shell hook to the user's bashrc for interactive sessions
    echo 'eval "$(micromamba shell hook -s bash)"' >> /home/vscode/.bashrc

# Copy the environment definition
COPY --chown=vscode:vscode linux_64.env.lock requirements.linux64.txt /tmp/

# Switch to the non-root user
USER vscode

# Download micromamba, create environment from file, and clean up
WORKDIR /tmp
RUN wget -qO- "https://micro.mamba.pm/api/micromamba/linux-64/latest" | tar -xvj bin/micromamba && \
    # Create the environment from the YAML file
    ./bin/micromamba create --yes --name dev -f /tmp/linux_64.env.lock && \    
    /opt/conda/envs/dev/bin/pip install -r requirements.linux64.txt && \
    # Move micromamba to a permanent location on the PATH
    mkdir -p "${CONDA_DIR}/bin" && \
    mv ./bin/micromamba "${CONDA_DIR}/bin/" && \
    # Clean up the temporary directory and conda cache
    micromamba clean --all -f -y && \
    rm -rf /tmp/*

# Set up a working directory for the project
WORKDIR /home/vscode/workspace

# Expose Jupyter port
EXPOSE 8888
