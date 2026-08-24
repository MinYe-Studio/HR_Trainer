"""学习进度路由：章节完成标记。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/progress", tags=["进度"])


@router.get("")
def get_progress(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前用户的章节学习进度。"""
    rows = (
        db.query(models.ChapterProgress)
        .filter(models.ChapterProgress.user_id == current_user.id)
        .all()
    )
    return {
        "chapter_progress": {
            row.chapter_id: {"completed": row.completed, "completed_at": row.completed_at}
            for row in rows
        }
    }


@router.post("/complete")
def mark_complete(
    payload: schemas.ChapterCompleteRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记/取消章节完成。"""
    chapter = db.get(models.Chapter, payload.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    row = (
        db.query(models.ChapterProgress)
        .filter(
            models.ChapterProgress.user_id == current_user.id,
            models.ChapterProgress.chapter_id == payload.chapter_id,
        )
        .first()
    )
    if not row:
        row = models.ChapterProgress(
            user_id=current_user.id, chapter_id=payload.chapter_id
        )
        db.add(row)

    row.completed = payload.completed
    if payload.completed:
        from datetime import datetime
        row.completed_at = datetime.utcnow()
    else:
        row.completed_at = None

    db.commit()
    return {"chapter_id": payload.chapter_id, "completed": row.completed}
