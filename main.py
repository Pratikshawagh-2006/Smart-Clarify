from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas, auth

Base.metadata.create_all(bind=engine)
app = FastAPI()

# Allow Streamlit (or any frontend) running on a different port to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Smart Clarify backend running"}


@app.post("/auth/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=auth.hash_password(user.password),
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email, "role": new_user.role}


@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_token({"sub": db_user.email, "role": db_user.role, "id": db_user.id})
    # id added here so the frontend (teacher panel) knows which teacher is answering
    return {"access_token": token, "token_type": "bearer", "role": db_user.role, "id": db_user.id}


@app.post("/student/questions")
def submit_question(q: schemas.QuestionCreate, db: Session = Depends(get_db)):
    new_q = models.Question(
        student_id=q.student_id,
        subject=q.subject,
        question_text=q.question_text
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return {"id": new_q.id, "status": new_q.status}


# ---------------------------------------------------------
# NEW: fetch a single student's own doubts (with teacher's
# answer attached, if the doubt has been resolved) — needed
# for the student panel dashboard
# ---------------------------------------------------------

@app.get("/student/questions/{student_id}")
def get_student_questions(student_id: int, db: Session = Depends(get_db)):
    questions = (
        db.query(models.Question)
        .filter(models.Question.student_id == student_id)
        .order_by(models.Question.id.desc())
        .all()
    )

    result = []
    for q in questions:
        answer_text = None

        if q.status == "resolved":
            ans = (
                db.query(models.Answer)
                .filter(models.Answer.question_id == q.id)
                .first()
            )
            if ans:
                answer_text = ans.answer_text

        result.append({
            "id": q.id,
            "subject": q.subject,
            "question_text": q.question_text,
            "status": q.status,
            "answer_text": answer_text
        })

    return result


# ---------------------------------------------------------
# NEW: Teacher-side endpoints (needed for admin.py to work)
# ---------------------------------------------------------

@app.get("/teacher/questions")
def get_questions(status: str = "pending", db: Session = Depends(get_db)):
    questions = db.query(models.Question).filter(models.Question.status == status).all()
    return [
        {
            "id": q.id,
            "student_id": q.student_id,
            "subject": q.subject,
            "question_text": q.question_text,
            "status": q.status
        }
        for q in questions
    ]


@app.post("/teacher/questions/{question_id}/answer")
def answer_question(question_id: int, answer: schemas.AnswerCreate, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    new_answer = models.Answer(
        question_id=question_id,
        teacher_id=answer.teacher_id,
        answer_text=answer.answer_text
    )
    db.add(new_answer)
    question.status = "resolved"
    db.commit()
    return {"message": "Answer submitted", "question_id": question_id}