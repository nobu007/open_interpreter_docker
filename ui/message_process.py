import asyncio
import time
import traceback

from langchain.memory import ConversationBufferWindowMemory

from .message_format import format_response


def process_messages_gradio(
    new_query: str,
    interpreter,
    memory: ConversationBufferWindowMemory,
):
    try:
        # Get the next message from the queue
        message = {"role": "user", "type": "message", "content": new_query}
        messages = memory.load_memory_variables({})["history"]
        print("memory.load_memory_variables=", messages)
        messages.append(message)

        response_list = []
        for (
            response,
            chunk_type,
            chunk_role,
            chunk_start,
            chunk_end,
        ) in process_and_format_message(message, interpreter):
            # Send out assistant message chunks
            response_data = {
                "type": chunk_type,
                "role": chunk_role,
                "content": response,
                "start": chunk_start,
                "end": chunk_end,
            }

            yield response_data
            response_list.append(response)
        full_response = "".join(response_list)
        memory.save_context({"input": messages}, {"output": full_response})

    except Exception as e:
        print(f"Error processing message: {e}")
        traceback.print_exc()


def process_and_format_message(message, interpreter):
    try:
        for chunk in interpreter.chat(message, display=False, stream=True):
            yield format_response(chunk)
    except Exception as e:
        print(f"Error in chat: {e}")
