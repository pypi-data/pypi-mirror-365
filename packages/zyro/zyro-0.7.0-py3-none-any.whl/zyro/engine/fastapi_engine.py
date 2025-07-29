import uvicorn
from pathlib import Path 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from zyro.core.router import mount_routes 
from zyro.core.parser import load_yaml_file, get_endpoints, get_active_environment

def create_app(config_path: Path) -> FastAPI:
    app = FastAPI(title="Zyro", description = "Deploy APIs from YAML configs. Instantly.", version="1.0.0")
    
    # Load configuration from the specified YAML file
    config = load_yaml_file(config_path)
    
    # Extract routes from the configuration
    routes = get_endpoints(config)

    env = get_active_environment(config)

    # Dynamically get the path to zyro/static relative to this file
    current_dir = Path(__file__).resolve().parent  # => zyro/engine/
    static_dir = current_dir.parent / "static"     # => zyro/static

    if not static_dir.exists():
        raise RuntimeError(f"Static directory not found at: {static_dir}")

    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Mount the routes to the FastAPI application
    mount_routes(app, routes)
    
    uvicorn.run(
            app, 
            host=config[env]["fastapi"].get('host'), 
            port=config[env]["fastapi"].get('port'), 
            # reload=config[env]["fastapi"].get('reload', False)
        )