import logging
import json
import time
from fastapi import Request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hybridrag")

async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_sec": round(duration, 4)
    }
    logger.info(json.dumps(log_data))
    return response
