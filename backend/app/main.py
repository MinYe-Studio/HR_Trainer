"""FastAPI 主应用入口。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine, apply_migrations
from .routers import auth, content, dashboard, exam, path as path_router, placement, practice, progress, stats
from . import models  # noqa: F401  确保模型注册到 Base.metadata

app = FastAPI(
    title="HR技能训练营 API",
    description="HR技能讲解·训练·考核一体化应用后端",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发期放开，生产需收紧
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 骨架阶段：启动时自动建表 + 轻量迁移（S2 起由 seed 脚本负责内容填充）
apply_migrations()
Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api")
app.include_router(placement.router, prefix="/api")
app.include_router(content.router, prefix="/api")
app.include_router(progress.router, prefix="/api")
app.include_router(practice.router, prefix="/api")
app.include_router(exam.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(path_router.router, prefix="/api")


@app.get("/api/health", tags=["系统"])
def health():
    return {"status": "ok", "service": "hrtrainer-api", "version": "0.1.0"}
