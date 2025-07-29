import importlib
from typing import Any, Dict, Union, Callable
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
import traceback


def handle_reponse(response_def: Dict[str, Any]) -> Union[Callable, Any]:
    response_type = response_def.get("type", "json")

    try:
        if response_type == "html":
            def handler():
                return HTMLResponse(
                    content=response_def.get("value", ""),
                    status_code=response_def.get("status_code", 200)
                )
            return handler

        elif response_type == "raw":
            def handler():
                return PlainTextResponse(
                    content=response_def.get("value", ""),
                    status_code=response_def.get("status_code", 200)
                )
            return handler

        elif response_type == "json":
            def handler():
                return JSONResponse(
                    content=response_def.get("value", {}),
                    status_code=response_def.get("status_code", 200)
                )
            return handler
        
        elif response_type == "python":
            module_path = response_def.get("value", "")
            function_name = response_def.get("function", "")
            module = importlib.import_module(module_path)
            function = getattr(module, function_name, None)

            if callable(function):
                return function()
            else:
                raise ValueError(f"Function '{function_name}' not found in module '{module_path}'")

        else:
            return JSONResponse(
                content={"error": f"Unsupported response type: {response_type}"},
                status_code=400
            )

    except Exception as e:
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)
