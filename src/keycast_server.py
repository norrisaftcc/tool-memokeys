from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import webbrowser
import threading
import time

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="../static"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("../static/keycast.html")

def open_browser():
    """Open browser after server starts"""
    time.sleep(1)  # Give server time to start
    webbrowser.open("http://127.0.0.1:8001")

if __name__ == "__main__":
    # Start browser opening in background thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Run server
    uvicorn.run(app, host="127.0.0.1", port=8001)