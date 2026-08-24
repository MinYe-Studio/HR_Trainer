"""考核路由：随机抽题组卷、提交判分、成绩记录。"""
import random
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..routers.auth import get_current_user

router = APIRouter(tags=["考核"])

KNOWLEDGE_PER_EXAM = 7   # 每卷知识题数
CASE_PER_EXAM = 3        # 每卷案例题数


def _q_out(q: models.Question) -> dict:
    return {
        "id": q.id,
        "chapter_id": q.chapter_id,
        "module_id": q.module_id,
        "category": q.category,
        "qtype": q.qtype,
        "stem": q.stem,
        "options": q.options or [],
        "sort_order": q.sort_order or 0,
    }


def _get_module(db: Session, code: str) -> models.SkillModule:
    module = db.query(models.SkillModule).filter(models.SkillModule.code == code).first()
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return module


def _get_paper(db: Session, module_id: int) -> models.ExamPaper:
    paper = (
        db.query(models.ExamPaper)
        .filter(models.ExamPaper.module_id == module_id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="该模块暂未配置考核卷")
    return paper


@router.get("/modules/{code}/exam", response_model=schemas.ExamInfoOut)
def get_exam_info(code: str, db: Session = Depends(get_db)):
    """获取模块考核卷信息。"""
    module = _get_module(db, code)
    paper = _get_paper(db, module.id)
    k = db.query(models.Question).filter(
        models.Question.module_id == module.id,
        models.Question.category == "exam").count()
    c = db.query(models.Question).filter(
        models.Question.module_id == module.id,
        models.Question.category == "exam_case").count()
    return schemas.ExamInfoOut(
        paper_id=paper.id,
        title=paper.title,
        description=paper.description or "",
        pass_score=paper.pass_score or 60,
        duration_minutes=paper.duration_minutes or 0,
        knowledge_count=k,
        case_count=c,
        total=k + c,
    )


@router.get("/modules/{code}/exam/questions", response_model=list[schemas.ExamQuestionOut])
def get_exam_questions(code: str, db: Session = Depends(get_db)):
    """随机抽题组卷：知识题 + 案例题（不含答案），每次不同。"""
    module = _get_module(db, code)
    _get_paper(db, module.id)

    knowledge = (
        db.query(models.Question)
        .filter(
            models.Question.module_id == module.id,
            models.Question.category == "exam",
        )
        .all()
    )
    cases = (
        db.query(models.Question)
        .filter(
            models.Question.module_id == module.id,
            models.Question.category == "exam_case",
        )
        .all()
    )
    if not knowledge:
        raise HTTPException(status_code=404, detail="考核知识题库为空")

    picked_k = random.sample(knowledge, min(KNOWLEDGE_PER_EXAM, len(knowledge)))
    picked_c = random.sample(cases, min(CASE_PER_EXAM, len(cases))) if cases else []
    picked = picked_k + picked_c
    random.shuffle(picked)
    return [_q_out(q) for q in picked]


@router.post("/exam/submit", response_model=schemas.ExamResult)
def submit_exam(
    payload: schemas.ExamSubmitRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """提交考核答卷：判分 + 保存记录 + 通过则自动标记模块章节完成。"""
    module = _get_module(db, payload.module_code)
    paper = _get_paper(db, module.id)
    if not payload.question_ids:
        raise HTTPException(status_code=400, detail="试卷为空，请重新获取题目")

    questions = (
        db.query(models.Question)
        .filter(
            models.Question.module_id == module.id,
            models.Question.category.in_(["exam", "exam_case"]),
            models.Question.id.in_(payload.question_ids),
        )
        .all()
    )
    if not questions:
        raise HTTPException(status_code=404, detail="考核题库为空")

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

    total = len(questions)
    score = round(correct_count / total * 100) if total else 0
    pass_score = paper.pass_score or 60
    passed = score >= pass_score

    record = models.ExamRecord(
        user_id=current_user.id,
        exam_paper_id=paper.id,
        score=score,
        passed=passed,
        answers=payload.answers,
        question_ids=payload.question_ids,
        duration_seconds=payload.duration_seconds or 0,
    )
    db.add(record)

    # 通过 → 自动标记该模块全部章节完成
    chapter_auto_completed = False
    if passed:
        chapters = (
            db.query(models.Chapter)
            .filter(models.Chapter.module_id == module.id)
            .all()
        )
        for ch in chapters:
            prog = (
                db.query(models.ChapterProgress)
                .filter(
                    models.ChapterProgress.user_id == current_user.id,
                    models.ChapterProgress.chapter_id == ch.id,
                )
                .first()
            )
            if not prog:
                prog = models.ChapterProgress(
                    user_id=current_user.id, chapter_id=ch.id
                )
                db.add(prog)
            if not prog.completed:
                prog.completed = True
                prog.completed_at = datetime.utcnow()
                chapter_auto_completed = True

    db.commit()
    db.refresh(record)

    return schemas.ExamResult(
        exam_record_id=record.id,
        module_id=module.id,
        module_code=module.code,
        module_name=module.name,
        score=score,
        passed=passed,
        pass_score=pass_score,
        duration_seconds=record.duration_seconds,
        chapter_auto_completed=chapter_auto_completed,
        details=details,
    )


@router.get("/exam/result/{record_id}", response_model=schemas.ExamResult)
def exam_result_detail(
    record_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """考核结果详情（从保存的答卷重算逐题反馈）。"""
    r = db.get(models.ExamRecord, record_id)
    if not r or r.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="成绩记录不存在")
    module = r.paper.module
    qids = r.question_ids or []
    questions = (
        db.query(models.Question)
        .filter(models.Question.id.in_(qids))
        .all()
    ) if qids else []
    details = []
    for q in questions:
        user_answer = (r.answers or {}).get(str(q.id), [])
        details.append(
            {
                "question_id": q.id,
                "category": q.category,
                "qtype": q.qtype,
                "stem": q.stem,
                "options": q.options or [],
                "user_answer": user_answer,
                "correct_answer": q.answer or [],
                "correct": sorted(user_answer) == sorted(q.answer or []),
                "explanation": q.explanation or "",
            }
        )
    return schemas.ExamResult(
        exam_record_id=r.id,
        module_id=module.id,
        module_code=module.code,
        module_name=module.name,
        score=r.score,
        passed=r.passed,
        pass_score=r.paper.pass_score or 60,
        duration_seconds=r.duration_seconds or 0,
        chapter_auto_completed=False,
        details=details,
    )


@router.get("/exam/records", response_model=list[schemas.ExamRecordOut])
def exam_records(
    module_code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """模块考核历史成绩（分数-时间曲线数据）。"""
    module = _get_module(db, module_code)
    paper = _get_paper(db, module.id)
    rows = (
        db.query(models.ExamRecord)
        .filter(
            models.ExamRecord.user_id == current_user.id,
            models.ExamRecord.exam_paper_id == paper.id,
        )
        .order_by(models.ExamRecord.id)
        .all()
    )
    return [
        schemas.ExamRecordOut(
            id=r.id,
            module_code=module.code,
            module_name=module.name,
            score=r.score,
            passed=r.passed,
            duration_seconds=r.duration_seconds or 0,
            submitted_at=r.submitted_at,
        )
        for r in rows
    ]


@router.get("/exam/latest", response_model=schemas.ExamRecordOut | None)
def latest_exam(
    module_code: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """模块最近一次考核成绩。"""
    module = _get_module(db, module_code)
    paper = _get_paper(db, module.id)
    r = (
        db.query(models.ExamRecord)
        .filter(
            models.ExamRecord.user_id == current_user.id,
            models.ExamRecord.exam_paper_id == paper.id,
        )
        .order_by(models.ExamRecord.id.desc())
        .first()
    )
    if not r:
        return None
    return schemas.ExamRecordOut(
        id=r.id,
        module_code=module.code,
        module_name=module.name,
        score=r.score,
        passed=r.passed,
        duration_seconds=r.duration_seconds or 0,
        submitted_at=r.submitted_at,
    )
