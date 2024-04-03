import os

from dotenv import load_dotenv

from interpreter.core.core import OpenInterpreter

# from ui.server_impl import server
from ui.server_impl_gradio import server

# Load the users .env file into environment variables
load_dotenv(verbose=True, override=False)

interpreter = OpenInterpreter(
    auto_run=True,
)
# interpreter.llm.model = "claude-3-haiku-20240307"
interpreter.llm.model = "anthropic/claude-3-haiku-20240307"
# interpreter.llm.model = "openrouter/anthropic/claude-3-haiku"
# interpreter.llm.model = "openrouter/anthropic/claude-3-haiku:beta"
# interpreter.llm.api_base = os.getenv("API_BASE")
print("api_base=", interpreter.llm.api_base)

interpreter.llm.max_tokens = 2000
interpreter.verbose = False
interpreter.sync_computer = False
interpreter.system_message += """
Your workdir is "/app/work". You should save any input and output files in this directory.
If you lost previous work, you should check this directory and result from files.
"""
interpreter.llm_drop_params = True
interpreter.llm_modify_params = True
computer = interpreter.computer
computer.debug = False
computer.verbose = False
interpreter.llm.supports_functions = False
server(interpreter)
