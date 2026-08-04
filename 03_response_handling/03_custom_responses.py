"""
CUSTOM RESPONSES
================
This script demonstrates how to return different types of responses,
such as HTML, Streaming chunks, file assets, and HTTP redirects.
"""

import time
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, FileResponse

app = FastAPI(title="Custom Responses")

# 1. Returning HTML Response
@app.get("/html", response_class=HTMLResponse)
def get_html():
    html_content = """
    <html>
        <head><title>FastAPI custom response</title></head>
        <body>
            <h1>Hello from HTMLResponse!</h1>
            <p>This is a raw HTML response returned by FastAPI.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# 2. Redirect Response
@app.get("/redirect")
def redirect_to_docs():
    return RedirectResponse(url="/docs")

# 3. Streaming Response
# Useful for large files, real-time generators, or AI model responses.
def slow_data_generator():
    for i in range(1, 6):
        time.sleep(1) # Simulate slow generation
        yield f"Chunk {i}\n"

@app.get("/stream")
def stream_data():
    return StreamingResponse(slow_data_generator(), media_type="text/plain")

# 4. File Response
# Returns a physical file from the server's workspace.
# To demonstrate, we return this script file itself!
@app.get("/file")
def download_code_file():
    # Return this file as an attachment download
    return FileResponse(
        path=__file__, 
        filename="custom_responses_example.py", 
        media_type="application/octet-stream"
    )

# To run this file:
# uvicorn 03_response_handling.03_custom_responses:app --reload
