# app/gamification/schemas.py
from typing import List, Dict
from pydantic import BaseModel


class OptionBase(BaseModel):
    text: str
    is_correct: bool = False


class OptionCreate(OptionBase):
    pass


class OptionRead(OptionBase):
    id: int

    class Config:
        from_attributes = True


class QuestionBase(BaseModel):
    text: str


class QuestionCreate(QuestionBase):
    options: List[OptionCreate]


class QuestionRead(QuestionBase):
    id: int
    options: List[OptionRead]

    class Config:
        from_attributes = True


class QuizBase(BaseModel):
    title: str
    description: str | None = None
    training_id: int


class QuizCreate(QuizBase):
    questions: List[QuestionCreate]


class QuizRead(QuizBase):
    id: int
    questions: List[QuestionRead]

    class Config:
        from_attributes = True


class QuizSubmissionCreate(BaseModel):
    # mapping question_id -> chosen option_id
    answers: Dict[int, int]


class QuizSubmissionRead(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    score: float
    max_score: float
    passed: bool

    class Config:
        from_attributes = True
