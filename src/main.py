from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import json
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, validator
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MemoKeys API", description="Keyboard shortcut testing platform")

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="../static"), name="static")

# Data directory
DATA_DIR = Path("../data/shortcuts").resolve()

# Ensure DATA_DIR exists and is secure
if not DATA_DIR.exists():
    logger.error(f"Data directory does not exist: {DATA_DIR}")
    raise RuntimeError("Data directory not found")


# Enums for validation
class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Platform(str, Enum):
    WINDOWS = "windows"
    MAC = "mac"


# Pydantic models for type safety
class Shortcut(BaseModel):
    id: str
    action: str
    keys: str
    category: str
    difficulty: Difficulty


class ShortcutSet(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: str
    platform: Optional[Platform] = None
    file_path: str

    @validator("file_path")
    def validate_file_path(cls, v):
        # Ensure file_path is relative and doesn't contain directory traversal
        if ".." in v or v.startswith("/") or "\\" in v:
            raise ValueError("Invalid file path")
        return v


def get_available_shortcut_sets() -> List[ShortcutSet]:
    """Scan the data directory for available shortcut sets"""
    shortcut_sets = []

    try:
        # Scan all subdirectories for JSON files
        for category_dir in DATA_DIR.iterdir():
            if not category_dir.is_dir():
                continue

            category = category_dir.name

            # Skip hidden directories and validate category name
            if (
                category.startswith(".")
                or not category.replace("-", "").replace("_", "").isalnum()
            ):
                logger.warning(f"Skipping invalid category directory: {category}")
                continue

            for json_file in category_dir.glob("*.json"):
                try:
                    # Security check: ensure file is within allowed directory
                    if not json_file.resolve().is_relative_to(DATA_DIR):
                        logger.warning(
                            f"Skipping file outside data directory: {json_file}"
                        )
                        continue

                    with open(json_file, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    # Validate required fields
                    if (
                        not isinstance(data, dict)
                        or "name" not in data
                        or "shortcuts" not in data
                    ):
                        logger.warning(f"Invalid JSON structure in {json_file}")
                        continue

                    # Create relative path safely
                    relative_path = json_file.relative_to(DATA_DIR)

                    # Create shortcut set info with validation
                    shortcut_set = ShortcutSet(
                        id=json_file.stem,  # filename without extension
                        name=data.get("name", json_file.stem),
                        description=data.get("description", ""),
                        category=category,
                        platform=data.get("platform"),
                        file_path=str(relative_path),
                    )
                    shortcut_sets.append(shortcut_set)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in {json_file}: {e}")
                    continue
                except ValueError as e:
                    logger.warning(f"Invalid data in {json_file}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error processing {json_file}: {e}")
                    continue

    except Exception as e:
        logger.error(f"Error scanning data directory: {e}")

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
async def get_shortcuts(shortcut_set_id: str, platform: Platform) -> Dict[str, Any]:
    """Get shortcuts for a specific set and platform"""

    # Validate shortcut_set_id format
    if not shortcut_set_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid shortcut set ID format")

    # Find the shortcut set from our validated list
    shortcut_sets = get_available_shortcut_sets()
    shortcut_set = next((s for s in shortcut_sets if s.id == shortcut_set_id), None)

    if not shortcut_set:
        raise HTTPException(status_code=404, detail="Shortcut set not found")

    # Construct file path securely
    file_path = DATA_DIR / shortcut_set.file_path

    # Additional security check: ensure resolved path is within DATA_DIR
    try:
        resolved_path = file_path.resolve()
        if not resolved_path.is_relative_to(DATA_DIR):
            logger.error(f"Path traversal attempt detected: {shortcut_set.file_path}")
            raise HTTPException(status_code=403, detail="Access denied")
    except (OSError, ValueError) as e:
        logger.error(f"Invalid file path: {shortcut_set.file_path}, error: {e}")
        raise HTTPException(status_code=400, detail="Invalid file path")

    try:
        with open(resolved_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Filter shortcuts for the requested platform
        filtered_shortcuts = []
        for shortcut in data["shortcuts"]:
            # Create platform-specific shortcut
            platform_shortcut = {
                "id": shortcut["id"],
                "action": shortcut["action"],
                "category": shortcut.get("category", "general"),
                "difficulty": shortcut.get("difficulty", "intermediate"),
            }

            # Add the appropriate key combination
            if platform == "mac":
                platform_shortcut["keys"] = shortcut.get(
                    "mac", shortcut.get("windows", "")
                )
            else:
                platform_shortcut["keys"] = shortcut.get("windows", "")

            # Skip shortcuts without keys for this platform
            if platform_shortcut["keys"]:
                filtered_shortcuts.append(platform_shortcut)

        return {
            "name": f"{data['name']} - {platform.title()}",
            "platform": platform,
            "shortcuts": filtered_shortcuts,
            "description": data.get("description", ""),
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in shortcut file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoint for backward compatibility
@app.get("/api/shortcuts/{platform}")
async def get_shortcuts_legacy(platform: Platform) -> Dict[str, Any]:
    """Legacy endpoint - redirects to appropriate system shortcuts based on platform"""
    # Choose appropriate default shortcut set based on platform
    if platform == Platform.MAC:
        default_set = "mac-basics"
    else:  # Windows
        default_set = "system-shortcuts-windows"

    logger.info(
        f"Legacy endpoint accessed for platform {platform}, redirecting to {default_set}"
    )
    return await get_shortcuts(default_set, platform)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
