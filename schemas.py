from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # "student", "teacher", or "hod"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class QuestionCreate(BaseModel):
    student_id: int
    subject: str
    question_text: str


class AnswerCreate(BaseModel):
    teacher_id: int
    answer_text: str


# NEW: OTP verification schemas
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str


class ResendOTP(BaseModel):
    email: EmailStr

# NEW: AI chatbot schemas
class ChatTurn(BaseModel):
    role: str  # "user" or "ai"
    text: str


class ChatRequest(BaseModel):
    student_id: int
    subject: str = "General"
    question_text: str = Field(..., min_length=1, max_length=2000)
    history: List[ChatTurn] = []  # last few chat turns, only used as context
