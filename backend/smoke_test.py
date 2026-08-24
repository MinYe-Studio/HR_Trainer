"""全功能冒烟测试脚本（S1~S5 回归验证）。

用法（后端需已启动）：
    cd backend && ../.venv/bin/python smoke_test.py

覆盖：认证 / 摸底测试(随机抽题·提交·任务) / 模块章节 / 训练(含案例题·满分自动完成) / 进度
"""
import json
import random
import sys
import urllib.request

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
    results = []

    def check(name, fn):
        try:
            fn()
            results.append((name, True, ""))
            print(f"  ✅ {name}")
        except Exception as e:
            results.append((name, False, str(e)[:100]))
            print(f"  ❌ {name}: {str(e)[:100]}")

    # 0. 健康检查
    def t_health():
        assert api("GET", "/api/health")["status"] == "ok"
    check("健康检查", t_health)

    # 1. 认证
    def t_auth():
        uname = f"smoke_{random.randint(1000, 9999)}"
        auth = api("POST", "/api/auth/register",
                   body={"username": uname, "password": "123456", "nickname": "冒烟测试"})
        assert auth["token"]
        me = api("GET", "/api/auth/me", token=auth["token"])
        assert me["username"] == uname
    check("注册/登录/当前用户", t_auth)

    # 2. 摸底测试
    def t_placement():
        token = api("POST", "/api/auth/login",
                    body={"username": "admin", "password": "admin123"})["token"]
        qs = api("GET", "/api/placement/questions", token=token)
        assert len(qs) == 30
        assert len({q["module_id"] for q in qs}) == 6  # 六大模块各抽 5 题
        answers = {str(q["id"]): [q["options"][0]["key"]] for q in qs}
        r = api("POST", "/api/placement/submit", token=token,
                body={"question_ids": [q["id"] for q in qs], "answers": answers})
        assert 0 <= r["total_score"] <= 100
        tasks = api("GET", "/api/placement/tasks", token=token)
        assert len(tasks["tasks"]) == 6 and tasks["has_placement"]
    check("摸底测试(随机抽题30/提交/教学任务)", t_placement)

    # 3. 模块与章节
    def t_content():
        token = api("POST", "/api/auth/login",
                    body={"username": "admin", "password": "admin123"})["token"]
        mods = api("GET", "/api/modules", token=token)
        assert len(mods) == 6
        rec = api("GET", "/api/modules/recruitment", token=token)
        assert len(rec["chapters"]) == 5
        ch = api("GET", f"/api/modules/recruitment/chapters/{rec['chapters'][0]['id']}", token=token)
        assert "案例引入" in ch["content"] and "费曼自检" in ch["content"]
    check("模块列表/详情/章节内容(案例驱动)", t_content)

    # 4. 训练（知识题+案例题+满分自动完成）
    def t_practice():
        from app.database import SessionLocal
        from app import models
        token = api("POST", "/api/auth/login",
                    body={"username": "admin", "password": "admin123"})["token"]
        qs = api("GET", "/api/modules/recruitment/chapters/1/practice", token=token)
        assert len(qs) == 7  # 5 知识 + 2 案例
        db = SessionLocal()
        real = {q.id: q.answer for q in db.query(models.Question).filter(
            models.Question.chapter_id == 1,
            models.Question.category.in_(["practice", "practice_case"]))}
        db.close()
        ans = {str(q["id"]): list(real[q["id"]]) for q in qs}
        r = api("POST", "/api/practice/submit", token=token,
                body={"chapter_id": 1, "answers": ans})
        assert r["score"] == 100 and r["chapter_completed"] is True
    check("训练(7题含案例/满分自动完成)", t_practice)

    # 5. 进度
    def t_progress():
        token = api("POST", "/api/auth/login",
                    body={"username": "admin", "password": "admin123"})["token"]
        p = api("GET", "/api/progress", token=token)
        assert "chapter_progress" in p
    check("学习进度", t_progress)

    ok = sum(1 for _, ok, _ in results if ok)
    print(f"\n=== 通过 {ok}/{len(results)} 项 ===")
    if ok != len(results):
        sys.exit(1)


if __name__ == "__main__":
    main()
