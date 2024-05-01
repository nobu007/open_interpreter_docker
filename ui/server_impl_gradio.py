import threading
import time
from functools import partial

import gradio as gr
from langchain.memory import ConversationBufferWindowMemory

from .message_format import show_data_debug
from .message_process import process_messages_gradio


# チャットボットの応答を生成する関数
def chat(interpreter, memory: ConversationBufferWindowMemory, new_query: str, history):
    print("interpreter=", type(interpreter))
    print("memory=", type(memory))
    show_data_debug(history, "history")
    show_data_debug(new_query, "new_query")
    if not new_query:
        print("skip no input")
        return ""

    # Start a separate task for processing messages
    response = ""
    for chunk in process_messages_gradio(new_query, interpreter, memory):
        response += chunk["content"]
        yield response

    # 最終的な応答を履歴に追加する
    yield response


def launch_interface_chat(interpreter, memory):
    # 部分適用された関数を作成する
    chat_with_llm = partial(chat, interpreter, memory)

    iface = gr.ChatInterface(
        fn=chat_with_llm,
        title="Chatbot",
        description="チャットボットとの会話",
        textbox=gr.Textbox(
            placeholder="こんにちは！何かお手伝いできることはありますか？",
            container=False,
            scale=7,
        ),
        theme="soft",
        examples=[
            "ステップバイステップで考えて原因を特定してから修正案を検討してください。",
            "設計方針をmarkdownで整理して報告してください。",
            "作成したファイルと配置先を報告してください。",
            "実装内容を自己レビューしてください。",
            "さらなる改善案を提案して内容を精査した上で作業を進めてください。",
        ],
        cache_examples=True,
        retry_btn=None,
        undo_btn="Delete Previous",
        clear_btn="Clear",
    )
    iface.launch(server_name="0.0.0.0")
    start_auto_input(iface)


def start_auto_input(iface):
    # 自動入力スレッドを開始する
    auto_input_thread = threading.Thread(target=auto_input, args=iface)
    auto_input_thread.daemon = True
    auto_input_thread.start()


def auto_input(iface):
    while True:
        print("auto_input start")
        time.sleep(30)

        # シミュレートされた入力を生成する
        simulated_input = "会話履歴で状況を確認してから自動的に処理を続けてください。"

        # 模擬実行
        iface.textbox.value = simulated_input
        iface.textbox.submit()
        print("auto_input submit")


def server(interpreter):
    # チャット履歴を保持するための状態
    print("ConversationBufferWindowMemory created.")
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="history",
        input_key="input",
        output_key="output",
        return_messages=True,
    )
    launch_interface_chat(interpreter, memory)
