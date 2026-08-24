"""种子数据脚本：建表 + 管理员账号 + 六大模块 + 摸底测试题 + 招聘模块课程内容。

用法：python -m app.seed
"""
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
        rec_mod = modules["recruitment"]
        for ch in RECRUITMENT["chapters"]:
            # 幂等：按模块+标题查重
            chapter = (
                db.query(models.Chapter)
                .filter(
                    models.Chapter.module_id == rec_mod.id,
                    models.Chapter.title == ch["title"],
                )
                .first()
            )
            if not chapter:
                chapter = models.Chapter(
                    module_id=rec_mod.id,
                    title=ch["title"],
                    summary=ch["summary"],
                    content=ch["content"],
                    sort_order=RECRUITMENT["chapters"].index(ch),
                )
                db.add(chapter)
                db.flush()
                print(f"  [章节] 新增: {ch['title']}")
            else:
                # 已存在：同步更新概要/内容/顺序（保留题目）
                chapter.summary = ch["summary"]
                chapter.content = ch["content"]
                chapter.sort_order = RECRUITMENT["chapters"].index(ch)
                print(f"  [章节] 已存在，内容已同步: {ch['title']}")
            _add_questions(db, ch["questions"], rec_mod, category="practice", chapter=chapter)
            if ch.get("case_questions"):
                _add_questions(
                    db,
                    ch["case_questions"],
                    rec_mod,
                    category="practice_case",
                    chapter=chapter,
                    start_order=100,
                )

        exam = RECRUITMENT["exam"]
        # 幂等：按模块+标题查重
        paper = (
            db.query(models.ExamPaper)
            .filter(
                models.ExamPaper.module_id == rec_mod.id,
                models.ExamPaper.title == exam["title"],
            )
            .first()
        )
        if not paper:
            paper = models.ExamPaper(
                module_id=rec_mod.id,
                title=exam["title"],
                description=exam["description"],
                pass_score=exam["pass_score"],
                duration_minutes=exam["duration_minutes"],
            )
            db.add(paper)
            db.flush()
            print(f"  [考核] 新增: {exam['title']}")
        else:
            paper.description = exam["description"]
            paper.pass_score = exam["pass_score"]
            paper.duration_minutes = exam["duration_minutes"]
            print(f"  [考核] 已存在，信息已同步: {exam['title']}")
        _add_questions(db, exam["questions"], rec_mod, category="exam")

        db.commit()
        print("[seed] 完成 ✅")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
