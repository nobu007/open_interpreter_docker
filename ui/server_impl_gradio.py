import time
from functools import partial

import gradio as gr
from langchain.memory import ConversationBufferWindowMemory

from .message_format import show_data_debug
from .message_process import process_messages_gradio


# チャットボットの応答を生成する関数
def chat_old(
    interpreter, memory: ConversationBufferWindowMemory, history, new_query: str
):
    show_data_debug(history, "history")
    show_data_debug(new_query, "new_query")
    history = history + [(new_query, None)]

    # Start a separate task for processing messages
    response = ""
    for chunk in process_messages_gradio(new_query, interpreter, memory):
        response += chunk["content"]
        history[-1] = (history[-1][0], response)
        yield history

    # 最終的な応答を履歴に追加する
    history[-1] = (history[-1][0], response)
    yield history


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


def launch_interface_chat_single(interpreter, memory):
    # 部分適用された関数を作成する
    chat_with_llm = partial(chat, interpreter, memory)

    iface = gr.Interface(
        fn=chat_with_llm,
        inputs=[
            gr.Chatbot(value=[("ユーザー", "こんにちは")], label="チャット履歴"),
            gr.Textbox(label="新しいメッセージ"),
        ],
        outputs=gr.Chatbot(label="更新されたチャット履歴"),
    )
    iface.launch(server_name="0.0.0.0")
    auto_input_single(iface, chat_with_llm, interpreter, memory)


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
    auto_input(iface)


def auto_input(iface):
    while True:
        time.sleep(30)

        # シミュレートされた入力を生成する
        simulated_input = "会話履歴で状況を確認してから自動的に処理を続けてください。"

        # 模擬実行
        iface.textbox.value = simulated_input
        iface.textbox.submit()


def auto_input_old(iface, chat_with_llm):
    while True:
        time.sleep(30)

        # シミュレートされた入力を生成する
        simulated_input = "会話履歴から状況を確認してから、自動的に処理を続けてください。"

        # チャット履歴を取得する
        history = iface.get_history()

        # 結果を出力する
        print("自動入力:", simulated_input)
        final_new_history = None
        for new_history in chat_with_llm(history, simulated_input):
            final_new_history = new_history
        print("結果:", final_new_history[-1][1])

        # 更新された履歴をチャットインターフェースに適用する
        iface.set_history(final_new_history)


def auto_input_single(iface, chat_with_llm, interpreter, memory):
    # 自動入力をシミュレートする
    while True:
        # 次の自動入力までの遅延を追加する
        time.sleep(30)

        simulated_input = "会話履歴から状況を確認して、自動的に処理を続けてください。"
        history = iface.outputs[0].value

        # 結果を出力する
        print("自動入力:", simulated_input)
        final_new_history = None
        for new_history in chat_with_llm(history, simulated_input):
            final_new_history = new_history
        print("結果:", final_new_history[-1][1])

        # 結果をGradioのUIに反映する
        iface.outputs[0].update(value=final_new_history)


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
