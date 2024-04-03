#!/bin/bash

# This is for litellm

eval "$(pyenv init -)"
cd litellm
pip install -e .
