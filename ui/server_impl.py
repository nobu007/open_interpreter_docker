import asyncio

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import PlainTextResponse
from langchain.memory import ConversationBufferWindowMemory
from message_process import process_messages_async

from ui.template_engine import TemplateEngine

memory = ConversationBufferWindowMemory(
    k=10,
    memory_key="history",
    input_key="input",
    output_key="output",
    return_messages=True,
)


def server(interpreter, host="0.0.0.0", port=8000):
    app = FastAPI()

    template_engine = TemplateEngine("ui/templates")
    rendered_html = template_engine.render_template(
        "test.html", ws_url="ws://localhost:8000/"
    )

    @app.get("/test")
    async def test_ui():
        return PlainTextResponse(
            rendered_html,
            media_type="text/html",
        )

    @app.websocket("/")
    async def i_test(websocket: WebSocket):
        print("i_test in")
        await websocket.accept()
        message_queue = asyncio.Queue()

        # Start a separate task for processing messages
        processing_task = asyncio.create_task(
            process_messages_async(websocket, message_queue, interpreter, memory)
        )

        while True:
            print("websocket.receive_json in")
            data = await websocket.receive_json()
            print("websocket.receive_json out")

            if data.get("type") == "stop":
                # Process "stop" command immediately
                print("Received stop command. Stopping.")
                break

            # Add the message to the queue
            await message_queue.put(data["content"])

        # Wait for the processing task to complete
        await processing_task

        # Cancel the processing task if it's still running
        processing_task.cancel()
        print("i_test out")

    print(
        "\nOpening an `i.protocol` compatible WebSocket endpoint at http://localhost:8000/."
    )
    print("\nVisit http://localhost:8000/test to test the WebSocket endpoint.\n")

    @app.on_event("startup")
    async def on_startup():
        print("WebSocket server started.")

    @app.on_event("shutdown")
    async def on_shutdown():
        print("WebSocket server stopped.")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        ws_ping_interval=300,
        ws_ping_timeout=300,
    )
