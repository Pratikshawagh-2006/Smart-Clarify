from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, TIMESTAMP, Boolean, func
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(Enum("student", "teacher", "hod"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    # NEW: email verification fields
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String(6), nullable=True)
    otp_expiry = Column(TIMESTAMP, nullable=True)


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    subject = Column(String(100))
    question_text = Column(Text)
    status = Column(Enum("pending", "auto_resolved", "escalated", "resolved"), default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    answer_text = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())