#!/bin/bash

# This is for zero resources

# nodejs
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs -y

sudo apt update
sudo apt install -y less vim emacs nano nkf tree git tmux zip cifs-utils fonts-noto-color-emoji curl wget sudo
