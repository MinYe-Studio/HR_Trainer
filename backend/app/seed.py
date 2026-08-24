"""种子数据脚本：建表 + 管理员账号 + 六大模块 + 摸底测试题 + 各模块课程内容。

用法：python -m app.seed
内容来源：
- content_data.py（招聘与面试模块 + 摸底题）
- content/module_*.json（S8 起其他模块，由子代理/外部编写）
"""
import json
from pathlib import Path

from .content_data import MODULES, PLACEMENT_QUESTIONS, RECRUITMENT
from .database import Base, SessionLocal, engine
from . import models  # noqa: F401
from .utils import auth as auth_utils

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def _upsert_module(db, m):
    mod = db.query(models.SkillModule).filter(models.SkillModule.code == m["code"]).first()
    if not mod:
        mod = models.SkillModule(**m)
        db.add(mod)
        db.flush()
        print(f"  [模块] 新增: {m['name']}")
    else:
        for k, v in m.items():
            setattr(mod, k, v)
    return mod


def _add_questions(db, questions, module, category, chapter=None, start_order=0):
    # 幂等：跳过已存在的题干，避免重复播种
    existing = {
        row[0]
        for row in db.query(models.Question.stem)
        .filter(
            models.Question.module_id == module.id,
            models.Question.category == category,
        )
        .all()
    }
    added = 0
    for i, q in enumerate(questions, start=start_order):
        if q["stem"] in existing:
            continue
        item = models.Question(
            module_id=module.id,
            chapter_id=chapter.id if chapter else None,
            category=category,
            qtype=q["qtype"],
            stem=q["stem"],
            options=q["options"],
            answer=q["answer"],
            explanation=q.get("explanation", ""),
            sort_order=i,
        )
        db.add(item)
        added += 1
    if added:
        print(f"    [新增] {category} 题库 +{added} 题")


def _upsert_exam_paper(db, module_id, exam, paper_title=None):
    """幂等：按模块+标题查重考核卷。"""
    title = exam.get("title") or paper_title
    paper = (
        db.query(models.ExamPaper)
        .filter(
            models.ExamPaper.module_id == module_id,
            models.ExamPaper.title == title,
        )
        .first()
    )
    if not paper:
        paper = models.ExamPaper(
            module_id=module_id,
            title=title,
            description=exam.get("description", ""),
            pass_score=exam.get("pass_score", 100),
            duration_minutes=exam.get("duration_minutes", 15),
        )
        db.add(paper)
        db.flush()
        print(f"  [考核] 新增: {title}")
    else:
        paper.description = exam.get("description", paper.description or "")
        paper.pass_score = exam.get("pass_score", paper.pass_score or 100)
        paper.duration_minutes = exam.get("duration_minutes", paper.duration_minutes or 15)
        print(f"  [考核] 已存在，信息已同步: {title}")
    return paper


def _seed_module_dict(db, data: dict) -> None:
    """从模块字典（JSON）播种完整模块内容。"""
    mod = _upsert_module(
        db,
        {
            "code": data["code"],
            "name": data["name"],
            "icon": data.get("icon", ""),
            "description": data.get("description", ""),
            "sort_order": data.get("sort_order", 0),
        },
    )
    for idx, ch in enumerate(data.get("chapters", [])):
        chapter = (
            db.query(models.Chapter)
            .filter(
                models.Chapter.module_id == mod.id,
                models.Chapter.title == ch["title"],
            )
            .first()
        )
        if not chapter:
            chapter = models.Chapter(
                module_id=mod.id,
                title=ch["title"],
                summary=ch.get("summary", ""),
                content=ch.get("content", ""),
                sort_order=idx,
            )
            db.add(chapter)
            db.flush()
            print(f"  [章节] 新增: {ch['title']}")
        else:
            chapter.summary = ch.get("summary", chapter.summary or "")
            chapter.content = ch.get("content", chapter.content or "")
            chapter.sort_order = idx
            print(f"  [章节] 已存在，内容已同步: {ch['title']}")
        _add_questions(db, ch.get("questions", []), mod, category="practice", chapter=chapter)
        if ch.get("case_questions"):
            _add_questions(db, ch["case_questions"], mod, category="practice_case", chapter=chapter, start_order=100)

    exam = data.get("exam")
    if exam:
        paper = _upsert_exam_paper(db, mod.id, exam)
        _add_questions(db, exam.get("questions", []), mod, category="exam")
        if exam.get("case_questions"):
            _add_questions(db, exam["case_questions"], mod, category="exam_case", start_order=100)


def _seed_json_modules(db) -> None:
    """播种 backend/content/ 目录下的模块 JSON 文件。"""
    content_dir = Path(__file__).resolve().parent.parent / "content"
    if not content_dir.exists():
        return
    for f in sorted(content_dir.glob("module_*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  ⚠️ 跳过 {f.name}：JSON 解析失败 {e}")
            continue
        print(f"[seed] 写入模块: {data.get('name')} ({f.name})")
        _seed_module_dict(db, data)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # ---- 管理员 ----
        if not db.query(models.User).filter(models.User.username == ADMIN_USERNAME).first():
            db.add(
                models.User(
                    username=ADMIN_USERNAME,
                    password_hash=auth_utils.hash_password(ADMIN_PASSWORD),
                    nickname="管理员",
                    role="admin",
                )
            )
            print(f"[seed] 已创建管理员账号: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")
        else:
            print("[seed] 管理员账号已存在，跳过")

        # ---- 六大模块 ----
        print("[seed] 写入技能模块...")
        modules = {}
        for m in MODULES:
            modules[m["code"]] = _upsert_module(db, m)
        db.flush()

        # ---- 摸底测试题（30 题）----
        print("[seed] 写入摸底测试题...")
        for code, questions in PLACEMENT_QUESTIONS.items():
            mod = modules[code]
            _add_questions(db, questions, mod, category="placement")
            print(f"  [摸底] {mod.name}: {len(questions)} 题")

        # ---- 招聘与面试模块完整内容 ----
        print("[seed] 写入招聘与面试模块课程...")
        rec_meta = next(m for m in MODULES if m["code"] == "recruitment")
        _seed_module_dict(db, {**rec_meta, **RECRUITMENT})

        # ---- 其他模块（JSON 文件，S8）----
        _seed_json_modules(db)

        db.commit()
        print("[seed] 完成 ✅")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
