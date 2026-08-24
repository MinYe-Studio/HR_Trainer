"""端到端联调测试：模拟新用户完整学习闭环。

注册 → 摸底测试 → 教学任务 → 学习章节(标记完成) → 章节训练(满分自动完成)
→ 模块考核(满分通过/自动标记全部章节) → 仪表盘/复习提醒 → 昵称修改

用法：cd backend && ../.venv/bin/python e2e_test.py
"""
import json
import random
import sys
import urllib.request

from app.database import SessionLocal
from app import models

BASE = "http://127.0.0.1:8000"


def api(method, path, token=None, body=None):
    req = urllib.request.Request(f"{BASE}{path}", method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if body is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(body).encode()
    return json.load(urllib.request.urlopen(req))


def main():
    ok = fail = 0
    def check(name, cond, extra=""):
        nonlocal ok, fail
        if cond:
            ok += 1
            print(f"  ✅ {name} {extra}")
        else:
            fail += 1
            print(f"  ❌ {name} {extra}")

    print("=== 新用户完整学习闭环 ===")
    # 1. 注册
    uname = f"e2e_{random.randint(1000, 9999)}"
    auth = api("POST", "/api/auth/register",
               body={"username": uname, "password": "123456", "nickname": "联调学员"})
    token = auth["token"]
    check("注册新用户", bool(token))

    # 2. 摸底测试（随机抽题30，全部答对 → 100分）
    qs = api("GET", "/api/placement/questions", token=token)
    check("摸底抽题30题", len(qs) == 30)
    db = SessionLocal()
    real = {q.id: q.answer for q in db.query(models.Question).filter(models.Question.category == "placement")}
    placement = api("POST", "/api/placement/submit", token=token,
                    body={"question_ids": [q["id"] for q in qs],
                          "answers": {str(q["id"]): list(real[q["id"]]) for q in qs}})
    check("摸底满分", placement["total_score"] == 100, f"({placement['total_score']}分)")

    # 3. 教学任务
    tasks = api("GET", "/api/placement/tasks", token=token)
    check("教学任务6项", len(tasks["tasks"]) == 6 and tasks["has_placement"])

    # 4. 学习章节：随机选一个模块（绩效）全部章节标记完成
    mod = api("GET", "/api/modules/performance", token=token)
    check("绩效模块3章", len(mod["chapters"]) == 3)
    for ch in mod["chapters"]:
        api("POST", "/api/progress/complete", token=token,
            body={"chapter_id": ch["id"], "completed": True})
    prog = api("GET", "/api/progress", token=token)
    done = [c for c in prog["chapter_progress"].values() if c["completed"]]
    check("章节标记完成", len(done) == 3)

    # 5. 章节训练（满分 → 自动完成）
    ch1 = mod["chapters"][0]
    pq = api("GET", f"/api/modules/performance/chapters/{ch1['id']}/practice", token=token)
    check("训练题≥7(含2案例)", len(pq) >= 7 and sum(1 for q in pq if q["category"] == "practice_case") == 2,
          f"({len(pq)}题)")
    rp = {q.id: q.answer for q in db.query(models.Question).filter(
        models.Question.chapter_id == ch1["id"],
        models.Question.category.in_(["practice", "practice_case"]))}
    res = api("POST", "/api/practice/submit", token=token,
              body={"chapter_id": ch1["id"],
                    "answers": {str(q["id"]): list(rp[q["id"]]) for q in pq}})
    check("训练满分", res["score"] == 100 and res["chapter_completed"])

    # 6. 模块考核（满分100通过线，随机抽题10，全对 → 通过 + 自动标记章节）
    eqs = api("GET", "/api/modules/performance/exam/questions", token=token)
    check("考核抽题10(7知识+3案例)",
          len(eqs) == 10 and sum(1 for q in eqs if q["category"] == "exam_case") == 3)
    rex = {q.id: q.answer for q in db.query(models.Question).filter(
        models.Question.module_id == mod["id"],
        models.Question.category.in_(["exam", "exam_case"]))}
    exam = api("POST", "/api/exam/submit", token=token,
               body={"module_code": "performance",
                     "question_ids": [q["id"] for q in eqs],
                     "answers": {str(q["id"]): list(rex[q["id"]]) for q in eqs},
                     "duration_seconds": 300})
    check("考核满分通过", exam["score"] == 100 and exam["passed"], f"({exam['score']}分)")

    # 7. 成绩曲线数据
    records = api("GET", "/api/exam/records?module_code=performance", token=token)
    check("成绩记录(曲线数据)", len(records) == 1 and records[0]["score"] == 100)

    # 8. 统计仪表盘
    stats = api("GET", "/api/stats", token=token)
    check("统计: 考核通过模块", "performance" in stats["exams"]["passed_modules"])
    check("统计: 章节进度", stats["chapters"]["completed"] >= 3)

    # 9. 遗忘曲线复习提醒（刚通过，未到期）
    reviews = api("GET", "/api/dashboard/review", token=token)
    perf = next((r for r in reviews["reviews"] if r["code"] == "performance"), None)
    check("复习提醒: 绩效模块在列", perf is not None)
    check("复习提醒: 未到期", perf and not perf["due"])

    # 10. 昵称修改
    updated = api("PUT", "/api/auth/me", token=token, body={"nickname": "联调学员v2"})
    check("昵称修改", updated["nickname"] == "联调学员v2")
    db.close()

    print(f"\n=== 联调测试: 通过 {ok}/{ok+fail} ===")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
