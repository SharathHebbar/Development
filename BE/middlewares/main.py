# Rate Limiting the APIs

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import time
from collections import defaultdict
from typing import Dict
app = FastAPI()


class AdvancedMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_records: Dict[str, float] = defaultdict(float)

    async def log_message(self, message:str):
        print(message)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        if current_time - self.rate_limit_records[client_ip] < 1: # 1 request per second
            return Response(content="Rate Limit Exceeded", status_code=429)
        
        self.rate_limit_records[client_ip] = current_time
        path = request.url.path
        await self.log_message(f"Request to {path}")

        # Process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Add custom headers without modifying the original headers object
        custom_headers = {"X-Process-Time": str(process_time)}
        for header, value in custom_headers.items():
            response.headers.append(header, value)

        # Asynchronous logging for processing time
        await self.log_message(f"Response for {path} took {process_time} seconds")

        return response

# Add the advanced middleware to the app
app.add_middleware(AdvancedMiddleware)

@app.get("/")
async def main():
    return {"message": "Hello"}