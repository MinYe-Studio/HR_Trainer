"""训练（练习）路由：章节练习判分与记录。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/practice", tags=["训练"])


@router.post("/submit", response_model=schemas.PracticeResult)
def submit_practice(
    payload: schemas.PracticeSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交章节练习答案，逐题判分并保存记录。"""
    chapter = db.get(models.Chapter, payload.chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    questions = (
        db.query(models.Question)
        .filter(
            models.Question.chapter_id == chapter.id,
            models.Question.category.in_(["practice", "practice_case"]),
        )
        .order_by(models.Question.sort_order)
        .all()
    )
    # 知识题在前，案例题在后
    questions.sort(key=lambda q: (1 if q.category == "practice_case" else 0, q.sort_order))
    if not questions:
        raise HTTPException(status_code=404, detail="本章暂无训练题")

    details = []
    correct_count = 0
    for q in questions:
        user_answer = payload.answers.get(str(q.id), [])
        is_correct = sorted(user_answer) == sorted(q.answer or [])
        if is_correct:
            correct_count += 1
        details.append(
            {
                "question_id": q.id,
                "category": q.category,
                "qtype": q.qtype,
                "stem": q.stem,
                "options": q.options or [],
                "user_answer": user_answer,
                "correct_answer": q.answer or [],
                "correct": is_correct,
                "explanation": q.explanation or "",
            }
        )

    total_count = len(questions)
    score = round(correct_count / total_count * 100) if total_count else 0

    record = models.PracticeRecord(
        user_id=current_user.id,
        chapter_id=chapter.id,
        correct_count=correct_count,
        total_count=total_count,
        answers=payload.answers,
    )
    db.add(record)

    # 满分（100分）自动标记章节完成
    chapter_completed = False
    if score == 100:
        prog = (
            db.query(models.ChapterProgress)
            .filter(
                models.ChapterProgress.user_id == current_user.id,
                models.ChapterProgress.chapter_id == chapter.id,
            )
            .first()
        )
        if not prog:
            prog = models.ChapterProgress(
                user_id=current_user.id, chapter_id=chapter.id
            )
            db.add(prog)
        if not prog.completed:
            from datetime import datetime

            prog.completed = True
            prog.completed_at = datetime.utcnow()
        chapter_completed = True

    db.commit()

    return schemas.PracticeResult(
        chapter_id=chapter.id,
        correct_count=correct_count,
        total_count=total_count,
        score=score,
        chapter_completed=chapter_completed,
        details=details,
    )


@router.get("/records")
def list_records(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """当前用户的章节练习历史记录。"""
    rows = (
        db.query(models.PracticeRecord)
        .filter(models.PracticeRecord.user_id == current_user.id)
        .order_by(models.PracticeRecord.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": r.id,
            "chapter_id": r.chapter_id,
            "correct_count": r.correct_count,
            "total_count": r.total_count,
            "score": round(r.correct_count / r.total_count * 100) if r.total_count else 0,
            "created_at": r.created_at,
        }
        for r in rows
    ]
