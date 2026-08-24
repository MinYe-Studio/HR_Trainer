"""数据库引擎与会话管理。"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base

from .config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 专用
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def _ensure_column(table: str, column: str, ddl: str) -> None:
    """轻量迁移：表已存在但缺少新列时自动补充（开发期用）。"""
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns(table)}
    if column not in cols:
        with engine.begin() as conn:
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}"))


def apply_migrations() -> None:
    """启动时执行的轻量迁移。"""
    _ensure_column("exam_records", "duration_seconds", "INTEGER DEFAULT 0")
    _ensure_column("exam_records", "question_ids", "JSON")


def get_db():
    """FastAPI 依赖：提供数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
