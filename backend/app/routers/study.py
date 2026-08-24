"""学习时长路由：按用户+日期累计学习时长。"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/study", tags=["学习时长"])


class StudyLogRequest(BaseModel):
    seconds: int


def _today_str() -> str:
    return date.today().isoformat()


@router.post("/log")
def log_study(
    payload: StudyLogRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上报学习时长（累加到今日记录）。"""
    seconds = max(0, min(payload.seconds, 3600))  # 单次上限 1 小时
    today = _today_str()
    row = (
        db.query(models.StudyRecord)
        .filter(
            models.StudyRecord.user_id == current_user.id,
            models.StudyRecord.study_date == today,
        )
        .first()
    )
    if not row:
        row = models.StudyRecord(
            user_id=current_user.id, study_date=today, seconds=seconds
        )
        db.add(row)
    else:
        row.seconds += seconds
    db.commit()
    return {"date": today, "seconds": row.seconds}


@router.get("/records")
def study_records(
    days: int = 7,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """最近 N 天的学习时长记录（每日累计）。"""
    start = (date.today() - timedelta(days=days - 1)).isoformat()
    rows = (
        db.query(models.StudyRecord)
        .filter(
            models.StudyRecord.user_id == current_user.id,
            models.StudyRecord.study_date >= start,
        )
        .order_by(models.StudyRecord.study_date)
        .all()
    )
    return [
        {"date": r.study_date, "seconds": r.seconds}
        for r in rows
    ]
