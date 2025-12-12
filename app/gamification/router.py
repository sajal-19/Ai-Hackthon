# app/gamification/router.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_db, require_roles
from app.users_org.models import User, UserRole
from app.trainings.models import Training
from app.gamification import models, schemas

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post(
    "",
    response_model=schemas.QuizRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(UserRole.ADMIN, UserRole.SUPER_ADMIN))],
)
def create_quiz(
    quiz_in: schemas.QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = db.query(Training).filter(Training.id == quiz_in.training_id).first()
    if not training:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training not found",
        )

    quiz = models.Quiz(
        training_id=quiz_in.training_id,
        title=quiz_in.title,
        description=quiz_in.description,
    )
    db.add(quiz)
    db.flush()

    for q in quiz_in.questions:
        question = models.Question(
            quiz_id=quiz.id,
            text=q.text,
        )
        db.add(question)
        db.flush()
        for opt in q.options:
            option = models.Option(
                question_id=question.id,
                text=opt.text,
                is_correct=opt.is_correct,
            )
            db.add(option)

    db.commit()
    db.refresh(quiz)

    # manually load questions/options for response
    return schemas.QuizRead(
        id=quiz.id,
        training_id=quiz.training_id,
        title=quiz.title,
        description=quiz.description,
        questions=[
            schemas.QuestionRead(
                id=question.id,
                text=question.text,
                options=[
                    schemas.OptionRead(
                        id=opt.id,
                        text=opt.text,
                        is_correct=opt.is_correct,
                    )
                    for opt in question.options
                ],
            )
            for question in quiz.questions
        ],
    )


@router.get(
    "/by-training/{training_id}",
    response_model=List[schemas.QuizRead],
    dependencies=[Depends(get_current_user)],
)
def list_quizzes_for_training(
    training_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quizzes = db.query(models.Quiz).filter(models.Quiz.training_id == training_id).all()
    result: List[schemas.QuizRead] = []
    for quiz in quizzes:
        result.append(
            schemas.QuizRead(
                id=quiz.id,
                training_id=quiz.training_id,
                title=quiz.title,
                description=quiz.description,
                questions=[
                    schemas.QuestionRead(
                        id=q.id,
                        text=q.text,
                        options=[
                            schemas.OptionRead(
                                id=o.id,
                                text=o.text,
                                is_correct=o.is_correct,
                            )
                            for o in q.options
                        ],
                    )
                    for q in quiz.questions
                ],
            )
        )
    return result


@router.post(
    "/{quiz_id}/submit",
    response_model=schemas.QuizSubmissionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def submit_quiz(
    quiz_id: int,
    submission_in: schemas.QuizSubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quiz = db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Compute score: 1 point per question if selected option is the correct one
    answers = submission_in.answers
    max_score = float(len(quiz.questions))
    score = 0.0

    for question in quiz.questions:
        selected_option_id = answers.get(question.id)
        if selected_option_id is None:
            continue
        option = next((o for o in question.options if o.id == selected_option_id), None)
        if option and option.is_correct:
            score += 1.0

    passed = score >= max_score * 0.6  # e.g., 60% threshold

    submission = models.QuizSubmission(
        quiz_id=quiz.id,
        user_id=current_user.id,
        score=score,
        max_score=max_score,
        passed=passed,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    return submission
