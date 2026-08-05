from typing import Optional, List
from pydantic import BaseModel, Field, field_validator


class CourseBase(BaseModel):
    course_name: str
    credits: int = Field(..., ge=1, le=6, description="Credits must be between 1 and 6 inclusive")


class CourseCreate(CourseBase):
    student_id: int


class CourseUpdate(BaseModel):
    course_name: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=6)
    student_id: Optional[int] = None


class CourseResponse(CourseBase):
    id: int
    student_id: int

    class Config:
        from_attributes = True


class StudentBase(BaseModel):
    name: str
    email: str
    age: int = Field(..., gt=0, description="Age must be strictly greater than 0")

    @field_validator("email")
    @classmethod
    def validate_email_contains_at(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email must contain an '@' character")
        return value


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = Field(None, gt=0)

    @field_validator("email")
    @classmethod
    def validate_email_contains_at(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and "@" not in value:
            raise ValueError("Email must contain an '@' character")
        return value


class StudentResponse(StudentBase):
    id: int
    courses: List[CourseResponse] = []

    class Config:
        from_attributes = True


class StudentCourseCountResponse(BaseModel):
    student_id: int
    course_count: int
