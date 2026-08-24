"""遗忘曲线复习计划（艾宾浩斯间隔复习）。

间隔：1 天 → 2 天 → 4 天 → 7 天 → 15 天 → 30 天
以模块最近一次考核通过时间为起点，计算各间隔的复习安排。
"""
from datetime import datetime, timedelta

REVIEW_INTERVALS = [1, 2, 4, 7, 15, 30]


def build_review(
    last_pass_at: datetime,
    now: datetime,
    review_count_after_pass: int = 0,
) -> dict:
    """根据上次通过时间与已复习次数，计算复习状态。

    返回: {elapsed_days, due, pending_reviews, next_interval_days, next_review_at}
    """
    elapsed_days = max(0, (now - last_pass_at).days)
    due_count = sum(1 for iv in REVIEW_INTERVALS if iv <= elapsed_days)
    pending = max(0, due_count - review_count_after_pass)

    next_idx = review_count_after_pass
    if next_idx >= len(REVIEW_INTERVALS):
        next_interval_days = None
        next_review_at = None
    else:
        next_interval_days = REVIEW_INTERVALS[next_idx]
        next_review_at = last_pass_at + timedelta(days=next_interval_days)

    return {
        "elapsed_days": elapsed_days,
        "due": pending > 0,
        "pending_reviews": pending,
        "next_interval_days": next_interval_days,
        "next_review_at": next_review_at,
    }
