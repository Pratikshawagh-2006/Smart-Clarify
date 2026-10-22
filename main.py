from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import engine, get_db, Base
import models, schemas, auth, email_utils

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "Smart Clarify backend running"}


# ---------------------------------------------------------
# AUTH — register sends an OTP instead of activating the
# account immediately. If an unverified account already
# exists for this email, we UPDATE it instead of deleting
# it (deleting could fail if it's already linked to other
# rows, like questions, via a foreign key).
# ---------------------------------------------------------

@app.post("/auth/register")
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    otp = email_utils.generate_otp()

    if existing:
        if existing.is_verified:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Unverified leftover — update it instead of deleting
        existing.name = user.name
        existing.password_hash = auth.hash_password(user.password)
        existing.role = user.role
        existing.otp_code = otp
        existing.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.commit()
        db.refresh(existing)
        target_user = existing
    else:
        target_user = models.User(
            name=user.name,
            email=user.email,
            password_hash=auth.hash_password(user.password),
            role=user.role,
            is_verified=False,
            otp_code=otp,
            otp_expiry=datetime.utcnow() + timedelta(minutes=10)
        )
        db.add(target_user)
        db.commit()
        db.refresh(target_user)

    email_sent = email_utils.send_otp_email(user.email, otp)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email. Check the email address / SMTP setup.")

    return {"message": "OTP sent to your email. Please verify to complete registration.", "id": target_user.id}


@app.post("/auth/verify-otp")
def verify_otp(data: schemas.OTPVerify, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == data.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.is_verified:
        return {"message": "Already verified"}

    if db_user.otp_code != data.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if datetime.utcnow() > db_user.otp_expiry:
        raise HTTPException(status_code=400, detail="OTP expired, please request a new one")

    db_user.is_verified = True
    db_user.otp_code = None
    db_user.otp_expiry = None
    db.commit()

    return {"message": "Email verified successfully. You can now log in."}


@app.post("/auth/resend-otp")
def resend_otp(data: schemas.ResendOTP, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == data.email).first()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if db_user.is_verified:
        return {"message": "Already verified"}

    otp = email_utils.generate_otp()
    db_user.otp_code = otp
    db_user.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
    db.commit()

    email_sent = email_utils.send_otp_email(data.email, otp)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send OTP email.")

    return {"message": "New OTP sent to your email."}


@app.post("/auth/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not db_user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified. Please verify the OTP sent to your email first.")

    token = auth.create_token({"sub": db_user.email, "role": db_user.role, "id": db_user.id})
    return {"access_token": token, "token_type": "bearer", "role": db_user.role, "id": db_user.id}


# ---------------------------------------------------------
# STUDENT
# ---------------------------------------------------------

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


@app.get("/student/questions/{student_id}")
def get_my_questions(student_id: int, db: Session = Depends(get_db)):
    """
    Returns every doubt a student has asked, along with the
    teacher's answer if one exists yet.
    """
    questions = (
        db.query(models.Question)
        .filter(models.Question.student_id == student_id)
        .order_by(models.Question.id.desc())
        .all()
    )

    result = []
    for q in questions:
        answer = db.query(models.Answer).filter(models.Answer.question_id == q.id).first()
        result.append({
            "id": q.id,
            "subject": q.subject,
            "question_text": q.question_text,
            "status": q.status,
            "answer_text": answer.answer_text if answer else None
        })

    return result


# ---------------------------------------------------------
# TEACHER
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


# ---------------------------------------------------------
# NEW: HOD DASHBOARD
# ---------------------------------------------------------

@app.get("/hod/teacher-performance")
def teacher_performance(db: Session = Depends(get_db)):
    """
    For each teacher: how many questions they've actually
    answered (proof of real work, not just claimed).
    """
    teachers = db.query(models.User).filter(models.User.role == "teacher").all()

    result = []
    for t in teachers:
        resolved_count = (
            db.query(models.Answer)
            .filter(models.Answer.teacher_id == t.id)
            .count()
        )
        result.append({
            "teacher_id": t.id,
            "name": t.name,
            "email": t.email,
            "questions_resolved": resolved_count
        })

    # Highest performer first
    result.sort(key=lambda x: x["questions_resolved"], reverse=True)
    return result


@app.get("/hod/overview")
def hod_overview(db: Session = Depends(get_db)):
    """
    High-level counts for the HOD dashboard's summary cards.
    """
    total_students = db.query(models.User).filter(models.User.role == "student").count()
    total_teachers = db.query(models.User).filter(models.User.role == "teacher").count()
    total_questions = db.query(models.Question).count()
    resolved_questions = db.query(models.Question).filter(models.Question.status == "resolved").count()
    pending_questions = db.query(models.Question).filter(models.Question.status == "pending").count()

    return {
        "total_students": total_students,
        "total_teachers": total_teachers,
        "total_questions": total_questions,
        "resolved_questions": resolved_questions,
        "pending_questions": pending_questions
    }