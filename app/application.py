import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics
from app.api.v1.posts.handlers import routers as post_route
from app.api.v1.comments.handlers import routers as comment_route
from app.api.v1.auth.handlers import routers as auth_route

from .settings import settings

app = FastAPI()


# Routes
app.add_route("/metrics", handle_metrics)
app.include_router(post_route)
app.include_router(comment_route)
app.include_router(auth_route)

# TODO кастомные ответы
# @app.exception_handler(CustomAPIException)
# async def update_exception_handler(request: Request, exc: CustomAPIException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": exc.msg, "success": False},
#     )


# Metrics
app.add_middleware(
    PrometheusMiddleware,
    skip_paths=settings.METRICS_SKIP_PATH,
    group_paths=True,
    app_name=settings.SERVICE_NAME,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cross_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sentry integration
sentry_sdk.init(dsn=settings.SENTRY_DSN)
app.add_middleware(SentryAsgiMiddleware)
