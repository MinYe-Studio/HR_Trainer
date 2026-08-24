"""个性化教学任务计算。

根据摸底测试各模块得分，生成推荐学习任务：
- score < 60  → focus        重点学习（先讲解→训练→考核）
- 60 <= score < 80 → consolidate  巩固提升（快速过讲解→重点训练→考核）
- score >= 80 → express      快速通道（直接训练+考核）
"""
from .. import models


def level_of(score: int) -> tuple[str, str, str]:
    """返回 (level, level_label, recommended_action)。"""
    if score < 60:
        return (
            "focus",
            "重点学习",
            "从讲解开始系统学习，完成章节训练与模块考核",
        )
    if score < 80:
        return (
            "consolidate",
            "巩固提升",
            "快速浏览讲解，重点完成训练并参加模块考核",
        )
    return (
        "express",
        "快速通道",
        "基础知识扎实，直接参加训练与模块考核",
    )


def build_tasks(module_scores: dict, modules: list[models.SkillModule]) -> list[dict]:
    """根据摸底得分构建排序后的学习任务列表。"""
    tasks = []
    for m in modules:
        ms = module_scores.get(m.code, {})
        score = ms.get("score", 0) if isinstance(ms, dict) else 0
        correct = ms.get("correct", 0) if isinstance(ms, dict) else 0
        total = ms.get("total", 0) if isinstance(ms, dict) else 0
        level, label, action = level_of(score)
        tasks.append(
            {
                "module_id": m.id,
                "code": m.code,
                "name": m.name,
                "icon": m.icon,
                "score": score,
                "correct": correct,
                "total": total,
                "level": level,
                "level_label": label,
                "recommended_action": action,
            }
        )

    # 排序：重点学习（得分低者优先）→ 巩固提升 → 快速通道
    level_rank = {"focus": 0, "consolidate": 1, "express": 2}
    tasks.sort(
        key=lambda t: (level_rank[t["level"]], t["score"])
    )
    for i, t in enumerate(tasks, start=1):
        t["order"] = i
    return tasks
