from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
from typing import List, Dict, Any

app = FastAPI(title="MemoKeys API", description="Keyboard shortcut testing platform")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Data directory
DATA_DIR = Path("../data/shortcuts/system")

@app.get("/")
async def read_root():
    """Serve the main application"""
    return FileResponse("../static/index.html")

@app.get("/api/shortcuts/{platform}")
async def get_shortcuts(platform: str) -> Dict[str, Any]:
    """Get shortcuts for a specific platform (windows/mac)"""
    
    if platform not in ["windows", "mac"]:
        raise HTTPException(status_code=400, detail="Platform must be 'windows' or 'mac'")
    
    # For MVP, use the basic system shortcuts
    file_path = DATA_DIR / "system-shortcuts-windows.json"
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Shortcut set not found")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Filter shortcuts for the requested platform
        filtered_shortcuts = []
        for shortcut in data["shortcuts"]:
            # Create platform-specific shortcut
            platform_shortcut = {
                "id": shortcut["id"],
                "action": shortcut["action"],
                "category": shortcut["category"],
                "difficulty": shortcut["difficulty"]
            }
            
            # Add the appropriate key combination
            if platform == "mac":
                platform_shortcut["keys"] = shortcut.get("mac", shortcut.get("windows", ""))
            else:
                platform_shortcut["keys"] = shortcut.get("windows", "")
            
            filtered_shortcuts.append(platform_shortcut)
        
        return {
            "name": f"{data['name']} - {platform.title()}",
            "platform": platform,
            "shortcuts": filtered_shortcuts
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in shortcut file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)