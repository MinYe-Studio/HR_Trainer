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
    # 幂等：跳过已存在的题干，避免重复播种；已存在则同步知识点/章节
    existing_rows = (
        db.query(models.Question)
        .filter(
            models.Question.module_id == module.id,
            models.Question.category == category,
        )
        .all()
    )
    existing = {q.stem: q for q in existing_rows}
    added = 0
    for i, q in enumerate(questions, start=start_order):
        row = existing.get(q["stem"])
        if row:
            # 同步知识点与章节关联（保留原题目内容）
            if q.get("knowledge_point"):
                row.knowledge_point = q["knowledge_point"]
            if chapter is not None:
                row.chapter_id = chapter.id
            elif q.get("chapter_id"):
                row.chapter_id = q["chapter_id"]
            continue
        item = models.Question(
            module_id=module.id,
            chapter_id=q.get("chapter_id") or (chapter.id if chapter else None),
            category=category,
            qtype=q["qtype"],
            stem=q["stem"],
            options=q["options"],
            answer=q["answer"],
            explanation=q.get("explanation", ""),
            knowledge_point=q.get("knowledge_point", ""),
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
    # 排序优先级：JSON 显式指定 > MODULES 规范排序
    canonical = next((m for m in MODULES if m["code"] == data["code"]), None)
    sort_order = data.get("sort_order", canonical["sort_order"] if canonical else 0)
    mod = _upsert_module(
        db,
        {
            "code": data["code"],
            "name": data["name"],
            "icon": data.get("icon", ""),
            "description": data.get("description", ""),
            "sort_order": sort_order,
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
        # 训练题自动标注知识点 = 章节主题（去掉"第X章 "前缀）
        topic = ch["title"].split(" ", 1)[1] if " " in ch["title"] else ch["title"]
        _annotate_practice_kp(db, mod.id, chapter.id, topic)

    exam = data.get("exam")
    if exam:
        paper = _upsert_exam_paper(db, mod.id, exam)
        # 考核题：支持 chapter_index（所属章节序号）与 knowledge_point（知识点）
        module_chapters = (
            db.query(models.Chapter)
            .filter(models.Chapter.module_id == mod.id)
            .order_by(models.Chapter.sort_order)
            .all()
        )
        for q in exam.get("questions", []):
            ch = None
            if q.get("chapter_index") is not None and q["chapter_index"] < len(module_chapters):
                ch = module_chapters[q["chapter_index"]]
            _add_questions(db, [q], mod, category="exam", chapter=ch)
        if exam.get("case_questions"):
            for q in exam["case_questions"]:
                ch = None
                if q.get("chapter_index") is not None and q["chapter_index"] < len(module_chapters):
                    ch = module_chapters[q["chapter_index"]]
                _add_questions(db, [q], mod, category="exam_case", chapter=ch, start_order=100)


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


# 招聘模块考核题的知识点标注（子串匹配 → 章节序号/知识点）
# 章节：0=岗位需求分析 1=结构化面试 2=评估与录用 3=战略性招聘 4=雇主品牌
RECRUITMENT_EXAM_META = [
    ("招聘流程的起点", 0, "岗位需求分析"),
    ("岗位的核心产出指标", 0, "岗位说明书构成"),
    ("任职资格越严格", 0, "任职资格匹配"),
    ("STAR 法则中 R", 1, "STAR法则"),
    ("结构化面试的优势", 1, "结构化面试"),
    ("最后一个问题回答出色", 1, "面试认知偏差"),
    ("概括性回答时应", 1, "行为面试与STAR追问"),
    ("背景调查的目的", 2, "背景调查"),
    ("专业能力通常占多少权重", 2, "评估维度与权重"),
    ("书面 Offer 应包含", 2, "Offer与录用决策"),
    ("人才规划四步法中", 3, "人才规划四步法"),
    ("高人才密度\"理念", 4, "高人才密度"),
    ("任期计划\"，其目的", 4, "任期制"),
    ("数据驱动招聘决策", 4, "数据驱动招聘"),
    ("EVP）在招聘中的作用", 4, "EVP雇主品牌"),
    ("【案例】陈工说", 0, "岗位需求分析"),
    ("【案例】\"聊得来\"但 STAR", 1, "结构化面试与行为证据"),
    ("【案例】何工因薪资低", 4, "EVP与任期制"),
]


def _annotate_recruitment_exam(db) -> None:
    """为招聘模块考核题补充知识点与章节关联。"""
    mod = db.query(models.SkillModule).filter(models.SkillModule.code == "recruitment").first()
    if not mod:
        return
    chapters = (
        db.query(models.Chapter)
        .filter(models.Chapter.module_id == mod.id)
        .order_by(models.Chapter.sort_order)
        .all()
    )
    qs = db.query(models.Question).filter(
        models.Question.module_id == mod.id,
        models.Question.category.in_(["exam", "exam_case"]),
    ).all()
    updated = 0
    for q in qs:
        for frag, ch_idx, kp in RECRUITMENT_EXAM_META:
            if frag in q.stem:
                q.knowledge_point = kp
                if ch_idx < len(chapters):
                    q.chapter_id = chapters[ch_idx].id
                updated += 1
                break
    if updated:
        print(f"  [标注] 招聘考核题知识点 +{updated}")


def _annotate_practice_kp(db, module_id, chapter_id, topic) -> None:
    """训练题知识点自动标注（按章节主题）。"""
    rows = (
        db.query(models.Question)
        .filter(
            models.Question.module_id == module_id,
            models.Question.chapter_id == chapter_id,
            models.Question.category.in_(["practice", "practice_case"]),
        )
        .all()
    )
    for r in rows:
        if not r.knowledge_point:
            r.knowledge_point = topic


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
        _annotate_recruitment_exam(db)

        # ---- 其他模块（JSON 文件，S8）----
        _seed_json_modules(db)

        db.commit()
        print("[seed] 完成 ✅")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
