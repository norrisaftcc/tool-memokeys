from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

app = FastAPI(title="MemoKeys API", description="Keyboard shortcut testing platform")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Data directory
DATA_DIR = Path("../data/shortcuts")

# Pydantic models for type safety
class Shortcut(BaseModel):
    id: str
    action: str
    keys: str
    category: str
    difficulty: str
    
class ShortcutSet(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    platform: Optional[str] = None
    file_path: str

def get_available_shortcut_sets() -> List[ShortcutSet]:
    """Scan the data directory for available shortcut sets"""
    shortcut_sets = []
    
    # Scan all subdirectories for JSON files
    for category_dir in DATA_DIR.iterdir():
        if category_dir.is_dir():
            category = category_dir.name
            for json_file in category_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Create shortcut set info
                    shortcut_set = ShortcutSet(
                        id=json_file.stem,  # filename without extension
                        name=data.get("name", json_file.stem),
                        description=data.get("description", ""),
                        category=category,
                        platform=data.get("platform"),
                        file_path=str(json_file.relative_to(DATA_DIR))
                    )
                    shortcut_sets.append(shortcut_set)
                except Exception:
                    # Skip files that can't be parsed
                    continue
    
    return shortcut_sets

@app.get("/")
async def read_root():
    """Serve the main application"""
    return FileResponse("../static/index.html")

@app.get("/api/shortcut-sets", response_model=List[ShortcutSet])
async def list_shortcut_sets():
    """List all available shortcut sets"""
    return get_available_shortcut_sets()

@app.get("/api/shortcuts/{shortcut_set_id}/{platform}")
async def get_shortcuts(shortcut_set_id: str, platform: str) -> Dict[str, Any]:
    """Get shortcuts for a specific set and platform"""
    
    if platform not in ["windows", "mac"]:
        raise HTTPException(status_code=400, detail="Platform must be 'windows' or 'mac'")
    
    # Find the shortcut set
    shortcut_sets = get_available_shortcut_sets()
    shortcut_set = next((s for s in shortcut_sets if s.id == shortcut_set_id), None)
    
    if not shortcut_set:
        raise HTTPException(status_code=404, detail="Shortcut set not found")
    
    file_path = DATA_DIR / shortcut_set.file_path
    
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
                "category": shortcut.get("category", "general"),
                "difficulty": shortcut.get("difficulty", "intermediate")
            }
            
            # Add the appropriate key combination
            if platform == "mac":
                platform_shortcut["keys"] = shortcut.get("mac", shortcut.get("windows", ""))
            else:
                platform_shortcut["keys"] = shortcut.get("windows", "")
            
            # Skip shortcuts without keys for this platform
            if platform_shortcut["keys"]:
                filtered_shortcuts.append(platform_shortcut)
        
        return {
            "name": f"{data['name']} - {platform.title()}",
            "platform": platform,
            "shortcuts": filtered_shortcuts,
            "description": data.get("description", "")
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in shortcut file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoint for backward compatibility
@app.get("/api/shortcuts/{platform}")
async def get_shortcuts_legacy(platform: str) -> Dict[str, Any]:
    """Legacy endpoint - redirects to system shortcuts"""
    return await get_shortcuts("system-shortcuts-windows", platform)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)