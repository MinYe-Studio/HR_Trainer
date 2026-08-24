"""考核题库合并脚本：将 content/extra_exam_*.json 的原创题并入各模块考核知识题库。

用法：cd backend && ../.venv/bin/python content/merge_extra_exam.py
（幂等：题干已存在的跳过）
"""
import json
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent


def main():
    for f in sorted(CONTENT_DIR.glob("extra_exam_*.json")):
        code = f.name.replace("extra_exam_", "").replace(".json", "")
        module_file = CONTENT_DIR / f"module_{code}.json"
        if not module_file.exists():
            print(f"⚠️ {code}: 模块文件不存在，跳过")
            continue
        try:
            extra = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"⚠️ {f.name}: JSON 解析失败 {e}")
            continue

        data = json.loads(module_file.read_text(encoding="utf-8"))
        exam = data.setdefault("exam", {})
        bank = exam.setdefault("questions", [])
        existing = {q["stem"] for q in bank}
        added = 0
        for q in extra:
            if q["stem"] not in existing:
                bank.append(q)
                existing.add(q["stem"])
                added += 1
        module_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"✅ {code}: 合并 {added} 道题（现有 {len(bank)} 道）")


if __name__ == "__main__":
    main()
