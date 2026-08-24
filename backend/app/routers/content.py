"""内容路由：技能模块、章节（讲解/训练/考核页面共用）。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/modules", tags=["内容"])


def _module_out(db: Session, m: models.SkillModule) -> schemas.ModuleOut:
    chapters = (
        db.query(models.Chapter)
        .filter(models.Chapter.module_id == m.id)
        .order_by(models.Chapter.sort_order)
        .all()
    )
    return schemas.ModuleOut(
        id=m.id,
        code=m.code,
        name=m.name,
        description=m.description or "",
        icon=m.icon or "",
        sort_order=m.sort_order or 0,
        chapters=[
            schemas.ChapterOut(
                id=c.id,
                module_id=c.module_id,
                title=c.title,
                summary=c.summary or "",
                sort_order=c.sort_order or 0,
            )
            for c in chapters
        ],
    )


@router.get("", response_model=list[schemas.ModuleOut])
def list_modules(db: Session = Depends(get_db)):
    """获取技能模块列表（含章节概要）。"""
    modules = (
        db.query(models.SkillModule)
        .order_by(models.SkillModule.sort_order)
        .all()
    )
    return [_module_out(db, m) for m in modules]


@router.get("/{code}", response_model=schemas.ModuleOut)
def get_module(code: str, db: Session = Depends(get_db)):
    """获取单个模块详情（含章节列表）。"""
    module = (
        db.query(models.SkillModule)
        .filter(models.SkillModule.code == code)
        .first()
    )
    if not module:
        raise HTTPException(status_code=404, detail="模块不存在")
    return _module_out(db, module)


@router.get("/{code}/chapters/{chapter_id}", response_model=schemas.ChapterDetail)
def get_chapter(code: str, chapter_id: int, db: Session = Depends(get_db)):
    """获取章节讲解内容（Markdown）。"""
    chapter = db.get(models.Chapter, chapter_id)
    if not chapter or chapter.module.code != code:
        raise HTTPException(status_code=404, detail="章节不存在")
    return schemas.ChapterDetail(
        id=chapter.id,
        module_id=chapter.module_id,
        title=chapter.title,
        summary=chapter.summary or "",
        sort_order=chapter.sort_order or 0,
        content=chapter.content or "",
    )


@router.get(
    "/{code}/chapters/{chapter_id}/practice",
    response_model=list[schemas.PracticeQuestionOut],
)
def get_practice_questions(code: str, chapter_id: int, db: Session = Depends(get_db)):
    """获取章节训练题（不含答案）：知识巩固题 + 案例应用题。"""
    chapter = db.get(models.Chapter, chapter_id)
    if not chapter or chapter.module.code != code:
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
    return [
        schemas.PracticeQuestionOut(
            id=q.id,
            chapter_id=q.chapter_id,
            module_id=q.module_id,
            category=q.category,
            qtype=q.qtype,
            stem=q.stem,
            options=q.options or [],
            sort_order=q.sort_order or 0,
        )
        for q in questions
    ]
