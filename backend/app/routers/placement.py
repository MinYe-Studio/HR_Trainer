"""摸底测试与个性化教学任务路由。

题库机制：题库中每模块有多道摸底题，每次测试按 per_module 随机抽题组卷，
提交时携带本次试卷的题目 ID，只对本次试卷判分。
"""
import random
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user
from ..services import learning_tasks

router = APIRouter(prefix="/placement", tags=["摸底测试"])

QUESTIONS_PER_MODULE = 5


def _question_out(q: models.Question) -> dict:
    return {
        "id": q.id,
        "chapter_id": q.chapter_id,
        "module_id": q.module_id,
        "category": q.category,
        "qtype": q.qtype,
        "stem": q.stem,
        "options": q.options or [],
        "sort_order": q.sort_order,
    }


@router.get("/questions", response_model=list[schemas.PlacementQuestionOut])
def get_placement_questions(
    per_module: int = QUESTIONS_PER_MODULE,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取摸底测试题目（不含答案）。

    从题库中为每个模块随机抽取 per_module 道题组卷，每次调用题目不同。
    """
    all_questions = (
        db.query(models.Question)
        .filter(models.Question.category == "placement")
        .all()
    )
    by_module: dict[int, list] = defaultdict(list)
    for q in all_questions:
        by_module[q.module_id].append(q)

    selected = []
    for module_id, qs in by_module.items():
        k = min(per_module, len(qs))
        selected.extend(random.sample(qs, k))

    selected.sort(key=lambda q: (q.module_id, q.sort_order))
    return [_question_out(q) for q in selected]


@router.post("/submit", response_model=schemas.PlacementResultOut)
def submit_placement(
    payload: schemas.PlacementSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交摸底测试答案：只对本次试卷（question_ids）中的题目判分。"""
    if not payload.question_ids:
        raise HTTPException(status_code=400, detail="试卷为空，请重新获取题目")

    questions = (
        db.query(models.Question)
        .filter(
            models.Question.category == "placement",
            models.Question.id.in_(payload.question_ids),
        )
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail="摸底测试题库为空，请先初始化种子数据")

    module_scores: dict = {}
    total_correct = 0
    total_count = len(questions)

    for q in questions:
        user_answer = payload.answers.get(str(q.id), [])
        correct = sorted(user_answer) == sorted(q.answer or [])
        ms = module_scores.setdefault(
            q.module.code,
            {"module_id": q.module_id, "correct": 0, "total": 0},
        )
        ms["total"] += 1
        if correct:
            ms["correct"] += 1
            total_correct += 1

    for code, ms in module_scores.items():
        ms["score"] = round(ms["correct"] / ms["total"] * 100) if ms["total"] else 0

    total_score = round(total_correct / total_count * 100) if total_count else 0

    record = models.PlacementRecord(
        user_id=current_user.id,
        answers=payload.answers,
        total_score=total_score,
        module_scores=module_scores,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    modules = db.query(models.SkillModule).order_by(models.SkillModule.sort_order).all()
    module_out = []
    for m in modules:
        ms = module_scores.get(m.code, {"correct": 0, "total": 0, "score": 0})
        level, _, _ = learning_tasks.level_of(ms.get("score", 0))
        module_out.append(
            schemas.ModuleScoreOut(
                module_id=m.id,
                code=m.code,
                name=m.name,
                icon=m.icon,
                correct=ms.get("correct", 0),
                total=ms.get("total", 0),
                score=ms.get("score", 0),
                level=level,
            )
        )

    return schemas.PlacementResultOut(
        record_id=record.id,
        total_score=total_score,
        submitted_at=record.created_at,
        module_scores=module_out,
    )


@router.get("/latest", response_model=schemas.PlacementResultOut | None)
def latest_placement(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取最近一次摸底测试结果。"""
    record = (
        db.query(models.PlacementRecord)
        .filter(models.PlacementRecord.user_id == current_user.id)
        .order_by(models.PlacementRecord.id.desc())
        .first()
    )
    if not record:
        return None

    modules = db.query(models.SkillModule).order_by(models.SkillModule.sort_order).all()
    module_out = []
    for m in modules:
        ms = record.module_scores.get(m.code, {"correct": 0, "total": 0, "score": 0})
        level, _, _ = learning_tasks.level_of(ms.get("score", 0))
        module_out.append(
            schemas.ModuleScoreOut(
                module_id=m.id,
                code=m.code,
                name=m.name,
                icon=m.icon,
                correct=ms.get("correct", 0),
                total=ms.get("total", 0),
                score=ms.get("score", 0),
                level=level,
            )
        )

    return schemas.PlacementResultOut(
        record_id=record.id,
        total_score=record.total_score,
        submitted_at=record.created_at,
        module_scores=module_out,
    )


@router.get("/tasks", response_model=schemas.TasksResponse)
def get_learning_tasks(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取个性化教学任务（基于最近一次摸底测试）。"""
    record = (
        db.query(models.PlacementRecord)
        .filter(models.PlacementRecord.user_id == current_user.id)
        .order_by(models.PlacementRecord.id.desc())
        .first()
    )
    modules = db.query(models.SkillModule).order_by(models.SkillModule.sort_order).all()

    if not record:
        # 未参加测试：全部按重点学习处理（新学员）
        empty = {m.code: {"correct": 0, "total": 0, "score": 0} for m in modules}
        tasks = learning_tasks.build_tasks(empty, modules)
        return schemas.TasksResponse(tasks=tasks, has_placement=False, updated_at=None)

    tasks = learning_tasks.build_tasks(record.module_scores, modules)
    return schemas.TasksResponse(
        tasks=tasks,
        has_placement=True,
        updated_at=record.created_at,
    )
