from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_students(db: Session, min_age: Optional[int] = None) -> List[models.Student]:
    query = db.query(models.Student)
    if min_age is not None:
        query = query.filter(models.Student.age >= min_age)
    return query.all()


def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(
        name=student.name,
        email=student.email,
        age=student.age,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session, student_id: int, student_data: schemas.StudentUpdate
) -> Optional[models.Student]:
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    update_dict = student_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_student, key, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    db.delete(db_student)
    db.commit()
    return True


def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses(db: Session) -> List[models.Course]:
    return db.query(models.Course).all()


def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(
        course_name=course.course_name,
        credits=course.credits,
        student_id=course.student_id,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update_course(
    db: Session, course_id: int, course_data: schemas.CourseUpdate
) -> Optional[models.Course]:
    db_course = get_course(db, course_id)
    if not db_course:
        return None
    
    update_dict = course_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    db_course = get_course(db, course_id)
    if not db_course:
        return False
    db.delete(db_course)
    db.commit()
    return True


def get_student_course_count(db: Session, student_id: int) -> int:
    """
    Computes course count for a student using a database-level aggregate query.
    Uses db.query(func.count(models.Course.id)).filter(...)
    """
    count = db.query(func.count(models.Course.id)).filter(models.Course.student_id == student_id).scalar()
    return count or 0
