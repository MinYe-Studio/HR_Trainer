"""统计路由：用户学习仪表盘汇总数据。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("")
def get_stats(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """用户学习统计汇总（首页仪表盘数据）。"""
    # 章节进度
    total_chapters = db.query(models.Chapter).count()
    completed_chapters = (
        db.query(models.ChapterProgress)
        .filter(
            models.ChapterProgress.user_id == current_user.id,
            models.ChapterProgress.completed.is_(True),
        )
        .count()
    )

    # 练习统计
    practice_records = (
        db.query(models.PracticeRecord)
        .filter(models.PracticeRecord.user_id == current_user.id)
        .all()
    )
    practice_total_q = sum(r.total_count for r in practice_records)
    practice_correct_q = sum(r.correct_count for r in practice_records)
    practice_accuracy = (
        round(practice_correct_q / practice_total_q * 100)
        if practice_total_q
        else None
    )

    # 考核状态（按模块）
    modules = (
        db.query(models.SkillModule)
        .order_by(models.SkillModule.sort_order)
        .all()
    )
    module_status = []
    passed_codes = []
    for m in modules:
        paper = (
            db.query(models.ExamPaper)
            .filter(models.ExamPaper.module_id == m.id)
            .first()
        )
        latest = None
        if paper:
            latest = (
                db.query(models.ExamRecord)
                .filter(
                    models.ExamRecord.user_id == current_user.id,
                    models.ExamRecord.exam_paper_id == paper.id,
                )
                .order_by(models.ExamRecord.id.desc())
                .first()
            )
        if latest and latest.passed:
            passed_codes.append(m.code)
        module_status.append(
            {
                "module_id": m.id,
                "code": m.code,
                "name": m.name,
                "icon": m.icon or "",
                "exam_score": latest.score if latest else None,
                "exam_passed": latest.passed if latest else False,
                "exam_taken": latest is not None,
                "exam_at": latest.submitted_at if latest else None,
            }
        )

    # 摸底测试
    placement = (
        db.query(models.PlacementRecord)
        .filter(models.PlacementRecord.user_id == current_user.id)
        .order_by(models.PlacementRecord.id.desc())
        .first()
    )

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "nickname": current_user.nickname,
        },
        "chapters": {
            "total": total_chapters,
            "completed": completed_chapters,
            "percent": round(completed_chapters / total_chapters * 100)
            if total_chapters
            else 0,
        },
        "practice": {
            "records": len(practice_records),
            "total_questions": practice_total_q,
            "correct_questions": practice_correct_q,
            "accuracy": practice_accuracy,
        },
        "exams": {
            "total_records": (
                db.query(models.ExamRecord)
                .filter(models.ExamRecord.user_id == current_user.id)
                .count()
            ),
            "passed_modules": passed_codes,
            "passed_count": len(passed_codes),
            "module_status": module_status,
        },
        "placement": {
            "taken": placement is not None,
            "total_score": placement.total_score if placement else None,
            "submitted_at": placement.created_at if placement else None,
        },
    }
