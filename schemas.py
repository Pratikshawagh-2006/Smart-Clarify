from pydantic import BaseModel, EmailStr


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