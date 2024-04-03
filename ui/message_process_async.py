import asyncio
import traceback

from langchain.memory import ConversationBufferWindowMemory
from message_format import format_response


async def process_messages_async(
    websocket, message_queue, interpreter, memory: ConversationBufferWindowMemory
):
    while True:
        try:
            # Get the next message from the queue
            message_content = await message_queue.get()
            message = {"role": "user", "type": "message", "content": message_content}
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
                await websocket.send_json(
                    {
                        "type": chunk_type,
                        "role": chunk_role,
                        "content": response,
                        "start": chunk_start,
                        "end": chunk_end,
                    }
                )
                await asyncio.sleep(0.01)
                response_list.append(response)
            full_response = "".join(response_list)
            memory.save_context({"input": messages}, {"output": full_response})

            message_queue.task_done()
        except Exception as e:
            print(f"Error processing message: {e}")
            traceback.print_exc()


async def process_messages_async_gradio(
    message_content, interpreter, memory: ConversationBufferWindowMemory
):
    try:
        # Get the next message from the queue
        message = {"role": "user", "type": "message", "content": message_content}
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
            yield {
                "type": chunk_type,
                "role": chunk_role,
                "content": response,
                "start": chunk_start,
                "end": chunk_end,
            }

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
