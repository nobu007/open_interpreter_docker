import time
from functools import partial

import gradio as gr
from langchain.memory import ConversationBufferWindowMemory

from ui.template_engine import TemplateEngine

from .message_format import show_data_debug
from .message_process import process_messages_gradio
from .message_process_async import process_messages_async_gradio


# チャットボットの応答を生成する関数
def chat(interpreter, memory, state, history, new_query):
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


async def chat_async(interpreter, memory, state, history, new_query):
    history = history + [(new_query, None)]

    # Start a separate task for processing messages
    response = ""
    async for chunk in process_messages_async_gradio(new_query, interpreter, memory):
        response += chunk["content"]
        history[-1] = (history[-1][0], response)
        yield history

    # 最終的な応答を履歴に追加する
    history[-1] = (history[-1][0], response)
    yield history


def init_gradio_single(interpreter, memory, state):
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

    return iface, chat_with_llm


def init_gradio_single_async(interpreter, memory, state):
    # 部分適用された関数を作成する
    async def chat_with_llm_async(history, new_query):
        async for result in chat_async(interpreter, memory, state, history, new_query):
            yield result

    iface = gr.Interface(
        fn=chat_with_llm_async,
        inputs=[
            gr.Chatbot(value=[("ユーザー", "こんにちは")], label="チャット履歴"),
            gr.Textbox(label="新しいメッセージ"),
        ],
        outputs=gr.Chatbot(label="更新されたチャット履歴"),
    )

    return iface, chat_with_llm_async


def init_gradio(state1, state2, interpreter, memory):
    # 部分適用された関数を作成する
    chat_with_llm = partial(process_messages_gradio, interpreter, memory)

    with gr.Blocks() as iface:
        with gr.Row():
            with gr.Column():
                chatbot1 = gr.Chatbot([])
                query1 = gr.Textbox()
                query1.submit(
                    fn=chat_with_llm,
                    inputs=[chatbot1, state1, query1, interpreter],
                    outputs=[chatbot1, state1, query1],
                )
                gr.Markdown("Chatbot 1")
            with gr.Column():
                chatbot2 = gr.Chatbot([])
                query2 = gr.Textbox()
                query2.submit(
                    fn=chat_with_llm,
                    inputs=[chatbot2, state2, query2, interpreter],
                    outputs=[chatbot2, state2, query2],
                )
                gr.Markdown("Chatbot 2")

    return iface


def auto_input(gradio_fn, interpreter, memory, state1):
    # 自動入力をシミュレートする
    while True:
        simulated_input = "会話履歴から状況を確認してから、自動的に処理を続けてください。"
        result = gradio_fn(simulated_input, interpreter, memory, state1)

        # 結果を出力する
        print("自動入力:", simulated_input)
        print("結果:", result)

        # 次の自動入力までの遅延を追加する
        time.sleep(5)


def server(interpreter):
    # チャット履歴を保持するための状態
    state1 = gr.State([])
    state2 = gr.State([])
    print("ConversationBufferWindowMemory created.")
    memory = ConversationBufferWindowMemory(
        k=10,
        memory_key="history",
        input_key="input",
        output_key="output",
        return_messages=True,
    )
    iface, gradio_fn = init_gradio_single(interpreter, memory, state1)
    # iface = init_gradio(state1, state2, interpreter, memory)
    iface.launch(server_name="0.0.0.0")
    auto_input(gradio_fn, interpreter, memory, state1)
