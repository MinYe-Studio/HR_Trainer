"""数据模型：用户、技能模块、章节、题目、考核、进度、成绩。

设计借鉴 yf-exam-lite / PlayEdu 的「课程→章节→测验→考核→成绩/进度」闭环，
数据库层参考 quizblitz 的 SQLAlchemy 组织方式。
"""
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    """学习者用户。"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    nickname = Column(String(50), default="")
    role = Column(String(20), default="learner")  # learner / admin
    learning_path = Column(JSON, default=list)  # 个性化学习路径（模块 code 顺序，空=默认）
    created_at = Column(DateTime, server_default=func.now())

    progress = relationship("ChapterProgress", back_populates="user")
    practice_records = relationship("PracticeRecord", back_populates="user")
    exam_records = relationship("ExamRecord", back_populates="user")
    placement_records = relationship("PlacementRecord", back_populates="user")
    review_records = relationship("ReviewRecord", back_populates="user")
    study_records = relationship("StudyRecord", back_populates="user")


class SkillModule(Base):
    """技能模块（如：招聘与面试、劳动法与合规）。"""
    __tablename__ = "skill_modules"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)  # recruitment / labor-law / ...
    name = Column(String(100), nullable=False)
    description = Column(Text, default="")
    icon = Column(String(50), default="")  # 前端图标名
    sort_order = Column(Integer, default=0)

    chapters = relationship("Chapter", back_populates="module", order_by="Chapter.sort_order")


class Chapter(Base):
    """知识点章节（讲解内容 + 训练题目归属）。"""
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("skill_modules.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text, default="")
    content = Column(Text, default="")  # Markdown 讲解内容
    sort_order = Column(Integer, default=0)

    module = relationship("SkillModule", back_populates="chapters")
    questions = relationship("Question", back_populates="chapter")
    progress = relationship("ChapterProgress", back_populates="chapter")


class Question(Base):
    """题目：讲解章节配套练习或模块考核用。"""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True, index=True)
    module_id = Column(Integer, ForeignKey("skill_modules.id"), nullable=False, index=True)
    category = Column(String(20), default="practice")  # practice(章节训练) / exam(模块考核)
    qtype = Column(String(20), default="single")  # single / multiple / judge
    stem = Column(Text, nullable=False)  # 题干
    options = Column(JSON, default=list)  # [{key:"A", text:"..."}]
    answer = Column(JSON, default=list)  # 正确答案 key 列表，如 ["A"]
    explanation = Column(Text, default="")  # 答案解析
    sort_order = Column(Integer, default=0)

    chapter = relationship("Chapter", back_populates="questions")
    module = relationship("SkillModule")


class ExamPaper(Base):
    """模块考核卷。"""
    __tablename__ = "exam_papers"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("skill_modules.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    pass_score = Column(Integer, default=60)  # 百分制通过线
    duration_minutes = Column(Integer, default=20)
    created_at = Column(DateTime, server_default=func.now())

    module = relationship("SkillModule")
    records = relationship("ExamRecord", back_populates="paper")


class ExamRecord(Base):
    """考核成绩记录。"""
    __tablename__ = "exam_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    exam_paper_id = Column(Integer, ForeignKey("exam_papers.id"), nullable=False, index=True)
    score = Column(Integer, default=0)  # 百分制
    passed = Column(Boolean, default=False)
    answers = Column(JSON, default=dict)  # {question_id: [key,...]}
    question_ids = Column(JSON, default=list)  # 本次试卷题目 ID（用于结果重算）
    duration_seconds = Column(Integer, default=0)  # 答题耗时（秒）
    submitted_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="exam_records")
    paper = relationship("ExamPaper", back_populates="records")


class ChapterProgress(Base):
    """章节学习进度（完成标记）。"""
    __tablename__ = "chapter_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="progress")
    chapter = relationship("Chapter", back_populates="progress")


class PracticeRecord(Base):
    """章节训练记录（答题情况）。"""
    __tablename__ = "practice_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=False, index=True)
    correct_count = Column(Integer, default=0)
    total_count = Column(Integer, default=0)
    answers = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="practice_records")


class PlacementRecord(Base):
    """入营能力摸底测试记录。"""
    __tablename__ = "placement_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    answers = Column(JSON, default=dict)              # {question_id: [key,...]}
    total_score = Column(Integer, default=0)          # 百分制总分
    module_scores = Column(JSON, default=dict)        # {module_code: {"correct":n,"total":n,"score":n}}
    completed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="placement_records")


class ReviewRecord(Base):
    """遗忘曲线复习记录（艾宾浩斯间隔复习打卡）。"""
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("skill_modules.id"), nullable=False, index=True)
    reviewed_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="review_records")


class StudyRecord(Base):
    """学习时长记录（按用户+日期累计）。"""
    __tablename__ = "study_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    study_date = Column(String(10), nullable=False, index=True)  # YYYY-MM-DD
    seconds = Column(Integer, default=0)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="study_records")
