#!/bin/bash

eval "$(pyenv init -)" && pip install -e .
cd litellm; eval "$(pyenv init -)" && pip install -e .
