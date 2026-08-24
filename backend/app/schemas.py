"""Pydantic 请求/响应模式。"""
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict


# ---------- 认证 ----------
class RegisterRequest(BaseModel):
    username: str
    password: str
    nickname: Optional[str] = ""


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    nickname: str
    role: str
    created_at: datetime


class AuthResponse(BaseModel):
    token: str
    user: UserOut


# ---------- 内容 ----------
class OptionOut(BaseModel):
    key: str
    text: str


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chapter_id: Optional[int]
    module_id: int
    category: str
    qtype: str
    stem: str
    options: List[OptionOut]
    sort_order: int


class ChapterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    module_id: int
    title: str
    summary: str
    sort_order: int


class ChapterDetail(ChapterOut):
    content: str


class ModuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str
    icon: str
    sort_order: int
    chapters: List[ChapterOut] = []


# ---------- 训练/考核 ----------
class PracticeSubmitRequest(BaseModel):
    chapter_id: int
    answers: dict[str, list[str]]  # {question_id: [key,...]}


class PracticeQuestionOut(QuestionOut):
    """章节训练题（不含答案）。"""


class SubmitAnswerRequest(BaseModel):
    answers: dict[str, list[str]]  # {question_id: [key,...]}


class PracticeResult(BaseModel):
    chapter_id: int
    correct_count: int
    total_count: int
    score: int  # 百分制
    chapter_completed: bool = False  # 满分时自动标记章节完成
    details: List[dict[str, Any]]


class ExamSubmitRequest(BaseModel):
    answers: dict[str, list[str]]


class ExamResult(BaseModel):
    exam_paper_id: int
    score: int
    passed: bool
    pass_score: int
    details: List[dict[str, Any]]


class ExamRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_paper_id: int
    score: int
    passed: bool
    submitted_at: datetime


# ---------- 进度 ----------
class ChapterCompleteRequest(BaseModel):
    chapter_id: int
    completed: bool = True


class StatsOut(BaseModel):
    total_chapters: int
    completed_chapters: int
    practice_count: int
    exam_count: int
    passed_exams: int


# ---------- 摸底测试 ----------
class PlacementQuestionOut(QuestionOut):
    """摸底测试题（不含答案）。"""


class ModuleScoreOut(BaseModel):
    module_id: int
    code: str
    name: str
    icon: str = ""
    correct: int
    total: int
    score: int          # 百分制
    level: str          # focus / consolidate / express


class PlacementSubmitRequest(BaseModel):
    question_ids: list[int]      # 本次试卷包含的题目 ID（随机抽题组卷）
    answers: dict[str, list[str]]


class PlacementResultOut(BaseModel):
    record_id: int
    total_score: int
    submitted_at: datetime
    module_scores: List[ModuleScoreOut]


class LearningTaskOut(BaseModel):
    module_id: int
    code: str
    name: str
    icon: str = ""
    score: int
    level: str                  # focus / consolidate / express
    level_label: str            # 重点学习 / 巩固提升 / 快速通道
    recommended_action: str     # 建议学习路径
    order: int


class TasksResponse(BaseModel):
    tasks: List[LearningTaskOut]
    has_placement: bool
    updated_at: Optional[datetime] = None
