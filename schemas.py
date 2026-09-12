from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str  # "student" or "teacher"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class QuestionCreate(BaseModel):
    student_id: int
    subject: str
    question_text: str


# NEW: used by /teacher/questions/{id}/answer
class AnswerCreate(BaseModel):
    teacher_id: int
    answer_text: str