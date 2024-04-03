#!/bin/bash

sudo apt update
sudo apt install -y less vim emacs nano nkf tree git tmux zip cifs-utils fonts-noto-color-emoji curl wget sudo
eval "$(pyenv init -)"
bash installers/oi-linux-installer_pre.sh
pip install -r requirements.txt
pip install 'uvicorn[standard]'
pip install google-generativeai
pip install langchain
pip install gradio
pip install toml
pip install platformdirs
