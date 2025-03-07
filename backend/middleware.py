import time
import logging
from urllib import response
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response


logging.basicConfig(
    filename="app.log", 
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("uvicorn.access")
logger.disabled = True  

def register_middleware(app: FastAPI):
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        start_time = time.time()

        request_info = (
            f"Incoming Request: {request.method} {request.url.path} | "
            f"Headers: {dict(request.headers)}"
        )
        print(request_info)
        logging.info(request_info)

        response: Response = await call_next(request)
        process_time = time.time() - start_time

        response_info = (
            f"Response: {response.status_code} | "
            f"Processed in {process_time:.6f} sec"
        )
        print(response_info)
        logging.info(response_info)

        return response
    


    return app


