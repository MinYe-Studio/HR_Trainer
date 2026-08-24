"""内容数据导出脚本：从数据库导出全部内容为前端静态数据 JS。

数据库是标注（知识点/章节关联）后的最终数据源。
用法：cd backend && ../.venv/bin/python export_content.py
输出：../frontend/src/data/app-content.js
"""
import json
from collections import Counter
from pathlib import Path

from app.database import SessionLocal
from app import models

BACKEND_DIR = Path(__file__).resolve().parent
OUT = BACKEND_DIR.parent / "frontend" / "src" / "data" / "app-content.js"


def build():
    db = SessionLocal()
    try:
        modules = []
        chapters = []
        questions = []

        for m in db.query(models.SkillModule).order_by(models.SkillModule.sort_order).all():
            modules.append({
                "code": m.code, "name": m.name, "icon": m.icon or "",
                "description": m.description or "", "sort_order": m.sort_order or 0,
            })

        for c in db.query(models.Chapter).order_by(models.Chapter.module_id, models.Chapter.sort_order).all():
            chapters.append({
                "id": c.id, "module_code": c.module.code,
                "title": c.title, "summary": c.summary or "",
                "content": c.content or "", "sort_order": c.sort_order or 0,
            })

        for q in db.query(models.Question).order_by(models.Question.module_id, models.Question.category, models.Question.sort_order).all():
            questions.append({
                "id": q.id, "module_code": q.module.code,
                "chapter_id": q.chapter_id, "category": q.category,
                "qtype": q.qtype, "stem": q.stem,
                "options": q.options or [], "answer": q.answer or [],
                "explanation": q.explanation or "",
                "knowledge_point": q.knowledge_point or "",
                "sort_order": q.sort_order or 0,
            })
    finally:
        db.close()

    data = {
        "meta": {
            "version": "1.0",
            "modules_count": len(modules),
            "chapters_count": len(chapters),
            "questions_count": len(questions),
        },
        "modules": modules,
        "chapters": chapters,
        "questions": questions,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    js = "// 自动生成：单机版内容数据（backend/export_content.py 生成，勿手改）\nexport default " + json.dumps(data, ensure_ascii=False)
    OUT.write_text(js, encoding="utf-8")
    print(f"✅ 导出完成: {OUT}")
    print(f"   模块 {len(modules)} | 章节 {len(chapters)} | 题目 {len(questions)}")
    print(f"   题类分布: {dict(Counter(q['category'] for q in questions))}")
    kp = sum(1 for q in questions if q["knowledge_point"])
    print(f"   带知识点: {kp}/{len(questions)}")


if __name__ == "__main__":
    build()
