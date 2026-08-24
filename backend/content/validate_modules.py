"""模块内容 JSON 校验脚本（S8 用）。

校验 backend/content/module_*.json：
- JSON 合法性
- 结构完整性（chapters/exam/questions）
- 题量（每章 5 知识 + 2 案例；考核 ≥7 知识 + 3 案例）
- 题目合法性（qtype/options/answer 有效，答案 key 存在于选项）
用法：cd backend && ../.venv/bin/python content/validate_modules.py
"""
import json
import sys
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent
VALID_QTYPES = {"single", "multiple", "judge"}


def validate_question(q, path):
    errors = []
    if q.get("qtype") not in VALID_QTYPES:
        errors.append(f"{path}: 非法 qtype={q.get('qtype')}")
    opts = q.get("options") or []
    keys = [o.get("key") for o in opts if isinstance(o, dict)]
    if len(keys) < 2:
        errors.append(f"{path}: 选项不足 (stem={q.get('stem', '')[:20]})")
    for a in q.get("answer") or []:
        if a not in keys:
            errors.append(f"{path}: 答案 key={a} 不在选项中 (stem={q.get('stem', '')[:20]})")
    if q.get("qtype") == "judge" and sorted(keys) != ["A", "B"]:
        errors.append(f"{path}: 判断题选项必须是 A/B")
    if not q.get("explanation"):
        errors.append(f"{path}: 缺少解析 (stem={q.get('stem', '')[:20]})")
    return errors


def validate_module(path: Path):
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"{path.name}: JSON 解析失败 - {e}"]

    code = data.get("code")
    name = data.get("name")
    if not code or not name:
        errors.append(f"{path.name}: 缺少 code/name")

    chapters = data.get("chapters") or []
    if len(chapters) != 3:
        errors.append(f"{path.name}: 章节数 {len(chapters)}（应为 3）")

    total_practice = 0
    total_case = 0
    for i, ch in enumerate(chapters):
        p = f"{path.name}/ch{i}"
        if not ch.get("title") or not ch.get("content"):
            errors.append(f"{p}: 缺少 title/content")
        # 案例驱动结构检查
        content = ch.get("content", "")
        for marker in ["案例引入", "带着问题学", "案例复盘", "费曼自检"]:
            if marker not in content:
                errors.append(f"{p}: 缺少「{marker}」结构")
        qs = ch.get("questions") or []
        cqs = ch.get("case_questions") or []
        if not (5 <= len(qs) <= 6):
            errors.append(f"{p}: 知识题 {len(qs)}（应为 5~6）")
        if len(cqs) != 2:
            errors.append(f"{p}: 案例题 {len(cqs)}（应为 2）")
        for j, q in enumerate(qs):
            errors += validate_question(q, f"{p}/q{j}")
        for j, q in enumerate(cqs):
            if not str(q.get("stem", "")).startswith("【案例】"):
                errors.append(f"{p}/case{j}: 案例题题干应以【案例】开头")
            errors += validate_question(q, f"{p}/case{j}")
        total_practice += len(qs)
        total_case += len(cqs)

    exam = data.get("exam")
    if not exam:
        errors.append(f"{path.name}: 缺少 exam")
    else:
        eqs = exam.get("questions") or []
        ecqs = exam.get("case_questions") or []
        if len(eqs) < 7:
            errors.append(f"{path.name}/exam: 知识题 {len(eqs)}（应 ≥7 供随机抽题）")
        if len(ecqs) != 3:
            errors.append(f"{path.name}/exam: 案例题 {len(ecqs)}（应为 3）")
        for j, q in enumerate(eqs):
            errors += validate_question(q, f"{path.name}/exam/q{j}")
        for j, q in enumerate(ecqs):
            if not str(q.get("stem", "")).startswith("【案例】"):
                errors.append(f"{path.name}/exam/case{j}: 案例题题干应以【案例】开头")
            errors += validate_question(q, f"{path.name}/exam/case{j}")

    return errors


def main():
    files = sorted(CONTENT_DIR.glob("module_*.json"))
    if not files:
        print("未找到 module_*.json 文件")
        return
    total_errors = 0
    for f in files:
        errors = validate_module(f)
        if errors:
            print(f"❌ {f.name}: {len(errors)} 个问题")
            for e in errors[:10]:
                print(f"   - {e}")
            if len(errors) > 10:
                print(f"   ... 共 {len(errors)} 个")
        else:
            print(f"✅ {f.name}: 结构完整")
        total_errors += len(errors)
    print(f"\n=== 校验完成: {'全部通过' if total_errors == 0 else f'{total_errors} 个问题'} ===")
    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
