from dotenv import load_dotenv
from gui_agent_loop_core.gui_agent_loop_core import GuiAgentLoopCore

from interpreter.core.core import OpenInterpreter

# Load the users .env file into environment variables
load_dotenv(verbose=True, override=False)

# memo: 2024/05/01
# structure of OpenInterpreter
#   interpreter: top layer
#       core:
#           core.py(OpenInterpreter): 3 topic exist
#               <llm main call sequence>
#                    chat() -> _streaming_chat() -> _respond_and_store() -> respond() -> llm.run()
#               <python code in system_message is run() via render_message() before llm>
#                    If python code exist in message, respond() -> render_message() -> computer.run() before llm.
#               <response sequence(use computer)>
#                   _respond_and_store() -> respond() -> computer.run() -> terminal._streaming_run()
#           computer: core functions like os, files, etc.
#           os: run shell command via computer.run()
#           terminal: run python command via computer.run()
#           llm: run() use litellm via run_text_llm() or run_function_calling_llm()
#               litellm: llm call
#           server.py: server version. fastapi and uvicorn. call interpreter.chat()
#           respond.py: respond()
#       terminal_interface:
#           terminal_interface: cli only version? call interpreter.chat()
#   ui: gradio interface
#       server_impl_gradio.py: call interpreter.chat()
# interpreter: top layer

# interpreter
interpreter = OpenInterpreter(
    auto_run=True,
)
# interpreter.llm.model = "anthropic/claude-3-haiku-20240307"
# interpreter.llm.model = "openrouter/anthropic/claude-3-haiku"
# interpreter.llm.model = "gemini/gemini-pro"
interpreter.llm.model = "gemini/gemini-1.5-pro-latest"
# interpreter.llm.model = "gemini/gemini-1.5-pro"  # not working at 2024/05/06
print("api_base=", interpreter.llm.api_base)

interpreter.verbose = False
interpreter.sync_computer = False
interpreter.system_message += """
Please use "/app/work". This is permanent place after reboot computer.
  /app/work/python: your python code.
  /app/work/input: input files for python.
  /app/work/output: output files for python.
You should save any important python source and input and output files here.
If you lost previous work, you should check here and resume from the files.

###IMPORTANT!!##
Put created python with main logic under "/app/work/python/main.py" for every time.
###IMPORTANT!!##
"""
interpreter.llm_drop_params = True
interpreter.llm_modify_params = True

# llm(litellm)
llm = interpreter.llm
llm.max_tokens = 4096
llm.context_window = 20000

# computer
computer = interpreter.computer
computer.debug = False
computer.verbose = False
computer.save_skills = True
interpreter.llm.supports_functions = False

core = GuiAgentLoopCore()
core.launch_server(interpreter)
