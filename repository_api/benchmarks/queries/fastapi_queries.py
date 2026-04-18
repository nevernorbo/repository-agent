"""
50 benchmark queries for fastapi/fastapi.
Python web framework with automatic API docs, dependency injection, and async support.
"""
from benchmarks.queries import Query

REPO_NAME = "fastapi/fastapi"

NL_QUERIES = [
    Query("fa_nl_01", "How does dependency injection work in FastAPI?", "natural_language", "DI system", ["fastapi/dependencies/utils.py"], ["solve_dependencies"]),
    Query("fa_nl_02", "How are request body models validated?", "natural_language", "Pydantic validation", ["fastapi/routing.py"], ["request_body_to_args"]),
    Query("fa_nl_03", "What is the middleware processing pipeline?", "natural_language", "Middleware stack", ["fastapi/applications.py"], ["add_middleware"]),
    Query("fa_nl_04", "How does FastAPI generate OpenAPI documentation?", "natural_language", "OpenAPI schema gen", ["fastapi/openapi/utils.py"], ["get_openapi"]),
    Query("fa_nl_05", "How are path parameters parsed and validated?", "natural_language", "Path param handling", ["fastapi/routing.py", "fastapi/params.py"], ["Path"]),
    Query("fa_nl_06", "How does the APIRouter class work?", "natural_language", "Router implementation", ["fastapi/routing.py"], ["APIRouter"]),
    Query("fa_nl_07", "How are HTTP exceptions handled?", "natural_language", "Exception handlers", ["fastapi/exception_handlers.py"], ["http_exception_handler"]),
    Query("fa_nl_08", "How does FastAPI handle file uploads?", "natural_language", "File upload support", ["fastapi/params.py", "fastapi/datastructures.py"], ["UploadFile"]),
    Query("fa_nl_09", "What is the request lifecycle in FastAPI?", "natural_language", "Request processing", ["fastapi/routing.py"], ["run_endpoint_function"]),
    Query("fa_nl_10", "How are response models used to filter output?", "natural_language", "Response serialization", ["fastapi/routing.py"], ["serialize_response"]),
    Query("fa_nl_11", "How does FastAPI handle WebSocket connections?", "natural_language", "WebSocket support", ["fastapi/routing.py"], ["WebSocketRoute"]),
    Query("fa_nl_12", "What security utilities does FastAPI provide?", "natural_language", "Security schemes", ["fastapi/security/oauth2.py"], ["OAuth2PasswordBearer"]),
    Query("fa_nl_13", "How are query parameters handled?", "natural_language", "Query param extraction", ["fastapi/params.py"], ["Query"]),
    Query("fa_nl_14", "How does FastAPI support background tasks?", "natural_language", "Background task system", ["fastapi/background.py", "fastapi/routing.py"], ["BackgroundTasks"]),
    Query("fa_nl_15", "How is CORS configured in FastAPI?", "natural_language", "CORS middleware", ["fastapi/middleware/cors.py", "fastapi/applications.py"], ["CORSMiddleware"]),
    Query("fa_nl_16", "How does the testclient work?", "natural_language", "Testing utilities", ["fastapi/testclient.py"], ["TestClient"]),
    Query("fa_nl_17", "How are custom validators defined for request data?", "natural_language", "Custom validation", ["fastapi/params.py"], ["Depends"]),
    Query("fa_nl_18", "How does FastAPI handle multiple response types?", "natural_language", "Response classes", ["fastapi/responses.py"], ["JSONResponse"]),
    Query("fa_nl_19", "What is the application startup and shutdown lifecycle?", "natural_language", "Lifespan events", ["fastapi/applications.py"], ["on_event"]),
    Query("fa_nl_20", "How are nested routers composed?", "natural_language", "Router composition", ["fastapi/routing.py"], ["include_router"]),
    Query("fa_nl_21", "How does FastAPI encode response data?", "natural_language", "JSON encoding", ["fastapi/encoders.py"], ["jsonable_encoder"]),
    Query("fa_nl_22", "How are form fields handled differently from JSON body?", "natural_language", "Form data parsing", ["fastapi/params.py"], ["Form"]),
    Query("fa_nl_23", "How does FastAPI auto-generate JSON Schema?", "natural_language", "Schema generation", ["fastapi/openapi/utils.py"], ["get_openapi_path"]),
    Query("fa_nl_24", "What status codes are used in route decorators?", "natural_language", "Status code handling", ["fastapi/routing.py"], ["status_code"]),
    Query("fa_nl_25", "How does FastAPI integrate with Starlette?", "natural_language", "Starlette base classes", ["fastapi/applications.py"], ["FastAPI"]),
]

