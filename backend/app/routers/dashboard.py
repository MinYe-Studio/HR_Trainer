"""首页仪表盘：遗忘曲线复习提醒。"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..routers.auth import get_current_user
from ..services import forgetting_curve

router = APIRouter(prefix="/dashboard", tags=["仪表盘"])


@router.get("/review")
def get_reviews(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """计算各模块的遗忘曲线复习提醒。"""
    modules = (
        db.query(models.SkillModule)
        .order_by(models.SkillModule.sort_order)
        .all()
    )
    now = datetime.utcnow()
    reviews = []
    for m in modules:
        # 最近一次通过考核的时间
        paper = (
            db.query(models.ExamPaper)
            .filter(models.ExamPaper.module_id == m.id)
            .first()
        )
        last_pass = None
        if paper:
            rec = (
                db.query(models.ExamRecord)
                .filter(
                    models.ExamRecord.user_id == current_user.id,
                    models.ExamRecord.exam_paper_id == paper.id,
                    models.ExamRecord.passed.is_(True),
                )
                .order_by(models.ExamRecord.id.desc())
                .first()
            )
            if rec:
                last_pass = rec.submitted_at

        if not last_pass:
            continue  # 尚未通过考核，不安排复习提醒

        review_count = (
            db.query(models.ReviewRecord)
            .filter(
                models.ReviewRecord.user_id == current_user.id,
                models.ReviewRecord.module_id == m.id,
                models.ReviewRecord.reviewed_at >= last_pass,
            )
            .count()
        )
        schedule = forgetting_curve.build_review(last_pass, now, review_count)
        reviews.append(
            {
                "module_id": m.id,
                "code": m.code,
                "name": m.name,
                "icon": m.icon or "",
                "last_pass_at": last_pass,
                "elapsed_days": schedule["elapsed_days"],
                "due": schedule["due"],
                "pending_reviews": schedule["pending_reviews"],
                "next_interval_days": schedule["next_interval_days"],
                "next_review_at": schedule["next_review_at"],
            }
        )

    reviews.sort(key=lambda r: (0 if r["due"] else 1, r["next_interval_days"] or 999))
    return {"reviews": reviews}


@router.post("/review/{module_code}/done")
def review_done(
    module_code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录一次复习打卡。"""
    module = (
        db.query(models.SkillModule)
        .filter(models.SkillModule.code == module_code)
        .first()
    )
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    record = models.ReviewRecord(
        user_id=current_user.id,
        module_id=module.id,
    )
    db.add(record)
    db.commit()
    return {"module_code": module_code, "reviewed_at": record.reviewed_at}
