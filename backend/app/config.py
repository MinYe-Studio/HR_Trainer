"""应用配置。"""
import os
from pathlib import Path

# backend/ 目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite 数据库（开发期），可通过环境变量覆盖
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'hrtrainer.db'}")

# JWT 配置（生产环境务必通过环境变量覆盖 SECRET_KEY）
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me-in-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天

# 考核通过分数（百分制）
EXAM_PASS_SCORE = 60
