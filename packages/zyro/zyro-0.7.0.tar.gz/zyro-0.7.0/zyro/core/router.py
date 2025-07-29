import os 
from fastapi import FastAPI, Request
from zyro.core.executor import handle_reponse
from fastapi.responses import HTMLResponse
from typing import Callable, Any, List, Dict, Union 
import re 
import importlib.resources as pkg_resources
from zyro import static

def zyro_info_page() -> HTMLResponse:
    try:
        # Reads intro.html as a binary stream
        with pkg_resources.files(static).joinpath("intro.html").open("r", encoding="utf-8") as file:
            content = file.read() 
        return HTMLResponse(content=content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Zyro API is running</h1>", status_code=200)

# This module provides functionality to handle responses and mount routes in a FastAPI application.
def generate_handler(response_def: Dict[str, Any]) -> Callable:
    handler = handle_reponse(response_def)
    if isinstance(handler, Callable):
        return handler
    
    async def async_handler(_: Request):
        return handler
    
    return async_handler 

# This function mounts a single route to the FastAPI application.
# It extracts the path, methods, and response definition from the route and adds it to the app.
# It also handles the case where the path may need to be cleaned up (e.g
def mount_single_route(app: FastAPI, base_path: str, route: List[Dict[str, Any]]) -> None:
    full_path = re.sub(r"^/|/$", "", base_path)
    methods = route.get("method", ["GET"]) 
    response_def = route.get("response") 

    app.add_api_route(
        path=f"/{full_path}",
        endpoint=generate_handler(response_def),
        methods=methods,
        name=full_path
    )

# Mounts routes to the FastAPI application
# This function iterates through the provided routes and mounts them to the FastAPI app.
# It handles nested routes and adds a default /zyro/ endpoint.
def mount_routes(app: FastAPI, routes: List[Dict[str, Any]]) -> None:
    for route in routes:
        if "routes" in route:
            base_path = route.get("path")
            nested_routes = route["routes"] 
            for nested_route in nested_routes:
                mount_single_route(app, base_path, nested_route)
        else:
            mount_single_route(app, route.get("path"), route)

    # Add /zyro info endpoint
    app.add_api_route(
        path="/zyro/",
        endpoint=zyro_info_page,
        methods=["GET"],
        name="zyro_info"
    )