CODE_QUERIES = [
    Query("fa_code_01", "def get_openapi(", "code", "OpenAPI generation function", ["fastapi/openapi/utils.py"], ["get_openapi"]),
    Query("fa_code_02", "class APIRouter", "code", "APIRouter class def", ["fastapi/routing.py"], ["APIRouter"]),
    Query("fa_code_03", "async def solve_dependencies(", "code", "Dependency resolver", ["fastapi/dependencies/utils.py"], ["solve_dependencies"]),
    Query("fa_code_04", "class FastAPI(", "code", "Main FastAPI class", ["fastapi/applications.py"], ["FastAPI"]),
    Query("fa_code_05", "def jsonable_encoder(", "code", "JSON encoder function", ["fastapi/encoders.py"], ["jsonable_encoder"]),
    Query("fa_code_06", "class Depends", "code", "Depends class", ["fastapi/params.py"], ["Depends"]),
    Query("fa_code_07", "async def serialize_response(", "code", "Response serializer", ["fastapi/routing.py"], ["serialize_response"]),
    Query("fa_code_08", "class UploadFile", "code", "File upload class", ["fastapi/datastructures.py"], ["UploadFile"]),
    Query("fa_code_09", "class OAuth2PasswordBearer", "code", "OAuth2 scheme", ["fastapi/security/oauth2.py"], ["OAuth2PasswordBearer"]),
    Query("fa_code_10", "def include_router(", "code", "Router inclusion method", ["fastapi/routing.py"], ["include_router"]),
    Query("fa_code_11", "class HTTPException", "code", "HTTP exception class", ["fastapi/exceptions.py"], ["HTTPException"]),
    Query("fa_code_12", "async def run_endpoint_function(", "code", "Endpoint runner", ["fastapi/routing.py"], ["run_endpoint_function"]),
    Query("fa_code_13", "class BackgroundTasks", "code", "Background tasks class", ["fastapi/background.py"], ["BackgroundTasks"]),
    Query("fa_code_14", "class Body(", "code", "Body parameter class", ["fastapi/params.py"], ["Body"]),
    Query("fa_code_15", "class Query(", "code", "Query parameter class", ["fastapi/params.py"], ["Query"]),
    Query("fa_code_16", "class Path(", "code", "Path parameter class", ["fastapi/params.py"], ["Path"]),
    Query("fa_code_17", "def add_api_route(", "code", "Route registration", ["fastapi/routing.py"], ["add_api_route"]),
    Query("fa_code_18", "class APIRoute(", "code", "APIRoute class", ["fastapi/routing.py"], ["APIRoute"]),
    Query("fa_code_19", "async def http_exception_handler(", "code", "Exception handler", ["fastapi/exception_handlers.py"], ["http_exception_handler"]),
    Query("fa_code_20", "class Form(", "code", "Form parameter class", ["fastapi/params.py"], ["Form"]),
    Query("fa_code_21", "def get_request_handler(", "code", "Request handler factory", ["fastapi/routing.py"], ["get_request_handler"]),
    Query("fa_code_22", "class Header(", "code", "Header parameter class", ["fastapi/params.py"], ["Header"]),
    Query("fa_code_23", "class Cookie(", "code", "Cookie parameter class", ["fastapi/params.py"], ["Cookie"]),
    Query("fa_code_24", "class WebSocket(", "code", "WebSocket class", ["fastapi/routing.py"], ["WebSocket"]),
    Query("fa_code_25", "class Response(", "code", "Response base class", ["fastapi/responses.py"], ["Response"]),
]

ALL_QUERIES = NL_QUERIES + CODE_QUERIES
