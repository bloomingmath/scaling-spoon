from starlette.middleware.base import BaseHTTPMiddleware

class RedirectNextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        next = request.query_params.get("next", None)
        response = await call_next(request)
        response.headers['X-Custom'] = next
        return response
