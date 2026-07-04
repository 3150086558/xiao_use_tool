from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys
import traceback

from .config import get_settings
from .redis_client import init_redis, close_redis
from .database import engine, Base
from .api import auth, records, todos, notes, menus, users, db_query, health

settings = get_settings()

logger.remove()
logger.add(sys.stdout, level="INFO" if settings.app_env == "production" else "DEBUG")
logger.add("logs/app.log", rotation="10 MB", retention="30 days", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")
    try:
        await init_redis()
        logger.info("Redis 连接成功")
    except Exception as e:
        logger.warning(f"Redis 连接失败: {e}（部分功能可能不可用）")
    yield
    await close_redis()
    logger.info("应用已关闭")


app = FastAPI(
    title="小肖的自用工具 API",
    description="多功能网页工具箱后端 API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"未处理的异常: {exc} - {request.method} {request.url}")
    logger.error(traceback.format_exc())
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误，请稍后重试"},
    )


app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(records.router, prefix="/api/v1/records", tags=["记账"])
app.include_router(todos.router, prefix="/api/v1/todos", tags=["待办事项"])
app.include_router(notes.router, prefix="/api/v1/notes", tags=["备忘录"])
app.include_router(menus.router, prefix="/api/v1/menus", tags=["菜单"])
app.include_router(users.router, prefix="/api/v1/users", tags=["用户管理"])
app.include_router(db_query.router, prefix="/api/v1/db-query", tags=["数据库查询"])


@app.get("/")
async def root():
    return {"message": "小肖的自用工具 API v2.0", "docs": "/docs"}
